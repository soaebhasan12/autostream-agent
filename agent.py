from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os

from knowledge_base import get_system_prompt
from tools import mock_lead_capture


# ── State ──────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    messages: List
    user_name: Optional[str]
    user_email: Optional[str]
    user_platform: Optional[str]
    lead_captured: bool
    collecting_lead: bool


# ── LLM ────────────────────────────────────────────────────────────────────

def get_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.7,
        max_tokens=1024,
        api_key=os.getenv("GROQ_API_KEY")
    )


# ── Intent Detection ───────────────────────────────────────────────────────

def detect_intent(message: str, llm) -> str:
    prompt = f"""Classify this user message into EXACTLY ONE category:

- GREETING: Simple hello, hi, hey, how are you
- PRODUCT_INQUIRY: Questions about features, pricing, plans, policies, refunds
- HIGH_INTENT: User wants to sign up, try, or buy. They mention their creator
  platform, say "I want", "sign me up", "let's do it", "I'll take the Pro plan",
  or express clear readiness to start.

User message: "{message}"

Reply with ONLY the category name. Nothing else."""

    response = llm.invoke([HumanMessage(content=prompt)])
    intent = response.content.strip().upper()

    if intent not in ["GREETING", "PRODUCT_INQUIRY", "HIGH_INTENT"]:
        intent = "PRODUCT_INQUIRY"

    return intent


# ── Info Extraction ────────────────────────────────────────────────────────

def extract_info(message: str, info_type: str, llm) -> Optional[str]:
    prompt = f"""Extract the {info_type} from this message.

Message: "{message}"

Rules:
- name: Return only the person's name
- email: Return only the email address
- platform: Return only the platform name (YouTube/Instagram/TikTok/Twitter/LinkedIn/Other)

If the {info_type} is NOT in the message, return: NOT_FOUND
Return ONLY the value, no explanation."""

    response = llm.invoke([HumanMessage(content=prompt)])
    result = response.content.strip()

    if result == "NOT_FOUND" or not result:
        return None
    return result


# ── Main Agent Node ────────────────────────────────────────────────────────

def agent_node(state: AgentState) -> AgentState:
    """Main logic node - runs on every user message."""

    llm = get_llm()

    last_message = state["messages"][-1]
    if not isinstance(last_message, HumanMessage):
        return state

    user_text = last_message.content
    updated_state = dict(state)

    # ── Branch 1: Lead Collection Mode ──
    if state["collecting_lead"] and not state["lead_captured"]:

        if not state["user_name"]:
            name = extract_info(user_text, "name", llm)
            if name:
                updated_state["user_name"] = name
                response_text = f"Nice to meet you, {name}! 😊 What's your email address so we can set up your account?"
            else:
                response_text = "I'd love to get you started! Could you share your name first?"

        elif not state["user_email"]:
            email = extract_info(user_text, "email", llm)
            if email and "@" in email:
                updated_state["user_email"] = email
                response_text = "Got it! And which platform do you mainly create content on? 🎬 (YouTube, Instagram, TikTok, etc.)"
            else:
                response_text = "I need a valid email address to set up your account. Could you share it?"

        elif not state["user_platform"]:
            platform = extract_info(user_text, "platform", llm)
            if platform:
                updated_state["user_platform"] = platform
                mock_lead_capture(
                    name=updated_state["user_name"],
                    email=updated_state["user_email"],
                    platform=platform,
                )
                updated_state["lead_captured"] = True
                response_text = (
                    f"🎉 You're all set, {updated_state['user_name']}!\n\n"
                    f"Our team will reach out at {updated_state['user_email']} within 24 hours.\n"
                    f"You'll get full access to AutoStream Pro — unlimited 4K videos + AI captions "
                    f"for your {platform} content!\n\n"
                    f"Is there anything else you'd like to know? 😊"
                )
            else:
                response_text = "Which platform do you create content on? (YouTube, Instagram, TikTok, etc.)"

        else:
            response_text = "Your details are all set! Our team will be in touch soon. Anything else I can help with?"

    # ── Branch 2: Normal Conversation ──
    else:
        intent = detect_intent(user_text, llm)

        if intent == "HIGH_INTENT" and not state["lead_captured"]:
            updated_state["collecting_lead"] = True
            response_text = (
                "That's exciting! I'd love to get you started with AutoStream 🚀\n\n"
                "To set up your account, may I know your name first?"
            )
        else:
            system_msg = SystemMessage(content=get_system_prompt())
            all_messages = [system_msg] + state["messages"]
            response = llm.invoke(all_messages)
            response_text = response.content

    updated_state["messages"] = state["messages"] + [AIMessage(content=response_text)]
    return updated_state


# ── Graph ──────────────────────────────────────────────────────────────────

def create_agent():
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", END)
    return workflow.compile()


def get_initial_state() -> AgentState:
    return {
        "messages": [],
        "user_name": None,
        "user_email": None,
        "user_platform": None,
        "lead_captured": False,
        "collecting_lead": False,
    }
