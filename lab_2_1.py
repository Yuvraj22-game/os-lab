import threading
import time


# Workload function
def do_work(start, end, results, thread_no):
    thread_id = threading.get_ident()

    print(f"Thread {thread_no} started")
    print(f"Thread ID: {thread_id}")
    print(f"Working on: {start} to {end}")

    total = 0

    for i in range(start, end):
        total += i

    results[thread_no] = total

    print(f"Thread {thread_no} completed")
    print(f"Result: {total}\n")


# -------------------------------
# 1. Single-threaded workload
# -------------------------------
N = 1000000

print("===== SINGLE THREADED =====")

start_time = time.perf_counter()

single_result = 0
for i in range(N):
    single_result += i

single_time = time.perf_counter() - start_time

print("Result:", single_result)
print("Time:", single_time, "seconds")


# -------------------------------
# 2 & 3. Multiple worker threads
# -------------------------------
print("\n===== MULTI THREADED =====")

number_of_threads = 4
threads = []
results = [0] * number_of_threads

chunk = N // number_of_threads

start_time = time.perf_counter()

for i in range(number_of_threads):

    start = i * chunk

    if i == number_of_threads - 1:
        end = N
    else:
        end = (i + 1) * chunk

    t = threading.Thread(
        target=do_work,
        args=(start, end, results, i)
    )

    threads.append(t)
    t.start()


# -------------------------------
# 5. Wait for all threads
# -------------------------------
for t in threads:
    t.join()


multi_time = time.perf_counter() - start_time

multi_result = sum(results)


# -------------------------------
# 6 & 7. Compare execution time
# -------------------------------
print("===== COMPARISON =====")

print("Single-threaded result :", single_result)
print("Single-threaded time   :", single_time, "seconds")

print("Multi-threaded result  :", multi_result)
print("Multi-threaded time    :", multi_time, "seconds")


# -------------------------------
# 8. Thread Models
# -------------------------------
print("\n===== THREAD MODELS =====")

print("""
1.⁠ ⁠User-Level Threads:
   Managed by a user-level library.

2.⁠ ⁠Kernel-Level Threads:
   Managed directly by the operating system.

3.⁠ ⁠Many-to-One:
   Many user threads mapped to one kernel thread.

4.⁠ ⁠One-to-One:
   Each user thread mapped to one kernel thread.

5.⁠ ⁠Many-to-Many:
   Many user threads mapped to multiple kernel threads.
""")


# -------------------------------
# 9. Multithreading Concepts
# -------------------------------
print("===== MULTITHREADING CONCEPTS =====")

print("""
Responsiveness:
Keeps applications responsive while tasks execute.

Resource Sharing:
Threads share memory and resources of the process.

Concurrency:
Multiple tasks make progress during overlapping time.

Parallelism:
Multiple tasks execute at the same time on multiple CPU cores.

Race Condition:
Occurs when threads access shared data simultaneously
and the result depends on execution order.

Deadlock:
Occurs when threads wait indefinitely for resources.

Overhead:
Thread creation, scheduling and synchronization require
additional system resources.
""")