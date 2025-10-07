import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Sparkles, Zap, Database, MessageSquare, BarChart3, Shield, LogIn, LogOut, User } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";

const HomePage = () => {
  const navigate = useNavigate();
  const { user, loading, signInWithGoogle, signOut, isAuthEnabled } = useAuth();
  const { toast } = useToast();

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
      await signOut();
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-card/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-gradient-button flex items-center justify-center shadow-lg">
                <Sparkles className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                  CAPI Demo Generator
                </h1>
                <p className="text-xs text-muted-foreground">AI-Powered Demo Provisioning</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
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
              <Button
                onClick={() => navigate("/ce-dashboard")}
                size="sm"
              >
                Go to Dashboard
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
            <Sparkles className="h-4 w-4" />
            <span>Automated Demo Provisioning Platform</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-primary bg-clip-text text-transparent">
            Generate Production-Ready Demos in Minutes
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Transform any website into a fully functional conversational AI demo with automatic data modeling,
            BigQuery provisioning, and intelligent query generation.
          </p>
          <div className="flex gap-4 justify-center">
            <Button
              size="lg"
              onClick={() => navigate("/ce-dashboard")}
              className="text-lg px-8"
            >
              <Zap className="mr-2 h-5 w-5" />
              Start Provisioning
            </Button>
            <Button
              size="lg"
              variant="outline"
              onClick={() => navigate("/analytics-dashboard")}
              className="text-lg px-8"
            >
              <BarChart3 className="mr-2 h-5 w-5" />
              View Analytics
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">How It Works</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Our AI-powered system analyzes your target website and automatically generates everything you need for a compelling demo.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          <Card className="border-2 hover:border-primary/50 transition-colors">
            <CardHeader>
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <Sparkles className="h-6 w-6 text-primary" />
              </div>
              <CardTitle>AI Research Agent</CardTitle>
              <CardDescription>
                Automatically crawls and analyzes your target website to understand business context, products, and use cases.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="border-2 hover:border-primary/50 transition-colors">
            <CardHeader>
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <Database className="h-6 w-6 text-primary" />
              </div>
              <CardTitle>Smart Data Modeling</CardTitle>
              <CardDescription>
                Generates realistic data schemas and populates BigQuery with synthetic data tailored to your demo scenario.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="border-2 hover:border-primary/50 transition-colors">
            <CardHeader>
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <MessageSquare className="h-6 w-6 text-primary" />
              </div>
              <CardTitle>Conversational AI</CardTitle>
              <CardDescription>
                Creates a Gemini-powered conversational analytics agent with golden queries and natural language understanding.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="border-2 hover:border-primary/50 transition-colors">
            <CardHeader>
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <Zap className="h-6 w-6 text-primary" />
              </div>
              <CardTitle>Instant Deployment</CardTitle>
              <CardDescription>
                One-click provisioning to BigQuery with automatic dataset creation, table generation, and agent configuration.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="border-2 hover:border-primary/50 transition-colors">
            <CardHeader>
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <BarChart3 className="h-6 w-6 text-primary" />
              </div>
              <CardTitle>Demo Assets</CardTitle>
              <CardDescription>
                Get executive summaries, talking tracks, golden queries, and schema documentation ready for presentations.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="border-2 hover:border-primary/50 transition-colors">
            <CardHeader>
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <Shield className="h-6 w-6 text-primary" />
              </div>
              <CardTitle>Secure & Scalable</CardTitle>
              <CardDescription>
                Firebase authentication, user-scoped data isolation, and enterprise-grade security built in.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-16">
        <Card className="border-2 border-primary/20 bg-gradient-to-br from-primary/5 to-primary/10 max-w-4xl mx-auto">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl mb-2">Ready to Create Your First Demo?</CardTitle>
            <CardDescription className="text-lg">
              Start provisioning AI-powered conversational analytics demos in minutes
            </CardDescription>
          </CardHeader>
          <CardContent className="flex justify-center">
            <Button
              size="lg"
              onClick={() => navigate("/ce-dashboard")}
              className="text-lg px-12"
            >
              <Zap className="mr-2 h-5 w-5" />
              Get Started
            </Button>
          </CardContent>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t mt-20">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <span className="text-sm text-muted-foreground">
                CAPI Demo Generator - Powered by Gemini & Claude
              </span>
            </div>
            <div className="flex gap-6 text-sm text-muted-foreground">
              <button
                onClick={() => navigate("/ce-dashboard")}
                className="hover:text-primary transition-colors"
              >
                Dashboard
              </button>
              <button
                onClick={() => navigate("/analytics-dashboard")}
                className="hover:text-primary transition-colors"
              >
                Analytics
              </button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
