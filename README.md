# AutoStream AI Sales Agent

> A conversational AI agent that handles product queries, detects high-intent users,
> and captures leads — built with **LangGraph + Claude Haiku + RAG**.

Built as part of the ServiceHive × Inflx Machine Learning Internship Assignment.



---

##  Features

- **Intent Detection** — Classifies user messages (Greeting / Product Inquiry / High Intent)
-  **RAG Pipeline** — Answers questions from a local knowledge base (no hallucinations)
-  **Lead Capture** — Collects name, email, platform when user shows buying intent
-  **State Management** — Remembers full conversation context across 5–6 turns
-  **Safe Tool Calling** — Lead capture only triggers after all 3 details collected

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Groq (`Llama 3`) |
| Agent Framework | LangGraph (StateGraph) |
| RAG | Local Markdown + System Prompt Injection |
| Language | Python 3.9+ |
| API | Groq API |

---

## How to Run Locally

### Prerequisites
- Python 3.9+
- Groq API key → [Get here](https://console.groq.com)

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/soaebhasan12/autostream-agent
cd autostream-agent

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file with your API key
echo "GROQ_API_KEY=your_key_here" > .env

# 5. Run the agent
python main.py
```

### Sample Conversation
```
You: Hi there!
 Hi! Welcome to AutoStream! Ask me about pricing or features.

You: What's included in the Pro plan?
 The Pro Plan ($79/month) includes unlimited 4K videos, AI captions,
   24/7 support, and custom branding...

You: That's perfect! I want to sign up for my YouTube channel
 Exciting! May I know your name first?

You: Rahul Sharma
 Nice to meet you, Rahul! What's your email address?

You: rahul@gmail.com
 Got it! Which platform do you mainly create on?

You: YouTube
 You're all set, Rahul! [LEAD CAPTURED in terminal]
```

---

## Architecture (~200 words)

### Why LangGraph?

LangGraph was chosen because our agent requires **explicit, typed state management** across multiple conversation turns. Unlike simple conversation loops, LangGraph's `StateGraph` makes state transitions predictable and debuggable. We need to track whether we're in lead-collection mode, what details have been collected so far, and maintain full conversation history — all simultaneously.

### State Management

The `AgentState` TypedDict maintains:
- `messages` — Full conversation history (Human + AI messages)
- `user_name`, `user_email`, `user_platform` — Progressive lead data (None until collected)
- `collecting_lead` — Boolean flag: are we in lead collection mode?
- `lead_captured` — Boolean flag: prevents duplicate submissions

Each `agent.invoke()` call receives the current state and returns an updated state, ensuring no context is lost between turns.

### RAG Pipeline

Product knowledge is stored in `knowledge/autostream.md`. At runtime, this file is loaded and injected directly into the LLM's system prompt. This **simple RAG** approach grounds all responses in accurate company data — the LLM cannot hallucinate pricing or policies.

### Intent Detection

LLM-based classification (GREETING / PRODUCT_INQUIRY / HIGH_INTENT) enables dynamic mode switching: casual reply, RAG-powered answer, or lead collection flow.

---

## 📱 WhatsApp Integration via Webhooks

```
User (WhatsApp) → Meta Servers → Your Webhook → Agent → WhatsApp Reply
```

**Implementation Steps:**

1. **Register** on Meta for Developers → Get WhatsApp Business API access
2. **Deploy** a Flask/FastAPI server with HTTPS (required by Meta)
3. **Configure** webhook URL in Meta Developer Dashboard
4. **Setup Redis** for session state persistence (phone number = session key)

```python
# Example webhook handler (Flask)
from flask import Flask, request
import redis, json
from langchain_core.messages import HumanMessage

app = Flask(__name__)
r = redis.Redis()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    phone = data['from']           # Session ID
    message = data['text']['body'] # User message

    # Load state from Redis
    state_json = r.get(f"state:{phone}")
    state = json.loads(state_json) if state_json else get_initial_state()

    # Process with agent
    state['messages'].append(HumanMessage(content=message))
    new_state = agent.invoke(state)

    # Save updated state (1 hour TTL)
    r.setex(f"state:{phone}", 3600, json.dumps(new_state, default=str))

    # Reply to WhatsApp
    reply = get_last_ai_response(new_state)
    send_whatsapp_message(phone, reply)

    return {"status": "ok"}, 200
```

---

## Project Structure

```
autostream-agent/
├── main.py              # Entry point - conversation loop
├── agent.py             # LangGraph agent + intent + extraction
├── knowledge_base.py    # RAG pipeline
├── tools.py             # Lead capture tool
├── knowledge/
│   └── autostream.md    # Company knowledge base
├── requirements.txt
├── .env                 # API key (not committed)
├── .gitignore
└── README.md
```

---

## Evaluation Criteria Checklist

- [x] Agent reasoning & intent detection (LLM-based classification)
- [x] Correct use of RAG (knowledge base → system prompt injection)
- [x] Clean state management (LangGraph StateGraph + TypedDict)
- [x] Proper tool calling logic (only after all 3 details collected)
- [x] Code clarity & structure (modular files, documented functions)
- [x] Real-world deployability (WhatsApp webhook design in README)

---

*Built with ❤️*
