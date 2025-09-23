import json
import asyncio
from typing import Dict, List
from agents import Runner
from .agent_core import agent

def draft_email(payload: Dict) -> str:
    """
    Streamlit-safe wrapper: run the async Runner in a fresh event loop.
    """
    user_msg = {"role": "user", "content": json.dumps(payload)}

    async def _run():
        return await Runner.run(agent, [user_msg])

    # Create and close a dedicated event loop for this thread (Streamlit worker)
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_run())
    finally:
        loop.close()

    texts: List[str] = [it.text for it in result.output if getattr(it, "type", "") == "output_text"]
    return "\n".join(texts) if texts else ""