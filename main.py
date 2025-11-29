from livekit import agents
from runner.entrypoint import entrypoint
from config.settings import *

if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint
        )
    )
