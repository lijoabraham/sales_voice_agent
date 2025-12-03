"""
Utility script to record LiveKit room sessions using Egress API.

This script can be used to start recording a LiveKit room session,
which is useful for recording conversations from the LiveKit playground.

Usage:
    python record_session.py start <room_name> [--output <output_path>]
    
Examples:
    # Record to default local folder (recordings/)
    python record_session.py start my-room
    
    # Record to specific local file
    python record_session.py start my-room --output ./recordings/my_recording.mp4
    
    # Record to S3
    python record_session.py start my-room --output s3://my-bucket/recordings/session.mp4
"""

import argparse
import asyncio
import os
from datetime import datetime
from pathlib import Path
from livekit import api
from config.settings import LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET

# Default recordings folder
DEFAULT_RECORDINGS_DIR = Path("recordings")


async def start_room_recording(
    room_name: str,
    output_path: str | None = None,
    layout: str = "speaker",
) -> dict:
    """
    Start recording a LiveKit room session using Egress API.
    
    Args:
        room_name: Name of the room to record
        output_path: Optional output path (S3: s3://bucket/path, GCS: gs://bucket/path, or local file path)
                    If not provided, saves to recordings/ folder with timestamp
        layout: Recording layout - "speaker", "grid", or "custom"
    
    Returns:
        Dictionary with recording information including egress_id
    """
    if not LIVEKIT_URL or not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        raise ValueError(
            "LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET must be set"
        )
    
    # Create LiveKitAPI client
    lkapi = api.LiveKitAPI(
        url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET,
    )
    
    # Configure recording options
    # For room composite recording (records all participants)
    # Default: save to local recordings folder with timestamp
    if output_path:
        # Use provided output path
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
    else:
        # Default: save to local recordings folder with timestamp
        DEFAULT_RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{room_name}_{timestamp}.mp4"
        output_file = DEFAULT_RECORDINGS_DIR / filename
    
    recording_request = api.RoomCompositeEgressRequest(
        room_name=room_name,
        layout=layout,
        file_outputs=[
            api.EncodedFileOutput(
                file_type=api.EncodedFileType.MP4,
                filepath=str(output_file),
            )
        ],
    )
    
    print(f"Recording will be saved to: {output_file.absolute()}")
    
    # Start the recording
    print(f"Starting recording for room: {room_name}")
    egress_info = await lkapi.egress.start_room_composite_egress(recording_request)
    
    # Close the API client
    await lkapi.aclose()
    
    print(f"Recording started successfully!")
    print(f"Egress ID: {egress_info.egress_id}")
    print(f"Room Name: {egress_info.room_name}")
    print(f"Status: {egress_info.status}")
    
    return {
        "egress_id": egress_info.egress_id,
        "room_name": egress_info.room_name,
        "status": egress_info.status,
    }


async def stop_recording(egress_id: str) -> dict:
    """
    Stop an active recording.
    
    Args:
        egress_id: The Egress ID returned when starting the recording
    
    Returns:
        Dictionary with updated recording status
    """
    if not LIVEKIT_URL or not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        raise ValueError(
            "LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET must be set"
        )
    
    # Create LiveKitAPI client
    lkapi = api.LiveKitAPI(
        url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET,
    )
    
    print(f"Stopping recording: {egress_id}")
    egress_info = await lkapi.egress.stop_egress(
        api.StopEgressRequest(egress_id=egress_id)
    )
    
    # Close the API client
    await lkapi.aclose()
    
    print(f"Recording stopped!")
    print(f"Status: {egress_info.status}")
    
    return {
        "egress_id": egress_info.egress_id,
        "status": egress_info.status,
    }


async def list_recordings(room_name: str | None = None) -> list:
    """
    List active or completed recordings.
    
    Args:
        room_name: Optional room name to filter recordings
    
    Returns:
        List of recording information
    """
    if not LIVEKIT_URL or not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        raise ValueError(
            "LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET must be set"
        )
    
    # Create LiveKitAPI client
    lkapi = api.LiveKitAPI(
        url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET,
    )
    
    request = api.ListEgressRequest(room_name=room_name) if room_name else api.ListEgressRequest()
    response = await lkapi.egress.list_egress(request)
    
    # Close the API client
    await lkapi.aclose()
    
    print(f"Found {len(response.items)} recording(s)")
    for item in response.items:
        print(f"  - Egress ID: {item.egress_id}, Room: {item.room_name}, Status: {item.status}")
    
    return [{"egress_id": item.egress_id, "room_name": item.room_name, "status": item.status} for item in response.items]


async def main():
    parser = argparse.ArgumentParser(
        description="Record LiveKit room sessions using Egress API"
    )
    parser.add_argument(
        "action",
        choices=["start", "stop", "list"],
        help="Action to perform: start recording, stop recording, or list recordings",
    )
    parser.add_argument(
        "room_name",
        nargs="?",
        help="Room name (required for start/stop actions)",
    )
    parser.add_argument(
        "--egress-id",
        help="Egress ID (required for stop action)",
    )
    parser.add_argument(
        "--output",
        help="Output path for recording (S3: s3://bucket/path, GCS: gs://bucket/path, or local path). Default: recordings/<room_name>_<timestamp>.mp4",
    )
    parser.add_argument(
        "--layout",
        choices=["speaker", "grid"],
        default="speaker",
        help="Recording layout (default: speaker)",
    )
    
    args = parser.parse_args()
    
    try:
        if args.action == "start":
            if not args.room_name:
                parser.error("room_name is required for start action")
            await start_room_recording(
                args.room_name, output_path=args.output, layout=args.layout
            )
        elif args.action == "stop":
            if not args.egress_id:
                parser.error("--egress-id is required for stop action")
            await stop_recording(args.egress_id)
        elif args.action == "list":
            await list_recordings(args.room_name)
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))

