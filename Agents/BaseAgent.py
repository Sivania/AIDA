
from langchain.agents import create_agent
from dotenv import load_dotenv
load_dotenv()
from Database import Database
database = Database.Database("database.db")

class BaseAgent:
    def add_message(self, message):
        self.messages.append(message)

    def reply(self, text):
        print(self.name, "says:\n", text, "\n")
    
    def execute_sql_query(self, query: str) -> str:
        """Execute a SQL query on the SQLite database."""
        print(f"Executing SQL query: {query}")
        try:
            if query.strip().lower().startswith(("select", "PRAGMA")):
                rows = database.execute_read(query)
                return "\n".join([str(row) for row in rows])
            if query.strip().lower().startswith(("insert", "update", "delete", "create", "alter")):
                database.execute_write(query)
                return "Query executed successfully."
            return "Query must start with SELECT, PRAGMA, INSERT, UPDATE, CREATE or ALTER."
        except Exception as e:
            return f"An error occurred while executing the query: {str(e)}"
        
    def __init__(self, agent_tools, system_prompt, few_shot_examples = [], name = "Agent", iterations = 20, model = "gpt-5.4-nano"):
        self.name = name
        self.iterations = iterations
        self.messages = []

        self.agent = create_agent(
            model=model,
            tools=[self.web_search] + agent_tools,
            system_prompt=system_prompt,
        )      
        
        for x in few_shot_examples:
            self.add_message(x)


    def invoke_agent(self, input):
        self.add_message({"role": "user", "content": input})
        print("message length: ", len(self.messages))
        result = self.agent.invoke(
            {"messages": self.messages},
            config={"recursion_limit": self.iterations},
        )
        self.messages = result["messages"]
        print("message length: ", len(self.messages))
        return self.messages[-1].content