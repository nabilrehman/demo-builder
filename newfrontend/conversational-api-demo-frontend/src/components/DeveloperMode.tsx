import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";

interface DeveloperModeProps {
  query: string;
  response: string;
}

export const DeveloperMode = ({ query, response }: DeveloperModeProps) => {
  return (
    <Card className="p-4 border-border bg-card/50 backdrop-blur-sm">
      <h3 className="text-sm font-semibold mb-3 text-foreground">Developer Mode</h3>
      <ScrollArea className="h-48">
        <div className="space-y-4 text-xs font-mono">
          <div>
            <p className="text-muted-foreground mb-1">Query:</p>
            <pre className="bg-muted p-2 rounded text-foreground overflow-x-auto">
              {query || "No query yet"}
            </pre>
          </div>
          <div>
            <p className="text-muted-foreground mb-1">Response:</p>
            <pre className="bg-muted p-2 rounded text-foreground overflow-x-auto">
              {response || "No response yet"}
            </pre>
          </div>
        </div>
      </ScrollArea>
    </Card>
  );
};
