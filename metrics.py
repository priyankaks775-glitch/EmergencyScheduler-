
def calculate_metrics(tasks, timeline):
    """Calculate performance metrics from tasks and execution timeline."""

    if not tasks:
        raise ValueError("Task list cannot be empty.")

    if not timeline:
        raise ValueError("Execution timeline cannot be empty.")

    # Store task completion and first-start times
    completion = {}
    first_start = {}

    for interval in timeline:
        task_id = interval["task_id"]

        # Ignore CPU idle intervals
        if task_id == "IDLE":
            continue

        start = interval["start"]
        end = interval["end"]

        if end <= start:
            raise ValueError("Invalid execution interval.")

        if task_id not in completion:
            completion[task_id] = end
            first_start[task_id] = start
        else:
            completion[task_id] = max(completion[task_id], end)
            first_start[task_id] = min(
                first_start[task_id], start
            )

    # Calculate metrics for each task
    task_results = []

    for task in tasks:
        task_id = task["id"]

        if task_id not in completion:
            raise ValueError(
                f"No execution recorded for task {task_id}."
            )

        arrival = task["arrival"]
        burst = task["burst"]
        deadline = task["deadline"]

        completion_time = completion[task_id]
        turnaround = completion_time - arrival
        response = first_start[task_id] - arrival
        waiting = turnaround - burst
        missed = completion_time > deadline

        task_results.append({
            "task_id": task_id,
            "name": task["name"],
            "completion_time": completion_time,
            "turnaround_time": turnaround,
            "response_time": response,
            "waiting_time": waiting,
            "deadline": deadline,
            "deadline_status": (
                "MISSED" if missed else "MET"
            )
        })

    # Calculate CPU utilization
    busy_time = sum(
        interval["end"] - interval["start"]
        for interval in timeline
        if interval["task_id"] != "IDLE"
    )

    total_time = max(
        interval["end"] for interval in timeline
    ) - min(
        interval["start"] for interval in timeline
    )

    cpu_utilization = (
        (busy_time / total_time) * 100
        if total_time > 0 else 0
    )

    count = len(task_results)

    summary = {
        "average_waiting_time": sum(
            r["waiting_time"] for r in task_results
        ) / count,

        "average_turnaround_time": sum(
            r["turnaround_time"] for r in task_results
        ) / count,

        "average_response_time": sum(
            r["response_time"] for r in task_results
        ) / count,

        "cpu_utilization": cpu_utilization,

        "missed_deadlines": sum(
            r["deadline_status"] == "MISSED"
            for r in task_results
        )
    }

    return {
        "task_results": task_results,
        "summary": summary
    }


def print_metrics(results, algorithm_name):
    """Display task metrics and overall performance."""

    print(f"\n===== {algorithm_name} Results =====")

    print("\nIndividual Task Results:")

    for task in results["task_results"]:
        print(
            f'{task["task_id"]} ({task["name"]}) | '
            f'Completion: {task["completion_time"]} | '
            f'Waiting: {task["waiting_time"]} | '
            f'Turnaround: {task["turnaround_time"]} | '
            f'Response: {task["response_time"]} | '
            f'Deadline: {task["deadline_status"]}'
        )

    print("\nOverall Performance:")

    for metric, value in results["summary"].items():
        if isinstance(value, float):
            print(f"{metric}: {value:.2f}")
        else:
            print(f"{metric}: {value}")


if __name__ == "__main__":
    # Import the other two members' modules
    from task_manager import get_sample_tasks
    from scheduler import schedule_edf, schedule_priority

    tasks = get_sample_tasks()

    # Test EDF
    edf_timeline = schedule_edf(tasks)
    edf_results = calculate_metrics(tasks, edf_timeline)
    print_metrics(edf_results, "EDF")

    # Test Priority Scheduling
    priority_timeline = schedule_priority(tasks)
    priority_results = calculate_metrics(
        tasks, priority_timeline
    )
    print_metrics(priority_results, "Priority Scheduling")
