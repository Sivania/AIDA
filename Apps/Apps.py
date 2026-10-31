from Apps.Planner.Planner import Planner
class Apps:
    def __init__(self, database):
        self.planner = Planner(database)

    def tools(self):
        return self.planner.tools()
    
    def context(self):
        return self.planner.get_context()