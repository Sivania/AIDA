class ContextBuilder:
    def __init__(self):
        pass
    def build_context_window_with_new_prompt(self, messages, prompt):
        print(messages)
        # Add the new prompt as a message from the user
        messages.append(("CONVERSATIONAL", "user", prompt, None, None))
        
        #TODO: Implement context window optimization logic here
        return messages
    