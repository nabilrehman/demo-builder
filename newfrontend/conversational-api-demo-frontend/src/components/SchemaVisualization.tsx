import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ChevronDown, ChevronRight, Database, Copy, Search } from 'lucide-react';
import { TableSchema } from '@/hooks/useDemoAssets';
import { toast } from 'sonner';

interface SchemaVisualizationProps {
  schema: TableSchema[];
}

const TYPE_COLORS: Record<string, string> = {
  STRING: 'bg-blue-100 text-blue-700',
  INTEGER: 'bg-green-100 text-green-700',
  FLOAT: 'bg-purple-100 text-purple-700',
  BOOLEAN: 'bg-orange-100 text-orange-700',
  TIMESTAMP: 'bg-pink-100 text-pink-700',
  DATE: 'bg-indigo-100 text-indigo-700',
};

export const SchemaVisualization = ({ schema }: SchemaVisualizationProps) => {
  const [expandedTables, setExpandedTables] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');

  const toggleTable = (tableName: string) => {
    const newExpanded = new Set(expandedTables);
    if (newExpanded.has(tableName)) {
      newExpanded.delete(tableName);
    } else {
      newExpanded.add(tableName);
    }
    setExpandedTables(newExpanded);
  };

  const copyTableName = async (tableName: string) => {
    await navigator.clipboard.writeText(tableName);
    toast.success('Table name copied', {
      description: tableName
    });
  };

  const filteredSchema = schema.filter((table) =>
    table.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    table.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalFields = schema.reduce((sum, table) => sum + table.fieldCount, 0);
  const totalRows = schema.reduce((sum, table) => sum + table.rowCount, 0);

  return (
    <div className="space-y-6">
      {/* Schema Stats */}
      <div className="grid grid-cols-3 gap-4">
        <Card className="bg-gradient-to-br from-indigo-50 to-blue-50">
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-indigo-600">{schema.length}</div>
            <div className="text-sm text-gray-600">Total Tables</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-purple-50 to-pink-50">
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-purple-600">{totalFields}</div>
            <div className="text-sm text-gray-600">Total Fields</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-green-50 to-emerald-50">
          <CardContent className="pt-6">
            <div className="text-2xl font-bold text-green-600">
              {totalRows.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Total Rows</div>
          </CardContent>
        </Card>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
        <Input
          placeholder="Search tables..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Tables List */}
      <div className="space-y-3">
        {filteredSchema.length === 0 ? (
          <Card>
            <CardContent className="pt-6 text-center text-gray-500">
              No tables match your search
            </CardContent>
          </Card>
        ) : (
          filteredSchema.map((table) => (
            <Card key={table.name} className="hover:shadow-md transition-shadow">
              <Collapsible
                open={expandedTables.has(table.name)}
                onOpenChange={() => toggleTable(table.name)}
              >
                <CardHeader className="cursor-pointer" onClick={() => toggleTable(table.name)}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1">
                      {expandedTables.has(table.name) ? (
                        <ChevronDown className="h-5 w-5 text-gray-400" />
                      ) : (
                        <ChevronRight className="h-5 w-5 text-gray-400" />
                      )}
                      <Database className="h-5 w-5 text-indigo-600" />
                      <div className="flex-1">
                        <CardTitle className="text-lg font-mono">{table.name}</CardTitle>
                        <CardDescription className="mt-1">
                          {table.description}
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right text-sm">
                        <div className="text-gray-600">
                          {table.rowCount.toLocaleString()} rows
                        </div>
                        <div className="text-gray-500">
                          {table.fieldCount} fields
                        </div>
                      </div>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => {
                          e.stopPropagation();
                          copyTableName(table.name);
                        }}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>

                <CollapsibleContent>
                  <CardContent>
                    <div className="border rounded-lg overflow-hidden">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead className="w-1/3">Field Name</TableHead>
                            <TableHead className="w-1/6">Type</TableHead>
                            <TableHead className="w-1/12">Mode</TableHead>
                            <TableHead>Description</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {table.fields.map((field) => (
                            <TableRow key={field.name}>
                              <TableCell className="font-mono text-sm">
                                {field.name}
                              </TableCell>
                              <TableCell>
                                <Badge
                                  variant="outline"
                                  className={`${TYPE_COLORS[field.type] || 'bg-gray-100 text-gray-700'} border-0`}
                                >
                                  {field.type}
                                </Badge>
                              </TableCell>
                              <TableCell>
                                {field.mode && (
                                  <Badge
                                    variant="outline"
                                    className={
                                      field.mode === 'REQUIRED'
                                        ? 'bg-red-100 text-red-700 border-red-200'
                                        : 'bg-gray-100 text-gray-600 border-gray-200'
                                    }
                                  >
                                    {field.mode}
                                  </Badge>
                                )}
                              </TableCell>
                              <TableCell className="text-sm text-gray-600">
                                {field.description || '-'}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </CardContent>
                </CollapsibleContent>
              </Collapsible>
            </Card>
          ))
        )}
      </div>

      {/* Relationships Info */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <h3 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
            <Database className="h-4 w-4" />
            Key Relationships
          </h3>
          <div className="space-y-2 text-sm text-blue-800">
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="bg-white">merchants</Badge>
              <span>→</span>
              <Badge variant="outline" className="bg-white">stores</Badge>
              <span className="text-xs">(1:N - merchant_id)</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="bg-white">merchants</Badge>
              <span>→</span>
              <Badge variant="outline" className="bg-white">orders</Badge>
              <span className="text-xs">(1:N - merchant_id)</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="bg-white">customers</Badge>
              <span>→</span>
              <Badge variant="outline" className="bg-white">orders</Badge>
              <span className="text-xs">(1:N - customer_id)</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="bg-white">orders</Badge>
              <span>→</span>
              <Badge variant="outline" className="bg-white">payments</Badge>
              <span className="text-xs">(1:1 - payment_id)</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="bg-white">orders</Badge>
              <span>→</span>
              <Badge variant="outline" className="bg-white">order_line_items</Badge>
              <span className="text-xs">(1:N - order_id)</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="bg-white">stores</Badge>
              <span>←→</span>
              <Badge variant="outline" className="bg-white">apps</Badge>
              <span className="text-xs">(N:M via store_app_installs)</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tips */}
      <Card className="bg-amber-50 border-amber-200">
        <CardContent className="pt-6">
          <h3 className="font-semibold text-amber-900 mb-2">Schema Tips</h3>
          <ul className="text-sm text-amber-800 space-y-1 ml-6 list-disc">
            <li>Click table names to expand and see field details</li>
            <li>Use the Copy button to quickly reference tables in queries</li>
            <li>REQUIRED fields are marked with red badges</li>
            <li>Foreign key relationships enable complex analytics queries</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};
