/**
 * QuickInsights Component
 *
 * Displays golden queries as clickable suggestions
 * Users can click to execute and auto-add to dashboard
 */

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Sparkles, ChevronDown, ChevronUp, Plus, Loader2 } from 'lucide-react';
import { GoldenQuery } from '../types';

interface QuickInsightsProps {
  queries: GoldenQuery[];
  onExecute: (query: GoldenQuery) => Promise<void>;
}

export function QuickInsights({ queries, onExecute }: QuickInsightsProps) {
  const [isOpen, setIsOpen] = useState(true);
  const [executingId, setExecutingId] = useState<string | null>(null);

  if (!queries || queries.length === 0) {
    return null;
  }

  const handleExecute = async (query: GoldenQuery) => {
    setExecutingId(query.id);
    try {
      await onExecute(query);
    } finally {
      setExecutingId(null);
    }
  };

  // Show top 5 queries only
  const displayQueries = queries.slice(0, 5);

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen} className="mb-6">
      <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-primary/10">
        <CollapsibleTrigger asChild>
          <button className="w-full p-4 flex items-center justify-between hover:bg-primary/5 transition-colors">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <h3 className="font-semibold text-foreground">Quick Insights</h3>
              <Badge variant="secondary" className="text-xs">
                {displayQueries.length} available
              </Badge>
            </div>
            {isOpen ? (
              <ChevronUp className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            )}
          </button>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <CardContent className="pt-0 pb-4 space-y-2">
            {displayQueries.map((query) => (
              <Card
                key={query.id}
                className="p-3 hover:shadow-md transition-all duration-200 border-border/50 bg-background/80"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm text-foreground leading-snug mb-2">
                      {query.question}
                    </p>
                    {query.businessValue && (
                      <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
                        🎯 {query.businessValue}
                      </p>
                    )}
                    <div className="flex items-center gap-2">
                      <Badge
                        variant={
                          query.complexity === 'SIMPLE'
                            ? 'default'
                            : query.complexity === 'MEDIUM'
                            ? 'secondary'
                            : 'outline'
                        }
                        className="text-xs"
                      >
                        {query.complexity}
                      </Badge>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    onClick={() => handleExecute(query)}
                    disabled={executingId !== null}
                    className="gap-1 flex-shrink-0"
                  >
                    {executingId === query.id ? (
                      <>
                        <Loader2 className="h-3 w-3 animate-spin" />
                        Adding...
                      </>
                    ) : (
                      <>
                        <Plus className="h-3 w-3" />
                        Add
                      </>
                    )}
                  </Button>
                </div>
              </Card>
            ))}
          </CardContent>
        </CollapsibleContent>
      </Card>
    </Collapsible>
  );
}
