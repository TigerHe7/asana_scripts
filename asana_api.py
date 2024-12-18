import asana

PERSONAL_ACCESS_TOKEN = ''
PROJECT_ID = ''
INPUT_FILE = 'asana_api_input.txt'
TASK_IDS_FILE = 'task_ids.txt'

# Initialize Asana client
client = asana.Client.access_token(PERSONAL_ACCESS_TOKEN)

# Disable SSL verification if necessary
# client.session.verify = False

def parse_file_to_dict(file_path):
    """
    Parses a file with lines of the format 'key, value' into a dictionary.
    
    Args:
        file_path (str): Path to the input file.
    
    Returns:
        dict: A dictionary where keys are task names and values are IDs.
    """
    parsed_data = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if ',' in line:  # Ensure it contains the expected format
                    key, value = map(str.strip, line.split(',', 1))
                    parsed_data[key] = value
        return parsed_data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return {}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

def parse_tasks(data):
    """Parses the input task data into a dictionary of tasks and their dependencies."""
    tasks = {}
    current_task = None
    for line in data.strip().split('\n'):
        line = line.strip()
        if not line:
            current_task = None
            continue
        if not line.startswith('*'):
            current_task = line
            tasks[current_task] = {'dependencies': []}
        else:
            dependency = line.lstrip('*').strip()
            tasks[current_task]['dependencies'].append(dependency)
    return tasks

def create_tasks(client, project_id, tasks):
    """Creates tasks in Asana and returns a dictionary mapping task names to task IDs."""
    task_ids = {}
    for task_name in tasks:
        task = client.tasks.create_task({
            'name': task_name,
            'projects': [project_id],
        })
        task_ids[task_name] = task['gid']
        print(f"'{task_name}', {task['gid']}")
    return task_ids

def set_dependencies(client, tasks, task_ids):
    # print(client.tasks)
    """Creates dependencies between tasks in Asana."""
    for task_name, details in tasks.items():
        for dependency_name in details['dependencies']:
            try:
                client.tasks.add_dependencies_for_task(
                    task_ids[task_name],
                    {
                        'dependencies': task_ids[dependency_name]
                    }
                )
                print(f"Set '{dependency_name}' as a dependency for '{task_name}'")
            except Exception as e:
                print(f"Error setting dependency for '{task_name}' '{task_ids[dependency_name]}': {e}")

if __name__ == '__main__':
    try:
        # Read the task data from the file
        with open(INPUT_FILE, 'r') as file:
            task_data = file.read()

        with open(TASK_IDS_FILE, 'r') as file:
            task_ids = file.read()

        task_ids = parse_file_to_dict(TASK_IDS_FILE)

        # Parse the tasks and dependencies
        tasks_and_deps = parse_tasks(task_data)

        # Create the tasks in Asana
        # task_ids = create_tasks(client, PROJECT_ID, tasks_and_deps)

        # Set up the dependencies
        set_dependencies(client, tasks_and_deps, task_ids)

        print("All tasks and dependencies have been created successfully.")
    except FileNotFoundError:
        print(f"Error: File '{INPUT_FILE}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
