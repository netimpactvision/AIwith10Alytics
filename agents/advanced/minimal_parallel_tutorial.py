#!/usr/bin/env python3
"""
Minimal Parallel Processing Tutorial
====================================
Learn the essentials of parallel processing in Python with detailed explanations.
"""

import asyncio
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def slow_task(name, duration):
    """
    Simulate I/O-bound task (network request, file read, database query).

    KEY CONCEPT: I/O-bound tasks spend most time waiting for external resources.
    During time.sleep(), the CPU is idle - this is where parallelism helps most.

    What happens:
    1. CPU starts the task
    2. CPU waits (doing nothing) during time.sleep()
    3. CPU finishes the task

    This waiting time is perfect for other tasks to run simultaneously.
    """
    print(f"Starting {name}...")
    time.sleep(duration)  # Simulates waiting for I/O (network, disk, etc.)
    print(f"Finished {name}")
    return f"Result from {name}"


def cpu_task(name, number):
    """
    Simulate CPU-bound task (calculations, data processing, image manipulation).

    KEY CONCEPT: CPU-bound tasks keep the processor busy with calculations.
    No waiting involved - CPU works at 100% capacity throughout.

    What happens:
    1. CPU starts intensive calculations
    2. CPU works continuously (no idle time)
    3. CPU finishes and returns result

    For CPU tasks, only multiple CPU cores can provide true parallelism.
    """
    print(f"Computing {name}...")
    # This loop keeps CPU busy - no waiting, pure computation
    result = sum(i**2 for i in range(number))
    print(f"Finished {name}")
    return f"{name}: {result}"


async def async_task(name, duration):
    """
    Asynchronous version of I/O task using cooperative multitasking.

    KEY CONCEPT: 'async' functions can voluntarily yield control to other tasks.
    When one task waits, another can run - all in a single thread.

    What happens:
    1. Task starts
    2. 'await' yields control to event loop
    3. Other tasks can run while this one waits
    4. Control returns when wait is complete

    This is extremely efficient for I/O because no thread overhead exists.
    """
    print(f"Starting {name}...")
    # await tells Python: "I'm waiting, let other async tasks run"
    await asyncio.sleep(duration)  # Non-blocking wait
    print(f"Finished {name}")
    return f"Result from {name}"


def demo_sequential():
    """
    SEQUENTIAL EXECUTION: Traditional single-threaded approach.

    MECHANISM: Python executes one function call at a time, waiting for each to complete.
    MEMORY: Single call stack, predictable memory usage.
    CPU USAGE: Only one CPU core used, others remain idle.

    EXECUTION FLOW:
    Task A starts -> Task A waits -> Task A finishes ->
    Task B starts -> Task B waits -> Task B finishes ->
    Task C starts -> Task C waits -> Task C finishes

    TOTAL TIME: Sum of all individual task times (1+1+1 = 3 seconds)
    """
    print("\n1. SEQUENTIAL (Baseline)")
    start = time.time()

    # Each function call blocks until completion - no parallelism
    results = [slow_task("Task A", 1), slow_task("Task B", 1), slow_task("Task C", 1)]

    print(f"Time: {time.time() - start:.1f}s | Results: {len(results)}")


def demo_threading():
    """
    THREADING: Multiple threads within the same process.

    MECHANISM: OS creates multiple threads that share the same memory space.
    MEMORY: Shared memory between threads (careful with data races!).
    CPU USAGE: Can utilize multiple cores, but Python's GIL limits true parallelism.

    KEY DIFFERENCE FROM SEQUENTIAL:
    - Multiple threads can wait simultaneously
    - While Thread A waits for I/O, Thread B can start working
    - All threads share the same process memory

    EXECUTION FLOW:
    All tasks start simultaneously -> All wait in parallel -> All finish ~same time

    TOTAL TIME: Maximum of individual task times (max(1,1,1) = 1 second)
    """
    print("\n2. THREADING (I/O Bound)")
    start = time.time()

    # ThreadPoolExecutor manages a pool of worker threads
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all tasks immediately - they start running in parallel
        futures = [executor.submit(slow_task, f"Task {i}", 1) for i in "ABC"]
        # .result() blocks until each specific task completes
        results = [f.result() for f in futures]

    print(f"Time: {time.time() - start:.1f}s | Results: {len(results)}")


def demo_multiprocessing():
    """
    MULTIPROCESSING: Multiple separate processes.

    MECHANISM: OS creates completely separate processes with isolated memory.
    MEMORY: Each process has its own memory space - no shared variables.
    CPU USAGE: True parallelism - can fully utilize all CPU cores.

    KEY DIFFERENCE FROM THREADING:
    - Separate processes, not threads
    - No shared memory (safer but requires data serialization)
    - No Python GIL limitations
    - Higher overhead for process creation

    EXECUTION FLOW:
    Process A starts -> Process B starts -> Process C starts ->
    All processes run simultaneously on different CPU cores ->
    All finish independently

    TOTAL TIME: Maximum of individual task times, but with process overhead
    """
    print("\n3. MULTIPROCESSING (CPU Bound)")
    start = time.time()

    # ProcessPoolExecutor creates separate Python processes
    with ProcessPoolExecutor(max_workers=3) as executor:
        # Each task runs in a completely separate process
        futures = [executor.submit(cpu_task, f"CPU-{i}", 100000) for i in "ABC"]
        # Data must be serialized/deserialized between processes
        results = [f.result() for f in futures]

    print(f"Time: {time.time() - start:.1f}s | Results: {len(results)}")


async def demo_async():
    """
    ASYNC/AWAIT: Cooperative multitasking in a single thread.

    MECHANISM: Single thread with an event loop that switches between tasks.
    MEMORY: Single thread memory, but multiple task contexts.
    CPU USAGE: Single thread, but extremely efficient for I/O.

    KEY DIFFERENCE FROM THREADING:
    - No thread creation overhead
    - No race conditions (single thread)
    - Tasks voluntarily yield control with 'await'
    - Event loop manages task switching

    EXECUTION FLOW:
    Task A starts -> awaits (yields) -> Task B starts -> awaits (yields) ->
    Task C starts -> awaits (yields) -> Event loop switches between waiting tasks ->
    All tasks complete as their waits finish

    TOTAL TIME: Maximum of individual task times (max(1,1,1) = 1 second)
    """
    print("\n4. ASYNC/AWAIT (I/O Bound)")
    start = time.time()

    # Create coroutine objects (not yet running)
    tasks = [async_task(f"Async {i}", 1) for i in "ABC"]
    # asyncio.gather() runs all coroutines concurrently in the event loop
    results = await asyncio.gather(*tasks)

    print(f"Time: {time.time() - start:.1f}s | Results: {len(results)}")


def demo_mixed():
    """
    MIXED APPROACH: Combines parallel and sequential execution patterns.

    REAL-WORLD PATTERN: Many applications have dependencies between tasks.
    Some tasks can run in parallel, others must wait for dependencies.

    EXECUTION STRATEGY:
    Phase 1: Independent tasks run in parallel (data gathering)
    Phase 2: Dependent tasks run sequentially (analysis needs all data)

    KEY INSIGHT: This mirrors real applications where:
    - API calls can be parallel
    - Database queries can be parallel
    - But analysis must wait for all data to be collected

    EXECUTION FLOW:
    Data A & Data B start simultaneously -> Both finish in parallel ->
    Analysis starts (using results from Phase 1) -> Analysis finishes

    TOTAL TIME: Phase 1 time + Phase 2 time (1 + 0.5 = 1.5 seconds)
    """
    print("\n5. MIXED APPROACH (Real World)")
    start = time.time()

    # Phase 1: Independent tasks that can run in parallel
    print("Phase 1: Gathering data...")
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Both data gathering tasks start immediately
        data_a = executor.submit(slow_task, "Data A", 1)
        data_b = executor.submit(slow_task, "Data B", 1)
        # Wait for both to complete before proceeding
        results = [data_a.result(), data_b.result()]

    # Phase 2: Dependent task that needs results from Phase 1
    print("Phase 2: Processing...")
    final_result = slow_task("Analysis", 0.5)

    print(f"Time: {time.time() - start:.1f}s | Final: {final_result}")


def main():
    """
    Run all demonstrations to compare parallel processing approaches.

    This tutorial shows the fundamental differences between execution models:
    1. How tasks are scheduled and executed
    2. Memory usage patterns
    3. CPU utilization differences
    4. When each approach is most effective
    """
    print("🚀 PARALLEL PROCESSING ESSENTIALS")
    print("=" * 40)

    demo_sequential()  # Baseline: 3 seconds (1+1+1)
    demo_threading()  # I/O parallel: 1 second (max of 1,1,1)
    demo_multiprocessing()  # CPU parallel: varies by CPU cores

    print("\nRunning async demo...")
    asyncio.run(demo_async())  # Event loop: 1 second (concurrent)

    demo_mixed()  # Real-world: 1.5 seconds (1 + 0.5)

    print("\n" + "=" * 40)
    print("📚 FUNDAMENTAL DIFFERENCES:")
    print("• Sequential: One task blocks all others")
    print("• Threading: Multiple threads, shared memory, GIL limitations")
    print("• Multiprocessing: Separate processes, isolated memory, true parallelism")
    print("• Async: Single thread, cooperative yielding, event loop")
    print("• Mixed: Strategic combination based on task dependencies")
    print("\n🎯 CHOOSE BASED ON:")
    print("• I/O-bound tasks → Threading or Async")
    print("• CPU-bound tasks → Multiprocessing")
    print("• Mixed workloads → Combined approach")
    print("=" * 40)


if __name__ == "__main__":
    main()
