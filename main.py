from Agents.AidaAgent.AidaAgent import AidaAgent
from ContextManager.ContextManager import ContextManager
from Database.Database import Database

agent = AidaAgent()
class CLI:
    def __init__(self):
        self.running = True
        self.database = Database("database.db")
        self.context_manager = ContextManager(self.database)
        self.current_conversation_id = None
        self.user_input = None
        
    def start(self):
        self.load_conversations()
        print("Welcome to the AIDA CLI! Type 'exit' to quit.")
        self.user_input = input("Enter id of conversation to load or -1 to start a new conversation \n User: ")
        if self.user_input == "exit":
            pass
        elif self.user_input == "-1":
            self.current_conversation_id = self.context_manager.create_conversation()
        else:
            self.current_conversation_id = self.user_input
            self.load_conversation()
                
        while self.running:
            self.user_input = input("You: ")

            if self.user_input == "exit":
                self.running = False
            else:
                messages = self.context_manager.construct_context(self.current_conversation_id, self.user_input)
                response = agent.invoke_agent(messages)
                print("AIDA response: ", response)
                for message in response:
                    type, sender, content, summary, metadata = message

                    print("saving message:", message)

                    self.context_manager.save_message(
                        type,
                        sender,
                        self.current_conversation_id,
                        content,
                        summary,
                        metadata
                    )
                    
    
    def load_conversations(self):
        conversations = self.context_manager.get_conversations()
        if not conversations:
            return print("No conversations found.")
        for conversation in conversations:
            print(f"ID: {conversation['id']}, Title: {conversation['title']}, Created At: {conversation['created_at']}, Updated At: {conversation['updated_at']}")
    
    def load_conversation(self):
        messages = self.context_manager.load_conversation(self.current_conversation_id)
        if not messages:
            return print("No messages found in this conversation.")
        for message in messages:
            print(f"{message['sender']}: {message['content']}")

    def create_conversation(self):
        title = input("Enter a title for the new conversation: ")
        self.context_manager.create_conversation(title)
        print(f"Conversation '{title}' created.")
        
cli = CLI()
cli.start()