import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { ChevronDown, ChevronUp, Search, Copy, Sparkles, TrendingUp } from 'lucide-react';
import { GoldenQuery } from '@/hooks/useDemoAssets';
import { toast } from 'sonner';

interface GoldenQueriesDisplayProps {
  queries: GoldenQuery[];
}

const COMPLEXITY_COLORS = {
  SIMPLE: 'bg-green-100 text-green-800 border-green-200',
  MEDIUM: 'bg-blue-100 text-blue-800 border-blue-200',
  COMPLEX: 'bg-orange-100 text-orange-800 border-orange-200',
  EXPERT: 'bg-purple-100 text-purple-800 border-purple-200',
};

const COMPLEXITY_DESCRIPTIONS = {
  SIMPLE: 'Single-table queries, basic aggregations',
  MEDIUM: 'Multi-table joins, moderate filtering',
  COMPLEX: 'CTEs, window functions, complex logic',
  EXPERT: 'Advanced analytics, cohort analysis, multiple CTEs',
};

export const GoldenQueriesDisplay = ({ queries }: GoldenQueriesDisplayProps) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [complexityFilter, setComplexityFilter] = useState<string>('all');
  const [expandedQueries, setExpandedQueries] = useState<Set<string>>(new Set());

  const filteredQueries = queries.filter((query) => {
    const matchesSearch = query.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
      query.businessValue.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesComplexity = complexityFilter === 'all' || query.complexity === complexityFilter;
    return matchesSearch && matchesComplexity;
  });

  const toggleQuery = (queryId: string) => {
    const newExpanded = new Set(expandedQueries);
    if (newExpanded.has(queryId)) {
      newExpanded.delete(queryId);
    } else {
      newExpanded.add(queryId);
    }
    setExpandedQueries(newExpanded);
  };

  const copyQuery = async (question: string) => {
    await navigator.clipboard.writeText(question);
    toast.success('Query copied to clipboard', {
      description: 'Paste it into the chat interface to test'
    });
  };

  const copySQL = async (sql: string) => {
    await navigator.clipboard.writeText(sql);
    toast.success('SQL copied to clipboard');
  };

  const complexityCounts = queries.reduce((acc, q) => {
    acc[q.complexity] = (acc[q.complexity] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card className="bg-gradient-to-br from-indigo-50 to-blue-50">
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-indigo-600">{queries.length}</div>
            <div className="text-sm text-gray-600">Total Queries</div>
          </CardContent>
        </Card>
        <Card className={`${COMPLEXITY_COLORS.SIMPLE} border`}>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{complexityCounts.SIMPLE || 0}</div>
            <div className="text-sm">Simple</div>
          </CardContent>
        </Card>
        <Card className={`${COMPLEXITY_COLORS.MEDIUM} border`}>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{complexityCounts.MEDIUM || 0}</div>
            <div className="text-sm">Medium</div>
          </CardContent>
        </Card>
        <Card className={`${COMPLEXITY_COLORS.COMPLEX} border`}>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{complexityCounts.COMPLEX || 0}</div>
            <div className="text-sm">Complex</div>
          </CardContent>
        </Card>
        <Card className={`${COMPLEXITY_COLORS.EXPERT} border`}>
          <CardContent className="pt-6">
            <div className="text-2xl font-bold">{complexityCounts.EXPERT || 0}</div>
            <div className="text-sm">Expert</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search queries or business value..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <Select value={complexityFilter} onValueChange={setComplexityFilter}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="All Complexities" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Complexities</SelectItem>
            <SelectItem value="SIMPLE">Simple</SelectItem>
            <SelectItem value="MEDIUM">Medium</SelectItem>
            <SelectItem value="COMPLEX">Complex</SelectItem>
            <SelectItem value="EXPERT">Expert</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Queries List */}
      <div className="space-y-4">
        {filteredQueries.length === 0 ? (
          <Card>
            <CardContent className="pt-6 text-center text-gray-500">
              No queries match your search criteria
            </CardContent>
          </Card>
        ) : (
          filteredQueries.map((query) => (
            <Card key={query.id} className="hover:shadow-md transition-shadow">
              <Collapsible
                open={expandedQueries.has(query.id)}
                onOpenChange={() => toggleQuery(query.id)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <Badge variant="outline" className="font-mono">
                          #{query.sequence}
                        </Badge>
                        <Badge className={`${COMPLEXITY_COLORS[query.complexity]} border`}>
                          {query.complexity}
                        </Badge>
                      </div>
                      <CardTitle className="text-lg leading-tight mb-2">
                        {query.question}
                      </CardTitle>
                      <CardDescription className="flex items-start gap-2">
                        <TrendingUp className="h-4 w-4 flex-shrink-0 mt-0.5" />
                        <span>{query.businessValue}</span>
                      </CardDescription>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation();
                          copyQuery(query.question);
                        }}
                      >
                        <Copy className="h-4 w-4 mr-1" />
                        Copy Query
                      </Button>
                      <CollapsibleTrigger asChild>
                        <Button size="sm" variant="outline">
                          {expandedQueries.has(query.id) ? (
                            <>
                              <ChevronUp className="h-4 w-4 mr-1" />
                              Hide SQL
                            </>
                          ) : (
                            <>
                              <ChevronDown className="h-4 w-4 mr-1" />
                              Show SQL
                            </>
                          )}
                        </Button>
                      </CollapsibleTrigger>
                    </div>
                  </div>
                </CardHeader>

                <CollapsibleContent>
                  <CardContent>
                    <div className="bg-gray-900 text-gray-100 p-4 rounded-lg relative">
                      <Button
                        size="sm"
                        variant="ghost"
                        className="absolute top-2 right-2 text-gray-400 hover:text-white"
                        onClick={() => copySQL(query.sql)}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                      <pre className="text-sm overflow-x-auto pr-12">
                        <code>{query.sql}</code>
                      </pre>
                    </div>
                    <div className="mt-3 text-xs text-gray-500">
                      <Sparkles className="inline h-3 w-3 mr-1" />
                      {COMPLEXITY_DESCRIPTIONS[query.complexity]}
                    </div>
                  </CardContent>
                </CollapsibleContent>
              </Collapsible>
            </Card>
          ))
        )}
      </div>

      {/* Tips */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <h3 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
            <Sparkles className="h-4 w-4" />
            Using Golden Queries in Demos
          </h3>
          <ul className="text-sm text-blue-800 space-y-1 ml-6 list-disc">
            <li>Start with SIMPLE queries to establish baseline understanding</li>
            <li>Progress to MEDIUM queries to show multi-table capabilities</li>
            <li>Use COMPLEX queries to demonstrate advanced analytics</li>
            <li>Close with EXPERT queries to showcase the platform's full power</li>
            <li>Click "Copy Query" to paste directly into the chat interface</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};
