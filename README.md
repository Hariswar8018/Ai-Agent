# LifeSync — Personal AI Concierge Agent

> A beautiful, minimal AI concierge agent powered by **Google ADK** and **Gemini**, served via **Flask**, and ready to deploy on **Railway**.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.1-green)
![Google ADK](https://img.shields.io/badge/Google_ADK-Agent-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 Problem Statement

Managing everyday micro-tasks — checking the time across timezones, doing quick calculations, tracking weather, or jotting down notes — often involves opening multiple apps. **LifeSync** consolidates these into a single, beautiful chat interface powered by an AI agent that understands natural language and uses tools to help you.

## 💡 Solution

LifeSync is a **personal concierge AI agent** built with:

- **Google ADK (Agent Development Kit)** for agent orchestration and tool calling
- **Google Gemini 2.5 Flash** as the underlying LLM
- **Flask** for the web server
- A **stunning dark-mode chat UI** with glassmorphism design

The agent has 5 tools it can call based on your request:

| Tool | Description |
|------|-------------|
| `get_current_datetime` | Get current date/time in any timezone |
| `calculate` | Safely evaluate math expressions |
| `get_weather` | Check weather for any city (simulated) |
| `take_note` | Save a note for later |
| `get_notes` | Retrieve all saved notes |

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│                  Browser                      │
│  ┌──────────────────────────────────────┐    │
│  │     Beautiful Chat UI (HTML/CSS/JS)  │    │
│  └────────────────┬─────────────────────┘    │
│                   │ POST /chat                │
└───────────────────┼──────────────────────────┘
                    │
┌───────────────────▼──────────────────────────┐
│              Flask Server (app.py)            │
│  ┌──────────────────────────────────────┐    │
│  │  Input Validation & Security Layer   │    │
│  └────────────────┬─────────────────────┘    │
│                   │                           │
│  ┌────────────────▼─────────────────────┐    │
│  │   Google ADK InMemoryRunner          │    │
│  │   + InMemorySessionService           │    │
│  └────────────────┬─────────────────────┘    │
│                   │                           │
│  ┌────────────────▼─────────────────────┐    │
│  │   LifeSync Agent (agent.py)          │    │
│  │   Model: gemini-2.5-flash            │    │
│  │   Tools: datetime, calc, weather,    │    │
│  │          take_note, get_notes        │    │
│  └──────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

## 🔒 Security Features

- **No hardcoded API keys** — all secrets loaded from environment variables
- **Input validation** — message length limits (2000 chars max)
- **Safe math evaluation** — calculator uses allowlisted functions only
- **No sensitive data in responses** — agent instructions prevent data leakage
- `.env` file excluded from git via `.gitignore`

## 📋 Key Concepts Demonstrated

| Concept | Where |
|---------|-------|
| Agent / Multi-agent system (ADK) | `agent.py` — Google ADK Agent with 5 tools |
| Deployability | `Dockerfile`, `Procfile`, `railway.json` |
| Security features | Environment variables, input sanitization, safe eval |

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.10+
- A [Google Gemini API key](https://aistudio.google.com)

### Local Development

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/lifesync-agent.git
cd lifesync-agent

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 5. Run the app
python app.py
```

Then open **http://localhost:5000** in your browser.

### Deploy to Railway

1. Push code to a GitHub repository
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**
3. Select your repo
4. Add environment variable: `GOOGLE_API_KEY` = your key
5. Railway will auto-detect the `Dockerfile` and deploy

Your app will be live at the Railway-provided URL.

## 📁 Project Structure

```
ai_agent/
├── app.py              # Flask server + ADK integration
├── agent.py            # ADK Agent definition + tools
├── requirements.txt    # Python dependencies
├── Procfile            # Railway/Heroku process file
├── Dockerfile          # Container deployment
├── railway.json        # Railway configuration
├── .env.example        # Example environment variables
├── .gitignore          # Git ignore rules
├── README.md           # This file
├── static/
│   ├── style.css       # Dark-mode glassmorphism UI
│   └── script.js       # Chat frontend logic
└── templates/
    └── index.html      # Main chat page
```

## 🎨 Tech Stack

- **Backend:** Python, Flask, Google ADK, Gemini 2.5 Flash
- **Frontend:** HTML5, CSS3 (custom dark theme), Vanilla JavaScript
- **Deployment:** Docker, Gunicorn, Railway
- **Design:** Glassmorphism, Inter font, gradient accents, micro-animations

## 📝 License

MIT License — feel free to use, modify, and share.

---

*Built for the Kaggle AI Agents: Intensive Vibe Coding Capstone Project 2026*
