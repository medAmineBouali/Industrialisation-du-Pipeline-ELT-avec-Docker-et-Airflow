INSERT INTO core_youtube_videos (
    video_id,
    title,
    published_at,
    publish_date,
    publish_hour,
    duration_seconds,
    duration_display,
    view_count,
    like_count,
    comment_count,
    thumbnail_url,
    video_type,
    updated_at
)
SELECT
    video_id,
    title,
    published_at::TIMESTAMP,
    published_at::TIMESTAMP::DATE,
    EXTRACT(HOUR FROM published_at::TIMESTAMP)::SMALLINT,
    EXTRACT(EPOCH FROM duration::INTERVAL)::INTEGER,
    -- Build a clean display string: "0:04:13" style
    TO_CHAR(
        (EXTRACT(EPOCH FROM duration::INTERVAL) || ' seconds')::INTERVAL,
        'HH24:MI:SS'
    ),
    view_count,
    like_count,
    comment_count,
    thumbnail_url,
    CASE
        WHEN EXTRACT(EPOCH FROM duration::INTERVAL) <= 60 THEN 'shorts'
        ELSE 'normal'
    END,
    NOW()
FROM staging_youtube_videos
ON CONFLICT (video_id) DO UPDATE SET
    title            = EXCLUDED.title,
    published_at     = EXCLUDED.published_at,
    publish_date     = EXCLUDED.publish_date,
    publish_hour     = EXCLUDED.publish_hour,
    duration_seconds = EXCLUDED.duration_seconds,
    duration_display = EXCLUDED.duration_display,
    view_count       = EXCLUDED.view_count,
    like_count       = EXCLUDED.like_count,
    comment_count    = EXCLUDED.comment_count,
    video_type       = EXCLUDED.video_type,
    updated_at       = NOW();

-- Bridge table: explode the topic_categories array
INSERT INTO core_video_topics (video_id, topic)
SELECT
    video_id,
    REPLACE(
        UNNEST(topic_categories),
        'https://en.wikipedia.org/wiki/', ''
    ) AS topic
FROM staging_youtube_videos
WHERE topic_categories IS NOT NULL
  AND array_length(topic_categories, 1) > 0
ON CONFLICT (video_id, topic) DO NOTHING;