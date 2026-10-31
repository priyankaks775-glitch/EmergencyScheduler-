def create_task(task_id, name, arrival, burst, deadline, priority):
    """Create one emergency task."""

    return {
        "id": task_id,
        "name": name,
        "arrival": arrival,
        "burst": burst,
        "deadline": deadline,
        "priority": priority
    }

def validate_tasks(tasks):
    """Return (is_valid, message) for a list of tasks."""

    if not tasks:
        return False, "Please add at least one task."

    required_fields = {
        "id", "name", "arrival",
        "burst", "deadline", "priority"
    }

    seen_ids = set()

    for index, task in enumerate(tasks, start=1):

        if not isinstance(task, dict):
            return False, f"Task {index} must be a dictionary."

        missing = required_fields - task.keys()

        if missing:
            return False, (
                f"Task {index} is missing: "
                + ", ".join(sorted(missing))
            )

        task_id = task["id"]

        if not isinstance(task_id, str) or not task_id.strip():
            return False, f"Task {index} needs a valid ID."

        if task_id in seen_ids:
            return False, f"Duplicate task ID: {task_id}."

        seen_ids.add(task_id)

        if not isinstance(task["name"], str) or not task["name"].strip():
            return False, f"{task_id}: task name cannot be empty."

        for field in ("arrival", "burst", "deadline", "priority"):
            value = task[field]

            # bool is a subclass of int in Python, so reject it explicitly.
            if isinstance(value, bool) or not isinstance(value, int):
                return False, f"{task_id}: {field} must be an integer."

        if task["arrival"] < 0:
            return False, f"{task_id}: arrival cannot be negative."

        if task["burst"] <= 0:
            return False, f"{task_id}: burst must be positive."

        if task["deadline"] <= task["arrival"]:
            return False, (
                f"{task_id}: deadline must be later than arrival."
            )

        if task["priority"] < 1:
            return False, f"{task_id}: priority must be at least 1."

    return True, "All tasks are valid."

def get_sample_tasks():
    """Return sample tasks for testing."""

    return [
        create_task(
            "P1", "Ambulance Alert",
            0, 4, 8, 2
        ),
        create_task(
            "P2", "Fire Alarm",
            1, 2, 3, 1
        ),
        create_task(
            "P3", "Traffic Update",
            0, 3, 6, 3
        ),
        create_task(
            "P4", "Data Logging",
            2, 2, 10, 4
        )
    ]

if __name__ == "__main__":
   
    print("\nTesting empty task list:")
    valid, message = validate_tasks([])
    print("Validation:", message)

    print("\nTesting duplicate task IDs:")
    duplicate_tasks = [
        create_task("P1", "Ambulance Alert", 0, 4, 8, 2),
        create_task("P1", "Fire Alarm", 1, 2, 5, 1)
    ]
    valid, message = validate_tasks(duplicate_tasks)
    print("Validation:", message)

    print("\nTesting negative arrival:")
    negative_arrival = [
        create_task("P5", "Test Task", -1, 2, 8, 1)
    ]
    valid, message = validate_tasks(negative_arrival)
    print("Validation:", message)

    print("\nTesting invalid deadline:")
    invalid_deadline = [
        create_task("P6", "Test Task", 3, 2, 3, 1)
    ]
    valid, message = validate_tasks(invalid_deadline)
    print("Validation:", message)

    print("\nTesting invalid priority:")
    invalid_priority = [
        create_task("P7", "Test Task", 0, 2, 8, 0)
    ]
    valid, message = validate_tasks(invalid_priority)
    print("Validation:", message)



def generate_next_task_id(tasks):
    existing_ids = {
        task["id"] for task in tasks
    }

    number = 1

    while f"P{number}" in existing_ids:
        number += 1

    return f"P{number}"