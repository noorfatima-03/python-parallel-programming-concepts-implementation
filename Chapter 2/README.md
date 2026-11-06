# Chapter 2 – Python Parallel Programming Concepts

## Project: Smart Supermarket Order Processing System

### 1. Introduction

This project is a scenario-based implementation of Python parallel programming concepts, developed as part of Chapter 2.

The project simulates an online supermarket where multiple customers place orders simultaneously. These orders are processed by different worker threads while the system manages product inventory, packing operations, and sales records.

The main objective of this implementation is to understand how multithreading works in Python and how synchronization techniques help coordinate multiple threads when they access shared resources.

Instead of implementing each threading technique separately, this project combines multiple concepts into one practical application.

---

### 2. Scenario Description

Consider an online supermarket receiving orders from different customers.

For example:
- Ali orders rice and milk.
- Sara orders bread and eggs.
- Ahmed orders rice and apples.
- Ayesha orders milk and bread.

The supermarket has three worker threads responsible for processing customer orders.

Each worker retrieves an order from the order queue, checks product availability, reserves the required inventory, and packs the order.

However, multiple workers may try to access the same inventory simultaneously. Some products may also be unavailable when an order is received.

To handle these situations, different synchronization mechanisms are implemented.

The system also automatically restocks products and maintains a record of completed orders and total sales.

---

### 3. Python Concepts Implemented

#### 1. Threading and Custom Thread Classes

The `threading.Thread` class is used to create multiple worker threads.

Custom classes such as `OrderWorker`, `OrderProducer`, and `RestockingThread` inherit from the Thread class and implement their own `run()` methods.

This allows different tasks, such as receiving orders, processing orders, and restocking products, to execute concurrently.

#### 2. Lock

A `threading.Lock()` is used to protect shared sales statistics.

Since multiple workers can complete orders at the same time, they may attempt to update the total sales and completed order count simultaneously.

The lock ensures that only one worker updates these shared variables at a time, preventing race conditions.

#### 3. RLock (Reentrant Lock)

A `threading.RLock()` is used for inventory management.

In this implementation, the `purchase_products()` method acquires the inventory lock and then calls `remove_stock()`, which acquires the same lock again.

A normal Lock would block the thread when it tries to acquire a lock it already owns. An RLock allows the same thread to acquire the lock multiple times.

This demonstrates the purpose of reentrant locking.

#### 4. Condition

A `threading.Condition()` is used to coordinate workers when products are unavailable.

If a customer order requires more products than are currently available, the worker waits instead of proceeding with an incomplete order.

When the inventory is restocked, the restocking thread calls `notify_all()` to wake up waiting workers.

The condition uses the inventory lock to protect shared stock data.

#### 5. Event

A `threading.Event()` is used for signaling between threads.

The `orders_ready` event informs workers that the producer has submitted all customer orders.

The `stop_restocking` event signals the restocking thread when it should stop executing.

Events allow one thread to signal another without continuously checking a shared variable.

#### 6. Semaphore

A `threading.Semaphore(2)` is used to control packing operations.

Although three workers are available, only two workers can pack orders simultaneously.

The third worker must wait until one of the packing slots becomes available.

This demonstrates how a semaphore controls access to a limited number of shared resources.

#### 7. Barrier

A `threading.Barrier(3)` is used to synchronize the three worker threads.

All three workers must reach the barrier before any of them can proceed with order processing.

This ensures that the workers begin the processing stage together.

#### 8. Queue

The `queue.Queue()` class is used to transfer customer orders from the producer to the workers.

The producer adds orders to the queue, and available workers retrieve them for processing.

A queue is thread-safe, which means multiple threads can safely add and retrieve items without manually implementing synchronization for the queue itself.

#### 9. join()

The `join()` method is used to make the main thread wait for other threads to complete their execution.

It ensures that the final sales report is displayed only after all customer orders have been processed and the worker threads have finished.

The queue's `join()` method is also used to wait until all submitted orders and shutdown signals have been handled.

---

### 4. Program Workflow

The overall execution follows these steps:

1. The supermarket system initializes its inventory and shared resources.
2. The restocking thread starts.
3. Three worker threads are created.
4. The order producer receives and submits customer orders to the queue.
5. Workers wait for the producer's readiness signal.
6. All workers synchronize at the barrier.
7. Workers retrieve orders from the queue.
8. Each worker checks the availability of the requested products.
9. If products are unavailable, the worker waits using the Condition mechanism.
10. The restocking thread updates the inventory and notifies waiting workers.
11. Workers reserve inventory and pack orders.
12. The semaphore ensures that no more than two workers pack simultaneously.
13. The Lock protects shared sales statistics.
14. After all orders are completed, the system shuts down its threads and displays the final report.

---

### 5. Sample Output

The following is an illustrative example of the type of output generated when the program runs. Actual execution order and timestamps may vary because threads execute concurrently.

```text
SMART SUPERMARKET SYSTEM STARTED

OrderProducer: Customer orders are arriving.

OrderProducer: New Order 101 received from Ali
OrderProducer: New Order 102 received from Sara
OrderProducer: New Order 103 received from Ahmed

Worker-1: Worker started processing orders.
Worker-2: Worker started processing orders.
Worker-3: Worker started processing orders.

Worker-1: Processing Order 101 for Ali
Worker-2: Processing Order 102 for Sara

Worker-3: Insufficient stock for Order 103. Waiting for restock.

RestockingThread: Inventory restocked

Worker-3: Inventory updated for Order 103
Worker-1: Order 101 successfully packed.
Worker-2: Order 102 successfully packed.

Worker-1: Order 101 completed. Sales so far: Rs. 1250

========== DAILY SALES REPORT ==========

Total orders completed: 6
Total sales: Rs. 6050

System shutdown successfully.
```

*Note: This is a simplified illustrative output, not a guaranteed exact terminal transcript.*

---

### 6. Learning Outcomes

Through this implementation, I learned:

- How to create and manage multiple threads in Python.
- How custom thread classes can be used to organize concurrent tasks.
- Why synchronization is necessary when multiple threads access shared data.
- How locks prevent race conditions.
- How RLock supports nested lock acquisition by the same thread.
- How Condition allows threads to wait for a particular condition and resume when notified.
- How Event provides signaling between threads.
- How Semaphore controls access to limited resources.
- How Barrier synchronizes multiple threads at a common execution point.
- How Queue enables safe communication between producer and consumer threads.
- How join() ensures proper thread completion.

Most importantly, this project helped me understand that multithreading is not simply about running multiple tasks simultaneously. It also requires proper coordination, communication, and synchronization to maintain data consistency.

---

### 7. Technologies and Libraries

- Python 3
- threading
- queue
- logging
- random
- time
- os

All libraries used in this project are part of Python's standard library. No additional package installation is required.

---

### 8. How to Run

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/python-parallel-programming-concepts-implementation.git
```

Navigate to the Chapter 2 folder:

```bash
cd "python-parallel-programming-concepts-implementation/Chapter 2"
```

Run the program:

```bash
python implementation.py
```

---

### 9. Conclusion

This project combines several Python parallel programming and synchronization techniques into a single practical scenario.

By simulating a supermarket order processing system, I explored how multiple threads can perform independent tasks while safely interacting with shared resources.

The implementation demonstrates the importance of thread synchronization, resource management, and inter-thread communication in developing concurrent applications.
