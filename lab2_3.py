"""Classical synchronization problems with bounded, observable executions."""

from threading import Lock, Semaphore, Thread
from time import sleep


def producer_consumer() -> None:
    """Use semaphores and a circular buffer with a fixed capacity."""
    print("=== PRODUCER-CONSUMER ===")
    capacity = 3
    item_count = 6
    buffer: list[int | None] = [None] * capacity
    in_position = 0
    out_position = 0
    buffer_lock = Lock()
    empty_slots = Semaphore(capacity)
    full_slots = Semaphore(0)
    consumed: list[int] = []

    def producer() -> None:
        nonlocal in_position
        for item in range(1, item_count + 1):
            empty_slots.acquire()
            with buffer_lock:
                buffer[in_position] = item
                position = in_position
                in_position = (in_position + 1) % capacity
                print(f"Producer: inserted {item} at slot {position}; buffer={buffer}")
            full_slots.release()
            sleep(0.005)

    def consumer() -> None:
        nonlocal out_position
        for _ in range(item_count):
            full_slots.acquire()
            with buffer_lock:
                item = buffer[out_position]
                buffer[out_position] = None
                position = out_position
                out_position = (out_position + 1) % capacity
                if item is None:
                    raise RuntimeError("buffer invariant violated: empty slot consumed")
                consumed.append(item)
                print(f"Consumer: removed {item} from slot {position}; buffer={buffer}")
            empty_slots.release()
            sleep(0.008)

    producer_thread = Thread(target=producer)
    consumer_thread = Thread(target=consumer)
    producer_thread.start()
    consumer_thread.start()
    producer_thread.join()
    consumer_thread.join()
    print(f"Producer-consumer complete: consumed={consumed}\n")


def readers_writers() -> None:
    """Allow concurrent readers while writers receive exclusive access.

    The turnstile prevents new readers from bypassing a waiting writer.
    """
    print("=== READERS-WRITERS ===")
    shared_data = 0
    reader_count = 0
    reader_count_lock = Lock()
    resource_lock = Lock()
    turnstile = Lock()
    operations: list[str] = []

    def reader(reader_id: int) -> None:
        nonlocal reader_count
        for _ in range(2):
            with turnstile:
                with reader_count_lock:
                    reader_count += 1
                    if reader_count == 1:
                        resource_lock.acquire()
            with reader_count_lock:
                value = shared_data
                operations.append(f"R{reader_id} read {value}")
                print(f"Reader {reader_id}: read {value}; active readers={reader_count}")
            with reader_count_lock:
                reader_count -= 1
                if reader_count == 0:
                    resource_lock.release()
            sleep(0.004)

    def writer(writer_id: int) -> None:
        nonlocal shared_data
        for _ in range(2):
            with turnstile:
                with resource_lock:
                    shared_data += 1
                    operations.append(f"W{writer_id} wrote {shared_data}")
                    print(f"Writer {writer_id}: wrote {shared_data}; exclusive access")
            sleep(0.006)

    threads = [
        Thread(target=reader, args=(1,)),
        Thread(target=reader, args=(2,)),
        Thread(target=writer, args=(1,)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print(f"Readers-writers complete: final shared value={shared_data}")
    print(f"Operations recorded: {len(operations)}\n")


def dining_philosophers() -> None:
    """Avoid circular wait with a waiter and a globally ordered fork lock."""
    print("=== DINING PHILOSOPHERS ===")
    philosopher_count = 5
    rounds = 2
    forks = [Lock() for _ in range(philosopher_count)]
    waiter = Semaphore(philosopher_count - 1)
    meals = [0] * philosopher_count

    def philosopher(philosopher_id: int) -> None:
        left = philosopher_id
        right = (philosopher_id + 1) % philosopher_count
        first, second = sorted((left, right))
        for round_number in range(1, rounds + 1):
            print(f"Philosopher {philosopher_id}: thinking (round {round_number})")
            with waiter:
                with forks[first]:
                    with forks[second]:
                        meals[philosopher_id] += 1
                        print(
                            f"Philosopher {philosopher_id}: eating with forks "
                            f"{first} and {second}"
                        )
            print(f"Philosopher {philosopher_id}: released forks")

    threads = [
        Thread(target=philosopher, args=(philosopher_id,))
        for philosopher_id in range(philosopher_count)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print(f"Dining complete: meals per philosopher={meals}")
    print("Deadlock prevention: at most four philosophers enter and forks use global order")


def main() -> None:
    producer_consumer()
    readers_writers()
    dining_philosophers()
    print("\nCorrectness: locks protect shared state and semaphores enforce availability.")
    print("Fairness: the readers-writers turnstile prevents new readers bypassing writers.")
    print("Starvation: bounded iterations and fair admission allow every operation to finish.")
    print("Deadlock: waiter capacity and fork ordering prevent circular wait.")


if __name__ == "__main__":
    main()