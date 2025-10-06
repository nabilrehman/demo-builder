# Demo Assets Viewer - Quick Start Guide

## Viewing the Demo Assets Page

### Development Mode

1. **Start the dev server:**
```bash
cd /home/admin_/final_demo/capi/demo-gen-capi/newfrontend/conversational-api-demo-frontend
npm run dev
```

2. **Open in browser:**
```
http://localhost:8080/demo-assets
```

3. **You'll see:** Complete Shopify demo with 12 golden queries, 15 tables, 403K rows

### URL Parameters

- **With job ID:** `http://localhost:8080/demo-assets?jobId=demo_shopify_20251004_1234`
- **Without job ID:** Uses default mock data automatically

---

## Mock Data

Currently using **Shopify demo** from SUMMARY.md:
- **Demo Title:** "From Dashboard Chaos to Merchant Intelligence..."
- **12 Golden Queries:** SIMPLE → EXPERT complexity
- **15 Tables:** merchants, orders, payments, customers, apps, etc.
- **403,200 rows** across all tables
- **25.51 MB** storage size

---

## Page Sections

### 1. Success Banner (Top)
- Green alert with "🎉 Provision Complete!"
- Shows provision URL and total time (11m 23s)
- Always visible at top of page

### 2. Launch Chat Button (Prominent)
- Large purple gradient button
- Opens chat interface: `https://chat.demo.com?website=shopify.com&dataset=shopify_capi_demo_20251004`
- Primary call-to-action

### 3. Action Buttons (4 buttons)
- **Download YAML:** Downloads capi_instructions_shopify.yaml (57KB)
- **Copy Dataset ID:** Copies to clipboard with toast
- **View in BigQuery:** Opens BigQuery console
- **Re-run Provision:** Triggers re-provisioning (with confirmation)

### 4. Tabs (Main Content)

#### Tab 1: Demo Title
- Large demo title with "Principal Architect Level" badge
- Executive summary card
- Business challenges (numbered list of 5 pain points)
- Talking track preview (demo flow recommendations)
- Demo tips

#### Tab 2: Golden Queries
- Statistics dashboard (2 SIMPLE, 3 MEDIUM, 4 COMPLEX, 3 EXPERT)
- Search box (searches question and business value)
- Complexity filter dropdown
- 12 query cards with:
  - Sequence number and complexity badge
  - Natural language question
  - Business value explanation
  - Expandable SQL (click "Show SQL")
  - Copy query button
  - Copy SQL button

**Example queries:**
- "What is our total GMV this month?" (SIMPLE)
- "Compare Shopify Payments vs third-party LTV" (EXPERT - shows $247M opportunity)

#### Tab 3: Schema
- Statistics (15 tables, total fields, 403K rows)
- Search box for tables
- Expandable table cards showing:
  - Table name (font-mono)
  - Description
  - Row count and field count
  - Copy table name button
- Expanded view shows field table:
  - Field name, type (color-coded badges), mode (REQUIRED), description
- Key relationships diagram (6 relationships shown)

**15 Tables:**
merchants, stores, orders, payments, customers, apps, store_app_installs, channels, product_categories, products, order_line_items, merchant_subscription_history, merchant_events, payment_methods

#### Tab 4: Metadata
- Dataset information (ID, project, full name with copy buttons)
- Statistics dashboard (tables, rows, storage, avg rows/table)
- Provisioning details (source URL, generation time, job ID)
- Quick links to BigQuery console (3 buttons)
- Cost information (storage + generation costs)

---

## Interactive Features

### Copy to Clipboard
All copy buttons trigger toast notifications:
- "Query copied to clipboard" → Paste into chat interface
- "SQL copied to clipboard"
- "Dataset ID copied to clipboard" → shopify_capi_demo_20251004
- "Table name copied" → merchants

### External Links
- **Launch Chat:** Opens chat with dataset params
- **View in BigQuery:** Opens BigQuery console at dataset
- **View Schema in BigQuery:** Opens schema view
- **Open Query Editor:** Opens BigQuery SQL editor
- **Source URL:** Opens original website (shopify.com)

### Search & Filter
- **Golden Queries Search:** Type "GMV" or "payment" to filter
- **Complexity Filter:** Select SIMPLE, MEDIUM, COMPLEX, or EXPERT
- **Schema Search:** Type "merchant" or "order" to filter tables

### Expand/Collapse
- **Query SQL:** Click "Show SQL" / "Hide SQL"
- **Table Schema:** Click table row to expand field details

---

## Customizing Mock Data

Edit `/src/hooks/useDemoAssets.ts`:

```typescript
const MOCK_SHOPIFY_ASSETS: DemoAssets = {
  jobId: 'your_job_id',
  customerUrl: 'https://your-customer.com',
  demoTitle: 'Your Demo Title',
  goldenQueries: [
    {
      id: 'q1',
      sequence: 1,
      complexity: 'SIMPLE',
      question: 'Your question?',
      sql: 'SELECT ...',
      businessValue: 'Why this matters'
    }
  ],
  // ... etc
}
```

---

## Connecting to Backend API

Replace mock data with real API call:

```typescript
// In useDemoAssets.ts
export const useDemoAssets = (jobId?: string) => {
  return useQuery<DemoAssets>({
    queryKey: ['demo-assets', jobId],
    queryFn: async () => {
      const response = await fetch(`/api/provision/assets/${jobId}`);
      if (!response.ok) throw new Error('Failed to fetch assets');
      return response.json();
    },
    enabled: !!jobId,
    staleTime: 5 * 60 * 1000,
  });
};
```

---

## Testing Scenarios

### 1. Success State (Default)
- Navigate to `/demo-assets`
- See success banner, tabs, all data loaded
- All buttons functional with toast notifications

### 2. Loading State
- Mock a slow API by adding `await new Promise(r => setTimeout(r, 3000))`
- See spinner with "Loading demo assets..."

### 3. Error State
- Set `jobId` to invalid value
- See error card with "Failed to load demo assets"

### 4. Empty Search Results
- Go to Golden Queries tab
- Search for "zzzzz"
- See "No queries match your search criteria"

---

## Integration with Other Pages

### From ProvisionProgress
When provision completes, redirect:
```typescript
navigate(`/demo-assets?jobId=${completedJobId}`);
```

Or show button:
```typescript
<Button onClick={() => navigate(`/demo-assets?jobId=${jobId}`)}>
  View Demo Assets
</Button>
```

### From CEDashboard
In job history table, add link:
```typescript
<Link to={`/demo-assets?jobId=${job.id}`}>
  View Assets
</Link>
```

---

## Design Notes

### Color Scheme
- **Success:** Green (#10b981)
- **Primary:** Indigo/Purple (#6366f1 → #9333ea)
- **Complexity:**
  - SIMPLE: Green (#10b981)
  - MEDIUM: Blue (#3b82f6)
  - COMPLEX: Orange (#f97316)
  - EXPERT: Purple (#a855f7)

### Typography
- **Titles:** 3xl-4xl, bold, gradient backgrounds
- **Code/IDs:** font-mono, gray background
- **Descriptions:** text-gray-700, leading-relaxed

### Spacing
- **Page padding:** p-6 (24px)
- **Card spacing:** space-y-6 (24px vertical)
- **Section spacing:** space-y-4 (16px vertical)

---

## Keyboard Shortcuts (Future)

Potential enhancements:
- `Cmd+K` → Search queries
- `Cmd+C` → Copy current tab content
- `Tab` → Navigate between tabs
- `Escape` → Close expanded SQL/schema

---

## Accessibility

- ✅ Semantic HTML (headings, lists, tables)
- ✅ ARIA labels on interactive elements
- ✅ Keyboard navigation support
- ✅ Color contrast compliance
- ✅ Screen reader friendly (descriptive labels)

---

## Troubleshooting

### Issue: "Failed to load demo assets"
**Solution:** Check jobId parameter, verify API endpoint, check network tab

### Issue: Tabs not switching
**Solution:** Ensure shadcn Tabs component properly installed, check console for errors

### Issue: Copy to clipboard not working
**Solution:** Requires HTTPS or localhost, check browser permissions

### Issue: BigQuery links broken
**Solution:** Verify projectId and datasetId format, check BigQuery console URL structure

---

## Quick Commands

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type check
npx tsc --noEmit
```

---

## File Locations

```
src/
├── hooks/
│   └── useDemoAssets.ts          # Data hook with mock data
├── pages/
│   └── DemoAssets.tsx             # Main page
├── components/
│   ├── DemoTitleDisplay.tsx       # Tab 1
│   ├── GoldenQueriesDisplay.tsx   # Tab 2
│   ├── SchemaVisualization.tsx    # Tab 3
│   └── MetadataDisplay.tsx        # Tab 4
└── App.tsx                         # Routes
```

---

## Need Help?

1. Check `PHASE_2C_SUMMARY.md` for detailed documentation
2. Review mock data structure in `useDemoAssets.ts`
3. Inspect component props and TypeScript interfaces
4. Check browser console for errors
5. Verify all shadcn/ui components installed

---

**Happy Demoing!** 🚀
