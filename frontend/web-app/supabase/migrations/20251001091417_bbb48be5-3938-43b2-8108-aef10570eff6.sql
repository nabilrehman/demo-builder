-- Create sessions table for managing unique user sessions
CREATE TABLE public.sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  website TEXT NOT NULL,
  agent_id TEXT,
  conversation_id TEXT,
  dataset_id TEXT,
  branding JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  expires_at TIMESTAMP WITH TIME ZONE DEFAULT (now() + interval '24 hours'),
  last_active_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create messages table for storing chat history
CREATE TABLE public.messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES public.sessions(id) ON DELETE CASCADE NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  chart_data JSONB,
  sql_query TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

-- RLS Policies for sessions (public read/write for demo purposes)
CREATE POLICY "Anyone can create sessions"
  ON public.sessions
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Anyone can view their session"
  ON public.sessions
  FOR SELECT
  USING (true);

CREATE POLICY "Anyone can update their session"
  ON public.sessions
  FOR UPDATE
  USING (true);

-- RLS Policies for messages (linked to sessions)
CREATE POLICY "Anyone can create messages"
  ON public.messages
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Anyone can view messages"
  ON public.messages
  FOR SELECT
  USING (true);

-- Create index for faster session lookups
CREATE INDEX idx_sessions_website ON public.sessions(website);
CREATE INDEX idx_sessions_expires_at ON public.sessions(expires_at);
CREATE INDEX idx_messages_session_id ON public.messages(session_id);
CREATE INDEX idx_messages_created_at ON public.messages(created_at);

-- Function to clean up expired sessions
CREATE OR REPLACE FUNCTION public.cleanup_expired_sessions()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  DELETE FROM public.sessions
  WHERE expires_at < now();
END;
$$;