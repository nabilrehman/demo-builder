import { Settings } from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

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
  const displayLogo = logoUrl || faviconUrl;

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
