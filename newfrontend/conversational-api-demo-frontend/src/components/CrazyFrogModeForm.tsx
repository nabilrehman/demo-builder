import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Loader2, Sparkles, Info } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface CrazyFrogFormData {
  customer_url: string;
  use_case_context: string;
  industry_hint?: string;
  target_persona?: string;
  demo_complexity?: string;
  special_focus?: string;
  integrations?: string;
  avoid_topics?: string;
}

interface CrazyFrogModeFormProps {
  onProvisionStart: (data: CrazyFrogFormData) => void;
}

export const CrazyFrogModeForm = ({ onProvisionStart }: CrazyFrogModeFormProps) => {
  const [formData, setFormData] = useState<CrazyFrogFormData>({
    customer_url: "",
    use_case_context: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.customer_url.trim()) {
      toast({
        title: "Error",
        description: "Please enter a customer website URL",
        variant: "destructive",
      });
      return;
    }

    if (formData.use_case_context.length < 50) {
      toast({
        title: "Error",
        description: "Please provide at least 50 characters of use case context",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      // Call the backend API
      const response = await fetch('/api/provision/crazy-frog', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const result = await response.json();

      if (result.status === 'success') {
        toast({
          title: "Success! 🐸",
          description: result.message,
        });
        onProvisionStart(formData);
      } else {
        throw new Error(result.message || 'Provisioning failed');
      }
    } catch (error) {
      console.error('Provisioning error:', error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to start provisioning",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const charCount = formData.use_case_context.length;
  const minChars = 50;
  const recommendedChars = 300;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-emerald-50/20 dark:to-emerald-950/20 p-4">
      <Card className="w-full max-w-3xl shadow-2xl border-2 animate-fade-in">
        <CardHeader className="text-center pb-4">
          <div className="flex items-center justify-center mb-4">
            <div className="relative">
              <div className="h-20 w-20 rounded-2xl bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center shadow-xl animate-bounce-slow">
                <span className="text-5xl">🐸</span>
              </div>
              <div className="absolute -top-1 -right-1">
                <Sparkles className="h-6 w-6 text-emerald-500 animate-pulse" />
              </div>
            </div>
          </div>
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-green-600 bg-clip-text text-transparent">
            Crazy Frog Mode
          </CardTitle>
          <CardDescription className="text-base mt-2">
            Advanced customization for Customer Engineers
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Customer URL */}
            <div className="space-y-2">
              <Label htmlFor="customer_url" className="text-base font-semibold">
                Customer Website URL *
              </Label>
              <Input
                id="customer_url"
                type="text"
                placeholder="example.com or https://example.com"
                value={formData.customer_url}
                onChange={(e) => setFormData({ ...formData, customer_url: e.target.value })}
                disabled={isLoading}
                className="text-base"
                required
              />
            </div>

            {/* Use Case Context */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="use_case_context" className="text-base font-semibold">
                  Use Case Context *
                </Label>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs">
                      <p className="text-sm">
                        The more context you provide, the better the demo! Include business challenges,
                        current analytics gaps, key stakeholders, desired outcomes, and specific scenarios.
                      </p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
              <Textarea
                id="use_case_context"
                placeholder="Describe the customer's use case, business challenges, and desired demo scenarios in detail..."
                value={formData.use_case_context}
                onChange={(e) => setFormData({ ...formData, use_case_context: e.target.value })}
                disabled={isLoading}
                className="min-h-[150px] text-base"
                required
              />
              <div className="flex justify-between text-sm">
                <span className={charCount < minChars ? "text-destructive" : charCount < recommendedChars ? "text-yellow-600" : "text-emerald-600"}>
                  {charCount} / {recommendedChars}+ characters
                </span>
                <span className="text-muted-foreground">
                  {charCount < minChars ? `${minChars - charCount} more needed` :
                   charCount < recommendedChars ? "Good, add more for best results" :
                   "Excellent detail! 🎯"}
                </span>
              </div>
            </div>

            {/* Optional Hints Accordion */}
            <Accordion type="single" collapsible className="border rounded-lg">
              <AccordionItem value="hints" className="border-0">
                <AccordionTrigger className="px-4 py-3 hover:no-underline">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-emerald-600" />
                    <span className="font-semibold">Optional Customization Hints</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="px-4 pb-4 pt-2 space-y-4">
                  {/* Industry Vertical */}
                  <div className="space-y-2">
                    <Label htmlFor="industry_hint">Industry Vertical</Label>
                    <Select
                      value={formData.industry_hint}
                      onValueChange={(value) => setFormData({ ...formData, industry_hint: value })}
                      disabled={isLoading}
                    >
                      <SelectTrigger id="industry_hint">
                        <SelectValue placeholder="Select industry..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="retail">Retail & E-commerce</SelectItem>
                        <SelectItem value="financial">Financial Services</SelectItem>
                        <SelectItem value="healthcare">Healthcare</SelectItem>
                        <SelectItem value="manufacturing">Manufacturing</SelectItem>
                        <SelectItem value="saas">SaaS / Technology</SelectItem>
                        <SelectItem value="media">Media & Entertainment</SelectItem>
                        <SelectItem value="telecom">Telecommunications</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Target Persona */}
                  <div className="space-y-2">
                    <Label htmlFor="target_persona">Target Persona</Label>
                    <Select
                      value={formData.target_persona}
                      onValueChange={(value) => setFormData({ ...formData, target_persona: value })}
                      disabled={isLoading}
                    >
                      <SelectTrigger id="target_persona">
                        <SelectValue placeholder="Select audience..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="cfo">CFO / Finance Executive</SelectItem>
                        <SelectItem value="cmo">CMO / Marketing Executive</SelectItem>
                        <SelectItem value="cto">CTO / Technical Executive</SelectItem>
                        <SelectItem value="analyst">Data Analyst / BI Professional</SelectItem>
                        <SelectItem value="business">Business User / Non-Technical</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Demo Complexity */}
                  <div className="space-y-2">
                    <Label htmlFor="demo_complexity">Demo Complexity</Label>
                    <Select
                      value={formData.demo_complexity}
                      onValueChange={(value) => setFormData({ ...formData, demo_complexity: value })}
                      disabled={isLoading}
                    >
                      <SelectTrigger id="demo_complexity">
                        <SelectValue placeholder="Select complexity..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="simple">Simple - Basic queries, single table</SelectItem>
                        <SelectItem value="medium">Medium - JOINs, GROUP BY, time-series</SelectItem>
                        <SelectItem value="advanced">Advanced - Window functions, CTEs, complex SQL</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Special Focus */}
                  <div className="space-y-2">
                    <Label htmlFor="special_focus">Special Focus</Label>
                    <Select
                      value={formData.special_focus}
                      onValueChange={(value) => setFormData({ ...formData, special_focus: value })}
                      disabled={isLoading}
                    >
                      <SelectTrigger id="special_focus">
                        <SelectValue placeholder="Select focus area..." />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="revenue">Revenue Analytics</SelectItem>
                        <SelectItem value="operations">Operational Efficiency</SelectItem>
                        <SelectItem value="marketing">Marketing Attribution</SelectItem>
                        <SelectItem value="customer">Customer Insights</SelectItem>
                        <SelectItem value="custom">Custom</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Integrations */}
                  <div className="space-y-2">
                    <Label htmlFor="integrations">Specific Integrations</Label>
                    <Input
                      id="integrations"
                      type="text"
                      placeholder="e.g., Salesforce, Google Analytics, SAP"
                      value={formData.integrations || ""}
                      onChange={(e) => setFormData({ ...formData, integrations: e.target.value })}
                      disabled={isLoading}
                    />
                  </div>

                  {/* Avoid Topics */}
                  <div className="space-y-2">
                    <Label htmlFor="avoid_topics">Topics to Avoid</Label>
                    <Input
                      id="avoid_topics"
                      type="text"
                      placeholder="e.g., competitor analysis, pricing strategies"
                      value={formData.avoid_topics || ""}
                      onChange={(e) => setFormData({ ...formData, avoid_topics: e.target.value })}
                      disabled={isLoading}
                    />
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>

            {/* Submit Button */}
            <Button
              type="submit"
              disabled={isLoading || charCount < minChars}
              className="w-full bg-gradient-to-r from-emerald-500 to-green-600 hover:from-emerald-600 hover:to-green-700 text-white text-lg py-6"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Unleashing the Frog...
                </>
              ) : (
                <>
                  <span className="mr-2 text-xl">🐸</span>
                  Unleash the Frog
                </>
              )}
            </Button>

            <p className="text-xs text-center text-muted-foreground">
              This will generate a fully customized demo based on your context.
              The process may take 5-10 minutes.
            </p>
          </form>
        </CardContent>
      </Card>

      <style>{`
        @keyframes bounce-slow {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-10px);
          }
        }
        .animate-bounce-slow {
          animation: bounce-slow 3s infinite;
        }
      `}</style>
    </div>
  );
};
