from dotenv import load_dotenv
import os
from langchain_core.messages import HumanMessage, AIMessage
from agent import create_agent, get_initial_state

load_dotenv()  # .env se API key load karo


def get_last_ai_response(state: dict) -> str:
    for msg in reversed(state["messages"]):
        if isinstance(msg, AIMessage):
            return msg.content
    return "Sorry, I couldn't generate a response."


def chat():
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY not found!")
        return

    print("\n" + "=" * 60)
    print("  🎬  AutoStream AI Sales Assistant")
    print("  Powered by Claude Haiku + LangGraph + RAG")
    print("=" * 60)
    print("  Commands: 'quit' to exit | 'reset' to start over")
    print("=" * 60 + "\n")

    agent = create_agent()
    state = get_initial_state()

    print("🤖 AutoStream Assistant: Hi! Welcome to AutoStream! 🎬")
    print("   I help content creators save 80% of their editing time.")
    print("   Ask me about pricing, features, or getting started!\n")

    while True:
        try:
            user_input = input("👤 You: ").strip()
        except KeyboardInterrupt:
            print("\n\n👋 Thanks for your interest in AutoStream. Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ["quit", "exit", "bye"]:
            print("\n🤖 AutoStream Assistant: Thanks for chatting! Have a great day! 👋")
            break

        if user_input.lower() == "reset":
            state = get_initial_state()
            print("\n🔄 Conversation reset!\n")
            print("🤖 AutoStream Assistant: Hi again! How can I help you? 😊\n")
            continue

        # User message state mein add karo
        state["messages"].append(HumanMessage(content=user_input))

        print("\n🤖 AutoStream Assistant: ", end="", flush=True)

        try:
            new_state = agent.invoke(state)
            response = get_last_ai_response(new_state)
            print(response)
            print()
            state = new_state

        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            # Rollback last message
            state["messages"] = state["messages"][:-1]


if __name__ == "__main__":
    chat()
