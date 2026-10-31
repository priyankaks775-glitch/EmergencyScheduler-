

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from scheduler import schedule_edf, schedule_priority
from task_manager import (
    create_task,
    validate_tasks,
    generate_next_task_id
)
from metrics import calculate_metrics


st.set_page_config(
    page_title="Emergency Scheduler",
    page_icon="🚨",
    layout="wide"
)

st.title("🚨 Real-Time Emergency Task Scheduler")
st.write(
    "Simulate emergency tasks, compare CPU scheduling algorithms, "
    "and monitor deadlines."
)

st.sidebar.header("Add Emergency Tasks")

if "tasks" not in st.session_state:
    st.session_state.tasks = [
       create_task("P1", "Data Logging", 0, 6, 15, 4),
       create_task("P2", "Ambulance Alert", 2, 2, 5, 1),
       create_task("P3", "Traffic Update", 20, 2, 30, 3),
       create_task("P4", "Fire Alarm", 20, 1, 30, 2)
    ]

with st.sidebar.form("task_form", clear_on_submit=True):
    task_name = st.text_input("Task name")
    arrival = st.number_input("Arrival time", min_value=0, value=0)
    burst = st.number_input("Execution time", min_value=1, value=2)
    deadline = st.number_input("Deadline", min_value=1, value=5)
    priority = st.selectbox("Priority (1 = highest)", [1, 2, 3, 4])

    add_task = st.form_submit_button("Add Task")

if add_task:
    next_id = generate_next_task_id(st.session_state.tasks)
    new_task = create_task(
        next_id, task_name, int(arrival), int(burst),
        int(deadline), int(priority)
    )

    candidate_tasks = st.session_state.tasks + [new_task]
    valid, message = validate_tasks(candidate_tasks)

    if valid:
        st.session_state.tasks.append(new_task)
        st.success(f"Added {task_name}")
    else:
        st.error(message)


st.subheader("Emergency Task List")

if st.session_state.tasks:
    st.dataframe(
        pd.DataFrame(st.session_state.tasks),
        use_container_width=True,
        hide_index=True
    )

    task_options = {
        f'{task["id"]} - {task["name"]}': task["id"]
        for task in st.session_state.tasks
    }

    selected_task = st.selectbox(
        "Select a task to delete",
        options=list(task_options.keys()),
        key="delete_task_select"
    )

    if st.button("🗑️ Delete Selected Task"):
        task_id = task_options[selected_task]

        st.session_state.tasks = [
            task for task in st.session_state.tasks
            if task["id"] != task_id
        ]

        st.success(f"Task {selected_task} deleted successfully!")
        st.rerun()
else:
    st.info("No tasks available. Add a task using the sidebar.")


algorithm = st.radio(
    "Choose scheduling algorithm",
    ["Earliest Deadline First (EDF)", "Priority Scheduling"],
    horizontal=True
)

if st.button("Run Simulation", type="primary"):
    tasks = st.session_state.tasks
    valid, message = validate_tasks(tasks)

    if not valid:
        st.error(message)
    else:
        if algorithm == "Earliest Deadline First (EDF)":
            timeline = schedule_edf(tasks)
        else:
            timeline = schedule_priority(tasks)

        results = calculate_metrics(tasks, timeline)
        # Run both algorithms using the same task list
        edf_timeline = schedule_edf(tasks)
        priority_timeline = schedule_priority(tasks)

        edf_results = calculate_metrics(tasks, edf_timeline)
        priority_results = calculate_metrics(tasks, priority_timeline)

        st.subheader("Scheduling Timeline")

        fig, ax = plt.subplots(figsize=(10, 4))
        task_names = {task["id"]: task["name"] for task in tasks}

        for interval in timeline:
            task_id = interval["task_id"]
            start = interval["start"]
            duration = interval["end"] - start

            if task_id == "IDLE":
                label = "CPU Idle"
            else:
                label = task_names[task_id]

            ax.barh(
                label,
                duration,
                left=start,
                edgecolor="black"
            )
            ax.text(
                start + duration / 2,
                label,
                f"{start}-{interval['end']}",
                ha="center",
                va="center",
                fontsize=8
            )

        ax.set_xlabel("Simulation Time")
        ax.set_ylabel("Task")
        ax.set_title(algorithm)
        ax.grid(axis="x", linestyle="--", alpha=0.4)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        st.subheader("Performance Summary")
        summary = results["summary"]

        c1, c2, c3 = st.columns(3)
        c1.metric(
            "Avg. Waiting Time",
            f"{summary['average_waiting_time']:.2f}"
        )
        c2.metric(
            "Avg. Turnaround Time",
            f"{summary['average_turnaround_time']:.2f}"
        )
        c3.metric(
            "Avg. Response Time",
            f"{summary['average_response_time']:.2f}"
        )

        c4, c5 = st.columns(2)
        c4.metric(
            "CPU Utilization",
            f"{summary['cpu_utilization']:.2f}%"
        )
        c5.metric(
            "Missed Deadlines",
            int(summary["missed_deadlines"])
        )

        st.subheader("Individual Task Results")
        st.dataframe(
            pd.DataFrame(results["task_results"]),
            use_container_width=True,
            hide_index=True
        )

        missed = [
            task for task in results["task_results"]
            if task["deadline_status"] == "MISSED"
        ]

        if missed:
            st.warning(
                "Missed deadlines: "
                + ", ".join(task["name"] for task in missed)
            )
        else:
            st.success("All tasks met their deadlines in this simulation.")
                # EDF vs Priority Scheduling Comparison

        st.subheader("EDF vs Priority Scheduling Comparison")

        edf_summary = edf_results["summary"]
        priority_summary = priority_results["summary"]

        comparison = pd.DataFrame({
            "Performance Metric": [
                "Average Waiting Time",
                "Average Turnaround Time",
                "Average Response Time",
                "CPU Utilization (%)",
                "Missed Deadlines"
            ],
            "EDF": [
                edf_summary["average_waiting_time"],
                edf_summary["average_turnaround_time"],
                edf_summary["average_response_time"],
                edf_summary["cpu_utilization"],
                edf_summary["missed_deadlines"]
            ],
            "Priority Scheduling": [
                priority_summary["average_waiting_time"],
                priority_summary["average_turnaround_time"],
                priority_summary["average_response_time"],
                priority_summary["cpu_utilization"],
                priority_summary["missed_deadlines"]
            ]
        })

        st.dataframe(
            comparison.round(2),
            use_container_width=True,
            hide_index=True
        )

        # Performance Comparison Graph

        st.subheader("Performance Comparison Graph")

        chart_data = comparison[
            comparison["Performance Metric"] != "Missed Deadlines"
        ].set_index("Performance Metric")

        fig, ax = plt.subplots(figsize=(10, 5))
        chart_data.plot(kind="bar", ax=ax)

        ax.set_title("EDF vs Priority Scheduling")
        ax.set_ylabel("Performance Value")
        ax.set_xlabel("Performance Metrics")
        ax.tick_params(axis="x", rotation=15)
        ax.legend(title="Scheduling Algorithm")
        ax.grid(axis="y", linestyle="--", alpha=0.4)

        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        # Missed Deadline Comparison

        st.subheader("Missed Deadline Comparison")

        fig, ax = plt.subplots(figsize=(7, 4))

        ax.bar(
            ["EDF", "Priority Scheduling"],
            [
                edf_summary["missed_deadlines"],
                priority_summary["missed_deadlines"]
            ]
        )

        ax.set_ylabel("Number of Missed Deadlines")
        ax.set_title("Missed Deadlines by Scheduling Algorithm")
        ax.grid(axis="y", linestyle="--", alpha=0.4)

        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)