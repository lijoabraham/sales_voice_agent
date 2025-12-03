import json
from livekit.agents import function_tool, RunContext

@function_tool()
async def submit_lead(
    context: RunContext,
    child_class: str,
    subjects: str,
    contact_phone: str,
    exam_info: str | None = None,
    budget_range: str | None = None,
    decision_maker: str | None = None,
    timeline: str | None = None,
    urgency: str | None = None,
):
    # Get conversation_id for tracking - try multiple sources
    conversation_id = None
    
    # First try to get from agent instance (primary source - set in entrypoint.py)
    try:
        if hasattr(context.agent, 'conversation_id'):
            conversation_id = context.agent.conversation_id
    except (AttributeError, TypeError):
        pass
    
    # Fallback: try to get from session userdata (if available)
    if not conversation_id:
        try:
            # Accessing userdata raises ValueError if not set, so catch that
            conversation_id = context.session.userdata.get("conversation_id")
        except (ValueError, AttributeError, TypeError):
            # userdata is not set or not available, continue with None
            pass
    
    lead = {
        "conversation_id": conversation_id,
        "child_class": child_class,
        "subjects": subjects,
        "exam_info": exam_info,
        "budget_range": budget_range,
        "decision_maker": decision_maker,
        "timeline": timeline,
        "urgency": urgency,
        "contact_phone": contact_phone,
    }

    # Store in session userdata if available
    try:
        context.session.userdata["lead"] = lead
    except (AttributeError, ValueError):
        # userdata not available or not set, continue without storing
        # The lead is still printed below
        pass
    # Store the lead in the database/CRM
    print(json.dumps(lead, indent=2, ensure_ascii=False))

    return {
        "status": "ok",
        "message": "Lead captured. A counselor will follow up soon."
    }
