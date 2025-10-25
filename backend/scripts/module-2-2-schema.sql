-- Module 2.2: Conversation Persistence Schema
-- Run this in Supabase SQL Editor

-- Table: conversations
-- Stores conversation metadata (one per chat session)
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT,  -- Auto-generated from first message or user-set
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast queries
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);

COMMENT ON TABLE conversations IS 'Chat conversations - one per session with the Life Coordinator agent';
COMMENT ON COLUMN conversations.title IS 'Auto-generated from first user message (truncated to 50 chars) or user-set';
COMMENT ON COLUMN conversations.updated_at IS 'Updated on every new message (for sorting most recent)';


-- Table: messages
-- Stores individual messages within conversations
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Optional metadata
    tool_calls JSONB  -- Function calls made by assistant (if any)
);

-- Indexes for fast queries
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

COMMENT ON TABLE messages IS 'Individual messages within conversations';
COMMENT ON COLUMN messages.role IS 'OpenAI message role: user, assistant, or system';
COMMENT ON COLUMN messages.content IS 'Message text content';
COMMENT ON COLUMN messages.tool_calls IS 'JSON metadata for function calls (optional, for assistant messages)';


-- Verification queries
-- After running above, verify tables exist:

-- Check tables created
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('conversations', 'messages');

-- Check indexes
SELECT indexname FROM pg_indexes 
WHERE tablename IN ('conversations', 'messages');
