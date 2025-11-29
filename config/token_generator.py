"""
Utility functions for generating LiveKit room access tokens for clients.
"""
import json
import uuid
from livekit import api
from .settings import LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL


def generate_conversation_id() -> str:
    """
    Generate a unique conversation ID for tracking.
    
    Returns:
        UUID string for conversation tracking
    """
    return str(uuid.uuid4())


async def create_room(
    room_name: str,
    conversation_id: str | None = None,
    max_participants: int = 2,
) -> dict:
    """
    Create a LiveKit room explicitly using the RoomService API.
    
    Note: Rooms are also created automatically when the first participant joins.
    Use this function if you want to create the room before participants connect.
    
    Args:
        room_name: Name of the room to create
        conversation_id: Optional conversation ID to store in room metadata
        max_participants: Maximum number of participants allowed in the room
        
    Returns:
        Dictionary containing room information
        
    Raises:
        ValueError: If LIVEKIT_URL, LIVEKIT_API_KEY, or LIVEKIT_API_SECRET are not set
    """
    if not LIVEKIT_URL or not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        raise ValueError("LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET must be set")
    
    # Create RoomService client
    room_service = api.RoomService(LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
    
    # Prepare room metadata
    metadata = {}
    if conversation_id:
        metadata["conversation_id"] = conversation_id
    
    # Create room configuration
    room_config = api.RoomConfiguration(
        agents=[
            api.RoomAgentDispatch(
                metadata=json.dumps(metadata) if metadata else None
            )
        ],
        max_participants=max_participants,
    )
    
    # Create the room
    room = await room_service.create_room(
        api.CreateRoomRequest(
            name=room_name,
            config=room_config,
        )
    )
    
    return {
        "name": room.name,
        "sid": room.sid,
        "empty_timeout": room.empty_timeout,
        "max_participants": room.max_participants,
        "creation_time": room.creation_time,
        "turn_password": room.turn_password,
        "enabled_codecs": room.enabled_codecs,
    }


def create_room_token(
    room_name: str,
    participant_identity: str,
    participant_name: str | None = None,
    can_publish: bool = True,
    can_subscribe: bool = True,
    can_publish_data: bool = True,
    conversation_id: str | None = None,
) -> tuple[str, str]:
    """
    Generate a LiveKit room access token for a client to connect.
    
    Args:
        room_name: Name of the room to join
        participant_identity: Unique identifier for the participant
        participant_name: Optional display name for the participant
        can_publish: Whether participant can publish audio/video
        can_subscribe: Whether participant can subscribe to tracks
        can_publish_data: Whether participant can publish data messages
        conversation_id: Optional conversation ID. If not provided, a new one will be generated.
        
    Returns:
        Tuple of (JWT token string, conversation_id) that can be used by clients to connect to the room
    """
    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        raise ValueError("LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set")
    
    # Generate conversation_id if not provided
    if conversation_id is None:
        conversation_id = generate_conversation_id()
    
    # Create access token
    token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
        .with_identity(participant_identity) \
        .with_name(participant_name or participant_identity) \
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=can_publish,
                can_subscribe=can_subscribe,
                can_publish_data=can_publish_data,
            )
        ).with_room_config(
                api.RoomConfiguration(
                    agents=[
                        api.RoomAgentDispatch(
                            metadata=json.dumps({"conversation_id": conversation_id})
                        )
                    ],
                    max_participants = 2,
                ),
            )
    
    return token.to_jwt(), conversation_id


def create_agent_token(room_name: str, conversation_id: str | None = None) -> tuple[str, str]:
    """
    Generate a token for an agent to connect to a room.
    Agents typically need full permissions.
    
    Args:
        room_name: Name of the room to join
        conversation_id: Optional conversation ID. If not provided, a new one will be generated.
        
    Returns:
        Tuple of (JWT token string, conversation_id) for the agent
    """
    return create_room_token(
        room_name=room_name,
        participant_identity="agent",
        participant_name="Voice Agent",
        can_publish=True,
        can_subscribe=True,
        can_publish_data=True,
        conversation_id=conversation_id,
    )


def create_client_token(
    room_name: str,
    participant_identity: str,
    participant_name: str | None = None,
    conversation_id: str | None = None,
) -> tuple[str, str]:
    """
    Generate a token for a client (parent) to connect to a room.
    Clients typically need to publish audio and subscribe to agent audio.
    
    Args:
        room_name: Name of the room to join
        participant_identity: Unique identifier for the client (e.g., phone number, user ID)
        participant_name: Optional display name for the client
        conversation_id: Optional conversation ID. If not provided, a new one will be generated.
        
    Returns:
        Tuple of (JWT token string, conversation_id) for the client
    """
    return create_room_token(
        room_name=room_name,
        participant_identity=participant_identity,
        participant_name=participant_name or participant_identity,
        can_publish=True,  # Client needs to publish audio
        can_subscribe=True,  # Client needs to subscribe to agent audio
        can_publish_data=False,  # Clients typically don't need to publish data
        conversation_id=conversation_id,
    )

