-- Layer 4: Longitudinal pattern intelligence (PostgreSQL production schema)
-- No raw transcripts: risk timelines, anonymized_session_id, embeddings optional.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS calls (
    call_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    anonymized_session_id TEXT NOT NULL,
    risk_timeline JSONB NOT NULL DEFAULT '[]'::jsonb,
    final_outcome TEXT NOT NULL CHECK (final_outcome IN ('resolved', 'escalated', 'dropped', 'unknown')),
    stt_reliable BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    transcript_embedding BYTEA,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_calls_session ON calls (anonymized_session_id);
CREATE INDEX IF NOT EXISTS idx_calls_expires ON calls (expires_at);
CREATE INDEX IF NOT EXISTS idx_calls_outcome ON calls (final_outcome);

CREATE TABLE IF NOT EXISTS operator_actions (
    id BIGSERIAL PRIMARY KEY,
    call_id UUID NOT NULL REFERENCES calls(call_id) ON DELETE CASCADE,
    action TEXT NOT NULL CHECK (action IN ('accepted', 'modified', 'rejected')),
    phrase_fingerprint TEXT,
    phrase_redacted TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_operator_actions_call ON operator_actions (call_id);

CREATE TABLE IF NOT EXISTS resource_usage (
    id BIGSERIAL PRIMARY KEY,
    call_id UUID NOT NULL REFERENCES calls(call_id) ON DELETE CASCADE,
    resource_label TEXT NOT NULL,
    followed BOOLEAN,
    suggested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_resource_usage_label ON resource_usage (resource_label);

CREATE TABLE IF NOT EXISTS aggregated_patterns (
    pattern_key TEXT PRIMARY KEY,
    pattern_value JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE calls IS 'PII-free call summaries; transcripts never stored as plain text.';
COMMENT ON TABLE aggregated_patterns IS 'Offline batch aggregates: phrase stats, early-risk priors, resource gaps.';
