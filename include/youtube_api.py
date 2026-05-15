from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook
import requests as req
import os

def get_api_key():
    return Variable.get("api_key")

def get_playlist_id(handle):
    params = {"part": "contentDetails", "forHandle": handle}
    res = req.get(
        "https://www.googleapis.com/youtube/v3/channels",
        params=params | {"key": get_api_key()}
    ).json()
    return res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

def get_all_video_ids(playlist_id):
    video_ids = []
    next_page_token = None
    while True:
        params = {
            "part": "contentDetails",
            "playlistId": playlist_id,
            "maxResults": 50,
            "pageToken": next_page_token
        }
        response = req.get(
            "https://www.googleapis.com/youtube/v3/playlistItems",
            params=params | {"key": get_api_key()}
        )
        data = response.json()
        print("Status:", response.status_code)
        print("Error:", data.get("error"))
        for item in data.get('items', []):
            video_ids.append(item['contentDetails']['videoId'])
        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break
    print(f"Total video ids fetched: {len(video_ids)}")
    return video_ids

def get_videos_data_batch(video_ids_list):
    ids_string = ",".join(video_ids_list)
    params = {
        "part": "snippet,contentDetails,statistics,topicDetails",
        "id": ids_string
    }
    res = req.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params=params | {"key": get_api_key()}
    ).json()
    batch_data = []
    for item in res.get("items", []):
        snippet = item.get("snippet", {})
        contentDetails = item.get("contentDetails", {})
        statistics = item.get("statistics", {})
        topicDetails = item.get("topicDetails", {})
        batch_data.append({
            "videoId": item.get("id"),
            "title": snippet.get("title"),
            "publishedAt": snippet.get("publishedAt"),
            "duration": contentDetails.get("duration"),
            "viewCount": statistics.get("viewCount"),
            "likeCount": statistics.get("likeCount"),
            "commentCount": statistics.get("commentCount"),
            "thumbnailUrl": snippet.get("thumbnails", {}).get("medium", {}).get("url"),
            "topicCategories": topicDetails.get("topicCategories", [])
        })
    return batch_data

def get_all_videos_dataset(all_video_ids):
    final_dataset = []
    for i in range(0, len(all_video_ids), 50):
        print(f"Batch {int(i/50 + 1)}")
        batch_ids = all_video_ids[i:i+50]
        batch_data = get_videos_data_batch(batch_ids)
        final_dataset.extend(batch_data)
    return final_dataset

def load_to_staging(videos_data: list):
    hook = PostgresHook(postgres_conn_id="postgres_db_yt_elt")
    conn = hook.get_conn()
    cursor = conn.cursor()
    insert_query = """
        INSERT INTO staging_youtube_videos (
            video_id, title, published_at, duration,
            view_count, like_count, comment_count,
            thumbnail_url, topic_categories
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (video_id) DO UPDATE SET
            title            = EXCLUDED.title,
            published_at     = EXCLUDED.published_at,
            duration         = EXCLUDED.duration,
            view_count       = EXCLUDED.view_count,
            like_count       = EXCLUDED.like_count,
            comment_count    = EXCLUDED.comment_count,
            thumbnail_url    = EXCLUDED.thumbnail_url,
            topic_categories = EXCLUDED.topic_categories,
            loaded_at        = NOW();
    """
    for video in videos_data:
        cursor.execute(insert_query, (
            video["videoId"],
            video["title"],
            video["publishedAt"],
            video["duration"],
            int(video["viewCount"]) if video["viewCount"] else None,
            int(video["likeCount"]) if video["likeCount"] else None,
            int(video["commentCount"]) if video["commentCount"] else None,
            video["thumbnailUrl"],
            video["topicCategories"],
        ))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Loaded {len(videos_data)} videos into staging.")


def transform_to_core():
    hook = PostgresHook(postgres_conn_id="postgres_db_yt_elt")
    sql_path = os.path.join(os.path.dirname(__file__), "sql", "transform_to_core.sql")
    with open(sql_path, "r") as f:
        sql = f.read()
    hook.run(sql)
    print("Transformation to core complete.")

def run_data_quality_checks():
    hook = PostgresHook(postgres_conn_id="postgres_db_yt_elt")
    sql_path = os.path.join(os.path.dirname(__file__), "sql", "data_quality_checks.sql")
    with open(sql_path, "r") as f:
        sql = f.read()
    hook.run(sql)
    print("All data quality checks passed.")

def extract_task():
    channel_handle = Variable.get("channel_handle")
    playlist_id = get_playlist_id(channel_handle)
    all_video_ids = get_all_video_ids(playlist_id)
    return get_all_videos_dataset(all_video_ids)