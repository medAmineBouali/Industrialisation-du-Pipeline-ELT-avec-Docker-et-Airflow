CREATE TABLE IF NOT EXISTS core_youtube_videos (
    video_id         VARCHAR(20) PRIMARY KEY,
    title            TEXT,
    published_at     TIMESTAMP,
    publish_date     DATE,
    publish_hour     SMALLINT,
    duration_seconds INTEGER,
    duration_display VARCHAR(20),
    view_count       BIGINT,
    like_count       BIGINT,
    comment_count    BIGINT,
    thumbnail_url     TEXT,
    video_type       VARCHAR(10),
    updated_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS core_video_topics (
    video_id   VARCHAR(20),
    topic      TEXT,
    PRIMARY KEY (video_id, topic)
);