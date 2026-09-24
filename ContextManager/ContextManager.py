from ContextManager.ContextBuilder import ContextBuilder
from ContextManager.ConversationRepository import ConversationRepository

class ContextManager:
    def __init__(self, database):
        self.conversation_repository = ConversationRepository(database)
        self.context_builder = ContextBuilder()
    def get_conversations(self):
        return self.conversation_repository.get_conversations()
    
    def create_conversation(self, title: str = "New conversation"):
        return self.conversation_repository.create_conversation(title)
    
    def load_conversation(self, conversation_id):
        return self.conversation_repository.get_conversation_messages(conversation_id)
    
    def construct_context(self, conversation_id, prompt):
        messages = self.load_conversation(conversation_id)
        messages = [
            (
                message["type"],
                message["sender"],
                message["content"],
                None
            )
            for message in messages
        ]
        messages = self.context_builder.build_context_window_with_new_prompt(messages, prompt)
        return messages
    
    def save_message(self, type, sender, conversation_id, content):
        self.conversation_repository.create_message(type, sender, conversation_id, content)