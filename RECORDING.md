# Recording LiveKit Playground Sessions

There are several ways to record video from the LiveKit playground. Here are the most common approaches:

## Method 1: Browser Screen Recording (Simplest)

The easiest way to record the LiveKit playground is using your browser's built-in screen recording feature:

### Chrome/Edge:
1. Open the LiveKit playground in your browser
2. Press `Ctrl+Shift+S` (Linux/Windows) or `Cmd+Shift+S` (Mac) to start screen recording
3. Select the browser tab or window containing the playground
4. Click "Start recording"
5. When done, click the stop button in the browser toolbar
6. The video will be saved to your Downloads folder

### Firefox:
1. Open the LiveKit playground
2. Click the three-dot menu → "More tools" → "Record screen"
3. Select the tab/window to record
4. Click "Start recording"
5. Stop when finished

### Alternative: Use OBS Studio or similar
- Install OBS Studio (free, open-source)
- Add a "Browser Source" or "Window Capture" source
- Record the LiveKit playground window
- Provides more control over quality, format, and editing

## Method 2: Programmatic Recording with LiveKit Egress API

For automated or programmatic recording, use LiveKit's Egress API:

### Prerequisites:
- LiveKit server with Egress enabled
- Proper storage configuration (S3, GCS, Azure, or local storage)

### Usage:

#### Start Recording:
```bash
python record_session.py start <room_name> [--output <output_path>] [--layout speaker|grid]
```

Examples:
```bash
# Record to default storage location
python record_session.py start my-room

# Record with custom output path
python record_session.py start my-room --output /path/to/recording.mp4

# Record to S3 (requires S3 credentials configured)
python record_session.py start my-room --output s3://my-bucket/recordings/session.mp4

# Use grid layout instead of speaker layout
python record_session.py start my-room --layout grid
```

#### Stop Recording:
```bash
python record_session.py stop --egress-id <egress_id>
```

#### List Active Recordings:
```bash
python record_session.py list [room_name]
```

### Integration in Your Agent Code

You can also start recording programmatically from within your agent:

```python
from livekit import api
from config.settings import LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET

async def start_recording(room_name: str):
    # Create LiveKitAPI client
    lkapi = api.LiveKitAPI(
        url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET,
    )
    
    request = api.RoomCompositeEgressRequest(
        room_name=room_name,
        layout="speaker",
        file_outputs=[
            api.EncodedFileOutput(
                file_type=api.EncodedFileType.MP4,
                filepath=f"{room_name}_recording.mp4",
            )
        ],
    )
    
    egress_info = await lkapi.egress.start_room_composite_egress(request)
    await lkapi.aclose()  # Close the API client
    return egress_info.egress_id
```

Add this to your `runner/entrypoint.py` to automatically start recording when a session begins:

```python
async def entrypoint(ctx: JobContext):
    await ctx.connect()
    
    # Start recording (optional)
    # egress_id = await start_recording(ctx.room.name)
    
    # ... rest of your agent code
```

## Method 3: Using LiveKit Recorder (Advanced)

For production use with individual participant recording, consider using [LiveKit Recorder](https://github.com/livekit/livekit-recorder):

1. Clone the repository
2. Configure Docker and S3 credentials
3. Run the recorder service
4. It will automatically record all participants in rooms

## Notes

- **Egress API** requires LiveKit server configuration with proper storage backends
- **Browser recording** is simplest for testing/demos but requires manual start/stop
- **Programmatic recording** is best for production automation
- Recordings can be stored in S3, Google Cloud Storage, Azure Blob Storage, or locally
- The Egress API supports different layouts: `speaker` (focuses on active speaker) or `grid` (shows all participants)

## Troubleshooting

- If Egress API fails, ensure your LiveKit server has Egress enabled
- Check that storage credentials are properly configured
- Verify room name matches exactly (case-sensitive)
- For S3/GCS uploads, ensure proper IAM permissions are set

