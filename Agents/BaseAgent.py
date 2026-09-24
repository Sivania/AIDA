
from langchain.agents import create_agent
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()

class BaseAgent:
    def add_message(self, message):
        self.messages.append(message)


    def convert_messages(self, messages):
        converted_messages = []
        for message in messages:
            if message[1] == "user":
                converted_messages.append(HumanMessage(content=message[2]))
            elif message[1] == "assistant" or message[1] == "AIDA":
                converted_messages.append(AIMessage(content=message[2]))
            elif message[1] == "system":
                converted_messages.append(SystemMessage(content=message[2]))
            else:
                raise ValueError(f"Unknown message sender: {message[1]}")
        return converted_messages

    def reply(self, text):
        print(self.name, "says:\n", text, "\n")
        
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

    def invoke_agent(self, messages):
        converted_messages = self.convert_messages(messages)
        messages = self.agent.invoke(
            {"messages": converted_messages},
            config={"recursion_limit": self.iterations},
        )
        print("Agent invoked with messages:", messages)
        return messages