import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Loader2, Globe } from "lucide-react";
import { useToast } from "@/hooks/use-toast";


interface BrandingData {
  brandName: string;
  logoUrl: string;
  websiteUrl: string;
  primaryColor?: string;
  faviconUrl?: string;
}

interface BrandingSetupProps {
  onComplete: (branding: BrandingData) => void;
}

export const BrandingSetup = ({ onComplete }: BrandingSetupProps) => {
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const extractBrandingFromWebsite = async (url: string): Promise<BrandingData | null> => {
    try {
      // Call backend API to extract branding (avoids CORS issues)
      console.log('Calling backend to extract branding from:', url);

      const response = await fetch('/api/extract-branding', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          websiteUrl: url
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to extract branding: ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      console.log('Branding extracted from backend:', data);

      return {
        brandName: data.brandName,
        logoUrl: data.logoUrl,
        websiteUrl: data.websiteUrl,
        faviconUrl: data.faviconUrl,
        primaryColor: data.primaryColor || '#8b5cf6'
      };
    } catch (error) {
      console.error('Error extracting branding:', error);
      return null;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!websiteUrl.trim()) {
      toast({
        title: "Error",
        description: "Please enter a website URL",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      console.log('Extracting branding from:', websiteUrl);
      const brandingData = await extractBrandingFromWebsite(websiteUrl);
      
      if (!brandingData) {
        throw new Error('Failed to extract branding information');
      }

      console.log('Branding extracted:', brandingData);

      // Store branding in localStorage only
      localStorage.setItem('chatbot_branding', JSON.stringify(brandingData));
      
      toast({
        title: "Success",
        description: "Branding configured successfully!",
      });

      onComplete(brandingData);
    } catch (error) {
      console.error('Setup error:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to set up branding",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-muted/20 p-4">
      <Card className="w-full max-w-md p-8 shadow-2xl border-2 animate-fade-in">
        <div className="text-center mb-8">
          <div className="h-16 w-16 rounded-2xl bg-gradient-button flex items-center justify-center shadow-xl mx-auto mb-4">
            <Globe className="h-8 w-8 text-primary-foreground" />
          </div>
          <h1 className="text-3xl font-bold mb-2 bg-gradient-primary bg-clip-text text-transparent">
            Configure Branding
          </h1>
          <p className="text-muted-foreground">
            Enter your customer's website to automatically extract branding
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="website">Customer Website URL</Label>
            <Input
              id="website"
              type="text"
              placeholder="example.com or https://example.com"
              value={websiteUrl}
              onChange={(e) => setWebsiteUrl(e.target.value)}
              disabled={isLoading}
              className="text-base"
            />
            <p className="text-xs text-muted-foreground">
              We'll extract the logo, brand name, and colors automatically
            </p>
          </div>

          <Button
            type="submit"
            disabled={isLoading || !websiteUrl}
            className="w-full bg-gradient-button hover:opacity-90 transition-opacity"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Extracting Branding...
              </>
            ) : (
              "Configure Chatbot"
            )}
          </Button>
        </form>

        <div className="mt-6 text-center text-xs text-muted-foreground">
          <p>The branding will be saved for future visits</p>
        </div>
      </Card>
    </div>
  );
};
