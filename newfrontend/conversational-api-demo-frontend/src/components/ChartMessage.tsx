import { Card } from "@/components/ui/card";
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface ChartData {
  type: "bar" | "line" | "pie";
  title: string;
  data: any[];
  xKey?: string;
  yKey?: string;
  nameKey?: string;
}

interface ChartMessageProps {
  chartData: ChartData;
}

// Vibrant color palette
const COLORS = [
  '#8b5cf6', // Purple
  '#ec4899', // Pink
  '#f59e0b', // Amber
  '#10b981', // Emerald
  '#3b82f6', // Blue
  '#6366f1', // Indigo
  '#14b8a6', // Teal
  '#f97316', // Orange
  '#84cc16', // Lime
  '#06b6d4', // Cyan
  '#a855f7', // Purple variant
  '#ef4444'  // Red
];

export const ChartMessage = ({ chartData }: ChartMessageProps) => {
  console.log("Rendering chart with data:", chartData);

  if (!chartData || !chartData.data || chartData.data.length === 0) {
    return (
      <Card className="p-6 bg-gradient-to-br from-card to-card/50 border-border shadow-xl animate-slide-up backdrop-blur-sm">
        <div className="text-center text-muted-foreground">
          No data available for visualization
        </div>
      </Card>
    );
  }

  const { type, title, data, xKey, yKey, nameKey } = chartData;

  const renderChart = () => {
    switch (type) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <defs>
                <linearGradient id="colorBar" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.9}/>
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0.6}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.5} />
              <XAxis
                dataKey={xKey}
                stroke="#6b7280"
                angle={-45}
                textAnchor="end"
                height={100}
                tick={{ fill: '#374151', fontSize: 12 }}
              />
              <YAxis
                stroke="#6b7280"
                tick={{ fill: '#374151', fontSize: 12 }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                  padding: '12px'
                }}
                labelStyle={{ color: '#111827', fontWeight: 600, marginBottom: '4px' }}
                itemStyle={{ color: '#6366f1' }}
              />
              <Legend
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="circle"
              />
              <Bar
                dataKey={yKey}
                fill="url(#colorBar)"
                radius={[8, 8, 0, 0]}
                animationDuration={800}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        );

      case 'line':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <defs>
                <linearGradient id="colorLine" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ec4899" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#ec4899" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.5} />
              <XAxis
                dataKey={xKey}
                stroke="#6b7280"
                angle={-45}
                textAnchor="end"
                height={100}
                tick={{ fill: '#374151', fontSize: 12 }}
              />
              <YAxis
                stroke="#6b7280"
                tick={{ fill: '#374151', fontSize: 12 }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                  padding: '12px'
                }}
                labelStyle={{ color: '#111827', fontWeight: 600 }}
                itemStyle={{ color: '#ec4899' }}
              />
              <Legend
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="circle"
              />
              <Line
                type="monotone"
                dataKey={yKey}
                stroke="#ec4899"
                strokeWidth={3}
                dot={{ fill: '#ec4899', r: 5 }}
                activeDot={{ r: 7, fill: '#f43f5e' }}
                animationDuration={800}
              />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={true}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={120}
                fill="#8884d8"
                dataKey={yKey}
                animationDuration={800}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                  padding: '12px'
                }}
                labelStyle={{ color: '#111827', fontWeight: 600 }}
              />
              <Legend
                verticalAlign="bottom"
                height={36}
                iconType="circle"
              />
            </PieChart>
          </ResponsiveContainer>
        );

      default:
        return <div className="text-muted-foreground">Unsupported chart type</div>;
    }
  };

  return (
    <Card className="p-6 bg-gradient-to-br from-card to-card/50 border-border shadow-xl animate-slide-up backdrop-blur-sm">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-foreground bg-clip-text bg-gradient-to-r from-primary to-primary/60">
          {title}
        </h3>
        <div className="px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium">
          {type.toUpperCase()}
        </div>
      </div>
      <div className="w-full h-[400px] rounded-lg bg-background/50 p-4">
        {renderChart()}
      </div>
      <p className="text-xs text-muted-foreground mt-4 flex items-center gap-2">
        <span className="inline-block w-2 h-2 rounded-full bg-primary animate-pulse"></span>
        Powered by Google Conversational Analytics API
      </p>
    </Card>
  );
};
