import logging
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from Aida import Aida

aida = Aida(Path(os.environ["AIDA_DATA_DIR"]))
app = FastAPI()
logger = logging.getLogger("uvicorn.error")


class NewConversation(BaseModel):
    title: str = "New conversation"


class ChatRequest(BaseModel):
    conversation_id: int
    message: str = Field(min_length=1)


class ChatReply(BaseModel):
    reply: str


@app.get("/api/conversations")
def get_conversations():
    return aida.context_manager.get_conversations()


@app.post("/api/conversations", status_code=201)
def create_conversation(body: NewConversation):
    conversation_id = aida.context_manager.create_conversation(body.title)
    return aida.context_manager.get_conversation(conversation_id)


@app.post("/api/chat")
def chat(body: ChatRequest) -> ChatReply:
    if aida.context_manager.get_conversation(body.conversation_id) is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    try:
        reply = aida.chat(body.conversation_id, body.message)
    except Exception as error:
        # Nothing was saved: the turn is only saved after the agent has answered.
        logger.exception("Turn failed in conversation %s", body.conversation_id)
        raise HTTPException(status_code=502, detail=f"AIDA could not answer ({type(error).__name__}).") from error

    return ChatReply(reply=reply)

@app.get("/api/conversations/{conversation_id}/messages")
def get_messages(conversation_id: int):
    if aida.context_manager.get_conversation(conversation_id) is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    # Only what you and AIDA said to each other. Tool calls, tool results and
    # app context stay on the server: they're AIDA's working memory, not the chat.
    return [
        {
            "id": message["id"],
            "role": "user" if message["sender"] == "user" else "assistant",
            "content": message["content"],
            "created_at": message["created_at"],
        }
        for message in aida.context_manager.load_conversation(conversation_id)
        if message["type"] == "CONVERSATIONAL" and message["sender"] in ("user", "AIDA")
    ]