import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import Index from "./pages/Index";
import CEDashboard from "./pages/CEDashboard";
import ProvisionProgress from "./pages/ProvisionProgress";
import DemoAssets from "./pages/DemoAssets";
import ChatInterface from "./pages/ChatInterface";
import NotFound from "./pages/NotFound";
import { AnalyticsDashboard } from "./features/analytics-dashboard";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/ce-dashboard" element={<CEDashboard />} />
            <Route path="/provision-progress" element={<ProvisionProgress />} />
            <Route path="/demo-assets" element={<DemoAssets />} />
            <Route path="/chat" element={<ChatInterface />} />
            <Route path="/analytics-dashboard" element={<AnalyticsDashboard />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;
