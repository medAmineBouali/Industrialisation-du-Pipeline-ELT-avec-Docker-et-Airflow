CREATE TABLE IF NOT EXISTS staging_youtube_videos (
    video_id          VARCHAR(20) PRIMARY KEY,
    title             TEXT,
    published_at      VARCHAR(30),
    duration          VARCHAR(20),
    view_count        BIGINT,
    like_count        BIGINT,
    comment_count     BIGINT,
    thumbnail_url     TEXT,
    topic_categories  TEXT[],
    loaded_at         TIMESTAMP DEFAULT NOW()
);