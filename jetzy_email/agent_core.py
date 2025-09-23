from agents import Agent, Runner, function_tool

from typing import List, Optional, Literal
from pydantic import BaseModel, Field
import json

# =========================
# Strict input/output models
# =========================


class Metric(BaseModel):
    label: str = Field(..., description="Metric name, e.g., 'Users'")
    value: str = Field(..., description="Metric value, e.g., '44,000+; ~25% MAU'")

class TractionItems(BaseModel):
    items: List[Metric] = Field(..., description="List of traction metrics as label/value pairs")

class BridgeAngleInput(BaseModel):
    themes: List[str] = Field(default_factory=list, description="Portfolio themes: marketplace, ai-ml, etc.")
    hooks: List[str] = Field(default_factory=list, description="Investor hooks/background keywords")
    firm: str = Field(..., description="Investor firm")
    product_one_liner: str = Field(..., description="Jetzy one-liner")
    positioning: str = Field(..., description="Jetzy positioning sentence")

class BridgeAngle(BaseModel):
    bridge: str
    angle: str

class EmailComposeInput(BaseModel):
    investor_first_name: str
    firm: str
    context_event: Optional[str] = "our recent conversation"
    bridge: str
    angle: str
    one_liner: str
    positioning: str
    differentiators: List[str]
    traction_items: List[Metric]
    partnerships: List[str]
    from_name: str = "Shama"
    from_title: str = ""
    from_company: str = "Jetzy"
    tone: Literal["crisp", "warm", "short"] = "crisp"

class EmailOut(BaseModel):
    subject: str
    body: str

class SoWhatInput(BaseModel):
    email_text: str
    investor_first_name: str
    firm_name: str

class SkimInput(BaseModel):
    email_text: str

class Issues(BaseModel):
    issues: List[str] = Field(default_factory=list)

# ===========
# Tools (strict)
# ===========

@function_tool
def traction_bullets(payload: TractionItems) -> str:
    """Return formatted bullets from traction items."""
    return "\n".join(f"• {m.label}: {m.value}" for m in payload.items)

@function_tool
def bridge_and_angle(payload: BridgeAngleInput) -> BridgeAngle:
    """Produce a personalized bridge (why them + why now) and a suggested angle."""
    firm_pattern = " and ".join(payload.themes) if payload.themes else "community-driven marketplaces"
    hook_phrase = ", ".join(payload.hooks) if payload.hooks else "your background"
    bridge = (
        f"{payload.firm} repeatedly backs {firm_pattern}. "
        f"Jetzy is {payload.product_one_liner} — the {payload.positioning}. "
        f"Given {hook_phrase}, you'll appreciate our AI/ML engine and social graph flywheel."
    )
    lower_themes = [t.lower() for t in payload.themes]
    if "ai-ml" in lower_themes or any(h.lower() in ("ai", "ml", "machine learning") for h in payload.hooks):
        angle = "Lead with technical moat (AI/ML + social graph) and community flywheel."
    elif "marketplace" in lower_themes:
        angle = "Position as category-defining community marketplace in travel/experiences."
    else:
        angle = "Emphasize community defensibility and traction as de-risking signals."
    return BridgeAngle(bridge=bridge, angle=angle)

@function_tool
def compose_email(payload: EmailComposeInput) -> EmailOut:
    """Compose the investor email (subject + body with bullets + CTA)."""
    subject = f"Jetzy — Following up from {payload.context_event}"
    greeting = "Hi"
    if payload.tone == "warm":
        greeting = "Hi"
    elif payload.tone == "short":
        greeting = "Hi"

    intro = (
        f"{greeting} {payload.investor_first_name},\n\n"
        f"It was great meeting you at {payload.context_event}. I took a closer look at {payload.firm}'s portfolio and the fit is compelling. "
        f"{payload.bridge}"
    )

    diffs = ", ".join(payload.differentiators)
    what_is = (
        f"\n\nJetzy in one line: {payload.one_liner}\n\n"
        f"Instead of a simple booking tool, we're the {payload.positioning}\n"
        f"For a technical audience, the core is our {diffs}. "
        f"({payload.angle})"
    )

    bullets = "\n".join(f"• {m.label}: {m.value}" for m in payload.traction_items)
    traction = (
        f"\n\nOur traction shows the model is working:\n{bullets}\n\n"
        f"Key partnerships: {', '.join(payload.partnerships)}."
    )

    closing = (
        "\n\nWe’re building the definitive platform for the experience economy, with community as our moat.\n"
        "Would you be open to a brief call next week to dive deeper?\n\n"
        f"Best regards,\n{payload.from_name}\n{payload.from_title}\n{payload.from_company}"
    )

    return EmailOut(subject=subject, body=f"Subject: {subject}\n\n{intro}{what_is}{traction}{closing}")

@function_tool
def so_what_check(payload: SoWhatInput) -> Issues:
    """Personalization & value checks."""
    txt = payload.email_text
    issues: List[str] = []
    if payload.investor_first_name.lower() not in txt.lower():
        issues.append("Personalization: investor first name is missing.")
    if payload.firm_name.lower() not in txt.lower():
        issues.append("Personalization: firm name is missing.")
    if "Jetzy" not in txt:
        issues.append("Clarity: Jetzy is not clearly introduced.")
    if "call" not in txt.lower() and "meeting" not in txt.lower():
        issues.append("CTA: add a specific ask (e.g., brief call next week?).")
    if "• " not in txt and "- " not in txt:
        issues.append("Proof points: add bullet points for traction.")
    return Issues(issues=issues)

@function_tool
def skim_check(payload: SkimInput) -> Issues:
    """Scannability checks: subject, bullets, paragraph length."""
    txt = payload.email_text
    issues: List[str] = []
    lines = txt.splitlines()
    if not lines or not lines[0].lower().startswith("subject:"):
        issues.append("Subject: first line should start with 'Subject: ...'.")
    if "• " not in txt and "- " not in txt:
        issues.append("Skim: include bullet points for traction.")
    if any(len(p) > 600 for p in txt.split("\n\n")):
        issues.append("Skim: shorten long paragraphs for faster reading.")
    return Issues(issues=issues)

# =====================
# Agent configuration
# =====================

INSTRUCTIONS = """
You are Jetzy’s Investor Outreach Agent. Follow this strict, tool-driven workflow:

1) If bridge/angle aren’t provided by the user, call bridge_and_angle(...) to generate them.
2) Call compose_email(...) with the provided inputs to draft the email.
3) Call so_what_check(...) and skim_check(...) on the draft.
4) If any issues are returned, revise the draft and re-check once.
Constraints:
- Tone: crisp, investor-friendly, confident.
- Never invent metrics. Only use user-provided inputs.
Return ONLY the final email body (first line must be 'Subject: ...').
"""
agent = Agent(
    name="Jetzy Investor Email Agent",
    instructions=INSTRUCTIONS,
    tools=[traction_bullets, bridge_and_angle, compose_email, so_what_check, skim_check],
    model="gpt-4.1-mini",
)


