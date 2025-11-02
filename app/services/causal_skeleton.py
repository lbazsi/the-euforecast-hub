from __future__ import annotations
from typing import List, Dict, Tuple
import re
from collections import defaultdict

KILLCHAIN = [
    "Reconnaissance","Weaponization","Delivery","Exploitation","Installation","Command & Control (C2)","Actions on Objectives"
]

def _norm_label(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s[:80].title()

def _node_id(label: str, idx: int) -> str:
    base = re.sub(r"[^A-Za-z0-9]+", "_", label).strip("_").upper()
    if not base:
        base = f"NODE_{idx:03d}"
    return base

def build_skeleton(entities: List[Dict], relations: List[Dict]) -> Dict:
    # Nodes from entities + from relations terms
    node_map: Dict[str, Dict] = {}
    def add_node(term: str):
        t = term.lower().strip()
        if t not in node_map:
            dom = "Environment"
            # try to find domain from entities list
            for e in entities:
                if e.get("entity","").lower() == t:
                    dom = e.get("domain","Environment")
                    break
            node_map[t] = {"label": _norm_label(t), "domain": dom, "type": "event", "confidence": 0.8}
    for e in entities:
        add_node(e.get("entity",""))
    for r in relations:
        add_node(r.get("cause",""))
        add_node(r.get("effect",""))

    nodes = []
    for i,(k,v) in enumerate(node_map.items()):
        nid = _node_id(v["label"], i)
        v.update({"id": nid})
        nodes.append(v)

    # Map label->id for edges
    id_by_label = {v["label"]: v["id"] for v in nodes}
    id_by_term = {k: v["id"] for k,v in node_map.items()}

    edges = []
    for r in relations:
        s_id = id_by_term.get(r["cause"].lower())
        t_id = id_by_term.get(r["effect"].lower())
        if not s_id or not t_id or s_id == t_id:
            continue
        edges.append({
            "source": s_id, "target": t_id, "sign": r.get("sign","+"), 
            "confidence": r.get("confidence",0.7)
        })

    # Stage anchoring: start at Reconnaissance
    return {"nodes": nodes, "edges": edges, "root_stage": "Reconnaissance"}

def to_dbn_spec(skel: Dict) -> Dict:
    nodes = []
    for n in skel.get("nodes", []):
        nodes.append({
            "id": n["id"],
            "label": n["label"],
            "domain": n.get("domain","Environment"),
            "stage": skel.get("root_stage","Reconnaissance"),
            "state_type": "discrete",
            "state_space": ["low","med","high"]
        })
    # All edges move one stage forward from root
    stage_from = skel.get("root_stage","Reconnaissance")
    idx = KILLCHAIN.index(stage_from) if stage_from in KILLCHAIN else 0
    stage_to = KILLCHAIN[min(idx+1, len(KILLCHAIN)-1)]
    edges = []
    for e in skel.get("edges", []):
        edges.append({
            "source": e["source"], "target": e["target"],
            "stage_transition": f"{stage_from}→{stage_to}",
            "strength_hint": float(max(0.05, min(0.95, 0.5 + (0.2 if e.get('sign','+')=='+' else -0.2)))),
            "llm_confidence": float(max(0.1, min(0.99, e.get("confidence", 0.7))))
        })
    return {"nodes": nodes, "edges": edges}

