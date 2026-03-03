# Chatbot Sandbox

A minimal AI chatbot built with **FastAPI** and the **OpenAI Python SDK**. It streams responses from OpenAI's chat completion API to a browser-based chat interface using Server-Sent Events (SSE). The project is intentionally simple and now includes a spec-driven workflow for AI-assisted development, making it a practical starting point for building and evolving AI-powered web applications safely.

## For Contributors

If you are contributing with an AI coding agent (or reviewing agent-generated work), start here:

- Read `AGENTS.md` for repository conventions, safety rules, and validation expectations.
- Use `docs/specs/0000-00-00-example-template.md` to create specs for non-trivial changes.
- Store new specs in `docs/specs/` using `YYYY-MM-DD-short-kebab-title.md` naming.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Running with Dev Containers](#running-with-dev-containers)
- [Configuration](#configuration)
- [How It Works](#how-it-works)
- [API Reference](#api-reference)
- [Changing the Model](#changing-the-model)
- [AI Agent Workflow](#ai-agent-workflow)
- [Development Notes](#development-notes)
- [Troubleshooting](#troubleshooting)

## Features

- Real-time streaming responses with a natural typing effect
- ChatGPT-style interface with left sidebar, thread history, and centered composer
- Multi-thread chat state in the browser with active-thread switching
- Frontend thread persistence via `localStorage` (no backend database)
- One-click `Clear chats` action to reset local thread history
- Async FastAPI backend for non-blocking I/O
- Dev Container support for GitHub Codespaces and VS Code
- Single-command startup with `uv`
- Spec-driven development support for AI agents via `AGENTS.md` and `docs/specs/`

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                     Browser                         │
│                                                     │
│  static/index.html                                  │
│  ┌───────────────────────────────────────────────┐  │
│  │  - Renders sidebar + thread-based chat UI     │  │
│  │  - Stores threads in localStorage             │  │
│  │  - Sends active-thread message history        │  │
│  │  - Consumes SSE stream via ReadableStream     │  │
│  │  - Token queue + render loop for smooth       │  │
│  │    typing animation (50ms interval)           │  │
│  └──────────────────┬────────────────────────────┘  │
│                     │                               │
└─────────────────────┼───────────────────────────────┘
                      │  HTTP (POST /chat, SSE response)
                      ▼
┌─────────────────────────────────────────────────────┐
│               FastAPI Backend                       │
│                                                     │
│  app/main.py                                        │
│  ┌───────────────────────────────────────────────┐  │
│  │  - POST /chat: accepts messages, streams      │  │
│  │    response as SSE (text/event-stream)         │  │
│  │  - GET /health: returns { "status": "ok" }    │  │
│  │  - Static file mount: serves index.html       │  │
│  │  - Prepends system prompt to every request    │  │
│  └──────────────────┬────────────────────────────┘  │
│                     │                               │
└─────────────────────┼───────────────────────────────┘
                      │  HTTPS (OpenAI API, streaming)
                      ▼
┌─────────────────────────────────────────────────────┐
│              OpenAI API                             │
│                                                     │
│  - Model: gpt-5-mini (configurable)                │
│  - Chat Completions endpoint                        │
│  - Streaming enabled                                │
└─────────────────────────────────────────────────────┘
```

**Request flow:**

1. User types a message in the browser and clicks Send (or presses Enter).
2. The frontend sends a `POST /chat` request with the active thread's full message history as JSON.
3. FastAPI prepends a system prompt and forwards the messages to OpenAI's Chat Completions API with `stream=True`.
4. As tokens arrive from OpenAI, the backend emits them as SSE events (`data: <token>\n\n`).
5. The frontend reads the stream using the `ReadableStream` API, queues tokens, and renders them at 50ms intervals for a smooth typing effect.
6. When the stream ends, the backend sends `data: [DONE]\n\n` and the frontend finalizes the message.

**Key design decisions:**

- **`AsyncOpenAI`** is used instead of the synchronous client so streaming does not block the FastAPI event loop.
- **No backend database** -- conversation threads are stored client-side in browser `localStorage`.
- **No authentication** -- this is a local development sandbox, not a production service.
- **No build tooling** -- the frontend is a single HTML file with inline CSS and JS, served as a static file.

## Project Structure

```
chatbot-sandbox/
├── .devcontainer/
│   ├── devcontainer.json      # Dev Container config (Codespaces / VS Code)
│   └── Dockerfile             # Python 3.12-slim + uv
├── designs/
│   ├── chatbot_design_1.png   # UI reference image
│   └── chatbot_design_2.png   # UI reference image
├── docs/
│   └── specs/
│       ├── 0000-00-00-example-template.md  # Spec template for non-trivial changes
│       └── 2026-03-03-chat-ui-sidebar-redesign.md  # UI redesign spec
├── app/
│   ├── __init__.py            # Makes app/ a Python package
│   └── main.py                # FastAPI application (endpoints, streaming, static mount)
├── static/
│   └── index.html             # Chat UI (HTML + CSS + JS, zero dependencies)
├── AGENTS.md                  # Working guide for AI coding agents in this repo
├── .env.example               # Template for environment variables
├── .gitignore                 # Ignores .env, .venv/, __pycache__/, IDE files
├── pyproject.toml             # Project metadata and dependencies
├── uv.lock                    # Lockfile for reproducible installs
└── README.md                  # This file
```

| File | Purpose |
|---|---|
| `app/main.py` | The entire backend -- FastAPI app with chat endpoint, health check, and static file serving |
| `static/index.html` | The entire frontend -- self-contained chat interface with no external dependencies |
| `AGENTS.md` | Repository rules for AI agents (workflow, safety, validation, and spec requirements) |
| `docs/specs/` | Spec files for non-trivial changes (feature work, behavior changes, risky refactors) |
| `pyproject.toml` | Declares Python version (>=3.12) and three dependencies |
| `.devcontainer/` | Enables one-click setup in GitHub Codespaces or VS Code Dev Containers |

## Prerequisites

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** -- a fast Python package manager from Astral. Install it with:
  ```bash
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Windows
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **An OpenAI API key** -- get one at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone git@github.com:nhat416/chatbot-sandbox.git
   cd chatbot-sandbox
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Open `.env` and replace the placeholder with your actual OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. **Install dependencies:**
   ```bash
   uv sync
   ```
   This creates a `.venv/` virtual environment and installs all dependencies from the lockfile.

4. **Start the development server:**
   ```bash
   uv run fastapi dev app/main.py
   ```
   The server starts at **http://localhost:8000**. Open that URL in your browser to use the chatbot.

   > `fastapi dev` enables auto-reload -- the server restarts automatically when you edit source files.

## Running with Dev Containers

This project includes a Dev Container configuration for **GitHub Codespaces** and **VS Code Remote - Containers**.

**GitHub Codespaces:**
1. Navigate to the repository on GitHub.
2. Click **Code > Codespaces > Create codespace on main**.
3. The container builds automatically, runs `uv sync`, and forwards port 8000.
4. Add your `OPENAI_API_KEY` as a Codespaces secret or in the terminal's `.env` file.

**VS Code:**
1. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).
2. Open the project folder and click **Reopen in Container** when prompted.
3. Dependencies install automatically via the post-create command.

The Dev Container uses `python:3.12-slim` as its base image, installs key CLI tools, and pre-configures the Python and Pylance VS Code extensions.

**Key tools available inside the Dev Container:**

- `opencode` - AI coding agent CLI installed in `/root/.opencode/bin`
- `python` - Python 3.12 runtime
- `uv` - fast Python package/project manager (`uv sync`, `uv run ...`)
- `fastapi` - app dev server CLI (available via environment)
- `git` - source control tooling (via Dev Container feature)

Quick sanity check after container startup:

```bash
opencode --version
python --version
uv --version
git --version
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key. The `AsyncOpenAI` client reads this automatically from the environment. |

The `.env` file is loaded at startup by `python-dotenv` and is excluded from version control via `.gitignore`.

### Dependencies

| Package | Version | Purpose |
|---|---|---|
| `fastapi[standard]` | >=0.115.0 | Web framework with Uvicorn, httpx, Jinja2, and other standard extras |
| `openai` | >=1.50.0 | Official OpenAI Python SDK (async support, streaming) |
| `python-dotenv` | >=1.0.0 | Loads `.env` files into `os.environ` |

## How It Works

### Backend (`app/main.py`)

The backend is a single-file FastAPI application with three routes:

- **`POST /chat`** -- Receives a JSON body with a `messages` array (OpenAI chat format), prepends a system prompt, calls the OpenAI Chat Completions API with streaming enabled, and returns the response as a Server-Sent Events stream.

- **`GET /health`** -- Returns `{ "status": "ok" }`. Useful for health checks and verifying the server is running.

- **`GET /*` (static mount)** -- Serves all files in the `static/` directory. The root URL (`/`) serves `static/index.html`.

The streaming implementation:
1. An async generator (`stream_response`) iterates over chunks from OpenAI.
2. Each chunk's text delta is emitted as `data: <token>\n\n`.
3. After all chunks, `data: [DONE]\n\n` signals the end of the stream.
4. FastAPI's `StreamingResponse` sends these events with `text/event-stream` content type.
5. Anti-buffering headers (`Cache-Control: no-cache`, `X-Accel-Buffering: no`) ensure tokens are delivered immediately, even behind reverse proxies.

### Frontend (`static/index.html`)

The frontend is a self-contained HTML file with inline CSS and JavaScript -- no frameworks, no build step, no external dependencies.

**Key behaviors:**

- **Thread-based chat UI** includes a left sidebar with chat threads, new chat action, and active-thread highlighting.
- **Conversation context** is maintained per thread. The active thread's full history is sent with each request so the model has context.
- **Persistence** uses browser `localStorage` to retain threads/messages across page refreshes on the same browser.
- **History reset** includes a `Clear chats` sidebar action that removes local thread history for the current browser origin.
- **Streaming display** uses a token queue architecture: the network reader fills a queue as tokens arrive, and a separate render loop drains the queue at 50ms intervals. This creates a smooth, readable typing animation regardless of network speed.
- **Keyboard shortcuts**: Enter sends the message, Shift+Enter inserts a newline, and input auto-resizes as you type.
- **Responsive layout**: Sidebar becomes off-canvas on smaller screens with a mobile toggle.
- **Error handling**: If the server is unreachable, an error message is displayed in the chat.

## API Reference

### `POST /chat`

Send a chat message and receive a streaming response.

**Request:**
```json
{
  "messages": [
    { "role": "user", "content": "Hello, how are you?" },
    { "role": "assistant", "content": "I'm doing well! How can I help you?" },
    { "role": "user", "content": "Tell me about Python." }
  ]
}
```

**Response:** `text/event-stream` (SSE)
```
data: Python

data:  is

data:  a

data:  versatile

data:  programming

data:  language

data: [DONE]
```

### `GET /health`

**Response:**
```json
{ "status": "ok" }
```

## Changing the Model

The model is set in `app/main.py` inside the `stream_response` function. To change it, edit the `model` parameter:

```python
response = await client.chat.completions.create(
    model="gpt-5-mini",  # Change this to your preferred model
    messages=all_messages,
    stream=True,
)
```

Available options (as noted in the source):
- `gpt-4o-mini` -- fast, cost-effective
- `gpt-4.1` -- high capability
- `gpt-5-nano` -- lightweight, fast option
- `gpt-5-mini` -- current default, balanced performance

Refer to [OpenAI's model documentation](https://platform.openai.com/docs/models) for the latest available models and pricing.

## AI Agent Workflow

This repository includes an agent operating guide in `AGENTS.md` and uses spec-driven development for non-trivial work.

**What this means in practice:**

- AI agents should treat specs as the source of truth for behavior changes.
- Non-trivial updates (new features, behavior changes, risky refactors) should start with a spec in `docs/specs/`.
- Spec file naming convention: `YYYY-MM-DD-short-kebab-title.md`.
- Trivial edits (small typo/docs fixes, obvious one-line fixes) can skip a full spec.

**Recommended flow:**

1. Read `AGENTS.md` before making changes.
2. Create or update a spec in `docs/specs/` if the change is non-trivial.
3. Implement in small steps mapped to acceptance criteria.
4. Run validation commands and perform manual checks.
5. Keep docs and `AGENTS.md` updated when workflow or conventions change.

## Development Notes

- **Auto-reload**: `fastapi dev` watches for file changes and restarts the server automatically. No need to manually restart during development.
- **No backend persistence**: There is no server-side database. Chat threads are persisted only in each browser's local storage.
- **No authentication**: All endpoints are open. Do not deploy this to the public internet without adding proper access controls.
- **Linting**: The `.ruff_cache/` directory in `.gitignore` indicates [Ruff](https://docs.astral.sh/ruff/) can be used for linting and formatting. Run it with:
  ```bash
  uv run ruff check .
  uv run ruff format .
  ```
- **Agent guidance**: See `AGENTS.md` for coding conventions, safety rules, and PR expectations when using AI coding agents.

## Troubleshooting

| Problem | Solution |
|---|---|
| `OPENAI_API_KEY not set` or `AuthenticationError` | Ensure your `.env` file exists with a valid API key. Run `cp .env.example .env` and add your key. |
| `ModuleNotFoundError` | Run `uv sync` to install dependencies. |
| `uv: command not found` | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Server starts but chat returns errors | Check that your OpenAI API key has available credits and that the selected model is accessible on your account. |
| Port 8000 already in use | Stop the other process or run with a different port: `uv run fastapi dev app/main.py --port 8001` |
| Tokens appear choppy or delayed | This may occur behind certain reverse proxies that buffer SSE streams. The `X-Accel-Buffering: no` header handles Nginx; other proxies may need similar configuration. |
| Need to reset old chat threads | Use the sidebar `Clear chats` action. If needed, manually delete `chatbot_sandbox_threads_v1` in browser DevTools under Application/Storage -> Local Storage for your app origin, then refresh. |

## License

This project is provided as a learning sandbox. See the repository for license details.
