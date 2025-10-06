# Demo Assets Viewer - Component Structure

## Page Hierarchy

```
DemoAssets.tsx (Main Page)
│
├── Success Banner (Alert Component)
│   └── "🎉 Provision Complete!" with URL and time
│
├── Launch Chat Button (Card with CTA)
│   └── Large button → Opens chat interface
│
├── Action Buttons Grid (4 buttons)
│   ├── Download YAML
│   ├── Copy Dataset ID
│   ├── View in BigQuery
│   └── Re-run Provision
│
└── Tabs Container (Card with Tabs)
    │
    ├── Tab 1: Demo Title
    │   └── <DemoTitleDisplay />
    │       ├── Title Section (gradient background)
    │       ├── Executive Summary Card
    │       ├── Business Challenges Card
    │       ├── Talking Track Card
    │       └── Demo Tips Card
    │
    ├── Tab 2: Golden Queries
    │   └── <GoldenQueriesDisplay />
    │       ├── Statistics Dashboard (4 cards)
    │       ├── Search & Filter Controls
    │       └── Query Cards (12 items)
    │           ├── Collapsible Header
    │           │   ├── Sequence Badge
    │           │   ├── Complexity Badge
    │           │   ├── Question Text
    │           │   ├── Business Value
    │           │   └── Action Buttons
    │           └── Collapsible Content
    │               ├── SQL Code Block
    │               └── Complexity Description
    │
    ├── Tab 3: Schema
    │   └── <SchemaVisualization />
    │       ├── Statistics Cards (3 cards)
    │       ├── Search Control
    │       ├── Table Cards (15 items)
    │       │   ├── Collapsible Header
    │       │   │   ├── Table Icon
    │       │   │   ├── Table Name
    │       │   │   ├── Description
    │       │   │   ├── Stats (rows, fields)
    │       │   │   └── Copy Button
    │       │   └── Collapsible Content
    │       │       └── Fields Table
    │       │           ├── Field Name
    │       │           ├── Type Badge
    │       │           ├── Mode Badge
    │       │           └── Description
    │       ├── Relationships Card
    │       └── Tips Card
    │
    └── Tab 4: Metadata
        └── <MetadataDisplay />
            ├── Dataset Information Card
            │   ├── Dataset ID (with copy)
            │   ├── Project ID (with copy)
            │   └── Full Name (with copy + link)
            ├── Statistics Dashboard (4 cards)
            ├── Provisioning Details Card
            │   ├── Source URL (with link)
            │   ├── Generation Time
            │   └── Job ID (with copy)
            ├── Quick Links Card (3 buttons)
            └── Cost Information Card
```

---

## Component Responsibilities

### **DemoAssets.tsx** (Main Container)
- **Purpose:** Page layout, routing, and state management
- **Responsibilities:**
  - Fetch data via `useDemoAssets()` hook
  - Handle URL params (`jobId`)
  - Manage loading and error states
  - Coordinate tab navigation
  - Dispatch actions (launch chat, download, copy, re-run)
  - Show toast notifications

- **Props:** None (reads from URL params)
- **State:**
  - Query state from React Query
  - Search params from URL

---

### **DemoTitleDisplay.tsx** (Tab 1)
- **Purpose:** Display demo narrative and presentation guidance
- **Props:**
  ```typescript
  {
    title: string;              // Demo title
    executiveSummary: string;   // High-level value prop
    businessChallenges: string[]; // Array of pain points
    talkingTrack: string;       // Demo flow recommendations
  }
  ```
- **Responsibilities:**
  - Display formatted demo title with badge
  - Show executive summary in card
  - List business challenges (numbered)
  - Present talking track in callout
  - Provide demo tips

---

### **GoldenQueriesDisplay.tsx** (Tab 2)
- **Purpose:** Interactive golden queries browser
- **Props:**
  ```typescript
  {
    queries: GoldenQuery[];  // Array of 12-18 queries
  }
  ```
- **State:**
  - `searchTerm: string` - Search filter
  - `complexityFilter: string` - Complexity dropdown
  - `expandedQueries: Set<string>` - Expanded SQL views

- **Responsibilities:**
  - Calculate complexity statistics
  - Filter queries by search and complexity
  - Toggle SQL visibility per query
  - Copy query/SQL to clipboard
  - Display business value

---

### **SchemaVisualization.tsx** (Tab 3)
- **Purpose:** Interactive database schema browser
- **Props:**
  ```typescript
  {
    schema: TableSchema[];  // Array of 10-20 tables
  }
  ```
- **State:**
  - `expandedTables: Set<string>` - Expanded table views
  - `searchTerm: string` - Table search filter

- **Responsibilities:**
  - Calculate schema statistics
  - Filter tables by search
  - Toggle field visibility per table
  - Display field details (type, mode, description)
  - Show relationships diagram
  - Copy table names

---

### **MetadataDisplay.tsx** (Tab 4)
- **Purpose:** Dataset metadata and external links
- **Props:**
  ```typescript
  {
    metadata: {
      datasetId: string;
      datasetFullName: string;
      projectId: string;
      totalRows: number;
      totalStorageMB: number;
      generationTimestamp: string;
      totalTables: number;
    };
    customerUrl: string;
    jobId: string;
  }
  ```
- **Responsibilities:**
  - Display dataset identifiers
  - Show statistics dashboard
  - Format timestamps and storage sizes
  - Generate BigQuery console URLs
  - Calculate cost estimates
  - Handle copy/external link actions

---

## Data Flow

```
URL Params (jobId)
    ↓
useDemoAssets() Hook
    ↓
React Query (fetch/cache)
    ↓
DemoAssets Page (main state)
    ↓
    ├→ DemoTitleDisplay (title, summary, challenges, track)
    ├→ GoldenQueriesDisplay (queries array)
    ├→ SchemaVisualization (schema array)
    └→ MetadataDisplay (metadata object, customerUrl, jobId)
```

---

## Shared Components Used

### From shadcn/ui:
- `Card, CardHeader, CardTitle, CardDescription, CardContent`
- `Tabs, TabsList, TabsTrigger, TabsContent`
- `Button`
- `Badge`
- `Alert, AlertDescription`
- `Collapsible, CollapsibleTrigger, CollapsibleContent`
- `Input`
- `Select, SelectTrigger, SelectValue, SelectContent, SelectItem`
- `Table, TableHeader, TableBody, TableRow, TableHead, TableCell`
- `Separator`

### From Lucide Icons:
- `Rocket, CheckCircle2, Clock` (success banner)
- `Download, Copy, ExternalLink, RefreshCw` (action buttons)
- `Lightbulb, Target, MessageSquare` (demo title icons)
- `Search, ChevronDown, ChevronUp, Sparkles, TrendingUp` (queries)
- `Database, ChevronRight` (schema)
- `Calendar, Globe, HardDrive, Layers` (metadata)

### From Sonner:
- `toast.success()` - Success notifications
- `toast.info()` - Info notifications
- `toast.error()` - Error notifications (if needed)

---

## State Management

### React Query (via useDemoAssets hook)
```typescript
const { data: assets, isLoading, error } = useDemoAssets(jobId);
```

**Benefits:**
- Automatic caching (5 min stale time)
- Loading states
- Error handling
- Refetch on window focus
- Background updates

### Local Component State

**DemoAssets.tsx:**
- URL search params (jobId)
- No additional state (all derived from query)

**GoldenQueriesDisplay.tsx:**
- Search term
- Complexity filter
- Expanded queries set

**SchemaVisualization.tsx:**
- Search term
- Expanded tables set

**Others:**
- No local state (pure display)

---

## User Interactions

### Click Actions
1. **Launch Chat** → `window.open(provisionUrl)`
2. **Download YAML** → Toast + trigger download (future: actual download)
3. **Copy Dataset ID** → Clipboard + toast
4. **View in BigQuery** → `window.open(bqConsoleUrl)`
5. **Re-run Provision** → Toast + API call (future)
6. **Copy Query** → Clipboard + toast
7. **Show/Hide SQL** → Toggle expanded state
8. **Copy SQL** → Clipboard + toast
9. **Copy Table Name** → Clipboard + toast
10. **External Links** → `window.open(url, '_blank')`

### Search/Filter
- **Query Search** → Filter by question/business value
- **Complexity Filter** → Filter by SIMPLE/MEDIUM/COMPLEX/EXPERT
- **Table Search** → Filter by table name/description

### Expand/Collapse
- **Query SQL** → Toggle CollapsibleContent
- **Table Fields** → Toggle CollapsibleContent

---

## Responsive Behavior

### Breakpoints (Tailwind)
- **Mobile (< 768px):**
  - Stack action buttons 2x2
  - Single column layouts
  - Smaller text sizes

- **Tablet (768px - 1024px):**
  - 2 column grids
  - Medium button sizes

- **Desktop (> 1024px):**
  - 4 column grids (action buttons, stats)
  - Full layouts
  - Large prominent CTAs

### Components Responsive
- Grid layouts: `grid-cols-1 md:grid-cols-2 lg:grid-cols-4`
- Text sizes: `text-2xl md:text-3xl lg:text-4xl`
- Padding: `p-4 md:p-6`
- Button sizes: `size="sm" md:size="lg"`

---

## Error States

### Loading State
```tsx
<div className="min-h-screen flex items-center justify-center">
  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
  <p>Loading demo assets...</p>
</div>
```

### Error State
```tsx
<Alert variant="destructive">
  <AlertDescription>
    Failed to load demo assets. Please check the job ID and try again.
  </AlertDescription>
</Alert>
```

### Empty State (Search Results)
```tsx
<Card>
  <CardContent className="pt-6 text-center text-gray-500">
    No queries match your search criteria
  </CardContent>
</Card>
```

---

## Performance Considerations

### Optimizations Applied
1. **React Query Caching:** 5 min stale time, reduces API calls
2. **Lazy SQL Rendering:** SQL only rendered when expanded
3. **Virtualization Ready:** Large query/table lists (could add react-window)
4. **Memoization:** Filter/search functions could use useMemo
5. **Code Splitting:** Page level (via React Router)

### Bundle Size
- Current: 932.84 KB (270.99 KB gzipped)
- Consider: Dynamic imports for heavy visualizations

---

## Testing Strategy

### Unit Tests (Future)
- `useDemoAssets.test.ts` - Hook logic, mock data
- `DemoTitleDisplay.test.tsx` - Rendering, props
- `GoldenQueriesDisplay.test.tsx` - Search, filter, expand
- `SchemaVisualization.test.tsx` - Table expand, search
- `MetadataDisplay.test.tsx` - Link generation, copy

### Integration Tests
- Full page render with mock data
- Tab navigation
- Search and filter functionality
- Copy to clipboard
- External link generation

### E2E Tests
- Navigate from ProvisionProgress → DemoAssets
- Launch chat interface
- Download YAML
- View in BigQuery

---

## Accessibility Checklist

- ✅ Semantic HTML (headings, lists, tables)
- ✅ Keyboard navigation (Tab, Enter, Escape)
- ✅ ARIA labels on interactive elements
- ✅ Color contrast (WCAG AA compliant)
- ✅ Screen reader friendly (descriptive text)
- ✅ Focus indicators (default + custom)
- ⏳ Keyboard shortcuts (future enhancement)

---

## Future Enhancements

### Planned Features
1. **Visual Schema Diagram:** ER diagram with react-flow
2. **Query Testing:** Run SQL in BigQuery, show results
3. **Query History:** Track which queries were tested
4. **Demo Sharing:** Generate shareable link
5. **Export Options:** PDF report, PowerPoint deck
6. **Query Favorites:** Star important queries
7. **Custom Query Builder:** Visual query creator
8. **Real-time Collaboration:** Multiple CEs viewing same demo

### Performance Improvements
1. Virtual scrolling for large query/table lists
2. Lazy load tab content (only render active tab)
3. Optimize bundle size (code splitting)
4. Service worker for offline access

---

## Component Reusability

### Can be reused in:
- **DemoTitleDisplay:** Any demo narrative display
- **GoldenQueriesDisplay:** Query documentation, SQL libraries
- **SchemaVisualization:** Database documentation, data catalogs
- **MetadataDisplay:** Dataset info pages, admin dashboards

### Extraction Potential
- **CopyButton:** Shared component with toast
- **ExpandableCard:** Collapsible card wrapper
- **StatCard:** Metric display card
- **SearchFilter:** Search + filter controls

---

This structure provides a clear, maintainable, and scalable foundation for the Demo Assets Viewer! 🎯
