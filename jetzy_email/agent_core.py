from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from agents import Agent, Runner, function_tool

# --- Strict models for the composer ---

from typing import Optional, Literal
from pydantic import BaseModel, Field
from agents import Agent, Runner, function_tool

class EmailComposeInput(BaseModel):
    investor_first_name: str = Field(..., description="e.g., Everett")
    firm: str = Field(..., description="e.g., Legendary Ventures")
    context_event: str = Field(..., description='e.g., "7BC Global VC Demo Day (NYC)"')

    # free-text lines for the two personalization sentences:
    investor_background_line: str = Field(
        ..., description='e.g., "former operator and technical founder with expertise in ML and full-stack development"'
    )
    firm_focus_line: str = Field(
        ..., description='e.g., "marketplace and AI/ML-driven investments"'
    )

    # traction + proof
    users_line: str = Field(..., description='e.g., "44,000+ users with ~25% MAU"')
    growth_line: str = Field(..., description='e.g., "entirely organic growth ($0 paid marketing)"')
    revenue_line: str = Field(..., description='e.g., "~$450K in early B2B revenue"')
    pipeline_line: str = Field(..., description='e.g., "$2M+ pipeline"')
    partnerships_line: str = Field(..., description='e.g., "China and India"')

    # optional tagline
    one_liner: Optional[str] = Field(
        None, description='Optional: "Social-first, AI-powered platform for authentic travel experiences."'
    )

    # signature + CTA
    meeting_preference: Literal["Either", "Zoom", "Coffee"] = "Either"
    from_name: str = "Shama"

class EmailOut(BaseModel):
    subject: str
    body: str

@function_tool
def compose_email(payload: EmailComposeInput) -> EmailOut:
    subject = f"Jetzy - Following up from the {payload.context_event}"
    title = f"Email Draft for {payload.investor_first_name} ({payload.firm})"

    p1 = (
        f"Hi {payload.investor_first_name},\n\n"
        f"It was a pleasure meeting you at the {payload.context_event} and learning about your background as a "
        f"{payload.investor_background_line}, as well as {payload.firm}'s focus on {payload.firm_focus_line}. "
        f"As we discussed, our work at Jetzy aligns closely with that thesis."
    )

    p2 = (
        "\n\nWe are building the social layer for the massive travel and leisure industry. "
        "Jetzy is an AI-powered platform where users can not only find unique experiences but also connect with "
        "like-minded people to enjoy them together. Our initial focus is on \"travel and experience seekers\" — "
        "a fast-growing segment seeking authentic, personalized travel."
    )

    p3 = (
        f"\n\nThe company is led by experienced leadership with deep expertise in AI and marketplace dynamics. "
        f"We’ve achieved strong, capital-efficient traction, growing to {payload.users_line}, "
        f"{payload.growth_line}. We’ve generated {payload.revenue_line}, built a {payload.pipeline_line}, "
        f"and established partnerships with major tourism boards across {payload.partnerships_line}."
    )

    one_liner_txt = f"\n\nJetzy in one line: {payload.one_liner}" if payload.one_liner else ""

    if payload.meeting_preference == "Zoom":
        cta = "I’d love to set up a Zoom call to walk you through our journey at a time that works for you."
    elif payload.meeting_preference == "Coffee":
        cta = "I’d love to set up a coffee chat to walk you through our journey at a time that works for you."
    else:
        cta = "I’d love to set up a Zoom call or coffee chat to walk you through our journey at a time that works for you."

    closing = f"\n\n{cta}\n\nSincerely,\n{payload.from_name}"

    body = f"{title}\nSubject: {subject}\n\n{p1}{p2}{p3}{one_liner_txt}{closing}"
    return EmailOut(subject=subject, body=body)

# =====================
# Agent configuration
# =====================

INSTRUCTIONS = """
You are Jetzy’s Investor Outreach Agent. Use the provided tools. When composing an email,
you MUST call compose_email(...) and follow its exact structure. Do not free-style the format.
Return only the final email body (starting with 'Email Draft for ...' then 'Subject: ...').
"""

agent = Agent(
    name="Jetzy Investor Email Agent",
    instructions=INSTRUCTIONS,
    tools=[
        # keep any other tools you already had, e.g. traction_bullets, bridge_and_angle, so_what_check, skim_check
        compose_email,
    ],
    model="gpt-4.1-mini",
)


