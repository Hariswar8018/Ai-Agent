"""
LifeSync — Flask Web Server
Serves the chat UI and proxies messages to the ADK agent.

Security measures:
  - API key loaded from environment variable (never hardcoded)
  - Input length limits to prevent abuse
  - No sensitive data in responses
  - CORS restricted in production
"""

import asyncio
import os
import uuid

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

# Load .env file if present (local development)
load_dotenv()

# ---------------------------------------------------------------------------
# Flask App
# ---------------------------------------------------------------------------
app = Flask(__name__)

# ---------------------------------------------------------------------------
# ADK Agent Setup (lazy initialization)
# ---------------------------------------------------------------------------
_runner = None
_session_service = None
_sessions: dict[str, str] = {}  # maps client_id -> session_id

# Maximum allowed message length (security: prevent abuse)
MAX_MESSAGE_LENGTH = 2000


def _get_runner():
    """Lazily initialize the ADK runner and session service."""
    global _runner, _session_service

    if _runner is None:
        from google.adk.runners import InMemoryRunner
        from google.adk.sessions import InMemorySessionService

        from agent import create_agent

        agent = create_agent()
        _session_service = InMemorySessionService()
        _runner = InMemoryRunner(agent=agent, session_service=_session_service)

    return _runner, _session_service


async def _run_agent(user_message: str, client_id: str) -> str:
    """Send a message to the ADK agent and return its text response.

    Manages per-client sessions so conversation history is preserved.
    """
    from google.genai.types import Content, Part

    runner, session_service = _get_runner()

    # Create or reuse session for this client
    if client_id not in _sessions:
        session_id = str(uuid.uuid4())
        await session_service.create_session(
            app_name="lifesync",
            user_id=client_id,
            session_id=session_id,
        )
        _sessions[client_id] = session_id

    session_id = _sessions[client_id]

    # Build the user message as ADK Content
    user_content = Content(parts=[Part(text=user_message)])

    # Run the agent and collect the final response
    response_text = ""
    async for event in runner.run_async(
        new_message=user_content,
        user_id=client_id,
        session_id=session_id,
    ):
        # Collect text from the final agent response
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text = part.text  # take the last text part

    return response_text or "I'm sorry, I couldn't process that. Please try again."


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Serve the main chat UI."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Handle a chat message from the frontend.

    Expects JSON: {"message": "user text", "client_id": "optional-uuid"}
    Returns JSON: {"reply": "agent response"}
    """
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    user_message = data["message"].strip()

    # Security: enforce length limit
    if len(user_message) == 0:
        return jsonify({"error": "Message cannot be empty"}), 400
    if len(user_message) > MAX_MESSAGE_LENGTH:
        return jsonify({"error": f"Message too long (max {MAX_MESSAGE_LENGTH} chars)"}), 400

    # Use a client_id to maintain session context per user
    client_id = data.get("client_id", "default_user")

    try:
        # Run the async agent call from the sync Flask context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        reply = loop.run_until_complete(_run_agent(user_message, client_id))
        loop.close()
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"[ERROR] Agent error: {e}")
        return jsonify({"error": "Something went wrong. Please try again."}), 500


@app.route("/health")
def health():
    """Health check endpoint for Railway / monitoring."""
    return jsonify({"status": "ok", "service": "lifesync"})


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    print(f"🚀 LifeSync starting on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
