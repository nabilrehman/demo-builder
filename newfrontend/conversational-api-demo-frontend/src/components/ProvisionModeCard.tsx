import { ReactNode } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface ProvisionModeCardProps {
  title: string;
  description: string;
  icon: ReactNode;
  children: ReactNode;
  variant?: "default" | "advanced";
  onClick?: () => void;
}

export const ProvisionModeCard = ({
  title,
  description,
  icon,
  children,
  variant = "default",
  onClick
}: ProvisionModeCardProps) => {
  const isAdvanced = variant === "advanced";

  return (
    <Card
      className={cn(
        "group relative overflow-hidden transition-all duration-300",
        "hover:shadow-xl hover:-translate-y-1",
        onClick && "cursor-pointer",
        isAdvanced && "border-primary/30"
      )}
      onClick={onClick}
    >
      {/* Gradient overlay for advanced mode */}
      {isAdvanced && (
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-pink-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      )}

      <CardHeader className="relative">
        <div className="flex items-start justify-between">
          <div className="space-y-2 flex-1">
            <CardTitle className="text-xl font-bold tracking-tight">
              {title}
            </CardTitle>
            <CardDescription className="text-sm">
              {description}
            </CardDescription>
          </div>
          <div
            className={cn(
              "p-3 rounded-xl transition-all duration-300",
              isAdvanced
                ? "bg-gradient-button text-primary-foreground group-hover:scale-110"
                : "bg-muted text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary group-hover:scale-110"
            )}
          >
            {icon}
          </div>
        </div>
      </CardHeader>

      <CardContent className="relative">
        {children}
      </CardContent>

      {/* Animated border effect on hover */}
      <div
        className={cn(
          "absolute inset-0 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none",
          isAdvanced && "border-2 border-primary/20"
        )}
      />
    </Card>
  );
};
