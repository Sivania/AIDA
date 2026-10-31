from Apps.Planner.PlannerRepository import PlannerRepository

class Planner:
    def __init__(self, database):
        self.conversation_repository = PlannerRepository(database)
        
    def create_lane(self, name, description, position, priority, created_by):
        return self.conversation_repository.create_lane(name, description, position, priority, created_by)
    
    def update_lane(self, lane_id, updated_by, name=None, description=None, position=None, priority=None, status=None):
        return self.conversation_repository.update_lane(lane_id, updated_by, name, description, position, priority)
    
    def create_task(self, lane_id, title, description, status, created_by):
        return self.conversation_repository.create_task(lane_id, title, description, status, created_by)
    
    def update_task(self, task_id, updated_by, lane_id=None, title=None, description=None, status=None, labels=None, depends_on=None, due_date=None, done_date=None):
        return self.conversation_repository.update_task(task_id, updated_by, lane_id, title, description, status, labels, depends_on, due_date, done_date)