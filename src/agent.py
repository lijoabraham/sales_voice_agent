"""
EdTech BANT Voice Agent using LiveKit Agents + OpenAI Realtime.

Features:
- Voice conversation with parents about their child's studies
- Collects BANT-style info: Budget, Authority, Need, Timeline (EdTech flavored)
- Uses a function tool `submit_lead` to emit structured lead data

Run:
    python agent.py dev

Then connect from:
- LiveKit Agents playground, or
- Your own LiveKit-based frontend / telephony
"""

import json
from typing import Any, Dict

from dotenv import load_dotenv

from livekit import agents
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RunContext,
    function_tool,
)
from livekit.plugins import openai as openai_plugin


# ------------- Agent Definition -------------


class EdtechBANTAgent(Agent):
    """
    Voice agent that talks to parents and qualifies them for EdTech programs
    using a BANT-style framework.
    """

    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a friendly voice assistant for an EdTech company. "
                "You are speaking with a parent about their child's education.\n\n"
                "Your main goals are to:\n"
                "1) Understand the child's situation (class/grade, subjects, exam goals).\n"
                "2) Identify their learning needs (weak subjects, exam prep, type of help).\n"
                "3) Gently ask about budget/fee comfort range.\n"
                "4) Confirm who makes the final decision (mother, father, guardian, both).\n"
                "5) Understand timeline/urgency (upcoming exams, when they want to start).\n\n"
                "You should have a short, natural conversation, not an interrogation.\n"
                "Ask one question at a time, listen, and adapt.\n\n"
                "Once you feel you have enough information for a sales counselor to call back, "
                "call the function tool `submit_lead` with the best values you inferred. "
                "Only call `submit_lead` once per conversation when you are done collecting details.\n\n"
                "After calling `submit_lead`, politely wrap up the call, telling the parent that "
                "a counselor will contact them soon with program details."
            ),
        )

    # Tool to emit the structured lead. This is where you'd normally
    # forward to your CRM, database, or webhook.
    @function_tool()
    async def submit_lead(
        self,
        context: RunContext,
        child_name: str | None,
        child_class: str,
        subjects: str,
        program_type: str,
        exam_info: str,
        budget_range: str,
        decision_maker: str,
        timeline: str,
        urgency: str,
        contact_phone: str | None,
        contact_email: str | None,
    ) -> Dict[str, Any]:
        """
        Submit a structured lead captured during the conversation.

        Call this when you have enough information to pass the lead to a human counselor.

        Args:
            child_name: Optional, child's first name if shared.
            child_class: The child's current class/grade (e.g., '8', '9', '10', '11', '12').
            subjects: Subjects where help is needed (e.g., 'Math and Science').
            program_type: Type of program (e.g., 'board exam preparation', 'JEE foundation').
            exam_info: Details about upcoming exams (e.g., 'CBSE boards in March', 'JEE 2026').
            budget_range: Parent's comfortable fee range (e.g., '₹10,000–₹15,000 per term').
            decision_maker: Who takes the final decision (e.g., 'Mother', 'Father', 'Both parents').
            timeline: When they want to start (e.g., 'this week', 'next academic year').
            urgency: Qualitative sense of urgency (e.g., 'high', 'medium', 'low').
            contact_phone: Parent's phone number if shared.
            contact_email: Parent's email if shared.
        """

        lead = {
            "child_name": child_name,
            "child_class": child_class,
            "subjects": subjects,
            "program_type": program_type,
            "exam_info": exam_info,
            "budget_range": budget_range,
            "decision_maker": decision_maker,
            "timeline": timeline,
            "urgency": urgency,
            "contact_phone": contact_phone,
            "contact_email": contact_email,
        }

        # Store in session userdata so other parts of your system can use it
        context.session.userdata["edtech_lead"] = lead

        # For now we just print it so you can see it's working.
        # Replace this with a DB insert or CRM API call.
        print("\n========== NEW EDTECH LEAD ==========")
        print(json.dumps(lead, indent=2, ensure_ascii=False))
        print("=====================================\n")

        # Optionally, you can return something for the LLM to read as context.
        return {
            "status": "ok",
            "message": "Lead captured successfully for sales follow-up.",
        }


# ------------- Entrypoint / Worker -------------


async def entrypoint(ctx: JobContext) -> None:
    """
    LiveKit Agents worker entrypoint.
    This is called whenever a new job (room/session) is started.
    """
    # Connect to the LiveKit room
    await ctx.connect()

    # Configure the OpenAI Realtime model via LiveKit plugin
    # This will handle STT, LLM reasoning, and TTS in realtime.
    llm = openai_plugin.realtime.RealtimeModel(
        # model defaults to 'gpt-realtime', but you can override:
        # model="gpt-realtime-preview",
        voice="alloy",  # pick any supported OpenAI realtime voice
        # You can tweak temperature, VAD, etc. if needed
        # temperature=0.8,
    )

    session = AgentSession(
        llm=llm,
        # You can also pass tts=..., stt=... if you want custom providers
    )

    agent = EdtechBANTAgent()

    # Start the agent in the current room
    await session.start(
        room=ctx.room,
        agent=agent,
    )

    # Optional: have the agent proactively greet the parent
    await session.generate_reply(
        instructions=(
            "Greet the parent warmly, briefly introduce yourself as an academic assistant, "
            "and ask for the child's class/grade to get started."
        )
    )


if __name__ == "__main__":
    load_dotenv()
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
