import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ProvisionModeCard } from "@/components/ProvisionModeCard";
import { JobHistoryTable } from "@/components/JobHistoryTable";
import { Link, Settings, Zap } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export interface ProvisionJob {
  id: string;
  url: string;
  status: "complete" | "failed" | "running";
  duration: string;
  date: string;
  mode: "default" | "advanced";
}

const CEDashboard = () => {
  const { toast } = useToast();
  const navigate = useNavigate();
  const [defaultUrl, setDefaultUrl] = useState("");
  const [isProvisioning, setIsProvisioning] = useState(false);

  // Mock job history data
  const [jobs] = useState<ProvisionJob[]>([
    {
      id: "1",
      url: "https://example.com",
      status: "complete",
      duration: "2m 34s",
      date: "2025-10-04 14:30",
      mode: "default"
    },
    {
      id: "2",
      url: "https://myshop.com",
      status: "complete",
      duration: "1m 52s",
      date: "2025-10-04 12:15",
      mode: "advanced"
    },
    {
      id: "3",
      url: "https://testsite.com",
      status: "failed",
      duration: "45s",
      date: "2025-10-04 10:22",
      mode: "default"
    },
    {
      id: "4",
      url: "https://demo.org",
      status: "running",
      duration: "1m 10s",
      date: "2025-10-04 09:45",
      mode: "default"
    },
    {
      id: "5",
      url: "https://portfolio.io",
      status: "complete",
      duration: "3m 12s",
      date: "2025-10-03 16:20",
      mode: "advanced"
    }
  ]);

  const handleDefaultProvision = async () => {
    if (!defaultUrl.trim()) {
      toast({
        title: "URL Required",
        description: "Please enter a website URL to provision",
        variant: "destructive",
      });
      return;
    }

    setIsProvisioning(true);

    try {
      // Call the real API endpoint
      const response = await fetch("/api/provision/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          customer_url: defaultUrl.startsWith("http") ? defaultUrl : `https://${defaultUrl}`,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to start provision: ${response.statusText}`);
      }

      const data = await response.json();

      // Show success toast
      toast({
        title: "Provision Started",
        description: `Provisioning chatbot for ${defaultUrl}`,
      });

      // REDIRECT TO PROGRESS PAGE
      navigate(`/provision-progress?jobId=${data.job_id}`);

    } catch (error) {
      setIsProvisioning(false);
      toast({
        title: "Provision Failed",
        description: error instanceof Error ? error.message : "Unknown error occurred",
        variant: "destructive",
      });
    }
  };

  const handleAdvancedSetup = () => {
    toast({
      title: "Coming Soon",
      description: "Advanced setup mode will be available in Phase 2D",
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      {/* Header */}
      <div className="border-b bg-card/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                CE Dashboard
              </h1>
              <p className="text-muted-foreground mt-1">
                Provision and manage conversational AI chatbots
              </p>
            </div>
            <Button variant="outline" className="gap-2">
              <Settings className="h-4 w-4" />
              Settings
            </Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          {/* Provision Modes Section */}
          <div>
            <h2 className="text-2xl font-semibold mb-4">Provision New Chatbot</h2>
            <div className="grid md:grid-cols-2 gap-6">
              {/* Default Mode Card */}
              <ProvisionModeCard
                title="DEFAULT MODE"
                description="Quick setup with automatic configuration"
                icon={<Link className="h-8 w-8" />}
                variant="default"
              >
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">
                      Website URL
                    </label>
                    <Input
                      type="url"
                      placeholder="https://example.com"
                      value={defaultUrl}
                      onChange={(e) => setDefaultUrl(e.target.value)}
                      className="w-full"
                      disabled={isProvisioning}
                    />
                  </div>
                  <Button
                    onClick={handleDefaultProvision}
                    disabled={isProvisioning}
                    className="w-full bg-gradient-button hover:opacity-90 transition-opacity"
                  >
                    {isProvisioning ? "Provisioning..." : "Start Provision"}
                  </Button>
                </div>
              </ProvisionModeCard>

              {/* Crazy Frog Mode Card */}
              <ProvisionModeCard
                title="CRAZY FROG MODE"
                description="Advanced setup with full customization"
                icon={<Zap className="h-8 w-8" />}
                variant="advanced"
              >
                <div className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    Unlock powerful features including:
                  </p>
                  <ul className="text-sm space-y-2">
                    <li className="flex items-start gap-2">
                      <span className="text-primary">•</span>
                      <span>Custom branding and styling</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary">•</span>
                      <span>Advanced AI configuration</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-primary">•</span>
                      <span>Integration options</span>
                    </li>
                  </ul>
                  <Button
                    onClick={handleAdvancedSetup}
                    variant="outline"
                    className="w-full border-primary/50 hover:border-primary hover:bg-primary/10"
                  >
                    Advanced Setup
                  </Button>
                </div>
              </ProvisionModeCard>
            </div>
          </div>

          {/* Job History Section */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-semibold">Recent Provisions</h2>
              <Button variant="ghost" size="sm">View All</Button>
            </div>
            <JobHistoryTable jobs={jobs} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default CEDashboard;
