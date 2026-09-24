
from langchain.agents import create_agent
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

load_dotenv()

class BaseAgent:
    def add_message(self, message):
        self.messages.append(message)


    def convert_messages_to_langchain_messages(self, messages):
        converted_messages = []

        for message in messages:
            print("converting current message:", message)

            message_type = message[0]
            sender = message[1]
            content = message[2]
            metadata = message[4]

            if message_type == "TOOL_CALL":
                converted_messages.append(
                    AIMessage(
                        content=content,
                        tool_calls=metadata["tool_calls"]
                    )
                )

            elif message_type == "TOOL_RESULT":
                converted_messages.append(
                    ToolMessage(
                        name=metadata.get("tool_name"),
                        content=content,
                        tool_call_id=metadata["tool_call_id"]
                    )
                )

            elif sender == "user":
                converted_messages.append(
                    HumanMessage(content=content)
                )

            elif sender in ("assistant", "AIDA"):
                converted_messages.append(
                    AIMessage(content=content)
                )

            elif sender == "system":
                converted_messages.append(
                    SystemMessage(content=content)
                )

            else:
                raise ValueError(
                    f"Unknown message: {message}"
                )

        return converted_messages
    def convert_messages_to_list(self, messages):
        converted_messages = []

        for message in messages:
            print("message type:", type(message))
            print("message content:", message)

            if isinstance(message, HumanMessage):
                converted_messages.append([
                    "CONVERSATIONAL",
                    "user",
                    message.content,
                    None,
                    None
                ])

            elif isinstance(message, AIMessage):

                # This AI message is requesting tools
                if message.tool_calls:
                    metadata = {
                        "tool_calls": [
                            {
                                "name": tool_call["name"],
                                "args": tool_call["args"],
                                "id": tool_call["id"],
                                "type": "tool_call"
                            }
                            for tool_call in message.tool_calls
                        ]
                    }

                    converted_messages.append([
                        "TOOL_CALL",
                        "AIDA",
                        message.content,
                        None,
                        metadata
                    ])

                # Ordinary AIDA response
                elif message.content:
                    converted_messages.append([
                        "CONVERSATIONAL",
                        "AIDA",
                        message.content,
                        None,
                        None
                    ])

            elif isinstance(message, ToolMessage):
                metadata = {
                    "tool_call_id": message.tool_call_id,
                    "tool_name": message.name
                }

                converted_messages.append([
                    "TOOL_RESULT",
                    message.name or "tool",
                    message.content,
                    None,
                    metadata
                ])

            elif isinstance(message, SystemMessage):
                converted_messages.append([
                    "LOGGING",
                    "system",
                    message.content,
                    None,
                    None
                ])

            else:
                raise ValueError(
                    f"Unknown message type: {type(message)}"
                )

        return converted_messages

    def reply(self, text):
        print(self.name, "says:\n", text, "\n")
        
    def __init__(self, agent_tools, system_prompt, few_shot_examples = [], name = "Agent", iterations = 20, model = "gpt-5.4-nano"):
        self.name = name
        self.iterations = iterations
        self.messages = []

        self.agent = create_agent(
            model=model,
            tools=agent_tools,
            system_prompt=system_prompt,
        )
        
        for x in few_shot_examples:
            self.add_message(x)

    def invoke_agent(self, messages):
        converted_messages = self.convert_messages_to_langchain_messages(messages)
        messages = self.agent.invoke(
            {"messages": converted_messages},
            config={"recursion_limit": self.iterations},
        )
        new_messages = messages['messages'][len(converted_messages)-1:]
        new_messages = self.convert_messages_to_list(new_messages)
        print("new", new_messages)
        return new_messages