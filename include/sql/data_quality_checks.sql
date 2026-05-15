-- 1. No nulls on critical columns
SELECT CASE WHEN COUNT(*) > 0
    THEN 1/0
    ELSE 1 END
FROM core_youtube_videos
WHERE video_id IS NULL OR title IS NULL OR published_at IS NULL;

-- 2. No negative counts
SELECT CASE WHEN COUNT(*) > 0
    THEN 1/0
    ELSE 1 END
FROM core_youtube_videos
WHERE view_count < 0 OR like_count < 0 OR comment_count < 0;

-- 3. video_type only contains expected values
-- Note: Make sure 'live' or 'stream' aren't creeping in here depending on your channel!
SELECT CASE WHEN COUNT(*) > 0
    THEN 1/0
    ELSE 1 END
FROM core_youtube_videos
WHERE video_type NOT IN ('shorts', 'normal');

-- 4. [UPDATED] Referential Integrity: No orphaned topics in the bridge table
-- Ensures every topic record maps back to a valid video in the core table.
SELECT CASE WHEN COUNT(*) > 0
    THEN 1/0
    ELSE 1 END
FROM core_video_topics t
LEFT JOIN core_youtube_videos v ON t.video_id = v.video_id
WHERE v.video_id IS NULL;

-- 5. Staging and core row counts match
SELECT CASE WHEN
    (SELECT COUNT(*) FROM staging_youtube_videos) !=
    (SELECT COUNT(*) FROM core_youtube_videos)
    THEN 1/0
    ELSE 1 END;