from livekit.agents import function_tool, RunContext
from .schema import pretty_print_lead

@function_tool()
async def submit_lead(
    context: RunContext,
    child_name: str | None,
    child_class: str,
    subjects: str,
    exam_info: str | None,
    budget_range: str | None,
    decision_maker: str | None,
    timeline: str | None,
    urgency: str | None,
    contact_phone: str,
):
    # Get conversation_id for tracking - try multiple sources
    conversation_id = None
    try:
        # First try to get from agent instance
        if hasattr(context.agent, 'conversation_id'):
            conversation_id = context.agent.conversation_id
    except (AttributeError, TypeError):
        pass
    
    # Fallback: try to get from session userdata
    if not conversation_id:
        try:
            conversation_id = context.session.userdata.get("conversation_id")
        except (ValueError, AttributeError, TypeError):
            # userdata not set or not available
            pass
    
    lead = {
        "conversation_id": conversation_id,
        "child_name": child_name,
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
    pretty_print_lead(lead)

    return {
        "status": "ok",
        "message": "Lead captured. A counselor will follow up soon."
    }
