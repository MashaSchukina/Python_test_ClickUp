import os
import requests
from dotenv import load_dotenv

load_dotenv()

class ClickUpAPI:
    def __init__(self):
        self.base_url = os.getenv("BASE_URL")
        self.token = os.getenv("CLICKUP_TOKEN")
        self.team_id = os.getenv("TEAM_ID")
        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }

    # CREATE GOAL
    def create_goal(self, payload, headers=None):
        url = f"{self.base_url}/team/{self.team_id}/goal"
        auth_header = headers if headers is not None else self.headers
        return requests.post(url, json=payload, headers=auth_header)

    # GET GOALS (ALL)
    def get_goals(self, headers=None):
        url = f"{self.base_url}/team/{self.team_id}/goal"
        auth_header = headers if headers is not None else self.headers
        return requests.get(url, headers=auth_header)

    # GET GOAL (SINGLE)
    def get_goal(self, goal_id, headers=None):
        url = f"{self.base_url}/goal/{goal_id}"
        auth_header = headers if headers is not None else self.headers
        return requests.get(url, headers=auth_header)

    # UPDATE GOAL
    def update_goal(self, goal_id, payload, headers=None):
        url = f"{self.base_url}/goal/{goal_id}"
        auth_header = headers if headers is not None else self.headers
        return requests.put(url, json=payload, headers=auth_header)

    # DELETE GOAL
    def delete_goal(self, goal_id, headers=None):
        url = f"{self.base_url}/goal/{goal_id}"
        auth_header = headers if headers is not None else self.headers
        return requests.delete(url, headers=auth_header)