
from langchain.agents import create_agent
from dotenv import load_dotenv
load_dotenv()

class BaseAgent:

    def web_search(self, query: str) -> str:
        """Perform a web search for a given query."""
        return f"Results for '{query}'"
    
    def add_message(self, message):
        self.messages.append(message)

    def reply(self, text):
        print(self.name, "says:\n", text, "\n")
        
    def get_response(self):
        pass
    
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
        result = self.agent.invoke(
            {"messages": self.messages},
            config={"recursion_limit": self.iterations},
        )
        self.messages = result["messages"]
        return self.messages[-1].content