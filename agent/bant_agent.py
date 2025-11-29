from livekit.agents import Agent
from .prompt import SYSTEM_PROMPT
from .tools import submit_lead


class EdTechBANTAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=SYSTEM_PROMPT,
            tools=[submit_lead]   
        )
