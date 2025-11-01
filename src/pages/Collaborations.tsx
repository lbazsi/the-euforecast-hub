import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, User, Mail, FileText } from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";

// Define the Collaboration interface
interface Collaboration {
  id: string;
  name: string;
  email: string;
  projectDescription: string;
  uploadedFileName?: string;
  uploadType?: string;
}

// Sample collaborations data - in a real app, this would come from a database/API
const sampleCollaborations: Collaboration[] = [
  {
    id: "1",
    name: "Dr. Sarah Chen",
    email: "sarah.chen@euresearch.eu",
    projectDescription: "Looking for AI/ML researchers to collaborate on a climate prediction model using satellite imagery and weather station data. We need expertise in deep learning and time-series analysis.",
    uploadedFileName: "project_overview.pdf",
    uploadType: "pdf"
  },
  {
    id: "2",
    name: "Marco Rossi",
    email: "marco.rossi@techfoundation.it",
    projectDescription: "Seeking economists and policy analysts for a joint forecast on the impact of renewable energy policies across Mediterranean countries. Background in econometrics preferred.",
    uploadedFileName: "collaboration_brief.png",
    uploadType: "image"
  },
  {
    id: "3",
    name: "Dr. Emma Thompson",
    email: "emma.thompson@demographicdata.uk",
    projectDescription: "Calling for demographers and social scientists to develop population forecast models. Interest in aging populations and migration patterns. International collaboration welcome.",
  },
  {
    id: "4",
    name: "Andreas Klein",
    email: "andreas.klein@greenfinance.de",
    projectDescription: "Building a consortium to forecast green technology adoption rates in Central Europe. Need partners with expertise in technology diffusion modeling and policy impact analysis.",
    uploadedFileName: "proposal_document.pdf",
    uploadType: "pdf"
  },
  {
    id: "5",
    name: "Prof. Maria Santos",
    email: "maria.santos@urbanplanning.es",
    projectDescription: "Seeking collaboration on smart city infrastructure forecasting. Looking for urban planners, data scientists, and civil engineers to predict future infrastructure needs.",
    uploadedFileName: "visual_dashboard.svg",
    uploadType: "image"
  },
  {
    id: "6",
    name: "Lukas Andersson",
    email: "lukas.andersson@healthdata.se",
    projectDescription: "Forecasting healthcare demand across Nordic countries. Need epidemiologists and data analysts to predict aging population's healthcare needs through 2050.",
  }
];

const Collaborations = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [collaborations] = useState<Collaboration[]>(sampleCollaborations);
  const [selectedCollaboration, setSelectedCollaboration] = useState<Collaboration | null>(null);
  const [isSheetOpen, setIsSheetOpen] = useState(false);

  // Filter collaborations based on search query
  const filteredCollaborations = collaborations.filter(
    (collaboration) =>
      collaboration.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      collaboration.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      collaboration.projectDescription.toLowerCase().includes(searchQuery.toLowerCase()) ||
      collaboration.uploadedFileName?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Handle view details
  const handleViewDetails = (collaboration: Collaboration) => {
    setSelectedCollaboration(collaboration);
    setIsSheetOpen(true);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header Section */}
      <div className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-4xl mx-auto text-center space-y-4">
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-foreground">
              Collaborate on Projects
            </h1>
            <p className="text-lg text-muted-foreground">
              Discover and connect with researchers looking for collaboration
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Search Bar */}
          <div className="mb-8">
            <div className="relative max-w-2xl mx-auto">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
              <Input
                type="text"
                placeholder="Search by name, email, project description, or uploaded file..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 h-12 text-base"
              />
            </div>
          </div>

          {/* Results Count */}
          <div className="mb-6 text-center">
            <p className="text-sm text-muted-foreground">
              {filteredCollaborations.length} {filteredCollaborations.length === 1 ? "collaboration" : "collaborations"} found
            </p>
          </div>

          {/* Collaboration Cards Grid */}
          {filteredCollaborations.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredCollaborations.map((collaboration) => (
                <Card key={collaboration.id} className="hover:shadow-lg transition-shadow duration-200">
                  <CardHeader>
                    <div className="flex items-start gap-3">
                      <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <User className="h-5 w-5 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <CardTitle className="text-xl line-clamp-1">{collaboration.name}</CardTitle>
                        <CardDescription className="text-sm line-clamp-1 mt-1">
                          {collaboration.email}
                        </CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground mb-2">Project Description</p>
                      <p className="text-sm text-muted-foreground line-clamp-3">
                        {collaboration.projectDescription}
                      </p>
                    </div>
                    {collaboration.uploadedFileName && (
                      <div className="flex items-center gap-2 p-2 bg-accent/10 rounded border border-accent/20">
                        <FileText className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                        <p className="text-xs font-medium text-foreground truncate">
                          {collaboration.uploadedFileName}
                        </p>
                      </div>
                    )}
                    <Button 
                      variant="outline" 
                      className="w-full mt-4"
                      onClick={() => handleViewDetails(collaboration)}
                    >
                      View Details
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-16">
              <p className="text-lg text-muted-foreground">
                No collaborations found matching your search.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Details Sheet */}
      <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
        <SheetContent side="right" className="w-full sm:max-w-2xl p-0">
          <ScrollArea className="h-full">
            <div className="p-6">
              {selectedCollaboration && (
                <>
                  <SheetHeader className="mb-6">
                    <div className="flex items-start gap-3">
                      <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                        <User className="h-6 w-6 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <SheetTitle className="text-2xl">{selectedCollaboration.name}</SheetTitle>
                        <SheetDescription className="text-base mt-1">
                          Collaboration Opportunity
                        </SheetDescription>
                      </div>
                    </div>
                  </SheetHeader>

                  <div className="space-y-6">
                    {/* Contact Info */}
                    <div className="flex items-start gap-3 p-4 bg-muted/50 rounded-lg">
                      <Mail className="h-5 w-5 text-primary mt-0.5" />
                      <div>
                        <p className="font-medium text-sm text-muted-foreground mb-1">Contact Email</p>
                        <p className="text-base font-semibold text-foreground">{selectedCollaboration.email}</p>
                      </div>
                    </div>

                    {/* Project Description */}
                    <div>
                      <div className="flex items-center gap-2 mb-3">
                        <FileText className="h-5 w-5 text-primary" />
                        <h3 className="text-lg font-semibold text-foreground">Project Description</h3>
                      </div>
                      <p className="text-base text-muted-foreground leading-relaxed">
                        {selectedCollaboration.projectDescription}
                      </p>
                    </div>

                    {/* Uploaded File */}
                    {selectedCollaboration.uploadedFileName && (
                      <div>
                        <h3 className="text-lg font-semibold text-foreground mb-3">Attached File</h3>
                        <div className="p-4 bg-accent/10 rounded-lg border border-accent/20">
                          <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                              <FileText className="h-5 w-5 text-primary" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-foreground truncate">
                                {selectedCollaboration.uploadedFileName}
                              </p>
                              <p className="text-xs text-muted-foreground capitalize">
                                {selectedCollaboration.uploadType || "File"}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Collaboration Status */}
                    <div className="border-t pt-6">
                      <h3 className="text-lg font-semibold text-foreground mb-4">Collaboration Status</h3>
                      <div className="space-y-4">
                        <div className="p-4 border rounded-lg">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="text-sm text-muted-foreground mb-1">Status</p>
                              <p className="text-base font-medium text-foreground">Open for Collaboration</p>
                            </div>
                            <Badge variant="secondary">Active</Badge>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-3 pt-4">
                      <Button className="flex-1">Contact Collaborator</Button>
                      <Button variant="outline" className="flex-1">
                        {selectedCollaboration.uploadedFileName ? "Download File" : "Share Project"}
                      </Button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </ScrollArea>
        </SheetContent>
      </Sheet>
    </div>
  );
};

export default Collaborations;

