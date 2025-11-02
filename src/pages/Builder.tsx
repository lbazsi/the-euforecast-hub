import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { FileText, Save, Download, Eye, HelpCircle, Send, Paperclip, Loader2, Home } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
import { builderApi, ApiError } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";


const Builder = () => {
  const { toast } = useToast();
  const navigate = useNavigate();
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
    publisherName: "",
    projectKeywords: "",
    projectDescription: ""
  });
  const [projectId, setProjectId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<Array<{type: 'user' | 'assistant', message: string, timestamp: string}>>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  
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

  const handleSendMessage = async () => {
    if (!messageInput.trim() || isLoading) return;

    const userMessage = messageInput.trim();
    setMessageInput("");
    setIsLoading(true);

    // Add user message to UI
    setMessages(prev => [...prev, {
      type: 'user',
      message: userMessage,
      timestamp: new Date().toISOString()
    }]);

    try {
      const response = await builderApi.sendMessage(projectId, userMessage, sessionId, stageConfigurations);
      
      if (response.sessionId) {
        setSessionId(response.sessionId);
      }

      // Add assistant response to UI
      if (response.response) {
        setMessages(prev => [...prev, {
          type: 'assistant',
          message: response.response,
          timestamp: new Date().toISOString()
        }]);
      }

      if (response.suggestions && response.suggestions.length > 0) {
        toast({
          title: "Suggestions",
          description: response.suggestions.join(", "),
        });
      }
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : "Failed to send message";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunForecast = async () => {
    if (Object.keys(stageConfigurations).length === 0) {
      toast({
        title: "Configuration Required",
        description: "Please configure at least one kill chain stage before running the forecast.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const result = await builderApi.runBuilder(projectId, stageConfigurations, messageInput);
      
      toast({
        title: "Forecast Generated",
        description: `Forecast ID: ${result.forecastId}`,
      });

      // You can navigate to a results view or display the results here
      console.log("Forecast results:", result);
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : "Failed to run forecast";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveProject = async () => {
    if (!publishForm.name || !publishForm.publisherName) {
      toast({
        title: "Required Fields",
        description: "Please fill in all required fields.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const result = await builderApi.createProject(
        publishForm.name,
        stageConfigurations,
        messages.map(m => ({
          timestamp: m.timestamp,
          message: m.message,
          // Backend expects 'system' but frontend uses 'assistant'
          type: m.type === 'assistant' ? 'system' : m.type
        }))
      );

      setProjectId(result.projectId);
      setIsPublishDialogOpen(false);
      toast({
        title: "Project Saved",
        description: "Your project has been saved successfully.",
      });
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : "Failed to save project";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Top Toolbar */}
      <div className="h-14 border-b border-border bg-card flex items-center px-4 gap-2">
        {/* Home Button - Left Side */}
        <Button 
          variant="ghost" 
          size="sm" 
          className="gap-2 mr-auto"
          onClick={() => navigate("/")}
        >
          <Home className="h-4 w-4" />
          Home
        </Button>
        
        {/* Centered Toolbar Buttons */}
        <div className="flex items-center justify-center flex-1 gap-2">
          <Button variant="ghost" size="sm" className="gap-2">
            <FileText className="h-4 w-4" />
            New
          </Button>
        <Button 
          variant="ghost" 
          size="sm" 
          className="gap-2" 
          onClick={() => setIsPublishDialogOpen(true)}
          disabled={isLoading}
        >
          <Save className="h-4 w-4" />
          {projectId ? "Update" : "Save"} Project
        </Button>
        <Button 
          variant="default" 
          size="sm" 
          className="gap-2"
          onClick={handleRunForecast}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Running...
            </>
          ) : (
            <>
              <Send className="h-4 w-4" />
              Run Forecast
            </>
          )}
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
              {messages.length === 0 ? (
                <div className="text-center space-y-4 py-12">
                  <h2 className="text-2xl font-semibold text-foreground">Build Your Forecast</h2>
                  <p className="text-muted-foreground">
                    Describe what you want to forecast, upload data, or ask questions to get started
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg p-4 ${
                          msg.type === 'user'
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted text-foreground'
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap">{msg.message}</p>
                        <p className="text-xs mt-2 opacity-70">
                          {new Date(msg.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-muted rounded-lg p-4">
                        <Loader2 className="h-4 w-4 animate-spin" />
                      </div>
                    </div>
                  )}
                </div>
              )}
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
                        handleSendMessage();
                      }
                    }}
                    disabled={isLoading}
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
                  onClick={handleSendMessage}
                  disabled={!messageInput.trim() || isLoading}
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
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
          
          <div className="space-y-2 py-1">
            <div className="space-y-1">
              <Label htmlFor="publish-name" className="text-sm">Name of Project *</Label>
              <Input
                id="publish-name"
                placeholder="Enter project name"
                value={publishForm.name}
                onChange={(e) => setPublishForm({ ...publishForm, name: e.target.value })}
                className="h-9"
              />
            </div>

            <div className="space-y-1">
              <Label htmlFor="publish-publisher-name" className="text-sm">Publisher's Name *</Label>
              <Input
                id="publish-publisher-name"
                placeholder="Enter publisher's name"
                value={publishForm.publisherName}
                onChange={(e) => setPublishForm({ ...publishForm, publisherName: e.target.value })}
                className="h-9"
              />
            </div>

            <div className="space-y-1">
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

            <div className="space-y-1">
              <Label htmlFor="publish-description" className="text-sm">Project Description *</Label>
              <Textarea
                id="publish-description"
                placeholder="Describe your forecast project..."
                value={publishForm.projectDescription}
                onChange={(e) => setPublishForm({ ...publishForm, projectDescription: e.target.value })}
                rows={1}
                className="resize-none text-sm"
              />
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsPublishDialogOpen(false);
                setPublishForm({ name: "", publisherName: "", projectKeywords: "", projectDescription: "" });
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSaveProject}
              disabled={!publishForm.name || !publishForm.publisherName || !publishForm.projectKeywords || !publishForm.projectDescription || isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save Project"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Builder;
