# Analytics Dashboard Feature

## Overview

A conversational dashboard builder that showcases the power of Google's Conversational Analytics API. Non-technical users can ask questions about their data and build custom dashboards on the fly.

## Core Capability

**"Ask questions → Get insights → Build your dashboard"**

- No SQL knowledge required
- No technical training needed
- Natural language queries
- Instant visualizations
- Custom dashboards built through conversation

## URL & Parameters

```
/analytics-dashboard?dataset_id=XXX&agent_id=XXX&job_id=XXX
```

**Required Parameters:**
- `dataset_id` - BigQuery dataset ID
- `agent_id` - CAPI agent ID
- `job_id` - Provisioning job ID (for golden queries)

## Features

### 1. **Chat Explorer** (Left Panel - 45%)
- Natural language chat interface
- Ask any question about your data
- Real-time AI responses
- Chart visualizations in chat
- **"Add to Dashboard"** button on charts

### 2. **Insights Dashboard** (Right Panel - 55%)
- Quick Insights panel (from golden queries)
- Grid of pinned charts (2 columns)
- Empty state with helpful guidance
- Read-only, additive experience (no remove)
- Session-only (no persistence)

### 3. **Supported Chart Types**
- **Bar Chart** - Comparisons, rankings
- **Line Chart** - Trends over time
- **Pie Chart** - Distribution, proportions

### 4. **Quick Insights**
- Pre-generated golden queries
- Click to execute and auto-add to dashboard
- Complexity badges (SIMPLE, MEDIUM, COMPLEX)
- Business value descriptions

## File Structure

```
src/features/analytics-dashboard/
├── AnalyticsDashboard.tsx         # Main page component
├── index.ts                       # Public exports
├── types.ts                       # TypeScript interfaces
├── components/
│   ├── ChatExplorer.tsx          # Chat interface (left panel)
│   ├── InsightsGrid.tsx          # Dashboard grid (right panel)
│   ├── InsightCard.tsx           # Individual chart wrapper
│   └── QuickInsights.tsx         # Golden query suggestions
└── hooks/
    ├── useDashboardInsights.ts   # Chart state management
    └── useGoldenQueries.ts       # Fetch golden queries from API
```

## User Flow

1. **Initial State**
   - Empty dashboard with helpful guidance
   - Quick Insights suggestions displayed
   - Example questions shown in chat

2. **Exploration**
   - User asks: "What is total revenue?"
   - AI responds with answer + chart
   - User clicks "Add to Dashboard"
   - Chart appears in grid

3. **Building Dashboard**
   - Continue asking questions
   - Pin useful insights
   - Try Quick Insights for instant additions
   - Dashboard grows organically

4. **Final State**
   - Custom dashboard with 5-10 insights
   - All built through conversation
   - No SQL, no configuration needed

## API Integration

### Chat API (`/api/chat`)
```typescript
POST /api/chat
{
  "message": "What is total revenue?",
  "dataset_id": "nike_demo_123",
  "agent_id": "agent_456"
}

Response:
{
  "response": "Total revenue is $1.2M",
  "chartData": {
    "type": "bar",
    "title": "Revenue by Month",
    "data": [...],
    "xKey": "month",
    "yKey": "revenue"
  },
  "sqlQuery": "SELECT ..."
}
```

### Golden Queries API (`/api/provision/assets/{jobId}`)
```typescript
GET /api/provision/assets/{jobId}

Response:
{
  "golden_queries": [
    {
      "id": "1",
      "question": "What are the top 10 customers?",
      "sql": "SELECT ...",
      "businessValue": "Identify key revenue drivers",
      "complexity": "SIMPLE"
    }
  ]
}
```

## Component Props

### AnalyticsDashboard
No props - reads from URL params

### ChatExplorer
```typescript
{
  datasetId: string | null;
  agentId: string | null;
  demoTitle?: string;
  goldenQueries: GoldenQuery[];
  onPinInsight: (question, chartData, sqlQuery?, source?) => void;
}
```

### InsightsGrid
```typescript
{
  insights: DashboardInsight[];
  goldenQueries: GoldenQuery[];
  demoTitle?: string;
  datasetId: string | null;
  agentId: string | null;
  onAddInsight: (question, chartData, sqlQuery?, source?) => void;
}
```

## State Management

### useDashboardInsights
```typescript
const { insights, addInsight, insightCount } = useDashboardInsights();

// Add insight
addInsight(
  "What is total revenue?",
  chartData,
  "SELECT SUM(amount)...",
  "conversation" // or "quick-insight"
);
```

### useGoldenQueries
```typescript
const { goldenQueries, loading, error } = useGoldenQueries(jobId);
```

## Customization

### Change Split Ratio
Edit `AnalyticsDashboard.tsx`:
```tsx
<ChatExplorer className="w-[40%]" />  {/* Default: 45% */}
<InsightsGrid className="w-[60%]" />  {/* Default: 55% */}
```

### Modify Grid Layout
Edit `InsightsGrid.tsx`:
```tsx
<div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
  {/* Default: 2 columns, change to 3 */}
</div>
```

### Change Quick Insights Limit
Edit `QuickInsights.tsx`:
```typescript
const displayQueries = queries.slice(0, 10); // Default: 5
```

## How to Delete This Feature

**Complete removal in 2 steps:**

1. Delete the feature directory:
   ```bash
   rm -rf src/features/analytics-dashboard
   ```

2. Remove route from `src/App.tsx`:
   ```diff
   - import { AnalyticsDashboard } from "./features/analytics-dashboard";
   - <Route path="/analytics-dashboard" element={<AnalyticsDashboard />} />
   ```

That's it! No other files are affected.

## Testing

### Local Development
```bash
# Navigate to dashboard with test parameters
http://localhost:8000/analytics-dashboard?dataset_id=test&agent_id=test&job_id=test
```

### Production URL
```
https://your-app.com/analytics-dashboard?dataset_id=XXX&agent_id=XXX&job_id=XXX
```

### Test Scenarios

1. **Empty State**: Visit without asking questions
2. **Chat Flow**: Ask "What is total revenue?" → Click "Add to Dashboard"
3. **Quick Insights**: Click Quick Insight card → Auto-adds to dashboard
4. **Multiple Charts**: Add 5+ insights → Verify grid layout
5. **No Data**: Ask question that returns no chart → Verify error handling

## Dependencies

**Existing Components (Reused):**
- `@/components/ChartMessage` - Chart rendering
- `@/components/ui/*` - UI primitives (Card, Button, etc.)

**External Libraries:**
- `react-router-dom` - URL params
- `recharts` - Chart rendering (via ChartMessage)
- `sonner` - Toast notifications

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Performance

- **Initial Load**: < 1s
- **Chat Response**: 2-5s (API dependent)
- **Chart Rendering**: < 100ms
- **State Updates**: Instant (React state)

## Accessibility

- Keyboard navigation supported
- ARIA labels on interactive elements
- Screen reader friendly
- Focus management

## Future Enhancements (Optional)

- [ ] Export dashboard as PDF
- [ ] Share dashboard via URL
- [ ] Save dashboard to backend
- [ ] Drag-and-drop chart reordering
- [ ] Chart customization (colors, titles)
- [ ] Remove/edit charts
- [ ] Chart annotations
- [ ] Dashboard templates

## License

Part of the Demo Generation CAPI project.

---

**Built to showcase:** How conversational AI democratizes data analytics for non-technical users.
