from Apps.Planner import Planner

class Apps:
    def __init__(self, database):
        self.planner = Planner(database)