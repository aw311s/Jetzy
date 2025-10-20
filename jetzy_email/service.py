import json, os, asyncio
from typing import Any, Dict, List, Union
from agents import Runner
from .agent_core import agent

DEBUG = os.getenv("JETZY_DEBUG", "0") == "1"

def _flatten_dict_texts(d: dict) -> List[str]:
    out: List[str] = []
    stack: List[Union[dict, list, tuple]] = [d]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            for k, v in cur.items():
                if isinstance(v, str) and k in {"output_text","final_output","text","content","message"}:
                    out.append(v)
                elif isinstance(v, (dict, list, tuple)):
                    stack.append(v)
        elif isinstance(cur, (list, tuple)):
            for v in cur:
                if isinstance(v, str):
                    out.append(v)
                elif isinstance(v, (dict, list, tuple)):
                    stack.append(v)
    return out

def _extract_text_from_result(result: Any) -> str:
    # direct string
    if isinstance(result, str):
        return result

    # common single-string attrs
    for attr in ("final_output","output_text","text","message"):
        val = getattr(result, attr, None)
        if isinstance(val, str) and val.strip():
            return val

    # list-like containers
    for attr in ("output","outputs","items","messages","events","content","choices"):
        val = getattr(result, attr, None)
        if isinstance(val, (list, tuple)):
            buf: List[str] = []
            for it in val:
                if hasattr(it, "type") and getattr(it, "type") == "output_text" and hasattr(it, "text"):
                    buf.append(getattr(it, "text"))
                elif hasattr(it, "message") and hasattr(getattr(it, "message"), "content"):
                    msg = getattr(it, "message")
                    if isinstance(msg.content, str):
                        buf.append(msg.content)
                elif isinstance(it, dict):
                    if it.get("type") == "output_text" and isinstance(it.get("text"), str):
                        buf.append(it["text"])
                    elif isinstance(it.get("content"), str):
                        buf.append(it["content"])
                elif isinstance(it, str):
                    buf.append(it)
            if buf:
                return "\n".join(buf)

    # dict-like dumps
    for to_dict in ("model_dump","dict","__dict__"):
        if hasattr(result, to_dict):
            try:
                data = getattr(result, to_dict)
                data = data() if callable(data) else data
                if isinstance(data, dict):
                    texts = _flatten_dict_texts(data)
                    if texts:
                        return "\n".join(texts)
            except Exception:
                pass

    # nested tuple/list
    if isinstance(result, (list, tuple)):
        parts = [ _extract_text_from_result(x) for x in result ]
        parts = [ p for p in parts if isinstance(p, str) and p.strip() ]
        if parts:
            return "\n".join(parts)

    return str(result)

def draft_email(payload: Dict) -> str:
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

    text = _extract_text_from_result(result)

    if DEBUG:
        try:
            import streamlit as st
            st.subheader("DEBUG: RunResult (type & repr)")
            st.write(type(result))
            st.write(result)
        except Exception:
            pass

    return text