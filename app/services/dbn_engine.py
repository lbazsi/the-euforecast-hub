from __future__ import annotations
from typing import Dict, Any, Tuple, List, DefaultDict
from collections import defaultdict
import numpy as np
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dbn import DBNModelSpec, DBNModelVersion, ForecastRun

logger = logging.getLogger(__name__)

FIXED_STAGES = [
    "Reconnaissance","Weaponization","Delivery","Exploitation","Installation","Command & Control (C2)","Actions on Objectives"
]

def _idx_stages() -> Dict[str, int]:
    return {s:i for i,s in enumerate(FIXED_STAGES)}

def validate_llm_json(spec: Dict[str, Any]):
    warnings = []
    out = dict(spec)
    out["stages"] = FIXED_STAGES
    
    # Normalize any ASCII arrow to Unicode
    for e in out.get("edges", []):
        st = e.get("stage_transition", "")
        if st and "->" in st:
            e["stage_transition"] = st.replace("->", "→")
            logger.warning(f"Normalized ASCII arrow to Unicode in edge: {e.get('source')} -> {e.get('target')}")
    
    # Build node index for stage backfilling
    node_by_id = {n["id"]: n for n in out.get("nodes", []) if n.get("id")}
    
    # Backfill node stages from edges if missing
    for e in out.get("edges", []):
        st = e.get("stage_transition", "")
        if "→" in st:
            a, b = st.split("→", 1)
            a = a.strip()
            b = b.strip()
            if e.get("source") in node_by_id and (not node_by_id[e["source"]].get("stage") or node_by_id[e["source"]].get("stage") == "Reconnaissance"):
                node_by_id[e["source"]]["stage"] = a
                logger.info(f"Backfilled stage '{a}' for node {e.get('source')} from edge transition")
            if e.get("target") in node_by_id and (not node_by_id[e["target"]].get("stage") or node_by_id[e["target"]].get("stage") == "Reconnaissance"):
                node_by_id[e["target"]]["stage"] = b
                logger.info(f"Backfilled stage '{b}' for node {e.get('target')} from edge transition")
    
    # Default any remaining nodes to Reconnaissance
    for n in out.get("nodes", []):
        n.setdefault("stage", "Reconnaissance")
        n.setdefault("state_type", "discrete")
        if n["state_type"] == "discrete" and "state_space" not in n:
            n["state_space"] = ["low", "med", "high"]
    
    # Validate and repair edges (try to repair instead of drop)
    node_ids = {n["id"] for n in out.get("nodes", []) if n.get("id")}
    stage_idx = _idx_stages()
    repaired = []
    edges_to_remove = []
    
    for e in out.get("edges", []):
        st = e.get("stage_transition", "")
        if not st or "→" not in st:
            # Repair from node stages
            src_stage = node_by_id.get(e.get("source"), {}).get("stage", "Reconnaissance")
            try:
                i = stage_idx[src_stage]
            except KeyError:
                i = 0
            a, b = FIXED_STAGES[i], FIXED_STAGES[min(i+1, len(FIXED_STAGES)-1)]
            e["stage_transition"] = f"{a}→{b}"
            repaired.append(e)
            logger.warning(f"Repaired missing stage_transition for edge {e.get('source')} -> {e.get('target')}: {e['stage_transition']}")
        
        a, b = e["stage_transition"].split("→", 1)
        a = a.strip()
        b = b.strip()
        
        if stage_idx.get(b, 99) - stage_idx.get(a, -99) != 1:
            warnings.append(f"Invalid stage transition {e['stage_transition']}; forcing next hop")
            i = stage_idx.get(a, 0)
            e["stage_transition"] = f"{a}→{FIXED_STAGES[min(i+1, len(FIXED_STAGES)-1)]}"
            logger.warning(f"Fixed invalid stage transition: {e['stage_transition']}")
        
        if e.get("source") not in node_ids or e.get("target") not in node_ids:
            warnings.append(f"Edge references unknown nodes; removing: {e}")
            edges_to_remove.append(e)
            logger.warning(f"Dropping edge with unknown nodes: {e.get('source')} -> {e.get('target')}")
    
    # Remove invalid edges
    out["edges"] = [e for e in out.get("edges", []) if e not in edges_to_remove]
    
    if repaired:
        logger.info(f"Repaired {len(repaired)} edges with missing stage_transition")
    if edges_to_remove:
        logger.warning(f"Removed {len(edges_to_remove)} edges with unknown node references")
    
    return out, warnings

def mk_priors_from_llm(spec: Dict[str, Any]) -> Dict[str, Any]:
    pri = {"leak": 0.05, "edge_weights": {}, "alpha0": 1.0}
    for e in spec.get("edges", []):
        w = e.get("strength_hint", 0.5) * e.get("llm_confidence", 0.5)
        pri["edge_weights"][(e["source"], e["target"])] = max(1e-3, min(0.99, w))
    return pri

class DiscreteDBN:
    def __init__(self, spec: Dict[str, Any], priors: Dict[str, Any]):
        self.spec = spec
        self.priors = priors
        self.stages = FIXED_STAGES
        self.stage_idx = _idx_stages()
        self.parents: DefaultDict[str, List[str]] = defaultdict(list)
        for e in spec.get("edges", []):
            self.parents[e["target"]].append(e["source"])
        self.q_params: Dict[tuple, float] = {}   # (parent, child) -> q
        self.q_leak: Dict[str, float] = {}       # child -> q_leak

        for e in spec.get("edges", []):
            s, t = e["source"], e["target"]
            p = priors["edge_weights"].get((s,t), 0.5)
            self.q_params[(s,t)] = max(1e-4, 1.0 - p)
        for n in spec.get("nodes", []):
            self.q_leak[n["id"]] = max(1e-4, 1.0 - priors.get("leak", 0.05))

    def _noisy_or(self, active_parents: List[str], child_id: str) -> float:
        prod = self.q_leak.get(child_id, 0.95)
        for p in active_parents:
            prod *= self.q_params.get((p, child_id), 0.5)
        return 1.0 - prod

    def _node_stage(self, node_id: str) -> str:
        for n in self.spec.get("nodes", []):
            if n["id"] == node_id:
                return n["stage"]
        return "Reconnaissance"

    def fit_em(self, sequences: List[Dict[str,int]], max_iter: int = 50, tol: float = 1e-4):
        last_ll = None
        for it in range(max_iter):
            num = defaultdict(float)
            den = defaultdict(float)
            leak_num = defaultdict(float)
            leak_den = defaultdict(float)
            ll = 0.0

            for seq in sequences:
                for e in self.spec.get("edges", []):
                    s, t = e["source"], e["target"]
                    t_stage = self.stage_idx[self._node_stage(t)]
                    s_stage = t_stage - 1
                    s_key = f"{s}@{s_stage}"
                    t_key = f"{t}@{t_stage}"

                    if s_key not in seq and t_key not in seq:
                        continue
                    parent_active = seq.get(s_key, 0) == 1
                    active_list = [s] if parent_active else []
                    # include other parents if observed
                    for op in self.parents[t]:
                        if op == s: continue
                        op_key = f"{op}@{s_stage}"
                        if seq.get(op_key, 0) == 1:
                            active_list.append(op)
                    p_child = self._noisy_or(active_list, t)

                    if t_key in seq:
                        y = seq[t_key]
                        eps = 1e-9
                        ll += y * np.log(max(eps, p_child)) + (1-y) * np.log(max(eps, 1-p_child))
                        if parent_active:
                            den[(s,t)] += 1.0
                            if y == 1:
                                num[(s,t)] += 1.0
                        leak_den[t] += 1.0
                        if y == 1 and len(active_list) == 0:
                            leak_num[t] += 1.0

            for k in den:
                p_eff = num[k] / max(1.0, den[k])
                self.q_params[k] = max(1e-4, 1.0 - p_eff)
            for t in leak_den:
                p_leak = leak_num[t] / max(1.0, leak_den[t])
                self.q_leak[t] = max(1e-4, 1.0 - p_leak)

            if last_ll is not None and abs(ll - last_ll) < tol:
                break
            last_ll = ll

        return {"iterations": it+1, "last_ll": last_ll}

    def forward_infer(self, evidence: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        stage_scores: Dict[str, Dict[str, float]] = {s: defaultdict(float) for s in FIXED_STAGES}
        for t_idx, stage in enumerate(FIXED_STAGES):
            for n in self.spec.get("nodes", []):
                if n["stage"] != stage: continue
                nid = n["id"]
                parents = self.parents.get(nid, [])
                active_parents = []
                prev_idx = max(0, t_idx-1)
                for p in parents:
                    key = f"{p}@{prev_idx}"
                    if evidence.get(key, 0) == 1:
                        active_parents.append(p)
                p_active = self._noisy_or(active_parents, nid)
                dom = n.get("domain", "General")
                stage_scores[stage][dom] = stage_scores[stage].get(dom, 0.0) + float(p_active)

        for s in FIXED_STAGES:
            total = sum(stage_scores[s].values()) or 1.0
            for d in list(stage_scores[s].keys()):
                stage_scores[s][d] = stage_scores[s][d] / total
        return stage_scores

async def build_spec(session: AsyncSession, spec: Dict[str, Any], settings: Dict[str, Any]):
    v_spec, warnings = validate_llm_json(spec)
    rec = DBNModelSpec(spec=v_spec, settings=settings)
    session.add(rec)
    await session.commit()
    await session.refresh(rec)
    return rec.id, warnings

async def fit_model(session: AsyncSession, spec_id: str, data_bindings: Dict[str, Any], weights: Dict[str, float]):
    spec = await session.get(DBNModelSpec, spec_id)
    if not spec: raise ValueError("Spec not found")
    priors = mk_priors_from_llm(spec.spec)
    model = DiscreteDBN(spec.spec, priors)

    sequences = []
    for src, rows in data_bindings.items():
        w = float(weights.get(src, 1.0))
        for r in rows:
            k = max(1, int(round(w*1)))
            for _ in range(k):
                seq = {k:int(1 if bool(v) else 0) for k,v in r.items()}
                sequences.append(seq)

    fit_info = model.fit_em(sequences, max_iter=50, tol=1e-4)
    # Serialize tuple keys to strings for JSONB storage
    q_params_serialized = {f"{s}->{t}": float(v) for (s, t), v in model.q_params.items()}
    params = {"type":"noisy-or-binary", "q_params": q_params_serialized, "q_leak": model.q_leak, "fit_info": fit_info}
    metrics = {"last_ll": fit_info.get("last_ll", 0.0), "iterations": fit_info.get("iterations", 0)}
    mv = DBNModelVersion(spec_id=spec_id, params=params, metrics=metrics)
    session.add(mv)
    await session.commit()
    await session.refresh(mv)
    return mv.id, metrics

def _coerce_binary_map(d: Dict[str, Any]) -> Dict[str, int]:
    """Normalize evidence/interventions to {node@stage: 0/1} explicitly."""
    out = {}
    for k, v in d.items():
        if isinstance(v, bool):
            out[k] = 1 if v else 0
        elif isinstance(v, (int, float)):
            out[k] = 1 if v != 0 else 0
        elif isinstance(v, str):
            out[k] = 1 if v.strip().lower() in ("1", "true", "yes", "y") else 0
        else:
            out[k] = 0
    return out

async def infer(session: AsyncSession, model_version_id: str, evidence: Dict[str, Any], interventions: Dict[str, Any]):
    mv = await session.get(DBNModelVersion, model_version_id)
    if not mv: raise ValueError("Model version not found")
    spec_row = await session.get(DBNModelSpec, mv.spec_id)
    pri = mk_priors_from_llm(spec_row.spec)
    model = DiscreteDBN(spec_row.spec, pri)
    # Deserialize string keys back to tuples
    q_params_dict = mv.params.get("q_params", {})
    # Handle both string keys (from JSONB) and list keys (if deserialized from JSONB as list)
    for k, v in q_params_dict.items():
        if isinstance(k, str) and "->" in k:
            parts = k.split("->")
            if len(parts) == 2:
                model.q_params[(parts[0], parts[1])] = float(v)
        elif isinstance(k, list) and len(k) == 2:
            # Handle case where JSONB deserialized tuple as list
            model.q_params[(k[0], k[1])] = float(v)
    model.q_leak.update({k: float(v) for k,v in mv.params.get("q_leak", {}).items()})
    
    # Coerce evidence and interventions to binary
    ev = _coerce_binary_map(evidence)
    iv = _coerce_binary_map(interventions)
    ev.update(iv)
    
    stage_post = model.forward_infer(ev)
    domains = set(d for st in stage_post.values() for d in st.keys())
    aggregates = {d: float(np.mean([stage_post[s].get(d,0.0) for s in FIXED_STAGES])) for d in domains}
    fr = ForecastRun(model_version_id=model_version_id, evidence=ev, results={"stage_posteriors": stage_post, "aggregates": aggregates})
    session.add(fr); await session.commit()
    return stage_post, aggregates
