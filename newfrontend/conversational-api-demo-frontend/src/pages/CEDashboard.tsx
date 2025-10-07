import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ProvisionModeCard } from "@/components/ProvisionModeCard";
import UserStatsCard from "@/components/UserStatsCard";
import JobFilters from "@/components/JobFilters";
import EnhancedJobHistoryTable from "@/components/EnhancedJobHistoryTable";
import { Link, Settings, Zap, LogIn, LogOut, User } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";

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
  const { user, loading, signInWithGoogle, signOut: firebaseSignOut, isAuthEnabled } = useAuth();
  const [defaultUrl, setDefaultUrl] = useState("");
  const [isProvisioning, setIsProvisioning] = useState(false);
  const [jobs, setJobs] = useState<ProvisionJob[]>([]);
  const [loadingJobs, setLoadingJobs] = useState(false);
  const [userStats, setUserStats] = useState<any>(null);
  const [loadingStats, setLoadingStats] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // Fetch user's job history
  useEffect(() => {
    const fetchJobs = async () => {
      setLoadingJobs(true);
      try {
        const headers: HeadersInit = {
          "Content-Type": "application/json",
        };

        // Add Firebase auth token if user is signed in
        if (user) {
          const token = await user.getIdToken();
          headers["Authorization"] = `Bearer ${token}`;
        }

        // Build query params
        const params = new URLSearchParams();
        if (statusFilter && statusFilter !== 'all') {
          params.append('status', statusFilter);
        }
        if (searchQuery) {
          params.append('search', searchQuery);
        }

        const url = `/api/provision/history${params.toString() ? `?${params.toString()}` : ''}`;

        const response = await fetch(url, { headers });

        if (!response.ok) {
          throw new Error(`Failed to fetch jobs: ${response.statusText}`);
        }

        const data = await response.json();

        // Map API response to ProvisionJob format
        const mappedJobs: ProvisionJob[] = data.jobs.map((job: any) => ({
          id: job.job_id,
          url: job.customer_url,
          status: job.status === "completed" ? "complete" :
                  job.status === "failed" ? "failed" : "running",
          duration: job.total_time || "N/A",
          date: new Date(job.created_at).toLocaleString(),
          mode: job.mode as "default" | "advanced",
        }));

        setJobs(mappedJobs);
      } catch (error) {
        console.error("Error fetching jobs:", error);
        // Don't show error toast - just log it
      } finally {
        setLoadingJobs(false);
      }
    };

    fetchJobs();
  }, [user, searchQuery, statusFilter, refreshTrigger]); // Refetch when filters change

  // Fetch user stats
  useEffect(() => {
    const fetchStats = async () => {
      // Only fetch stats if user is authenticated
      if (!user) {
        setUserStats(null);
        return;
      }

      setLoadingStats(true);
      try {
        const token = await user.getIdToken();

        const response = await fetch("/api/user/stats", {
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch stats: ${response.statusText}`);
        }

        const data = await response.json();
        setUserStats(data);
      } catch (error) {
        console.error("Error fetching user stats:", error);
        // Don't show error - stats are optional
      } finally {
        setLoadingStats(false);
      }
    };

    fetchStats();
  }, [user]);

  const handleSignIn = async () => {
    try {
      await signInWithGoogle();
      toast({
        title: "Success",
        description: "Signed in successfully",
      });
    } catch (error: any) {
      toast({
        title: "Sign In Failed",
        description: error.message || "Failed to sign in",
        variant: "destructive",
      });
    }
  };

  const handleSignOut = async () => {
    try {
      await firebaseSignOut();
      toast({
        title: "Success",
        description: "Signed out successfully",
      });
    } catch (error: any) {
      toast({
        title: "Sign Out Failed",
        description: error.message || "Failed to sign out",
        variant: "destructive",
      });
    }
  };

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
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      // Add Firebase auth token if user is signed in
      if (user) {
        const token = await user.getIdToken();
        headers["Authorization"] = `Bearer ${token}`;
      }

      // Call the real API endpoint
      const response = await fetch("/api/provision/start", {
        method: "POST",
        headers,
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

  const handleDeleteJob = async (jobId: string) => {
    try {
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      // Add Firebase auth token if user is signed in
      if (user) {
        const token = await user.getIdToken();
        headers["Authorization"] = `Bearer ${token}`;
      }

      const response = await fetch(`/api/user/jobs/${jobId}`, {
        method: "DELETE",
        headers,
      });

      if (!response.ok) {
        throw new Error(`Failed to delete job: ${response.statusText}`);
      }

      toast({
        title: "Job Deleted",
        description: "The provisioning job has been deleted successfully",
      });

      // Refresh the job list
      setRefreshTrigger((prev) => prev + 1);
    } catch (error) {
      toast({
        title: "Delete Failed",
        description: error instanceof Error ? error.message : "Unknown error occurred",
        variant: "destructive",
      });
    }
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
            <div className="flex items-center gap-4">
              {/* Authentication UI (only show if enabled) */}
              {isAuthEnabled && (
                <div className="flex items-center gap-2">
                  {loading ? (
                    <span className="text-sm text-muted-foreground">Loading...</span>
                  ) : user ? (
                    <>
                      <div className="flex items-center gap-2 px-3 py-1 rounded-lg bg-muted/50">
                        <User className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm text-foreground max-w-[150px] truncate">
                          {user.email}
                        </span>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleSignOut}
                        title="Sign out"
                      >
                        <LogOut className="h-4 w-4 mr-2" />
                        Sign Out
                      </Button>
                    </>
                  ) : (
                    <Button
                      variant="default"
                      size="sm"
                      onClick={handleSignIn}
                      title="Sign in with Google"
                    >
                      <LogIn className="h-4 w-4 mr-2" />
                      Sign In
                    </Button>
                  )}
                </div>
              )}

              <Button variant="outline" className="gap-2">
                <Settings className="h-4 w-4" />
                Settings
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          {/* User Stats Section - Only show when authenticated */}
          {user && (
            <div>
              <h2 className="text-2xl font-semibold mb-4">Your Dashboard</h2>
              <UserStatsCard stats={userStats} loading={loadingStats} />
            </div>
          )}

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
              <h2 className="text-2xl font-semibold">
                {user ? "Your Recent Provisions" : "Recent Provisions"}
              </h2>
              <Button variant="ghost" size="sm">View All</Button>
            </div>
            {loadingJobs ? (
              <div className="text-center py-8 text-muted-foreground">
                Loading jobs...
              </div>
            ) : (
              <>
                <JobFilters
                  search={searchQuery}
                  status={statusFilter}
                  onSearchChange={setSearchQuery}
                  onStatusChange={setStatusFilter}
                  onClear={() => {
                    setSearchQuery("");
                    setStatusFilter("all");
                  }}
                  resultsCount={jobs.length}
                />
                <EnhancedJobHistoryTable
                  jobs={jobs}
                  onDelete={handleDeleteJob}
                  onViewJob={(jobId) => navigate(`/provision-progress?jobId=${jobId}`)}
                />
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CEDashboard;
