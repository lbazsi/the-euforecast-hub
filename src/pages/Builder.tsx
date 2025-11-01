import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { FileText, Save, Download, Eye, HelpCircle, X, ChevronDown, Send, Paperclip } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";

interface LinearTrendConfig {
  targetVariable: string;
  predictorVariables: string;
  timeWindowStart: string;
  timeWindowEnd: string;
  forecastHorizon: number;
  regularization: "none" | "ridge" | "lasso";
  confidenceLevel: number;
}

interface PolynomialTrendConfig {
  targetVariable: string;
  predictorVariables: string;
  degree: number;
  forecastHorizon: number;
  regularization: "none" | "ridge" | "lasso";
  confidenceLevel: number;
}

interface CanvasBlock {
  id: string;
  name: string;
  type: string;
  description: string;
  position: { x: number; y: number };
  uploadedFile?: File;
  linearTrendConfig?: LinearTrendConfig;
  polynomialTrendConfig?: PolynomialTrendConfig;
}

const Builder = () => {
  const navigate = useNavigate();
  const [selectedModule, setSelectedModule] = useState("Data");
  const [selectedComponent, setSelectedComponent] = useState<string | null>(null);
  const [canvasBlocks, setCanvasBlocks] = useState<CanvasBlock[]>([]);
  const [selectedBlock, setSelectedBlock] = useState<string | null>(null);
  const [draggingBlock, setDraggingBlock] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [messageInput, setMessageInput] = useState("");
  const [selectedKillChainStage, setSelectedKillChainStage] = useState<string | null>(null);
  const [isCollaborateDialogOpen, setIsCollaborateDialogOpen] = useState(false);
  const [collaborateForm, setCollaborateForm] = useState({
    name: "",
    email: "",
    projectDescription: "",
    uploadedFile: null as File | null
  });
  const [isPublishDialogOpen, setIsPublishDialogOpen] = useState(false);
  const [publishForm, setPublishForm] = useState({
    name: "",
    projectKeywords: "",
    projectDescription: ""
  });
  
  // Store configurations per kill chain stage
  const [stageConfigurations, setStageConfigurations] = useState<{
    [key: string]: {
      domainWeights: {
        environment: number;
        economy: number;
        society: number;
        policy: number;
        technology: number;
      };
      nlRuleInput: string;
      importance: number;
    };
  }>({});

  // Get current stage configuration or default values
  const getCurrentConfig = () => {
    if (!selectedKillChainStage) {
      return {
        domainWeights: { environment: 20, economy: 20, society: 20, policy: 20, technology: 20 },
        nlRuleInput: "",
        importance: 0.5
      };
    }
    return stageConfigurations[selectedKillChainStage] || {
      domainWeights: { environment: 20, economy: 20, society: 20, policy: 20, technology: 20 },
      nlRuleInput: "",
      importance: 0.5
    };
  };

  const currentConfig = getCurrentConfig();

  // Update configuration for current stage
  const updateStageConfig = (updates: Partial<typeof currentConfig>) => {
    if (!selectedKillChainStage) return;
    
    setStageConfigurations(prev => ({
      ...prev,
      [selectedKillChainStage]: {
        ...getCurrentConfig(),
        ...updates
      }
    }));
  };

  const dataComponents = [
    {
      name: "Dataset Selector",
      description: "Connects to Eurostat, Copernicus, and other EU repositories through API links."
    },
    {
      name: "Manual Upload",
      description: "Allows CSV, Excel, or API input with variable mapping."
    },
    {
      name: "Live Feed Connector",
      description: "Integrates near-real-time updates (e.g., weather stations, satellite indices)."
    },
    {
      name: "Preprocessing Block",
      description: "Cleans data — handling missing values, scaling, smoothing, and noise filtering."
    },
    {
      name: "Feature Constructor",
      description: "Lets users create derived indicators (growth rates, moving averages, lag features)."
    }
  ];

  const modelComponents = {
    "Trend Projection Models": [
      { name: "Linear Trend", description: "Simple linear regression model for trend analysis." },
      { name: "Polynomial Trend", description: "Polynomial regression for non-linear trend patterns." },
      { name: "Exponential Growth / Decay", description: "Models exponential growth or decay patterns." },
      { name: "Logistic (Sigmoidal) Trend", description: "S-shaped curve for growth with saturation limits." },
      { name: "Piecewise Regression", description: "Regression with breakpoints for changing trends." }
    ],
    "Causal Models": [
      { name: "Multiple Linear Regression", description: "Linear model with multiple predictor variables." },
      { name: "Bayesian Network", description: "Probabilistic graphical model for causal relationships." },
      { name: "Structural Equation Model (SEM)", description: "Models complex relationships between variables." },
      { name: "Granger Causality Tester", description: "Tests whether one time series predicts another." }
    ]
  };

  const addBlockToCanvas = (component: { name: string; description: string }) => {
    const newBlock: CanvasBlock = {
      id: `block-${Date.now()}`,
      name: component.name,
      type: component.name,
      description: component.description,
      position: { x: 100 + canvasBlocks.length * 30, y: 100 + canvasBlocks.length * 30 }
    };
    setCanvasBlocks([...canvasBlocks, newBlock]);
    setSelectedBlock(newBlock.id);
    setSelectedComponent(null);
  };

  const handleBlockMouseDown = (e: React.MouseEvent, blockId: string) => {
    e.stopPropagation();
    const block = canvasBlocks.find(b => b.id === blockId);
    if (block) {
      setDraggingBlock(blockId);
      setSelectedBlock(blockId);
      setDragOffset({
        x: e.clientX - block.position.x,
        y: e.clientY - block.position.y
      });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (draggingBlock) {
      setCanvasBlocks(canvasBlocks.map(block =>
        block.id === draggingBlock
          ? { ...block, position: { x: e.clientX - dragOffset.x, y: e.clientY - dragOffset.y } }
          : block
      ));
    }
  };

  const handleMouseUp = () => {
    setDraggingBlock(null);
  };

  const handleFileUpload = (blockId: string, file: File) => {
    setCanvasBlocks(canvasBlocks.map(block =>
      block.id === blockId ? { ...block, uploadedFile: file } : block
    ));
  };

  const updateLinearTrendConfig = (blockId: string, config: Partial<LinearTrendConfig>) => {
    setCanvasBlocks(canvasBlocks.map(block => {
      if (block.id === blockId) {
        const currentConfig = block.linearTrendConfig || {
          targetVariable: "",
          predictorVariables: "time",
          timeWindowStart: "",
          timeWindowEnd: "",
          forecastHorizon: 12,
          regularization: "none" as const,
          confidenceLevel: 95
        };
        return {
          ...block,
          linearTrendConfig: { ...currentConfig, ...config }
        };
      }
      return block;
    }));
  };

  const updatePolynomialTrendConfig = (blockId: string, config: Partial<PolynomialTrendConfig>) => {
    setCanvasBlocks(canvasBlocks.map(block => {
      if (block.id === blockId) {
        const currentConfig = block.polynomialTrendConfig || {
          targetVariable: "",
          predictorVariables: "time",
          degree: 2,
          forecastHorizon: 12,
          regularization: "none" as const,
          confidenceLevel: 95
        };
        return {
          ...block,
          polynomialTrendConfig: { ...currentConfig, ...config }
        };
      }
      return block;
    }));
  };

  const getComponentDescription = (componentName: string) => {
    // Check in data components
    const dataComp = dataComponents.find(c => c.name === componentName);
    if (dataComp) return dataComp.description;
    
    // Check in model components
    for (const subsections of Object.values(modelComponents)) {
      const modelComp = subsections.find(c => c.name === componentName);
      if (modelComp) return modelComp.description;
    }
    
    return "No description available.";
  };

  const selectedBlockData = canvasBlocks.find(b => b.id === selectedBlock);

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Top Toolbar */}
      <div className="h-14 border-b border-border bg-card flex items-center justify-center px-4 gap-2">
        <Button variant="ghost" size="sm" className="gap-2">
          <FileText className="h-4 w-4" />
          New
        </Button>
        <Button variant="ghost" size="sm" className="gap-2" onClick={() => setIsPublishDialogOpen(true)}>
          <Save className="h-4 w-4" />
          Publish
        </Button>
        <Button variant="ghost" size="sm" className="gap-2">
          <Download className="h-4 w-4" />
          Export
        </Button>
        <Button variant="ghost" size="sm" className="gap-2" onClick={() => setIsCollaborateDialogOpen(true)}>
          <Eye className="h-4 w-4" />
          Collaborate
        </Button>
        <Button variant="ghost" size="sm" className="gap-2">
          <HelpCircle className="h-4 w-4" />
          Help
        </Button>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <div className="w-64 border-r border-border bg-card p-4 overflow-y-auto">
          <h3 className="font-semibold text-sm mb-4 text-foreground">Configuration</h3>
          {selectedKillChainStage ? (
            <div className="space-y-4">
              <div>
                <label className="text-xs text-muted-foreground mb-2 block">Selected Stage</label>
                <h4 className="font-medium text-sm mb-2 text-foreground">{selectedKillChainStage}</h4>
              </div>

              <Separator />

              <div className="space-y-4">
                <h4 className="font-medium text-sm text-foreground">Domain Weight Sliders</h4>
                <p className="text-xs text-muted-foreground">
                  Adjust probability that new nodes spawn in each domain (sum normalized to 100%)
                </p>

                {/* Environment */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <Label className="text-xs text-muted-foreground">Environment</Label>
                    <span className="text-xs font-medium text-foreground">{currentConfig.domainWeights.environment}%</span>
                  </div>
                  <Slider
                    value={[currentConfig.domainWeights.environment]}
                    onValueChange={([value]) => updateStageConfig({ 
                      domainWeights: { ...currentConfig.domainWeights, environment: value }
                    })}
                    min={0}
                    max={100}
                    step={1}
                    className="w-full"
                  />
                </div>

                {/* Economy */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <Label className="text-xs text-muted-foreground">Economy</Label>
                    <span className="text-xs font-medium text-foreground">{currentConfig.domainWeights.economy}%</span>
                  </div>
                  <Slider
                    value={[currentConfig.domainWeights.economy]}
                    onValueChange={([value]) => updateStageConfig({ 
                      domainWeights: { ...currentConfig.domainWeights, economy: value }
                    })}
                    min={0}
                    max={100}
                    step={1}
                    className="w-full"
                  />
                </div>

                {/* Society */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <Label className="text-xs text-muted-foreground">Society</Label>
                    <span className="text-xs font-medium text-foreground">{currentConfig.domainWeights.society}%</span>
                  </div>
                  <Slider
                    value={[currentConfig.domainWeights.society]}
                    onValueChange={([value]) => updateStageConfig({ 
                      domainWeights: { ...currentConfig.domainWeights, society: value }
                    })}
                    min={0}
                    max={100}
                    step={1}
                    className="w-full"
                  />
                </div>

                {/* Policy */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <Label className="text-xs text-muted-foreground">Policy</Label>
                    <span className="text-xs font-medium text-foreground">{currentConfig.domainWeights.policy}%</span>
                  </div>
                  <Slider
                    value={[currentConfig.domainWeights.policy]}
                    onValueChange={([value]) => updateStageConfig({ 
                      domainWeights: { ...currentConfig.domainWeights, policy: value }
                    })}
                    min={0}
                    max={100}
                    step={1}
                    className="w-full"
                  />
                </div>

                {/* Technology */}
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <Label className="text-xs text-muted-foreground">Technology</Label>
                    <span className="text-xs font-medium text-foreground">{currentConfig.domainWeights.technology}%</span>
                  </div>
                  <Slider
                    value={[currentConfig.domainWeights.technology]}
                    onValueChange={([value]) => updateStageConfig({ 
                      domainWeights: { ...currentConfig.domainWeights, technology: value }
                    })}
                    min={0}
                    max={100}
                    step={1}
                    className="w-full"
                  />
                </div>
              </div>

              <Separator />

              <div className="space-y-2">
                <Label className="text-xs text-muted-foreground">NL Based Rule Input</Label>
                <Input
                  placeholder="e.g., I want a specific sub-scenario in step 3..."
                  value={currentConfig.nlRuleInput}
                  onChange={(e) => updateStageConfig({ nlRuleInput: e.target.value })}
                  className="text-sm"
                />
                <p className="text-xs text-muted-foreground">
                  Define specific sub-scenarios for certain steps
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <Label className="text-xs text-muted-foreground">Importance</Label>
                  <span className="text-xs font-medium text-foreground">{currentConfig.importance.toFixed(2)}</span>
                </div>
                <Slider
                  value={[currentConfig.importance]}
                  onValueChange={([value]) => updateStageConfig({ importance: value })}
                  min={0}
                  max={1}
                  step={0.01}
                  className="w-full"
                />
                <p className="text-xs text-muted-foreground">
                  Set importance level (0-1)
                </p>
              </div>
            </div>
          ) : selectedBlockData ? (
            <div className="space-y-4">
              <div>
                <label className="text-xs text-muted-foreground mb-2 block">Block Name</label>
                <h4 className="font-medium text-sm mb-2 text-foreground">{selectedBlockData.name}</h4>
              </div>
              
              <div>
                <label className="text-xs text-muted-foreground mb-2 block">Description</label>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {getComponentDescription(selectedBlockData.type)}
                </p>
              </div>
              
              <Separator />
              
              {selectedBlockData.type === "Manual Upload" && (
                <div>
                  <label className="text-xs text-muted-foreground mb-2 block">Upload File</label>
                  <div className="space-y-2">
                    <input
                      type="file"
                      accept=".csv,.xlsx,.xls"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file && selectedBlock) {
                          handleFileUpload(selectedBlock, file);
                        }
                      }}
                      className="w-full text-xs file:mr-2 file:py-2 file:px-3 file:rounded file:border-0 file:text-xs file:font-medium file:bg-accent file:text-accent-foreground hover:file:bg-accent/90 file:cursor-pointer"
                    />
                    {selectedBlockData.uploadedFile && (
                      <div className="p-2 bg-accent/10 rounded border border-accent/20">
                        <p className="text-xs font-medium text-foreground">
                          {selectedBlockData.uploadedFile.name}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {(selectedBlockData.uploadedFile.size / 1024).toFixed(2)} KB
                        </p>
                      </div>
                    )}
                    <p className="text-xs text-muted-foreground">
                      Accepted formats: CSV, Excel (.xlsx, .xls)
                    </p>
                  </div>
                </div>
              )}

              {selectedBlockData.type === "Linear Trend" && (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="target-variable" className="text-xs text-muted-foreground">
                      Target Variable *
                    </Label>
                    <Input
                      id="target-variable"
                      placeholder="e.g., CO₂ concentration"
                      value={selectedBlockData.linearTrendConfig?.targetVariable || ""}
                      onChange={(e) => updateLinearTrendConfig(selectedBlock!, { targetVariable: e.target.value })}
                      className="h-8 text-sm"
                    />
                    <p className="text-xs text-muted-foreground">
                      Defines what is being forecasted
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="predictor-variables" className="text-xs text-muted-foreground">
                      Predictor Variable(s) *
                    </Label>
                    <Input
                      id="predictor-variables"
                      placeholder="e.g., time, GDP"
                      value={selectedBlockData.linearTrendConfig?.predictorVariables || "time"}
                      onChange={(e) => updateLinearTrendConfig(selectedBlock!, { predictorVariables: e.target.value })}
                      className="h-8 text-sm"
                    />
                    <p className="text-xs text-muted-foreground">
                      Independent variables (comma-separated)
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-xs text-muted-foreground">
                      Time Window
                    </Label>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <Label htmlFor="time-start" className="text-xs">Start</Label>
                        <Input
                          id="time-start"
                          type="date"
                          value={selectedBlockData.linearTrendConfig?.timeWindowStart || ""}
                          onChange={(e) => updateLinearTrendConfig(selectedBlock!, { timeWindowStart: e.target.value })}
                          className="h-8 text-sm"
                        />
                      </div>
                      <div>
                        <Label htmlFor="time-end" className="text-xs">End</Label>
                        <Input
                          id="time-end"
                          type="date"
                          value={selectedBlockData.linearTrendConfig?.timeWindowEnd || ""}
                          onChange={(e) => updateLinearTrendConfig(selectedBlock!, { timeWindowEnd: e.target.value })}
                          className="h-8 text-sm"
                        />
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Historical range for fitting the model
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="forecast-horizon" className="text-xs text-muted-foreground">
                      Forecast Horizon *
                    </Label>
                    <Input
                      id="forecast-horizon"
                      type="number"
                      min="1"
                      placeholder="e.g., 12"
                      value={selectedBlockData.linearTrendConfig?.forecastHorizon || 12}
                      onChange={(e) => updateLinearTrendConfig(selectedBlock!, { forecastHorizon: parseInt(e.target.value) || 12 })}
                      className="h-8 text-sm"
                    />
                    <p className="text-xs text-muted-foreground">
                      Number of periods to predict into the future
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="regularization" className="text-xs text-muted-foreground">
                      Regularization
                    </Label>
                    <Select
                      value={selectedBlockData.linearTrendConfig?.regularization || "none"}
                      onValueChange={(value: "none" | "ridge" | "lasso") => 
                        updateLinearTrendConfig(selectedBlock!, { regularization: value })
                      }
                    >
                      <SelectTrigger className="h-8 text-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">None</SelectItem>
                        <SelectItem value="ridge">Ridge (L2)</SelectItem>
                        <SelectItem value="lasso">Lasso (L1)</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-muted-foreground">
                      Penalty to prevent overfitting with multiple predictors
                    </p>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <Label htmlFor="confidence-level" className="text-xs text-muted-foreground">
                        Confidence Level
                      </Label>
                      <span className="text-sm font-medium text-foreground">
                        {selectedBlockData.linearTrendConfig?.confidenceLevel || 95}%
                      </span>
                    </div>
                    <Slider
                      id="confidence-level"
                      value={[selectedBlockData.linearTrendConfig?.confidenceLevel || 95]}
                      onValueChange={([value]) => updateLinearTrendConfig(selectedBlock!, { confidenceLevel: value })}
                      min={80}
                      max={99}
                      step={1}
                      className="w-full"
                    />
                    <p className="text-xs text-muted-foreground">
                      Determines the interval width for uncertainty display
                    </p>
                  </div>
                </div>
              )}

              {selectedBlockData.type === "Polynomial Trend" && (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="poly-target-variable" className="text-xs text-muted-foreground">
                      Target Variable *
                    </Label>
                    <Input
                      id="poly-target-variable"
                      placeholder="e.g., CO₂ concentration"
                      value={selectedBlockData.polynomialTrendConfig?.targetVariable || ""}
                      onChange={(e) => updatePolynomialTrendConfig(selectedBlock!, { targetVariable: e.target.value })}
                      className="h-8 text-sm"
                    />
                    <p className="text-xs text-muted-foreground">
                      Defines what is being forecasted
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="poly-predictor-variables" className="text-xs text-muted-foreground">
                      Predictor Variable(s) *
                    </Label>
                    <Input
                      id="poly-predictor-variables"
                      placeholder="e.g., time, GDP"
                      value={selectedBlockData.polynomialTrendConfig?.predictorVariables || "time"}
                      onChange={(e) => updatePolynomialTrendConfig(selectedBlock!, { predictorVariables: e.target.value })}
                      className="h-8 text-sm"
                    />
                    <p className="text-xs text-muted-foreground">
                      Independent variables (comma-separated)
                    </p>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <Label htmlFor="poly-degree" className="text-xs text-muted-foreground">
                        Polynomial Degree *
                      </Label>
                      <span className="text-sm font-medium text-foreground">
                        {selectedBlockData.polynomialTrendConfig?.degree || 2}
                      </span>
                    </div>
                    <Slider
                      id="poly-degree"
                      value={[selectedBlockData.polynomialTrendConfig?.degree || 2]}
                      onValueChange={([value]) => updatePolynomialTrendConfig(selectedBlock!, { degree: value })}
                      min={1}
                      max={5}
                      step={1}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>1 (Linear)</span>
                      <span>2 (Quadratic)</span>
                      <span>3 (Cubic)</span>
                      <span>4</span>
                      <span>5</span>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Higher degrees capture curvature but risk overfitting
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="poly-forecast-horizon" className="text-xs text-muted-foreground">
                      Forecast Horizon *
                    </Label>
                    <Input
                      id="poly-forecast-horizon"
                      type="number"
                      min="1"
                      placeholder="e.g., 12"
                      value={selectedBlockData.polynomialTrendConfig?.forecastHorizon || 12}
                      onChange={(e) => updatePolynomialTrendConfig(selectedBlock!, { forecastHorizon: parseInt(e.target.value) || 12 })}
                      className="h-8 text-sm"
                    />
                    <p className="text-xs text-muted-foreground">
                      Number of periods to predict into the future
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="poly-regularization" className="text-xs text-muted-foreground">
                      Regularization
                    </Label>
                    <Select
                      value={selectedBlockData.polynomialTrendConfig?.regularization || "none"}
                      onValueChange={(value: "none" | "ridge" | "lasso") => 
                        updatePolynomialTrendConfig(selectedBlock!, { regularization: value })
                      }
                    >
                      <SelectTrigger className="h-8 text-sm">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">None</SelectItem>
                        <SelectItem value="ridge">Ridge (L2)</SelectItem>
                        <SelectItem value="lasso">Lasso (L1)</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-muted-foreground">
                      Penalty to prevent overfitting with multiple predictors
                    </p>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <Label htmlFor="poly-confidence-level" className="text-xs text-muted-foreground">
                        Confidence Level
                      </Label>
                      <span className="text-sm font-medium text-foreground">
                        {selectedBlockData.polynomialTrendConfig?.confidenceLevel || 95}%
                      </span>
                    </div>
                    <Slider
                      id="poly-confidence-level"
                      value={[selectedBlockData.polynomialTrendConfig?.confidenceLevel || 95]}
                      onValueChange={([value]) => updatePolynomialTrendConfig(selectedBlock!, { confidenceLevel: value })}
                      min={80}
                      max={99}
                      step={1}
                      className="w-full"
                    />
                    <p className="text-xs text-muted-foreground">
                      Determines the interval width for uncertainty display
                    </p>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-sm text-muted-foreground">
                Select a kill chain stage to configure
              </p>
            </div>
          )}
        </div>

        {/* Main Content Area */}
        <div className="flex-1 bg-muted/20 flex flex-col">
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6">
            <div className="max-w-4xl mx-auto">
              <div className="text-center space-y-4 py-12">
                <h2 className="text-2xl font-semibold text-foreground">Build Your Forecast</h2>
                <p className="text-muted-foreground">
                  Describe what you want to forecast, upload data, or ask questions to get started
                </p>
              </div>
            </div>
          </div>

          {/* Input Area */}
          <div className="border-t border-border bg-card p-4">
            <div className="max-w-4xl mx-auto">
              <div className="flex gap-2 items-end">
                <div className="flex-1 relative">
                  <Input
                    placeholder="Describe your forecast or ask a question..."
                    value={messageInput}
                    onChange={(e) => setMessageInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        // Handle send message
                        setMessageInput("");
                      }
                    }}
                    className="pr-12 min-h-[44px] resize-none"
                  />
                  <Button
                    variant="ghost"
                    size="sm"
                    className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 p-0"
                    onClick={() => {
                      // Handle file upload
                      const input = document.createElement('input');
                      input.type = 'file';
                      input.accept = '.csv,.xlsx,.xls,.json';
                      input.onchange = (e) => {
                        const file = (e.target as HTMLInputElement).files?.[0];
                        if (file) {
                          console.log('File selected:', file.name);
                        }
                      };
                      input.click();
                    }}
                  >
                    <Paperclip className="h-4 w-4" />
                  </Button>
                </div>
                <Button
                  className="h-11 px-6"
                  onClick={() => {
                    if (messageInput.trim()) {
                      // Handle send message
                      console.log('Sending:', messageInput);
                      setMessageInput("");
                    }
                  }}
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              <p className="text-xs text-muted-foreground mt-2 text-center">
                Press Enter to send, Shift+Enter for new line
              </p>
            </div>
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="w-64 border-l border-border bg-card p-4 overflow-y-auto">
          <h3 className="font-semibold text-sm mb-4 text-foreground">
            Kill Chain Stages
          </h3>
          
            <div className="space-y-2">
            <Button
              variant={selectedKillChainStage === "Reconnaissance" ? "default" : "outline"}
              className="w-full justify-start text-left h-auto py-3 hover:bg-accent/10"
              onClick={() => setSelectedKillChainStage("Reconnaissance")}
            >
              <span className="font-medium text-sm">Reconnaissance</span>
            </Button>
            <Button
              variant={selectedKillChainStage === "Weaponization" ? "default" : "outline"}
              className="w-full justify-start text-left h-auto py-3 hover:bg-accent/10"
              onClick={() => setSelectedKillChainStage("Weaponization")}
            >
              <span className="font-medium text-sm">Weaponization</span>
            </Button>
            <Button
              variant={selectedKillChainStage === "Delivery" ? "default" : "outline"}
              className="w-full justify-start text-left h-auto py-3 hover:bg-accent/10"
              onClick={() => setSelectedKillChainStage("Delivery")}
            >
              <span className="font-medium text-sm">Delivery</span>
            </Button>
            <Button
              variant={selectedKillChainStage === "Exploitation" ? "default" : "outline"}
              className="w-full justify-start text-left h-auto py-3 hover:bg-accent/10"
              onClick={() => setSelectedKillChainStage("Exploitation")}
            >
              <span className="font-medium text-sm">Exploitation</span>
            </Button>
            <Button
              variant={selectedKillChainStage === "Installation" ? "default" : "outline"}
              className="w-full justify-start text-left h-auto py-3 hover:bg-accent/10"
              onClick={() => setSelectedKillChainStage("Installation")}
            >
              <span className="font-medium text-sm">Installation</span>
            </Button>
            <Button
              variant={selectedKillChainStage === "Command & Control (C2)" ? "default" : "outline"}
              className="w-full justify-start text-left h-auto py-3 hover:bg-accent/10"
              onClick={() => setSelectedKillChainStage("Command & Control (C2)")}
            >
              <span className="font-medium text-sm">Command & Control (C2)</span>
            </Button>
            <Button
              variant={selectedKillChainStage === "Actions on Objectives" ? "default" : "outline"}
              className="w-full justify-start text-left h-auto py-3 hover:bg-accent/10"
              onClick={() => setSelectedKillChainStage("Actions on Objectives")}
            >
              <span className="font-medium text-sm">Actions on Objectives</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Collaborate Dialog */}
      <Dialog open={isCollaborateDialogOpen} onOpenChange={setIsCollaborateDialogOpen}>
        <DialogContent className="sm:max-w-[450px]">
          <DialogHeader>
            <DialogTitle>Collaborate on Project</DialogTitle>
            <DialogDescription className="text-sm">
              Share your project details to collaborate with others.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-3 py-2">
            <div className="space-y-1.5">
              <Label htmlFor="collab-name" className="text-sm">Name *</Label>
              <Input
                id="collab-name"
                placeholder="Enter your name"
                value={collaborateForm.name}
                onChange={(e) => setCollaborateForm({ ...collaborateForm, name: e.target.value })}
                className="h-9"
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="collab-email" className="text-sm">Email *</Label>
              <Input
                id="collab-email"
                type="email"
                placeholder="your.email@example.com"
                value={collaborateForm.email}
                onChange={(e) => setCollaborateForm({ ...collaborateForm, email: e.target.value })}
                className="h-9"
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="collab-description" className="text-sm">Project Description *</Label>
              <Textarea
                id="collab-description"
                placeholder="Describe your project..."
                value={collaborateForm.projectDescription}
                onChange={(e) => setCollaborateForm({ ...collaborateForm, projectDescription: e.target.value })}
                rows={2}
                className="resize-none text-sm"
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="collab-upload" className="text-sm">Upload Graphs/Visuals</Label>
              <input
                id="collab-upload"
                type="file"
                accept="image/*,.pdf,.png,.jpg,.jpeg,.svg"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    setCollaborateForm({ ...collaborateForm, uploadedFile: file });
                  }
                }}
                className="w-full text-xs file:mr-3 file:py-1.5 file:px-3 file:rounded file:border-0 file:text-xs file:font-medium file:bg-accent file:text-accent-foreground hover:file:bg-accent/90 file:cursor-pointer"
              />
              {collaborateForm.uploadedFile && (
                <div className="p-1.5 bg-accent/10 rounded border border-accent/20">
                  <p className="text-xs font-medium text-foreground">
                    {collaborateForm.uploadedFile.name}
                  </p>
                </div>
              )}
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsCollaborateDialogOpen(false);
                setCollaborateForm({ name: "", email: "", projectDescription: "", uploadedFile: null });
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={() => {
                // Handle form submission here
                console.log("Collaborate form submitted:", collaborateForm);
                setIsCollaborateDialogOpen(false);
                setCollaborateForm({ name: "", email: "", projectDescription: "", uploadedFile: null });
              }}
              disabled={!collaborateForm.name || !collaborateForm.email || !collaborateForm.projectDescription}
            >
              Submit
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Publish Dialog */}
      <Dialog open={isPublishDialogOpen} onOpenChange={setIsPublishDialogOpen}>
        <DialogContent className="sm:max-w-[450px]">
          <DialogHeader>
            <DialogTitle>Publish Project</DialogTitle>
            <DialogDescription className="text-sm">
              Publish your forecast project to the platform.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-3 py-2">
            <div className="space-y-1.5">
              <Label htmlFor="publish-name" className="text-sm">Name *</Label>
              <Input
                id="publish-name"
                placeholder="Enter project name"
                value={publishForm.name}
                onChange={(e) => setPublishForm({ ...publishForm, name: e.target.value })}
                className="h-9"
              />
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="publish-keywords" className="text-sm">Project Keywords *</Label>
              <Input
                id="publish-keywords"
                placeholder="e.g., climate, economy, forecast"
                value={publishForm.projectKeywords}
                onChange={(e) => setPublishForm({ ...publishForm, projectKeywords: e.target.value })}
                className="h-9"
              />
              <p className="text-xs text-muted-foreground">Comma-separated keywords</p>
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="publish-description" className="text-sm">Project Description *</Label>
              <Textarea
                id="publish-description"
                placeholder="Describe your forecast project..."
                value={publishForm.projectDescription}
                onChange={(e) => setPublishForm({ ...publishForm, projectDescription: e.target.value })}
                rows={2}
                className="resize-none text-sm"
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsPublishDialogOpen(false);
                setPublishForm({ name: "", projectKeywords: "", projectDescription: "" });
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={() => {
                // Handle form submission here
                console.log("Publish form submitted:", publishForm);
                setIsPublishDialogOpen(false);
                setPublishForm({ name: "", projectKeywords: "", projectDescription: "" });
              }}
              disabled={!publishForm.name || !publishForm.projectKeywords || !publishForm.projectDescription}
            >
              Publish
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Builder;


