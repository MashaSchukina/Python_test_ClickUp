import os

import pytest
from faker import Faker
from clickup_api_helpers import ClickUpAPI

fake = Faker()

bad_headers_with_invalid_token = {
        "Authorization": os.getenv("INVALID_TOKEN"),
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="module")
def api():
    return ClickUpAPI()


@pytest.fixture
def goal_lifecycle(api):
    payload = {
        "name": fake.name(),
        "due_date": 4126131456000,
        "description": fake.name() + "This is Goal Description",
        "multiple_owners": True,
        "owners": []
    }

    response = api.create_goal(payload)
    assert response.status_code == 200, f"Не вдалося створити Goal. {response.text}"

    goal_data = response.json().get("goal")
    goal_id = goal_data["id"]

    yield goal_data

    delete_res = api.delete_goal(goal_id)
    assert delete_res.status_code == 200, f"Не вдалося видалити Goal {goal_id}."

####################
# TEST FOR CREATE GOAL

def test_create_goal_positive(api):
    payload = {
        "name": fake.name(),
        "due_date": 4126131456000,
        "description": fake.name() + " This is Goal Description",
        "multiple_owners": True,
        "owners": []
    }

    response = api.create_goal(payload)
    assert response.status_code == 200
    goal_data = response.json().get("goal", {})

    assert "id" in goal_data, "Goal ID is missing in response"
    assert isinstance(goal_data["id"], str)

    assert goal_data["name"] == payload["name"], "Name in response dont match  name in payload"
    assert goal_data["description"] == payload[
        "description"], "Description  in response dont match Description in payload"
    assert int(goal_data["due_date"]) == payload["due_date"], "due_date in response dont match  due_date in payload"
    assert goal_data["archived"] is False, "New goal should not be archived"

    api.delete_goal(goal_data["id"])


def test_create_goal_without_name_in_payload(api):
    payload = {
        "due_date": 4126131456000,
        "description": fake.name() + " This is Goal Description",
        "multiple_owners": True,
        "owners": []

    }
    response = api.create_goal(payload)
    # Тут тест падає, бо очікую 400, але API повертає 500
    assert response.status_code == 400


def test_create_goal_without_auth_token(api):
    payload = {"name": fake.name()}
    invalid_headers = {"Content-Type": "application/json"}
    response = api.create_goal(payload, headers=invalid_headers)
    assert response.status_code == 400
    error_response = response.json()
    assert error_response.get("err") == "Authorization header required"
    assert error_response.get("ECODE") == "OAUTH_017"


def test_create_goal_wit_invalid_token(api):
    payload = {"name": fake.name()}
    response = api.create_goal(payload, headers=bad_headers_with_invalid_token)
    assert response.status_code == 401
    error_response = response.json()
    assert error_response.get("err") == "Token invalid"
    assert error_response.get("ECODE") == "OAUTH_025"

####################
# TEST FOR GET GOAL

def test_get_goal_positive(api, goal_lifecycle):
    goal_id = goal_lifecycle["id"]

    response = api.get_goal(goal_id)
    assert response.status_code == 200
    goal_data = response.json().get("goal", {})
    assert goal_data["id"] == goal_id, "ID don't matches"
    assert goal_data["name"] == goal_lifecycle["name"], "Nane don't matches"
    assert goal_data["description"] == goal_lifecycle["description"], "Description don't matches"
    assert goal_data["multiple_owners"] == goal_lifecycle["multiple_owners"], "multiple_owners don't matches"

    assert goal_data["archived"] is False, "Created goal is archived"


def test_get_goal_wit_invalid_token(api, goal_lifecycle):
    goal_id = goal_lifecycle["id"]

    response = api.get_goal(goal_id, headers=bad_headers_with_invalid_token)
    assert response.status_code == 401
    error_response = response.json()
    assert error_response.get("err") == "Token invalid"
    assert error_response.get("ECODE") == "OAUTH_025"


def test_get_goal_without_auth_token(api, goal_lifecycle):
    goal_id = goal_lifecycle["id"]
    bad_headers = {"Content-Type": "application/json"}

    response = api.get_goal(goal_id, headers=bad_headers)
    assert response.status_code == 400
    error_response = response.json()
    assert error_response.get("err") == "Authorization header required"
    assert error_response.get("ECODE") == "OAUTH_017"

####################
# TEST FOR GET LIST OF GOALS


def test_get_all_goals_positive(api, goal_lifecycle):
    response = api.get_goals()
    assert response.status_code == 200

    goals_list = response.json().get("goals", [])

    assert isinstance(goals_list, list), "The 'goals' field must be a list!"
    assert len(goals_list) > 0, "An empty list of goals was returned!"
    assert "id" in goals_list[0], "The objects in the list do not have the key 'id'"
    assert "name" in goals_list[0], "The objects in the list do not have the key 'name'"

    # Перевіряємо, що наш створений Goal точно є у цьому списку
    all_ids = [g["id"] for g in goals_list]
    assert goal_lifecycle["id"] in all_ids, f"The created goal {goal_lifecycle['id']} was not found in the general list"


def test_get_all_goals_without_auth_token(api, goal_lifecycle):
    bad_headers = {"Content-Type": "application/json"}

    response = api.get_goals(headers=bad_headers)
    assert response.status_code == 400
    error_response = response.json()
    assert error_response.get("err") == "Authorization header required"
    assert error_response.get("ECODE") == "OAUTH_017"


def test_get_all_goals_wit_invalid_token(api):

    response = api.get_goals(headers=bad_headers_with_invalid_token)
    assert response.status_code == 401
    error_response = response.json()
    assert error_response.get("err") == "Token invalid"
    assert error_response.get("ECODE") == "OAUTH_025"


#######################
# TEST FOR UPDATE GOAL


def test_update_goal_positive(api, goal_lifecycle):
    goal_id = goal_lifecycle["id"]
    new_name = fake.name() + " Updated Name"
    new_description = fake.name() + " Updated Description"
    payload = {
        "name": new_name,
        "description": new_description,
        "multiple_owners": False,
        "owners": []
    }
    response = api.update_goal(goal_id, payload)
    assert response.status_code == 200

    goal_data = response.json().get("goal", {})

    assert goal_data["id"] == goal_id, "ID don't matches"

    assert goal_data["name"] == payload["name"], "Updated name don't matches"
    assert goal_data["description"] == payload["description"], "Updated Description don't matches"
    assert goal_data["multiple_owners"] == payload["multiple_owners"], "The multiple_owners parameter has not changed."
    assert isinstance(goal_data["owners"], list)
    assert len(goal_data["owners"]) == len(payload["owners"]), "Owners list dont matches"

    assert goal_data["archived"] is False, "Updated goal is archived"

    get_response = api.get_goal(goal_id)
    assert get_response.status_code == 200

    updated_goal_data = get_response.json().get("goal", {})

    assert updated_goal_data["id"] == goal_id, "Updated ID don't matches"
    assert updated_goal_data["name"] == new_name, "Updated name don't matches"
    assert updated_goal_data["description"] == new_description, "Updated Description don't matches"
    assert updated_goal_data["multiple_owners"] is False, "The multiple_owners parameter has not changed"
    assert isinstance(updated_goal_data["owners"], list)
    assert len(updated_goal_data["owners"]) == len(payload["owners"]), "Owners list don't matches"

    assert updated_goal_data["archived"] is False, "Updated goal is archived"


def test_update_goal_with_invalid_id(api, goal_lifecycle):
    payload = {"name": "New Name"}
    invalid_goal_id = "00000000"

    response = api.update_goal(invalid_goal_id, payload)
    assert response.status_code == 404


def test_update_goal_without_auth_token(api, goal_lifecycle):
    goal_id = goal_lifecycle["id"]
    payload = {"name": fake.word()}
    bad_headers = {"Content-Type": "application/json"}

    response = api.update_goal(goal_id, payload, headers=bad_headers)
    assert response.status_code == 400
    error_response = response.json()
    assert error_response.get("err") == "Authorization header required"
    assert error_response.get("ECODE") == "OAUTH_017"


def test_update_goal_wit_invalid_token(api, goal_lifecycle):
    goal_id = goal_lifecycle["id"]
    payload = {"name": fake.word()}
    response = api.update_goal(goal_id, payload, headers=bad_headers_with_invalid_token)
    assert response.status_code == 401
    error_response = response.json()
    assert error_response.get("err") == "Token invalid"
    assert error_response.get("ECODE") == "OAUTH_025"


# TEST FOR DELETED GOAL

def test_delete_goal_positive(api):
    payload = {"name": fake.word()}
    create_res = api.create_goal(payload)
    goal_id = create_res.json()["goal"]["id"]

    delete_res = api.delete_goal(goal_id)
    assert delete_res.status_code == 200
    assert delete_res.json() == {}

    get_res = api.get_goal(goal_id)
    assert get_res.status_code == 404

def test_delete_goal_without_auth_token(api):
    payload = {"name": fake.word()}
    create_res = api.create_goal(payload)
    goal_id = create_res.json()["goal"]["id"]

    bad_headers = {"Content-Type": "application/json"}
    delete_res = api.delete_goal(goal_id,headers=bad_headers)

    assert delete_res.status_code == 400
    error_response = delete_res.json()
    assert error_response.get("err") == "Authorization header required"
    assert error_response.get("ECODE") == "OAUTH_017"


def test_delete_goal_wit_invalid_token(api):
    payload = {"name": fake.word()}
    create_res = api.create_goal(payload)
    goal_id = create_res.json()["goal"]["id"]

    bad_headers = {"Content-Type": "application/json"}
    delete_res = api.delete_goal(goal_id, headers=bad_headers_with_invalid_token)

    assert delete_res.status_code == 401
    error_response = delete_res.json()
    assert error_response.get("err") == "Token invalid"
    assert error_response.get("ECODE") == "OAUTH_025"

