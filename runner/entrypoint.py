import json
from livekit.agents import JobContext, AgentSession
from livekit.plugins import openai as openai_plugin

from agent.bant_agent import EdTechBANTAgent
from config.token_generator import generate_conversation_id


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    # Extract or generate conversation_id
    conversation_id = None
    try:
        # Try to extract conversation_id from room metadata
        if ctx.room and hasattr(ctx.room, 'metadata'):
            metadata = ctx.room.metadata
            if metadata:
                try:
                    metadata_dict = json.loads(metadata)
                    conversation_id = metadata_dict.get("conversation_id")
                except (json.JSONDecodeError, AttributeError):
                    pass
    except (AttributeError, TypeError):
        pass
    
    # Generate new conversation_id if not found
    if not conversation_id:
        conversation_id = generate_conversation_id()
    
    llm = openai_plugin.realtime.RealtimeModel(
        voice="alloy"
    )

    session = AgentSession(
        llm=llm,
    )

    agent = EdTechBANTAgent()
    
    # Store conversation_id on the agent instance for tracking
    # This is accessible from tools via context.agent
    agent.conversation_id = conversation_id

    await session.start(room=ctx.room, agent=agent)

    # Try to store conversation_id in session userdata after session is started
    # userdata is a property that raises ValueError if not set
    try:
        session.userdata["conversation_id"] = conversation_id
    except (ValueError, AttributeError):
        # If userdata is not available, that's okay - we have it on the agent
        pass

    # Greet parent
    await session.generate_reply(
        instructions="Greet the parent by introducing yourself as Sales Agent. Say that you want to know more about the student and ask which class their child is studying in."
    )
