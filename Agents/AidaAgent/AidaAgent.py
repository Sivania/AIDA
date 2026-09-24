from Agents.BaseAgent import BaseAgent
from . system_message import system_message
from . few_shot_examples import few_shot_examples

class AidaAgent(BaseAgent):
    def web_search(self, query: str) -> str:
        """Perform a web search for a given query."""
        return "Not inplemented yet"
    
    def get_AIDA_files(self, query: str, read_file: bool = False) -> str:
        """AI Native: Freely get AIDA implementation files of choice by file path.
        Args:
            query (str): Look at files in query, start with "./".
            read_file (bool): If single file is chosen, set true to read the contents of the file.
        """
        return "Not inplemented yet"
    
    def __init__(self):
        super().__init__(
            agent_tools=[self.web_search, self.get_AIDA_files],
            system_prompt=system_message,
            few_shot_examples=few_shot_examples,
        )