"""
Movie Review Bot - YouTube Uploader
Uploads videos to YouTube using YouTube Data API v3.
"""

import os
import pickle
from pathlib import Path
from typing import Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from config import YOUTUBE_CLIENT_SECRET_FILE, YOUTUBE_CATEGORY_ID, YOUTUBE_PRIVACY


# YouTube API scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = "token.pickle"


def get_youtube_service():
    """Get authenticated YouTube API service."""
    creds = None

    # Load existing token
    if Path(TOKEN_FILE).exists():
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    # Refresh or create new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not Path(YOUTUBE_CLIENT_SECRET_FILE).exists():
                print(f"Error: {YOUTUBE_CLIENT_SECRET_FILE} not found")
                print("Download it from Google Cloud Console")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                YOUTUBE_CLIENT_SECRET_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    # Build service
    service = build("youtube", "v3", credentials=creds)
    return service


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    thumbnail_path: str = None,
    privacy: str = None,
    category_id: str = None,
    language: str = "vi",
) -> Optional[str]:
    """Upload a video to YouTube."""
    privacy = privacy or YOUTUBE_PRIVACY
    category_id = category_id or YOUTUBE_CATEGORY_ID

    # Verify video file exists
    if not Path(video_path).exists():
        print(f"Error: Video file not found: {video_path}")
        return None

    try:
        # Get YouTube service
        service = get_youtube_service()
        if service is None:
            return None

        print(f"Uploading video: {title}")

        # Prepare video metadata
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id,
                "defaultLanguage": language,
                "defaultAudioLanguage": language,
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False,
                "embeddable": True,
                "publicStatsViewable": True,
            },
        }

        # Create media upload
        media = MediaFileUpload(
            video_path,
            mimetype="video/mp4",
            resumable=True,
            chunksize=1024 * 1024 * 10,  # 10MB chunks
        )

        # Execute upload
        request = service.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Upload progress: {int(status.progress() * 100)}%")

        video_id = response.get("id")
        print(f"Video uploaded successfully!")
        print(f"Video ID: {video_id}")
        print(f"URL: https://www.youtube.com/watch?v={video_id}")

        # Upload thumbnail if provided
        if thumbnail_path and Path(thumbnail_path).exists():
            upload_thumbnail(service, video_id, thumbnail_path)

        return video_id

    except HttpError as e:
        print(f"YouTube API error: {e}")
        return None
    except Exception as e:
        print(f"Error uploading video: {e}")
        return None


def upload_thumbnail(service, video_id: str, thumbnail_path: str) -> bool:
    """Upload a custom thumbnail for a video."""
    try:
        print(f"Uploading thumbnail for video {video_id}...")

        media = MediaFileUpload(
            thumbnail_path,
            mimetype="image/jpeg",
        )

        service.thumbnails().set(
            videoId=video_id,
            media_body=media,
        ).execute()

        print("Thumbnail uploaded successfully!")
        return True

    except HttpError as e:
        print(f"Error uploading thumbnail: {e}")
        return False
    except Exception as e:
        print(f"Error uploading thumbnail: {e}")
        return False


def create_playlist(title: str, description: str, privacy: str = "public") -> Optional[str]:
    """Create a new playlist."""
    try:
        service = get_youtube_service()
        if service is None:
            return None

        body = {
            "snippet": {
                "title": title,
                "description": description,
            },
            "status": {
                "privacyStatus": privacy,
            },
        }

        response = service.playlists().insert(
            part="snippet,status",
            body=body,
        ).execute()

        playlist_id = response.get("id")
        print(f"Playlist created: {playlist_id}")
        return playlist_id

    except HttpError as e:
        print(f"Error creating playlist: {e}")
        return None


def add_to_playlist(video_id: str, playlist_id: str) -> bool:
    """Add a video to a playlist."""
    try:
        service = get_youtube_service()
        if service is None:
            return False

        body = {
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id,
                },
            },
        }

        service.playlistItems().insert(
            part="snippet",
            body=body,
        ).execute()

        print(f"Video {video_id} added to playlist {playlist_id}")
        return True

    except HttpError as e:
        print(f"Error adding to playlist: {e}")
        return False


# ── Test Function ────────────────────────────────────────────
if __name__ == "__main__":
    print("YouTube Uploader")
    print("=" * 50)
    print("\nThis module requires:")
    print("1. client_secret.json from Google Cloud Console")
    print("2. YouTube Data API v3 enabled")
    print("3. OAuth2 consent screen configured")
    print("\nTo set up:")
    print("1. Go to https://console.cloud.google.com")
    print("2. Create a project or select existing")
    print("3. Enable YouTube Data API v3")
    print("4. Create OAuth2 credentials (Desktop app)")
    print("5. Download client_secret.json")
    print("6. Place it in the project root")
