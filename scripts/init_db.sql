-- AI Video GPU Database Initialization Script
-- PostgreSQL schema and initial data setup

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create enum types
CREATE TYPE job_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled');
CREATE TYPE video_quality AS ENUM ('low', 'medium', 'high', 'ultra', '4k');
CREATE TYPE user_role AS ENUM ('user', 'admin', 'api_key');

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'user',
    api_key VARCHAR(255) UNIQUE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    
    -- Usage tracking
    total_videos_generated INTEGER DEFAULT 0,
    total_processing_time INTERVAL DEFAULT INTERVAL '0',
    monthly_quota INTEGER DEFAULT 100,
    quota_used_this_month INTEGER DEFAULT 0,
    quota_reset_date DATE DEFAULT CURRENT_DATE + INTERVAL '1 month'
);

-- Video generation jobs table
CREATE TABLE IF NOT EXISTS video_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Job configuration
    job_name VARCHAR(255),
    template_name VARCHAR(100),
    status job_status DEFAULT 'pending',
    priority INTEGER DEFAULT 5, -- 1-10, higher is more priority
    
    -- Input parameters
    script_text TEXT,
    avatar_path VARCHAR(500),
    voice_settings JSONB,
    background_settings JSONB,
    video_settings JSONB,
    
    -- Processing details
    quality video_quality DEFAULT 'medium',
    duration_seconds INTEGER,
    estimated_processing_time INTERVAL,
    actual_processing_time INTERVAL,
    
    -- Output information
    output_path VARCHAR(500),
    output_size_bytes BIGINT,
    output_format VARCHAR(20) DEFAULT 'mp4',
    
    -- Metadata
    metadata JSONB,
    error_message TEXT,
    progress_percentage INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System metrics table
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- GPU metrics
    gpu_utilization_percent DECIMAL(5,2),
    gpu_memory_used_mb INTEGER,
    gpu_memory_total_mb INTEGER,
    gpu_temperature_celsius DECIMAL(5,2),
    
    -- System metrics
    cpu_utilization_percent DECIMAL(5,2),
    memory_used_mb INTEGER,
    memory_total_mb INTEGER,
    disk_used_gb INTEGER,
    disk_total_gb INTEGER,
    
    -- Application metrics
    active_jobs INTEGER,
    queue_length INTEGER,
    total_jobs_completed INTEGER,
    error_rate_percent DECIMAL(5,2),
    
    -- Performance metrics
    avg_response_time_ms INTEGER,
    requests_per_second DECIMAL(8,2)
);

-- Model cache table
CREATE TABLE IF NOT EXISTS model_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(255) UNIQUE NOT NULL,
    model_type VARCHAR(100) NOT NULL, -- 'tts', 'diffusion', 'wav2lip', etc.
    model_path VARCHAR(500) NOT NULL,
    model_size_bytes BIGINT,
    
    -- Usage statistics
    download_count INTEGER DEFAULT 0,
    last_used TIMESTAMP WITH TIME ZONE,
    usage_count INTEGER DEFAULT 0,
    
    -- Metadata
    version VARCHAR(50),
    description TEXT,
    supported_languages TEXT[],
    requirements JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- API usage logs
CREATE TABLE IF NOT EXISTS api_usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Request details
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    
    -- Timing and size
    response_time_ms INTEGER,
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    
    -- Client information
    user_agent TEXT,
    ip_address INET,
    api_key_used VARCHAR(255),
    
    -- Metadata
    parameters JSONB,
    error_details TEXT,
    
    -- Timestamp
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Templates table
CREATE TABLE IF NOT EXISTS templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL,
    
    -- Template configuration
    description TEXT,
    config JSONB NOT NULL,
    thumbnail_path VARCHAR(500),
    
    -- Usage and ratings
    usage_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.0,
    rating_count INTEGER DEFAULT 0,
    
    -- Metadata
    tags TEXT[],
    is_public BOOLEAN DEFAULT true,
    is_featured BOOLEAN DEFAULT false,
    created_by UUID REFERENCES users(id),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_video_jobs_user_id ON video_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_video_jobs_status ON video_jobs(status);
CREATE INDEX IF NOT EXISTS idx_video_jobs_created_at ON video_jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_video_jobs_priority_status ON video_jobs(priority DESC, status);

CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_api_usage_logs_timestamp ON api_usage_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_api_usage_logs_user_id ON api_usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_logs_endpoint ON api_usage_logs(endpoint);

CREATE INDEX IF NOT EXISTS idx_model_cache_type ON model_cache(model_type);
CREATE INDEX IF NOT EXISTS idx_model_cache_last_used ON model_cache(last_used);

CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category);
CREATE INDEX IF NOT EXISTS idx_templates_public_featured ON templates(is_public, is_featured);

-- Create indexes for text search
CREATE INDEX IF NOT EXISTS idx_templates_name_trgm ON templates USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_video_jobs_script_trgm ON video_jobs USING gin(script_text gin_trgm_ops);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_video_jobs_updated_at BEFORE UPDATE ON video_jobs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_model_cache_updated_at BEFORE UPDATE ON model_cache 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON templates 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123)
INSERT INTO users (username, email, password_hash, role, api_key) 
VALUES (
    'admin', 
    'admin@ai-video-gpu.local', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewVyVH4EsDAGl.0u', -- bcrypt hash of 'admin123'
    'admin',
    'admin_' || encode(gen_random_bytes(32), 'hex')
) ON CONFLICT (username) DO NOTHING;

-- Insert default templates
INSERT INTO templates (name, category, description, config, tags, is_featured) VALUES 
(
    'corporate-presentation',
    'business',
    'Professional corporate presentation template with clean styling',
    '{"voice": {"style": "professional", "speed": 1.0}, "visual": {"background": "corporate", "style": "clean"}, "quality": "high"}',
    ARRAY['business', 'corporate', 'professional'],
    true
),
(
    'educational-tutorial',
    'education',
    'Educational content template optimized for learning',
    '{"voice": {"style": "educational", "speed": 0.9}, "visual": {"background": "classroom", "style": "friendly"}, "quality": "medium"}',
    ARRAY['education', 'tutorial', 'learning'],
    true
),
(
    'social-media-short',
    'social',
    'Quick social media content template for platforms like TikTok',
    '{"voice": {"style": "energetic", "speed": 1.1}, "visual": {"background": "dynamic", "style": "trendy"}, "quality": "medium", "duration": 30}',
    ARRAY['social', 'short-form', 'trendy'],
    true
),
(
    'healthcare-education',
    'healthcare',
    'Medical and healthcare education template with professional tone',
    '{"voice": {"style": "clinical-professional", "speed": 0.9}, "visual": {"background": "medical", "style": "clean"}, "quality": "high", "compliance": {"hipaa": true}}',
    ARRAY['healthcare', 'medical', 'education'],
    false
)
ON CONFLICT (name) DO NOTHING;

-- Insert some sample models
INSERT INTO model_cache (model_name, model_type, model_path, description, supported_languages) VALUES 
(
    'tortoise-tts-base',
    'tts',
    '/app/models/tts/tortoise/base',
    'Base Tortoise TTS model for high-quality voice synthesis',
    ARRAY['en']
),
(
    'stable-diffusion-v1-5',
    'diffusion',
    '/app/models/diffusion/sd-v1-5',
    'Stable Diffusion v1.5 for background generation',
    ARRAY['universal']
),
(
    'wav2lip-gan',
    'lip_sync',
    '/app/models/wav2lip/gan',
    'Wav2Lip GAN model for lip synchronization',
    ARRAY['universal']
)
ON CONFLICT (model_name) DO NOTHING;

-- Create views for common queries
CREATE OR REPLACE VIEW job_statistics AS
SELECT 
    DATE_TRUNC('day', created_at) as date,
    status,
    COUNT(*) as job_count,
    AVG(EXTRACT(EPOCH FROM actual_processing_time)) as avg_processing_time_seconds,
    SUM(output_size_bytes) as total_output_size_bytes
FROM video_jobs 
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at), status
ORDER BY date DESC;

CREATE OR REPLACE VIEW user_usage_summary AS
SELECT 
    u.id,
    u.username,
    u.email,
    u.total_videos_generated,
    u.quota_used_this_month,
    u.monthly_quota,
    COUNT(vj.id) as jobs_last_30_days,
    AVG(EXTRACT(EPOCH FROM vj.actual_processing_time)) as avg_processing_time
FROM users u
LEFT JOIN video_jobs vj ON u.id = vj.user_id 
    AND vj.created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY u.id, u.username, u.email, u.total_videos_generated, u.quota_used_this_month, u.monthly_quota;

-- Grant appropriate permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ai_video_gpu_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ai_video_gpu_app;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO ai_video_gpu_app;

-- Performance optimization settings
-- These should be adjusted based on your hardware
-- Uncomment and modify as needed:

-- ALTER SYSTEM SET shared_buffers = '256MB';
-- ALTER SYSTEM SET effective_cache_size = '1GB';
-- ALTER SYSTEM SET maintenance_work_mem = '64MB';
-- ALTER SYSTEM SET checkpoint_completion_target = 0.9;
-- ALTER SYSTEM SET wal_buffers = '16MB';
-- ALTER SYSTEM SET default_statistics_target = 100;
-- ALTER SYSTEM SET random_page_cost = 1.1;
-- ALTER SYSTEM SET effective_io_concurrency = 200;

-- Reload configuration (requires superuser privileges)
-- SELECT pg_reload_conf();

COMMIT;
