#!/usr/bin/env python3
"""
CLI script to generate LiveKit room access tokens.

Usage examples:
    # Generate a client token
    python generate_token.py client --room "sales-room-123" --identity "parent-9876543210"

    # Generate an agent token
    python generate_token.py agent --room "sales-room-123"

    # Generate a custom token with specific permissions
    python generate_token.py custom --room "sales-room-123" --identity "user-123" --name "John Doe" --no-publish-data

    # Output as JSON (useful for API responses)
    python generate_token.py client --room "sales-room-123" --identity "parent-123" --json
"""
import argparse
import json
import sys
from config import (
    create_client_token,
    create_agent_token,
    create_room_token,
    LIVEKIT_URL,
)


def main():
    parser = argparse.ArgumentParser(
        description="Generate LiveKit room access tokens",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest="token_type", help="Type of token to generate")
    subparsers.required = True
    
    # Client token parser
    client_parser = subparsers.add_parser("client", help="Generate a token for a client (parent)")
    client_parser.add_argument("--room", required=True, help="Room name")
    client_parser.add_argument("--identity", required=True, help="Participant identity (e.g., phone number, user ID)")
    client_parser.add_argument("--name", help="Participant display name (defaults to identity)")
    client_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Agent token parser
    agent_parser = subparsers.add_parser("agent", help="Generate a token for an agent")
    agent_parser.add_argument("--room", required=True, help="Room name")
    agent_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Custom token parser
    custom_parser = subparsers.add_parser("custom", help="Generate a custom token with specific permissions")
    custom_parser.add_argument("--room", required=True, help="Room name")
    custom_parser.add_argument("--identity", required=True, help="Participant identity")
    custom_parser.add_argument("--name", help="Participant display name (defaults to identity)")
    custom_parser.add_argument("--no-publish", action="store_true", help="Disable publish permission")
    custom_parser.add_argument("--no-subscribe", action="store_true", help="Disable subscribe permission")
    custom_parser.add_argument("--no-publish-data", action="store_true", help="Disable publish data permission")
    custom_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    try:
        if args.token_type == "client":
            token, conversation_id = create_client_token(
                room_name=args.room,
                participant_identity=args.identity,
                participant_name=args.name,
            )
        elif args.token_type == "agent":
            token, conversation_id = create_agent_token(room_name=args.room)
        elif args.token_type == "custom":
            token, conversation_id = create_room_token(
                room_name=args.room,
                participant_identity=args.identity,
                participant_name=args.name,
                can_publish=not args.no_publish,
                can_subscribe=not args.no_subscribe,
                can_publish_data=not args.no_publish_data,
            )
        else:
            parser.error(f"Unknown token type: {args.token_type}")
        
        if args.json:
            output = {
                "token": token,
                "conversation_id": conversation_id,
                "url": LIVEKIT_URL,
                "room": args.room,
            }
            if args.token_type == "client" or args.token_type == "custom":
                output["identity"] = args.identity
                if args.name:
                    output["name"] = args.name
            print(json.dumps(output, indent=2))
        else:
            print("=" * 60)
            print("LiveKit Room Access Token")
            print("=" * 60)
            print(f"Room: {args.room}")
            print(f"Conversation ID: {conversation_id}")
            if args.token_type == "client" or args.token_type == "custom":
                print(f"Identity: {args.identity}")
                if args.name:
                    print(f"Name: {args.name}")
            print(f"URL: {LIVEKIT_URL}")
            print("-" * 60)
            print("Token:")
            print(token)
            print("=" * 60)
            print("\nUse this token with the URL above to connect to the room.")
            print(f"Conversation ID '{conversation_id}' will be used for tracking this conversation.")
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

