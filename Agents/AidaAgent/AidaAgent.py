from Agents.BaseAgent import BaseAgent
from . import system_message
from langchain.agents import create_agent

class AidaAgent(BaseAgent):
    
    def get_weather(self, city: str) -> str:
        """Get weather for a given city."""
        return f"It's always sunny in {city}!"
    
    def __init__(self):
        super().__init__(
            agent_tools=[self.get_weather],
            system_prompt=system_message.system_message
        )