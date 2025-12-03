import asyncio
import json
from livekit.agents import ConversationItemAddedEvent, JobContext, AgentSession, MetricsCollectedEvent, RoomInputOptions, metrics
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
            metadata = ctx.job.metadata
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

    def _on_conversation_item(event: ConversationItemAddedEvent):
        asyncio.create_task(log_transcription(event))

    async def log_transcription(event: ConversationItemAddedEvent):
        item = event.item
        role = item.role
        text = item.text_content or ""
        print(f"Logging History: {role} : {text}")

    session = AgentSession(
        llm=llm,
    )

    agent = EdTechBANTAgent()
    
    # Usage Metrics
    usage_collector = metrics.UsageCollector()
    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        usage_collector.collect(ev.metrics)

    @session.on("close")
    def _on_close(_):
        asyncio.create_task(log_llm_tokens())
    
    async def log_llm_tokens():
        usage = usage_collector.get_summary()
        print(f"LLM Tokens: {usage}")
    # Store conversation_id on the agent instance for tracking
    # This is accessible from tools via context.agent
    agent.conversation_id = conversation_id

    await session.start(room=ctx.room, agent=agent,room_input_options=RoomInputOptions(
            close_on_disconnect = True
        ))

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
