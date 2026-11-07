from pathlib import Path

from Agents.AidaAgent.AidaAgent import AidaAgent
from Apps.Apps import Apps
from ContextManager.ContextManager import ContextManager
from Database.Database import Database


class Aida:
    """AIDA as one program. The CLI and the server are both ways into it."""

    def __init__(self, data_dir: Path):
        self.database = Database(data_dir / "data.db")
        self.apps = Apps(self.database)
        self.agent = AidaAgent(self.apps.tools())
        self.context_manager = ContextManager(self.database, self.apps)
        
        
    def chat(self, conversation_id: int, prompt: str) -> str:
        """One turn: build context from the database, let the agent work, save the turn, return the reply."""
        messages = self.context_manager.construct_context(conversation_id, prompt)
        new_messages = self.agent.invoke_agent(messages)

        for message_type, sender, content, summary, metadata in new_messages:
            self.context_manager.save_message(message_type, sender, conversation_id, content, summary, metadata)

        return self.final_reply(new_messages)

    @staticmethod
    def final_reply(new_messages) -> str:
        # The last thing AIDA said to you, not a tool call or a tool result.
        for message_type, sender, content, summary, metadata in reversed(new_messages):
            if message_type == "CONVERSATIONAL" and sender == "AIDA":
                return content
        return ""