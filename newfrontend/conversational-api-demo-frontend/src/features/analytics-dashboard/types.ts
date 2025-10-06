/**
 * Analytics Dashboard Feature Types
 *
 * All TypeScript interfaces for the conversational dashboard feature
 */

// Chart data structure (from existing ChartMessage component)
export interface ChartData {
  type: "bar" | "line" | "pie";
  title: string;
  data: any[];
  xKey?: string;
  yKey?: string;
  nameKey?: string;
}

// Dashboard insight (a pinned chart)
export interface DashboardInsight {
  id: string;
  question: string;
  chartData: ChartData;
  sqlQuery?: string;
  timestamp: number;
  source: 'conversation' | 'quick-insight';
}

// Golden query from provisioning API
export interface GoldenQuery {
  id: string;
  question: string;
  sql: string;
  businessValue: string;
  complexity: string;
  sequence?: number;
}

// Chat message structure
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  chartData?: ChartData;
  sqlQuery?: string;
  timestamp: number;
}

// API response from /api/chat
export interface ChatResponse {
  response: string;
  chartData?: ChartData;
  sqlQuery?: string;
}

// API response from /api/provision/assets/{jobId}
export interface DemoAssets {
  job_id: string;
  customer_url: string;
  status: string;
  demo_title?: string;
  golden_queries?: GoldenQuery[];
  schema?: any[];
  metadata?: any;
}
