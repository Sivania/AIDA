from Agents.AidaAgent.AidaAgent import AidaAgent
from Database import Database

database = Database.Database("database.db")
agent = AidaAgent()


while True:
    user_input = input("User: ")
    print("AIDA: ", agent.invoke_agent(user_input))