import json
import asyncio
from typing import Any, Dict, Optional
from agents import Runner
from .agent_core import agent

def _safe_getattr(obj: Any, name: str) -> Optional[Any]:
    try:
        return getattr(obj, name)
    except Exception:
        return None

def _extract_text(result: Any) -> str:
    """
    Be ultra-conservative: try a few common attributes only.
    Do NOT traverse nested structures to avoid touching SDK-internal attrs
    (like .output) that may not exist on older/newer builds.
    """
    # direct string
    if isinstance(result, str):
        return result

    # most common single-string attributes
    for attr in ("final_output", "output_text", "text"):
        val = _safe_getattr(result, attr)
        if isinstance(val, str) and val.strip():
            return val

    # OpenAI-style message holder (very common)
    # - result.message.content (obj)
    # - result["message"]["content"] (dict-like)
    msg = _safe_getattr(result, "message")
    if msg is not None:
        content = _safe_getattr(msg, "content")
        if isinstance(content, str) and content.strip():
            return content

    # very conservative dict-like fallback (only top level)
    to_dict = None
    for name in ("model_dump", "dict"):
        try:
            maybe = getattr(result, name, None)
            if callable(maybe):
                d = maybe()
            else:
                d = maybe
            if isinstance(d, dict):
                to_dict = d
                break
        except Exception:
            pass

    if isinstance(to_dict, dict):
        # look for a few well-known keys only (top-level)
        for key in ("final_output", "output_text", "text"):
            val = to_dict.get(key)
            if isinstance(val, str) and val.strip():
                return val
        # message.content at top level (dict-like)
        msg = to_dict.get("message")
        if isinstance(msg, dict):
            content = msg.get("content")
            if isinstance(content, str) and content.strip():
                return content

    # last resort
    return str(result)

def draft_email(payload: Dict) -> str:
    """
    Streamlit-safe runner: create a fresh event loop and use a very
    defensive extractor that avoids accessing SDK-internal attributes.
    """
    user_msg = {"role": "user", "content": json.dumps(payload)}

    async def _run_once():
        return await Runner.run(agent, [user_msg])

    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_run_once())
    finally:
        try:
            loop.run_until_complete(asyncio.sleep(0))
        except Exception:
            pass
        loop.close()

    return _extract_text(result)