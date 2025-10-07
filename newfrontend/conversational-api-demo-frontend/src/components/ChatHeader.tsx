import { Settings, LogIn, LogOut, User } from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";

interface ChatHeaderProps {
  brandName: string;
  logoUrl?: string;
  faviconUrl?: string;
  developerMode: boolean;
  onDeveloperModeChange: (enabled: boolean) => void;
  onReconfigure?: () => void;
}

export const ChatHeader = ({
  brandName,
  logoUrl,
  faviconUrl,
  developerMode,
  onDeveloperModeChange,
  onReconfigure
}: ChatHeaderProps) => {
  const { user, loading, signInWithGoogle, signOut: firebaseSignOut, isAuthEnabled } = useAuth();
  const { toast } = useToast();
  const displayLogo = logoUrl || faviconUrl;

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

  return (
    <header className="border-b bg-card/80 backdrop-blur-sm shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {displayLogo ? (
              <div className="h-10 w-10 rounded-xl overflow-hidden shadow-lg bg-background flex items-center justify-center">
                <img
                  src={displayLogo}
                  alt={`${brandName} logo`}
                  className="h-full w-full object-contain"
                  onError={(e) => {
                    // Fallback to favicon or gradient if logo fails
                    if (e.currentTarget.src === logoUrl && faviconUrl) {
                      e.currentTarget.src = faviconUrl;
                    } else {
                      e.currentTarget.style.display = 'none';
                      const parent = e.currentTarget.parentElement;
                      if (parent) {
                        parent.className = "h-10 w-10 rounded-xl bg-gradient-button flex items-center justify-center shadow-lg";
                        parent.innerHTML = `<span class="text-xl font-bold text-primary-foreground">${brandName.charAt(0)}</span>`;
                      }
                    }
                  }}
                />
              </div>
            ) : (
              <div className="h-10 w-10 rounded-xl bg-gradient-button flex items-center justify-center shadow-lg">
                <span className="text-xl font-bold text-primary-foreground">
                  {brandName.charAt(0)}
                </span>
              </div>
            )}
            <div>
              <h1 className="text-xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                {brandName}
              </h1>
              <p className="text-xs text-muted-foreground">AI-Powered Assistant</p>
            </div>
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

            <div className="flex items-center gap-2">
              <Label htmlFor="dev-mode" className="text-sm text-muted-foreground cursor-pointer">
                Developer Mode
              </Label>
              <Switch
                id="dev-mode"
                checked={developerMode}
                onCheckedChange={onDeveloperModeChange}
              />
            </div>
            {onReconfigure && (
              <Button
                variant="outline"
                size="icon"
                onClick={onReconfigure}
                title="Reconfigure branding"
              >
                <Settings className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
