"""Deadlock conditions, prevention, and Banker’s algorithm."""

from threading import Event, Lock, Thread
from typing import Sequence


def circular_wait_demo() -> None:
    """Create a bounded circular wait and recover by releasing both locks."""
    print("=== CONTROLLED CIRCULAR-WAIT SCENARIO ===")
    first_resource = Lock()
    second_resource = Lock()
    first_acquired = Event()
    second_acquired = Event()
    stop = Event()

    def worker(
        name: str,
        first: Lock,
        second: Lock,
        first_event: Event,
    ) -> None:
        with first:
            print(f"{name} holds its first resource")
            first_event.set()
            first_event.wait()
            if not stop.wait(0.1):
                acquired = second.acquire(timeout=0.5)
                if acquired:
                    second.release()

    process_a = Thread(
        target=worker, args=("Process A", first_resource, second_resource, first_acquired)
    )
    process_b = Thread(
        target=worker, args=("Process B", second_resource, first_resource, second_acquired)
    )
    process_a.start()
    process_b.start()
    process_a.join(timeout=0.2)
    process_b.join(timeout=0.2)
    blocked = process_a.is_alive() or process_b.is_alive()
    print(f"Circular wait observed: {blocked}")
    print("Conditions: mutual exclusion, hold and wait, no preemption, circular wait")

    stop.set()
    process_a.join(timeout=1)
    process_b.join(timeout=1)
    print("Controlled recovery: signalled workers and released held resources")
    print(f"Workers terminated: {not process_a.is_alive() and not process_b.is_alive()}")


def ordered_lock_demo() -> None:
    """Prevent circular wait by acquiring resources in one global order."""
    print("\n=== DEADLOCK PREVENTION: RESOURCE ORDERING ===")
    resources = {"R1": Lock(), "R2": Lock()}
    completed: list[str] = []

    def ordered_worker(name: str, requested: Sequence[str]) -> None:
        ordered = sorted(requested)
        acquired: list[Lock] = []
        try:
            for resource_name in ordered:
                resources[resource_name].acquire()
                acquired.append(resources[resource_name])
            completed.append(name)
        finally:
            for resource in reversed(acquired):
                resource.release()

    threads = [
        Thread(target=ordered_worker, args=("Process A", ("R1", "R2"))),
        Thread(target=ordered_worker, args=("Process B", ("R2", "R1"))),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=1)

    print("Rule: every process acquires resources in sorted order (R1 before R2)")
    print(f"Completed without circular wait: {len(completed) == len(threads)}")


def read_matrix(name: str, process_count: int, resource_count: int) -> list[list[int]]:
    matrix: list[list[int]] = []
    print(f"\nEnter {name} matrix rows ({resource_count} non-negative integers each):")
    for process_index in range(process_count):
        while True:
            try:
                values = [
                    int(value)
                    for value in input(f"  P{process_index + 1}: ").split()
                ]
                if len(values) != resource_count:
                    raise ValueError(f"expected {resource_count} values")
                if any(value < 0 for value in values):
                    raise ValueError("values cannot be negative")
                matrix.append(values)
                break
            except ValueError as error:
                print(f"Invalid row: {error}. Please re-enter it.")
    return matrix


def read_vector(name: str, resource_count: int) -> list[int]:
    while True:
        try:
            values = [int(value) for value in input(f"Enter {name}: ").split()]
            if len(values) != resource_count:
                raise ValueError(f"expected {resource_count} values")
            if any(value < 0 for value in values):
                raise ValueError("values cannot be negative")
            return values
        except ValueError as error:
            print(f"Invalid vector: {error}. Please re-enter it.")


def read_banker_data() -> tuple[list[list[int]], list[list[int]], list[int]]:
    while True:
        try:
            process_count = int(input("\nEnter number of processes: "))
            resource_count = int(input("Enter number of resource types: "))
            if process_count <= 0 or resource_count <= 0:
                raise ValueError("counts must be greater than zero")
            break
        except ValueError as error:
            print(f"Invalid dimensions: {error}.")

    allocation = read_matrix("Allocation", process_count, resource_count)
    maximum = read_matrix("Maximum", process_count, resource_count)
    available = read_vector("Available resources", resource_count)

    for process_index, (allocated, maximum_claim) in enumerate(
        zip(allocation, maximum), start=1
    ):
        if any(
            allocated_resource > maximum_resource
            for allocated_resource, maximum_resource in zip(allocated, maximum_claim)
        ):
            raise ValueError(f"allocation exceeds maximum for P{process_index}")
    return allocation, maximum, available


def calculate_need(
    allocation: Sequence[Sequence[int]], maximum: Sequence[Sequence[int]]
) -> list[list[int]]:
    return [
        [maximum_value - allocated_value for allocated_value, maximum_value in zip(allocated, maximum_claim)]
        for allocated, maximum_claim in zip(allocation, maximum)
    ]


def can_complete(need: Sequence[int], work: Sequence[int]) -> bool:
    return all(need_value <= available_value for need_value, available_value in zip(need, work))


def bankers_safety(
    allocation: Sequence[Sequence[int]],
    need: Sequence[Sequence[int]],
    available: Sequence[int],
) -> tuple[bool, list[int]]:
    work = list(available)
    finished = [False] * len(allocation)
    sequence: list[int] = []
    changed = True
    while changed:
        changed = False
        for process_index, (process_allocation, process_need) in enumerate(zip(allocation, need)):
            if not finished[process_index] and can_complete(process_need, work):
                work = [available_value + allocated_value for available_value, allocated_value in zip(work, process_allocation)]
                finished[process_index] = True
                sequence.append(process_index)
                changed = True
    return all(finished), sequence


def detect_deadlock(
    allocation: Sequence[Sequence[int]],
    need: Sequence[Sequence[int]],
    available: Sequence[int],
) -> list[int]:
    """Treat each remaining Need as its outstanding request."""
    safe, sequence = bankers_safety(allocation, need, available)
    if safe:
        return []
    completed = set(sequence)
    return [index for index in range(len(allocation)) if index not in completed]


def display_matrix(title: str, matrix: Sequence[Sequence[int]]) -> None:
    print(f"\n{title}:")
    for index, row in enumerate(matrix, start=1):
        print(f"  P{index}: {' '.join(map(str, row))}")


def banker_demo() -> None:
    print("\n=== BANKER'S ALGORITHM ===")
    try:
        allocation, maximum, available = read_banker_data()
    except ValueError as error:
        print(f"Input error: {error}")
        return

    need = calculate_need(allocation, maximum)
    display_matrix("Allocation", allocation)
    display_matrix("Maximum", maximum)
    display_matrix("Need = Maximum - Allocation", need)
    print(f"\nAvailable: {' '.join(map(str, available))}")

    safe, sequence = bankers_safety(allocation, need, available)
    if safe:
        print("Safe state")
        print("Safe sequence: " + " -> ".join(f"P{index + 1}" for index in sequence))
    else:
        print("Unsafe state: no complete safe sequence exists")

    deadlocked = detect_deadlock(allocation, need, available)
    if not deadlocked:
        print("Deadlock detection: no deadlocked processes")
        return

    print(
        "Deadlock detection: "
        + ", ".join(f"P{index + 1}" for index in deadlocked)
    )
    recovery_index = deadlocked[0]
    recovered_available = [
        available_value + allocated_value
        for available_value, allocated_value in zip(available, allocation[recovery_index])
    ]
    print(f"Controlled recovery: terminate P{recovery_index + 1} and release its allocation")
    remaining_allocation = [
        row for index, row in enumerate(allocation) if index != recovery_index
    ]
    remaining_need = [row for index, row in enumerate(need) if index != recovery_index]
    recovered_safe, recovered_sequence = bankers_safety(
        remaining_allocation, remaining_need, recovered_available
    )
    print(f"Recovery result: {'safe' if recovered_safe else 'still unsafe'}")
    if recovered_safe:
        print(
            "Recovery sequence: "
            + " -> ".join(
                f"P{index + 1 if index < recovery_index else index + 2}"
                for index in recovered_sequence
            )
        )


def main() -> None:
    circular_wait_demo()
    ordered_lock_demo()
    banker_demo()


if __name__ == "__main__":
    main()