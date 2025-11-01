import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, User, Tag } from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { ScrollArea } from "@/components/ui/scroll-area";

// Define the Forecast interface
interface Forecast {
  id: string;
  name: string;
  publisherName: string;
  projectKeywords: string;
  projectDescription: string;
}

// Sample forecasts data - in a real app, this would come from a database/API
const sampleForecasts: Forecast[] = [
  {
    id: "1",
    name: "EU Climate Trends 2030",
    publisherName: "European Climate Institute",
    projectKeywords: "climate, environment, temperature, CO2",
    projectDescription: "A comprehensive forecast of European climate trends focusing on temperature variations and CO2 emissions through 2030, utilizing advanced machine learning models and climate datasets."
  },
  {
    id: "2",
    name: "Economic Growth Forecast",
    publisherName: "EU Economic Research Center",
    projectKeywords: "economy, GDP, growth, inflation",
    projectDescription: "Long-term economic forecasting model predicting GDP growth rates and inflation trends across EU member states, incorporating policy impacts and global economic factors."
  },
  {
    id: "3",
    name: "Green Energy Transition",
    publisherName: "Sustainability Analytics Group",
    projectKeywords: "renewable energy, solar, wind, transition",
    projectDescription: "Forecasting the shift to renewable energy sources in Europe, analyzing solar and wind capacity growth, investment trends, and policy-driven adoption rates."
  },
  {
    id: "4",
    name: "Population Demographics 2050",
    publisherName: "European Demographic Institute",
    projectKeywords: "demographics, population, aging, migration",
    projectDescription: "Long-term demographic projections examining population growth, aging patterns, and migration trends across European countries with policy implications for healthcare and social systems."
  },
  {
    id: "5",
    name: "Digital Infrastructure Expansion",
    publisherName: "Tech Policy Foundation",
    projectKeywords: "technology, digital, infrastructure, broadband",
    projectDescription: "Forecasting the expansion of digital infrastructure including 5G networks, broadband coverage, and digital service adoption rates across rural and urban areas in the EU."
  }
];

const Forecasts = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [forecasts] = useState<Forecast[]>(sampleForecasts);
  const [selectedForecast, setSelectedForecast] = useState<Forecast | null>(null);
  const [isSheetOpen, setIsSheetOpen] = useState(false);

  // Filter forecasts based on search query
  const filteredForecasts = forecasts.filter(
    (forecast) =>
      forecast.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      forecast.publisherName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      forecast.projectKeywords.toLowerCase().includes(searchQuery.toLowerCase()) ||
      forecast.projectDescription.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Handle view details
  const handleViewDetails = (forecast: Forecast) => {
    setSelectedForecast(forecast);
    setIsSheetOpen(true);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header Section */}
      <div className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-4xl mx-auto text-center space-y-4">
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-foreground">
              Explore Forecasts
            </h1>
            <p className="text-lg text-muted-foreground">
              Discover and explore forecasts created by the community
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
                placeholder="Search forecasts by name, publisher, keywords, or description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 h-12 text-base"
              />
            </div>
          </div>

          {/* Results Count */}
          <div className="mb-6 text-center">
            <p className="text-sm text-muted-foreground">
              {filteredForecasts.length} {filteredForecasts.length === 1 ? "forecast" : "forecasts"} found
            </p>
          </div>

          {/* Forecast Cards Grid */}
          {filteredForecasts.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredForecasts.map((forecast) => (
                <Card key={forecast.id} className="hover:shadow-lg transition-shadow duration-200">
                  <CardHeader>
                    <CardTitle className="text-xl line-clamp-2">{forecast.name}</CardTitle>
                    <CardDescription className="text-base font-medium text-foreground">
                      {forecast.publisherName}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground mb-2">Keywords</p>
                      <div className="flex flex-wrap gap-2">
                        {forecast.projectKeywords.split(",").map((keyword, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {keyword.trim()}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-muted-foreground mb-2">Description</p>
                      <p className="text-sm text-muted-foreground line-clamp-3">
                        {forecast.projectDescription}
                      </p>
                    </div>
                    <Button 
                      variant="outline" 
                      className="w-full mt-4"
                      onClick={() => handleViewDetails(forecast)}
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
                No forecasts found matching your search.
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
              {selectedForecast && (
                <>
                  <SheetHeader className="mb-6">
                    <SheetTitle className="text-3xl">{selectedForecast.name}</SheetTitle>
                    <SheetDescription className="text-base">
                      Detailed project information and forecast data
                    </SheetDescription>
                  </SheetHeader>

                  <div className="space-y-6">
                    {/* Publisher Info */}
                    <div className="flex items-start gap-3 p-4 bg-muted/50 rounded-lg">
                      <User className="h-5 w-5 text-primary mt-0.5" />
                      <div>
                        <p className="font-medium text-sm text-muted-foreground mb-1">Published by</p>
                        <p className="text-lg font-semibold text-foreground">{selectedForecast.publisherName}</p>
                      </div>
                    </div>

                    {/* Keywords */}
                    <div>
                      <div className="flex items-center gap-2 mb-3">
                        <Tag className="h-5 w-5 text-primary" />
                        <h3 className="text-lg font-semibold text-foreground">Project Keywords</h3>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {selectedForecast.projectKeywords.split(",").map((keyword, index) => (
                          <Badge key={index} variant="secondary" className="text-sm py-1.5 px-3">
                            {keyword.trim()}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* Description */}
                    <div>
                      <h3 className="text-lg font-semibold text-foreground mb-3">Project Description</h3>
                      <p className="text-base text-muted-foreground leading-relaxed">
                        {selectedForecast.projectDescription}
                      </p>
                    </div>

                    {/* Additional Project Details Section */}
                    <div className="border-t pt-6">
                      <h3 className="text-lg font-semibold text-foreground mb-4">Project Overview</h3>
                      <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="p-4 border rounded-lg">
                            <p className="text-sm text-muted-foreground mb-1">Status</p>
                            <p className="text-base font-medium text-foreground">Active</p>
                          </div>
                          <div className="p-4 border rounded-lg">
                            <p className="text-sm text-muted-foreground mb-1">Category</p>
                            <p className="text-base font-medium text-foreground">
                              {selectedForecast.projectKeywords.split(",")[0].trim()}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-3 pt-4">
                      <Button className="flex-1">View Full Analysis</Button>
                      <Button variant="outline" className="flex-1">Download Data</Button>
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

export default Forecasts;

