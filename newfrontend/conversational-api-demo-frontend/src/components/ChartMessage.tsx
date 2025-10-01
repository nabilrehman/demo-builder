import { Card } from "@/components/ui/card";
import { useEffect, useRef, useState } from "react";
import embed from "vega-embed";

// Vega-Lite specification type (from Google Conversational Analytics API)
interface VegaLiteSpec {
  $schema?: string;
  [key: string]: any;
}

interface ChartMessageProps {
  chartData: VegaLiteSpec;
}

export const ChartMessage = ({ chartData }: ChartMessageProps) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (chartRef.current && chartData) {
      console.log("Rendering Vega chart with spec:", JSON.stringify(chartData, null, 2));
      
      // Clear previous chart and errors
      chartRef.current.innerHTML = '';
      setError(null);

      // Ensure data has a unique name to avoid Vega errors
      const spec = {
        ...chartData,
        data: {
          ...chartData.data,
          name: chartData.data?.name || `data_${Date.now()}`, // Ensure unique name
        },
        width: 600,
        height: 300,
        background: "transparent",
        padding: 20,
      };

      console.log("Final spec being rendered:", JSON.stringify(spec, null, 2));

      // Embed the Vega-Lite chart
      embed(chartRef.current, spec as any, {
        actions: {
          export: true,
          source: false,
          compiled: false,
          editor: false,
        },
        renderer: "canvas",
      }).then((result) => {
        console.log("Vega chart rendered successfully");
      }).catch((err) => {
        console.error("Vega chart rendering error:", err);
        setError(err.message || "Unknown error");
      });
    }
  }, [chartData]);

  const title = chartData?.title?.text || chartData?.title || 'Data Visualization';

  return (
    <Card className="p-6 bg-card border-border shadow-lg animate-slide-up">
      <h3 className="text-lg font-semibold mb-4 text-foreground">{title}</h3>
      {error ? (
        <div className="w-full min-h-[340px] flex items-center justify-center bg-destructive/10 rounded-lg p-8">
          <div className="text-center">
            <p className="text-destructive font-semibold mb-2">Error rendering chart</p>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
        </div>
      ) : (
        <div ref={chartRef} className="w-full min-h-[340px] flex items-center justify-center" />
      )}
      <p className="text-xs text-muted-foreground mt-4">
        Visualization powered by Google Conversational Analytics API
      </p>
    </Card>
  );
};
