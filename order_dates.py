import asana
import networkx as nx
from datetime import datetime, timedelta

# --- CONFIGURATION ---
ASANA_ACCESS_TOKEN = "ACCESS_TOKEN"
PROJECT_ID = "PROJECT_ID"
START_DATE = datetime(2025, 1, 6)
TASK_DURATION = 1  # Duration of each task in days
WEEKENDS = [5, 6]  # Saturday=5, Sunday=6
MAX_TASKS_PER_DAY = 4 # None for infinite

# --- ASANA CLIENT SETUP ---
client = asana.Client.access_token(ASANA_ACCESS_TOKEN)
client.headers = {"asana-enable": "new_goal_memberships,new_user_task_lists"}

# --- HELPER FUNCTIONS ---
def is_weekend(date):
    """Check if a date falls on a weekend."""
    return date.weekday() in WEEKENDS

def next_workday(date):
    """Find the next valid workday after a given date."""
    date += timedelta(days=TASK_DURATION)
    while is_weekend(date):
        date += timedelta(days=1)
    return date

def fetch_tasks_and_dependencies():
    """Fetch all tasks and dependencies from the project."""
    # task_gid_to_name_and_dependencies = {}
    dependency_edges = []

    result = client.tasks.find_by_project(PROJECT_ID, opt_fields="gid,name,dependencies")
    for task in result:
        task_gid = task["gid"]
        # task_gid_to_name_and_dependencies[task_gid] = {"name": task["name"], "dependencies": []}

        # Fetch dependencies for the task
        dependencies = client.tasks.dependencies(task_gid)
        for dep in dependencies:
            dep_gid = dep["gid"]
            dependency_edges.append((dep_gid, task_gid))
            # task_gid_to_name_and_dependencies[task_gid]["dependencies"].append(dep_gid)

    return dependency_edges

def assign_dates_to_tasks(edges, start_date):
    G = nx.DiGraph()
    G.add_edges_from(edges)

    # Check for cycles
    if not nx.is_directed_acyclic_graph(G):
        raise Exception("Project has circular dependencies!")

    # Dictionary to store scheduled dates for tasks

    if (MAX_TASKS_PER_DAY):
        # Perform topological sorting
        ordered_tasks = []
        while G.nodes:
            # Find all leaf nodes (nodes with no incoming edges)
            leaf_nodes = [node for node in G.nodes if G.in_degree(node) == 0]
            ordered_tasks += leaf_nodes
            G.remove_nodes_from(leaf_nodes)

        task_schedule = {}
        for i in range(len(ordered_tasks)):
            task_schedule[ordered_tasks[i]] = start_date
            if i % MAX_TASKS_PER_DAY == MAX_TASKS_PER_DAY - 1:
                start_date = next_workday(next_workday(start_date + timedelta(days=TASK_DURATION - 1)))
        return task_schedule
    else:
        task_schedule = {}
        # Perform topological sorting with layers
        while G.nodes:
            # Find all leaf nodes (nodes with no incoming edges)
            leaf_nodes = [node for node in G.nodes if G.in_degree(node) == 0]

            print(str(len(leaf_nodes)) + " leaf nodes found, setting due " + str(start_date.date()))

            # Assign the current date to all leaf nodes
            for node in leaf_nodes:
                task_schedule[node] = start_date

            # Remove leaf nodes from the graph
            G.remove_nodes_from(leaf_nodes)

            # Increment the start date to the next workday
            start_date = next_workday(next_workday(start_date + timedelta(days=TASK_DURATION - 1)))

        return task_schedule



def set_task_dates(task_gid, start_date):
    """Set the start and due date for a task."""
    due_date = next_workday(start_date + timedelta(days=TASK_DURATION - 1))
    client.tasks.update(task_gid, {
        "start_on": start_date.strftime("%Y-%m-%d"),
        "due_on": due_date.strftime("%Y-%m-%d")
    })
    print(f"Task {task_gid} scheduled from {start_date.date()} to {due_date.date()}")

# --- MAIN SCRIPT ---
def main():
    print("Fetching tasks and dependencies...")
    edges = fetch_tasks_and_dependencies()

    print("Performing topological sort...")
    tasks_to_dates = assign_dates_to_tasks(edges, START_DATE)
    print(tasks_to_dates)

    for task_gid, date in tasks_to_dates.items():
        set_task_dates(task_gid, date)

    print("All tasks scheduled successfully!")

if __name__ == "__main__":
    main()
