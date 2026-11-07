from fastapi import FastAPI

app = FastAPI()

MOCK_CONVERSATIONS = [
    {"id": 2, "title": "Planning next week", "created_at": "2026-11-07 14:02:11", "updated_at": "2026-11-07 15:40:03"},
    {"id": 1, "title": "New conversation", "created_at": "2026-11-06 09:15:40", "updated_at": "2026-11-06 09:20:12"},
]

@app.get("/api/conversations")
def get_conversations():
    return MOCK_CONVERSATIONS