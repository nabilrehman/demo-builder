# Analytics Chatbot - React Frontend

A beautiful, responsive React-based chatbot interface designed to work with Google's Conversational Analytics API for BigQuery data analysis.

## 🎯 Overview

This project provides a complete frontend solution for conversational analytics, featuring automatic branding extraction, dynamic chart generation, and a clean chat interface. It's designed to integrate seamlessly with a Python backend that uses Google's Conversational Analytics API.

## ✨ Features

- 🎨 **Automatic Branding**: Extract logos, colors, and branding from any website URL
- 💬 **Chat Interface**: Clean, modern chat UI for conversational analytics
- 📊 **Dynamic Charts**: Bar, line, and pie charts automatically generated from query results
- 🎯 **Developer Mode**: View raw API responses and SQL queries
- 📱 **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- 🌗 **Dark Mode Support**: Automatic dark/light theme support
- 🔄 **No Backend Required**: Works with mock data out of the box (integrate with Python backend for real data)

## 🗂️ Project Structure

```
web-app/
├── src/
│   ├── components/
│   │   ├── BrandingSetup.tsx      # Initial branding configuration
│   │   ├── ChatHeader.tsx         # Top navigation with logo/branding
│   │   ├── ChatInput.tsx          # Message input component
│   │   ├── ChatMessage.tsx        # Individual message display
│   │   ├── ChartMessage.tsx       # Chart visualization component
│   │   ├── LoadingState.tsx       # Loading indicators
│   │   └── DeveloperMode.tsx      # Debug panel
│   ├── pages/
│   │   └── Index.tsx              # Main chat interface
│   └── main.tsx                   # App entry point
├── public/
├── index.html
└── package.json
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- (Optional) Python 3.11+ for backend integration

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

The app will be available at `http://localhost:5173`

### Try It Out

1. Visit `http://localhost:5173`
2. Enter a website URL (e.g., "klick.com", "shopify.com")
3. Start chatting! Try asking:
   - "What's the sentiment distribution?"
   - "Show me traffic trends"
   - "What are the top conversation topics?"

## 🔗 Backend Integration

This frontend is designed to work with a Python backend that uses Google's Conversational Analytics API.

### Two Options:

**Option 1: Use Mock Data (Current Setup)**
- Works out of the box
- Great for demos and development
- No backend required

**Option 2: Integrate with Python Backend**
- Connect to your BigQuery data
- Real conversational analytics
- See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for detailed setup

### Expected API Format

If you connect a backend, it should return data in this format:

```json
{
  "success": true,
  "response": "Your query returned 150 results showing...",
  "chartData": {
    "type": "bar",
    "title": "Sales by Region",
    "data": [
      {"region": "North", "sales": 1250},
      {"region": "South", "sales": 980}
    ],
    "xKey": "region",
    "yKey": "sales"
  },
  "sqlQuery": "SELECT region, SUM(sales) as sales FROM ..."
}
```

## 📊 Chart Types

The app supports three chart types:

### Bar Chart
Best for: Comparing categories
```typescript
{
  type: "bar",
  data: [
    { category: "A", value: 100 },
    { category: "B", value: 150 }
  ],
  xKey: "category",
  yKey: "value"
}
```

### Line Chart
Best for: Time series and trends
```typescript
{
  type: "line",
  data: [
    { date: "2024-01", value: 100 },
    { date: "2024-02", value: 150 }
  ],
  xKey: "date",
  yKey: "value"
}
```

### Pie Chart
Best for: Proportions and distributions
```typescript
{
  type: "pie",
  data: [
    { name: "Category A", value: 60 },
    { name: "Category B", value: 40 }
  ],
  nameKey: "name",
  yKey: "value"
}
```

## 🎨 Customization

### Branding

The app uses a design token system. Customize colors in `src/index.css`:

```css
:root {
  --primary: 250 80% 60%;
  --primary-foreground: 0 0% 100%;
  /* ... more tokens */
}
```

### Components

All UI components use shadcn/ui and can be customized in `src/components/ui/`.

## 🛠️ Development

### Available Scripts

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component library
- **Recharts** - Chart visualization
- **Lucide React** - Icons

## 📦 Deployment

### Option 1: Deploy via Lovable (Easiest)

This project is built on Lovable, so deploying is as simple as:

1. Visit your [Lovable Project](https://lovable.dev/projects/35fa31cf-31f5-4e0f-9269-e1066b0a9674)
2. Click "Share" → "Publish"
3. Your app is live!

### Option 2: Manual Deployment

Build and deploy to any static hosting:

```bash
# Build
npm run build

# Deploy dist/ folder to:
# - Vercel: vercel --prod
# - Netlify: netlify deploy --prod --dir=dist
# - Firebase: firebase deploy
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file for configuration:

```env
# Backend API URL (optional)
VITE_API_URL=http://localhost:8000

# Or for production
# VITE_API_URL=https://your-api.run.app
```

## 📖 Documentation

- **[INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)** - How to connect frontend to Python backend
- **[LLM_INTEGRATION_GUIDE.md](./LLM_INTEGRATION_GUIDE.md)** - Guide for AI-assisted code changes
- **[Python Backend Repo](https://github.com/nabilrehman/capi)** - Backend code and examples

## 🐛 Troubleshooting

### Charts Not Displaying

Charts require properly formatted data:
1. Check Developer Mode to see the raw `chartData` response
2. Ensure `type`, `data`, `xKey`, and `yKey` are present
3. Verify data is an array of objects

### Branding Not Saving

Branding is stored in localStorage:
1. Check browser console for errors
2. Ensure localStorage is not disabled
3. Try clearing cache and localStorage

### CORS Errors

If connecting to a backend:
1. Ensure your backend has CORS headers configured
2. Check that `VITE_API_URL` points to the correct backend
3. For development, backend should allow `http://localhost:5173`

## 🤝 Contributing

This project is designed to work with various BigQuery datasets. To add support for a new domain:

1. See [LLM_INTEGRATION_GUIDE.md](./LLM_INTEGRATION_GUIDE.md) for AI-assisted modifications
2. Focus on backend changes (agent creation, system instructions)
3. Frontend should work without changes for most use cases

## 📄 License

MIT

## 🔗 Links

- **Lovable Project**: https://lovable.dev/projects/35fa31cf-31f5-4e0f-9269-e1066b0a9674
- **Integration Guide**: [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)
- **LLM Guide**: [LLM_INTEGRATION_GUIDE.md](./LLM_INTEGRATION_GUIDE.md)
- **Backend Repo**: https://github.com/nabilrehman/capi

## 💡 Usage Examples

### Basic Setup
```bash
npm install && npm run dev
```

### With Backend Integration
See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for complete setup instructions.

### Custom Branding
Visit `?website=yourcompany.com` to auto-extract branding.

---

Built with ❤️ using [Lovable](https://lovable.dev)
