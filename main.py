from Agents.AidaAgent.AidaAgent import AidaAgent
agent = AidaAgent()

while True:
    user_input = input("User: ")
    print("AIDA: ", agent.invoke_agent(user_input) + "\n")