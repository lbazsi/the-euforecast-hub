import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, Building2, Globe, Network, ArrowRight, Github } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Index = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Animated Network Background */}
        <div className="absolute inset-0 z-0">
          <NetworkAnimation />
        </div>
        
        <div className="relative z-10 container mx-auto px-4 py-24 md:py-32">
          <div className="max-w-5xl mx-auto text-center space-y-8">
            <div className="space-y-4">
              <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-foreground">
                Forecast the Future, Together
              </h1>
              <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto font-light">
                Build and share transparent forecasts — empower policy with open foresight.
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
              <Button 
                size="lg" 
                className="text-lg px-8 py-6 bg-primary hover:bg-primary/90 text-primary-foreground font-medium group"
                onClick={() => navigate("/builder")}
              >
                <Network className="mr-2 h-5 w-5" />
                Forecast With Killchain
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button 
                size="lg" 
                variant="outline" 
                className="text-lg px-8 py-6 border-2 border-border font-medium"
                onClick={() => navigate("/forecasts")}
              >
                Explore Forecasts
              </Button>
              <Button 
                size="lg" 
                variant="secondary" 
                className="text-lg px-8 py-6 bg-card hover:bg-secondary font-medium"
                onClick={() => navigate("/collaborations")}
              >
                <Users className="mr-2 h-5 w-5" />
                Collaborate
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Role-Based Entry Cards */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
          <RoleCard
            icon={<Users className="h-12 w-12 text-accent" />}
            title="Researchers"
            description="Build sophisticated forecast models with transparent methodologies. Contribute to open knowledge and validate your predictions."
            features={["Advanced modeling tools", "Open methodology sharing", "Peer validation system"]}
          />
          <RoleCard
            icon={<Building2 className="h-12 w-12 text-accent" />}
            title="Policymakers"
            description="Access evidence-based forecasts to inform strategic decisions. Understand uncertainty and explore future scenarios."
            features={["Scenario analysis", "Risk assessment tools", "Evidence-based insights"]}
          />
          <RoleCard
            icon={<Globe className="h-12 w-12 text-accent" />}
            title="Citizens"
            description="Explore forecasts on topics that matter to you. Understand how decisions are made and participate in open governance."
            features={["Transparent data access", "Interactive visualizations", "Public engagement"]}
          />
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-card mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-accent rounded flex items-center justify-center">
                  <span className="text-accent-foreground font-bold text-sm">EU</span>
                </div>
                <span className="text-sm text-muted-foreground">EU Open Data Initiative</span>
              </div>
            </div>
            
            <div className="flex items-center gap-6">
              <a 
                href="https://github.com/euforecasthub" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-muted-foreground hover:text-accent transition-colors"
              >
                <Github className="h-5 w-5" />
                <span className="text-sm">View on GitHub</span>
              </a>
            </div>
          </div>
          
          <div className="mt-6 pt-6 border-t border-border text-center">
            <p className="text-xs text-muted-foreground">
              © 2025 EU ForecastHUB. Open source forecasting platform for evidence-based policy.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Role Card Component
const RoleCard = ({ 
  icon, 
  title, 
  description, 
  features 
}: { 
  icon: React.ReactNode; 
  title: string; 
  description: string; 
  features: string[];
}) => {
  return (
    <Card className="bg-card border-border hover:border-accent/50 transition-all duration-300 group cursor-pointer">
      <CardHeader>
        <div className="mb-4 group-hover:scale-110 transition-transform duration-300">
          {icon}
        </div>
        <CardTitle className="text-2xl text-foreground">{title}</CardTitle>
        <CardDescription className="text-muted-foreground leading-relaxed">
          {description}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {features.map((feature, idx) => (
            <li key={idx} className="flex items-center gap-2 text-sm text-muted-foreground">
              <div className="w-1.5 h-1.5 rounded-full bg-accent"></div>
              {feature}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
};

// Network Animation Component
const NetworkAnimation = () => {
  const nodes = [
    { x: 15, y: 20, delay: 0 },
    { x: 35, y: 15, delay: 0.5 },
    { x: 65, y: 25, delay: 1 },
    { x: 85, y: 18, delay: 1.5 },
    { x: 25, y: 60, delay: 0.7 },
    { x: 50, y: 55, delay: 1.2 },
    { x: 75, y: 65, delay: 0.3 },
    { x: 45, y: 85, delay: 0.9 },
  ];

  const connections = [
    { from: 0, to: 1 },
    { from: 1, to: 2 },
    { from: 2, to: 3 },
    { from: 0, to: 4 },
    { from: 1, to: 5 },
    { from: 2, to: 6 },
    { from: 4, to: 5 },
    { from: 5, to: 6 },
    { from: 5, to: 7 },
  ];

  return (
    <svg className="w-full h-full opacity-20" style={{ minHeight: '600px' }}>
      <defs>
        <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style={{ stopColor: 'hsl(186 79% 82%)', stopOpacity: 0.2 }} />
          <stop offset="50%" style={{ stopColor: 'hsl(186 79% 82%)', stopOpacity: 0.6 }} />
          <stop offset="100%" style={{ stopColor: 'hsl(186 79% 82%)', stopOpacity: 0.2 }} />
        </linearGradient>
      </defs>
      
      {/* Connection Lines */}
      {connections.map((conn, idx) => {
        const from = nodes[conn.from];
        const to = nodes[conn.to];
        return (
          <line
            key={idx}
            x1={`${from.x}%`}
            y1={`${from.y}%`}
            x2={`${to.x}%`}
            y2={`${to.y}%`}
            stroke="url(#lineGradient)"
            strokeWidth="2"
            style={{
              animation: `pulse-line 3s ease-in-out infinite`,
              animationDelay: `${conn.from * 0.2}s`,
            }}
          />
        );
      })}
      
      {/* Nodes */}
      {nodes.map((node, idx) => (
        <g key={idx}>
          <circle
            cx={`${node.x}%`}
            cy={`${node.y}%`}
            r="8"
            fill="hsl(186 79% 82%)"
            style={{
              animation: `dot-pulse 2s ease-in-out infinite`,
              animationDelay: `${node.delay}s`,
            }}
          />
          <circle
            cx={`${node.x}%`}
            cy={`${node.y}%`}
            r="4"
            fill="hsl(0 0% 100%)"
          />
        </g>
      ))}
    </svg>
  );
};

export default Index;
