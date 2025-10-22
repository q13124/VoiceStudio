-- VoiceStudio Database Initialization
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create additional indexes for better performance
-- (Tables will be created by Alembic migrations)

-- Create a view for A/B summary statistics
CREATE OR REPLACE VIEW ab_summary_stats AS
SELECT 
    engine,
    COUNT(*) as total_sessions,
    AVG(win_rate) as avg_win_rate,
    AVG(mean_score) as avg_score,
    AVG(median_lufs) as avg_lufs,
    AVG(clip_hit_rate) as avg_clip_rate,
    MIN(created_utc) as first_session,
    MAX(created_utc) as last_session
FROM ab_summary 
GROUP BY engine;

-- Create a view for evaluation trends
CREATE OR REPLACE VIEW eval_trends AS
SELECT 
    engine,
    date,
    AVG(wr) as avg_win_rate,
    AVG(latency_p50) as avg_latency_p50,
    AVG(latency_p95) as avg_latency_p95,
    AVG(clip_rate) as avg_clip_rate,
    AVG(lufs_med) as avg_lufs_med,
    COUNT(*) as runs_count
FROM eval_runs 
GROUP BY engine, date
ORDER BY date DESC;

-- Grant permissions
GRANT SELECT ON ab_summary_stats TO voicestudio;
GRANT SELECT ON eval_trends TO voicestudio;
