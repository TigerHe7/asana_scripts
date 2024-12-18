import requests
import json

# --- CONFIGURATION ---
ACCESS_TOKEN = ""
PROJECT_ID = ""
ASANA_API_BASE_URL = "https://app.asana.com/api/1.0"
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}

# --- FUNCTION TO GET TASKS FROM PROJECT ---
def get_project_tasks(project_id):
    url = f"{ASANA_API_BASE_URL}/projects/{project_id}/tasks?opt_fields=name,dependencies"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()  # Raise an error for HTTP issues
    return response.json().get("data", [])

# --- FUNCTION TO FETCH DEPENDENCIES FOR EACH TASK ---
def get_task_dependencies(task_id):
    url = f"{ASANA_API_BASE_URL}/tasks/{task_id}?opt_fields=dependencies.name"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    task_data = response.json().get("data", {})
    dependencies = task_data.get("dependencies", [])
    return [dep.get("name") for dep in dependencies]  # Extract dependency names

# --- MAIN FUNCTION ---
def main():
    print("Fetching tasks and their dependencies from Asana...")
    try:
        tasks = get_project_tasks(PROJECT_ID)
        for task in tasks:
            task_name = task.get("name")
            task_id = task.get("gid")
            dependencies = get_task_dependencies(task_id)
            dep_names = ", ".join(dependencies) if dependencies else "No dependencies"
            print(f"Task: {task_name} | Dependencies: {dep_names}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Asana: {e}")

if __name__ == "__main__":
    main()
