class ConversationRepository:
    def __init__(self, database):
        self.database = database
        self._initialize_tables()

    def _initialize_tables(self):
        self.database.execute_write("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL DEFAULT 'New conversation',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.database.execute_write("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL DEFAULT 'CONVERSATIONAL',
                sender TEXT NOT NULL DEFAULT 'user',
                conversation_id INTEGER,
                content TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        """)

    def get_conversations(self):
        return self.database.execute_read("""
            SELECT *
            FROM conversations
            ORDER BY updated_at DESC
        """)
        
    def get_conversation_messages(self, conversation_id):
        return self.database.execute_read("""
            SELECT *
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
        """, (conversation_id,))

    def create_conversation(self, title: str = "New conversation"):
        return self.database.execute_write("""INSERT INTO conversations (title)VALUES (?)""", (title,))
    
    def create_message(self, type, sender, conversation_id: int, content: str):
        self.database.execute_write("""
            INSERT INTO messages (type, sender, conversation_id, content)
            VALUES (?, ?, ?, ?)
        """, (type, sender, conversation_id, content))