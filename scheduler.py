
# Real-Time Emergency Scheduler
# Member 1: Scheduling Algorithms


def schedule_edf(tasks):
    """Earliest Deadline First Scheduling"""

    remaining = {
        task["id"]: task["burst"]
        for task in tasks
    }

    timeline = []
    time = 0

    while any(value > 0 for value in remaining.values()):

        # Find arrived and unfinished tasks
        ready = [
            task for task in tasks
            if task["arrival"] <= time
            and remaining[task["id"]] > 0
        ]

        # Select task with the earliest deadline
        if not ready:
            selected = None
        else:
            selected = min(
                ready,
                key=lambda task: (
                    task["deadline"],
                    task["arrival"],
                    task["id"]
                )
            )

        task_id = selected["id"] if selected else "IDLE"

        # Execute for one time unit
        if selected:
            remaining[task_id] -= 1

        # Record execution timeline
        if timeline and timeline[-1]["task_id"] == task_id:
            timeline[-1]["end"] = time + 1
        else:
            timeline.append({
                "task_id": task_id,
                "start": time,
                "end": time + 1
            })

        time += 1

    return timeline


def schedule_priority(tasks):
    """Preemptive Priority Scheduling (1 = highest priority)"""

    remaining = {
        task["id"]: task["burst"]
        for task in tasks
    }

    timeline = []
    time = 0

    while any(value > 0 for value in remaining.values()):

        # Find arrived and unfinished tasks
        ready = [
            task for task in tasks
            if task["arrival"] <= time
            and remaining[task["id"]] > 0
        ]

        # Select the highest-priority task
        if not ready:
            selected = None
        else:
            selected = min(
                ready,
                key=lambda task: (
                    task["priority"],
                    task["arrival"],
                    task["id"]
                )
            )

        task_id = selected["id"] if selected else "IDLE"

        # Execute for one time unit
        if selected:
            remaining[task_id] -= 1

        # Record execution timeline
        if timeline and timeline[-1]["task_id"] == task_id:
            timeline[-1]["end"] = time + 1
        else:
            timeline.append({
                "task_id": task_id,
                "start": time,
                "end": time + 1
            })

        time += 1

    return timeline


# Test both algorithms
if __name__ == "__main__":

    tasks = [
        {
            "id": "P1",
            "name": "Ambulance Alert",
            "arrival": 0,
            "burst": 4,
            "deadline": 8,
            "priority": 2
        },
        {
            "id": "P2",
            "name": "Fire Alarm",
            "arrival": 1,
            "burst": 2,
            "deadline": 3,
            "priority": 1
        },
        {
            "id": "P3",
            "name": "Traffic Update",
            "arrival": 0,
            "burst": 3,
            "deadline": 6,
            "priority": 3
        }
    ]

    print("EDF Schedule:")
    print(schedule_edf(tasks))

    print("\nPriority Schedule:")
    print(schedule_priority(tasks))
