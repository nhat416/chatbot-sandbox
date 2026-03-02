"""
Chatbot Sandbox - A simple AI chatbot built with FastAPI and OpenAI.

This is the entire backend. It does three things:
1. Serves a static HTML page (the chat UI)
2. Accepts chat messages via a POST endpoint
3. Streams responses from OpenAI back to the browser
"""

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the async OpenAI client (reads OPENAI_API_KEY from env automatically)
# IMPORTANT: We use AsyncOpenAI so streaming doesn't block the event loop.
# The synchronous OpenAI() client would freeze the server until the full
# response is generated, defeating the purpose of streaming.
client = AsyncOpenAI()

# Create the FastAPI app
app = FastAPI(title="Chatbot Sandbox")

# --------------------------------------------------------------------------- #
#  Chat endpoint - this is where the magic happens
# --------------------------------------------------------------------------- #


@app.post("/chat")
async def chat(request: Request):
    """
    Accepts a JSON body like:
        { "messages": [ {"role": "user", "content": "Hello!"} ] }

    Streams the assistant's response back as plain text using
    Server-Sent Events (SSE) so the UI can display tokens as they arrive.
    """
    body = await request.json()
    messages = body.get("messages", [])

    # Prepend a system message to set the chatbot's personality
    system_message = {
        "role": "system",
        "content": (
            "You are a helpful, friendly AI assistant. "
            "Keep your answers concise and conversational."
        ),
    }

    async def generate():
        """Stream tokens from OpenAI as Server-Sent Events."""
        stream = await client.chat.completions.create(
            model="gpt-5-mini", # gpt-4o-mini, gpt-4.1, gpt-5-nano, gpt-5-mini
            messages=[system_message] + messages,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                # SSE format: each message is "data: <text>\n\n"
                yield f"data: {delta.content}\n\n"
        # Signal the end of the stream
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            # Prevent any buffering that would batch chunks together
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disables buffering in nginx proxies
        },
    )


# --------------------------------------------------------------------------- #
#  Health check
# --------------------------------------------------------------------------- #


@app.get("/health")
async def health():
    return {"status": "ok"}


# --------------------------------------------------------------------------- #
#  Serve the static frontend (index.html)
# --------------------------------------------------------------------------- #

# Mount static files LAST so it doesn't shadow API routes
app.mount("/", StaticFiles(directory="static", html=True), name="static")
