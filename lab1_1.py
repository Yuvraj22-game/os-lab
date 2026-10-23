"""Compare FCFS and non-preemptive SJF scheduling."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Process:
    process_id: str
    arrival_time: int
    burst_time: int
    input_order: int


@dataclass(frozen=True)
class ExecutionInterval:
    process_id: str
    start_time: int
    end_time: int


def read_processes() -> tuple[Process, ...]:
    """Read and validate one shared, immutable process dataset."""
    while True:
        try:
            count = int(input("Enter number of processes: "))
            if count <= 0:
                raise ValueError("number of processes must be greater than zero")
            break
        except ValueError as error:
            print(f"Invalid input: {error}. Enter a positive integer.")

    processes: list[Process] = []
    process_ids: set[str] = set()
    for input_order in range(count):
        while True:
            try:
                process_id = input(f"\nProcess {input_order + 1} ID: ").strip()
                if not process_id:
                    raise ValueError("process ID cannot be empty")
                if process_id in process_ids:
                    raise ValueError("process ID must be unique")

                arrival_time = int(input("Arrival time (>= 0): "))
                if arrival_time < 0:
                    raise ValueError("arrival time cannot be negative")

                burst_time = int(input("Burst time (> 0): "))
                if burst_time <= 0:
                    raise ValueError("burst time must be greater than zero")
            except ValueError as error:
                print(f"Invalid process data: {error}. Please re-enter this process.")
                continue

            processes.append(
                Process(process_id, arrival_time, burst_time, input_order)
            )
            process_ids.add(process_id)
            break

    return tuple(processes)


def add_idle_interval(
    intervals: list[ExecutionInterval], start_time: int, end_time: int
) -> None:
    if start_time < end_time:
        intervals.append(ExecutionInterval("IDLE", start_time, end_time))


def schedule_fcfs(processes: tuple[Process, ...]) -> tuple[ExecutionInterval, ...]:
    """Schedule by arrival time, preserving input order for equal arrivals."""
    ordered = sorted(processes, key=lambda process: (process.arrival_time, process.input_order))
    intervals: list[ExecutionInterval] = []
    current_time = 0

    for process in ordered:
        if current_time < process.arrival_time:
            add_idle_interval(intervals, current_time, process.arrival_time)
            current_time = process.arrival_time
        end_time = current_time + process.burst_time
        intervals.append(ExecutionInterval(process.process_id, current_time, end_time))
        current_time = end_time

    return tuple(intervals)


def schedule_sjf(processes: tuple[Process, ...]) -> tuple[ExecutionInterval, ...]:
    """Schedule the shortest arrived process without preemption.

    Ties are resolved by shorter burst time, earlier arrival time, then input order.
    """
    waiting = list(processes)
    intervals: list[ExecutionInterval] = []
    current_time = 0

    while waiting:
        arrived = [
            process for process in waiting if process.arrival_time <= current_time
        ]
        if not arrived:
            next_arrival = min(process.arrival_time for process in waiting)
            add_idle_interval(intervals, current_time, next_arrival)
            current_time = next_arrival
            arrived = [
                process for process in waiting if process.arrival_time <= current_time
            ]

        process = min(
            arrived,
            key=lambda candidate: (
                candidate.burst_time,
                candidate.arrival_time,
                candidate.input_order,
            ),
        )
        waiting.remove(process)
        end_time = current_time + process.burst_time
        intervals.append(ExecutionInterval(process.process_id, current_time, end_time))
        current_time = end_time

    return tuple(intervals)


def display_schedule(name: str, intervals: tuple[ExecutionInterval, ...]) -> None:
    print(f"\n=== {name} ===")
    print("Execution sequence: " + " -> ".join(interval.process_id for interval in intervals))
    print("Start/End intervals:")
    for interval in intervals:
        print(
            f"  {interval.process_id}: "
            f"start={interval.start_time}, end={interval.end_time}"
        )


def main() -> None:
    processes = read_processes()
    print("\nOriginal process data (shared by both algorithms):")
    for process in processes:
        print(
            f"  {process.process_id}: "
            f"arrival={process.arrival_time}, burst={process.burst_time}"
        )

    fcfs_intervals = schedule_fcfs(processes)
    sjf_intervals = schedule_sjf(processes)
    display_schedule("FCFS (arrival order)", fcfs_intervals)
    display_schedule("SJF (non-preemptive)", sjf_intervals)


if __name__ == "__main__":
    main()