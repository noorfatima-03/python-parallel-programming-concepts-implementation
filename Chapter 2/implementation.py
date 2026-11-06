import threading
import time
import random
import os
import logging
from queue import Queue

# ==========================================
# CONFIGURATION AND LOGGING
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(threadName)-15s | %(message)s',
    datefmt='%H:%M:%S'
)

# Number of workers
NUM_WORKERS = 3

# Shared resources
order_queue = Queue()

# Event: Workers wait until orders are ready
orders_ready = threading.Event()

# Barrier: All workers start processing together
start_barrier = threading.Barrier(NUM_WORKERS)

# Semaphore: Only 2 workers can pack orders at once
packing_slots = threading.Semaphore(2)

# Lock: Protect shared sales statistics
sales_lock = threading.Lock()

# Event: Stop the restocking thread
stop_restocking = threading.Event()

# Shared statistics
total_sales = 0
completed_orders = 0


# ==========================================
# INVENTORY MANAGEMENT USING RLOCK
# AND CONDITION
# ==========================================

class Inventory:

    def __init__(self):
        self.stock = {
            'Rice': 3,
            'Milk': 2,
            'Bread': 2,
            'Eggs': 4,
            'Apples': 3
        }

        # RLock allows the same thread to acquire
        # the lock multiple times.
        self.lock = threading.RLock()

        # Condition coordinates inventory access
        self.condition = threading.Condition(self.lock)

    def remove_stock(self, product, quantity):

        # This method acquires the RLock.
        with self.lock:
            self.stock[product] -= quantity

    def purchase_products(self, order):

        with self.condition:

            # Wait until all requested products are available.
            while any(
                self.stock.get(product, 0) < quantity
                for product, quantity in order['items'].items()
            ):

                logging.info(
                    'Insufficient stock for Order %s. Waiting for restock.',
                    order['id']
                )

                self.condition.wait()

            # Nested lock acquisition demonstrates RLock.
            for product, quantity in order['items'].items():
                self.remove_stock(product, quantity)

            logging.info(
                'Inventory updated for Order %s',
                order['id']
            )

    def restock(self):

        with self.condition:

            for product in self.stock:
                self.stock[product] += 3

            logging.info(
                'Inventory restocked: %s',
                self.stock
            )

            # Wake up workers waiting for stock.
            self.condition.notify_all()


# Create shared inventory
inventory = Inventory()


# ==========================================
# ORDER PRODUCER USING CUSTOM THREAD CLASS
# ==========================================

class OrderProducer(threading.Thread):

    def __init__(self, queue, orders):
        super().__init__(name='OrderProducer')
        self.queue = queue
        self.orders = orders

    def run(self):

        logging.info('Customer orders are arriving.')

        for order in self.orders:

            self.queue.put(order)

            logging.info(
                'New Order %s received from %s',
                order['id'],
                order['customer']
            )

            time.sleep(0.5)

        # Send shutdown signals to workers.
        for i in range(NUM_WORKERS):
            self.queue.put(None)

        # Notify workers that orders are ready.
        orders_ready.set()

        logging.info('All customer orders have been submitted.')


# ==========================================
# ORDER PROCESSING WORKER
# USING THREAD CLASS, BARRIER,
# EVENT, SEMAPHORE AND QUEUE
# ==========================================

class OrderWorker(threading.Thread):

    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def run(self):

        logging.info(
            'Worker created. Process ID: %s',
            os.getpid()
        )

        # Wait until the producer has submitted orders.
        orders_ready.wait()

        # All workers must reach this point before continuing.
        start_barrier.wait()

        logging.info('Worker started processing orders.')

        while True:

            order = self.queue.get()

            try:

                # None means there are no more orders.
                if order is None:
                    logging.info('No more orders. Worker exiting.')
                    break

                self.process_order(order)

            finally:
                self.queue.task_done()

    def process_order(self, order):

        global total_sales, completed_orders

        logging.info(
            'Processing Order %s for %s',
            order['id'],
            order['customer']
        )

        # Check and reserve inventory.
        inventory.purchase_products(order)

        # Semaphore limits packing to 2 workers.
        with packing_slots:

            logging.info(
                'Packing Order %s',
                order['id']
            )

            time.sleep(random.uniform(1, 2))

            logging.info(
                'Order %s successfully packed.',
                order['id']
            )

        # Lock protects shared statistics.
        with sales_lock:

            total_sales += order['total']
            completed_orders += 1

            logging.info(
                'Order %s completed. Sales so far: Rs. %s',
                order['id'],
                total_sales
            )


# ==========================================
# AUTOMATIC RESTOCKING THREAD
# USING EVENT AND CONDITION
# ==========================================

class RestockingThread(threading.Thread):

    def __init__(self):
        super().__init__(name='RestockingThread')
        self.daemon = True

    def run(self):

        while not stop_restocking.wait(1.5):

            inventory.restock()


# ==========================================
# CUSTOMER ORDER DATA
# ==========================================

orders = [

    {
        'id': 101,
        'customer': 'Ali',
        'items': {'Rice': 2, 'Milk': 1},
        'total': 1250
    },

    {
        'id': 102,
        'customer': 'Sara',
        'items': {'Bread': 2, 'Eggs': 2},
        'total': 650
    },

    {
        'id': 103,
        'customer': 'Ahmed',
        'items': {'Rice': 3, 'Apples': 2},
        'total': 1400
    },

    {
        'id': 104,
        'customer': 'Ayesha',
        'items': {'Milk': 3, 'Bread': 1},
        'total': 900
    },

    {
        'id': 105,
        'customer': 'Usman',
        'items': {'Eggs': 3, 'Apples': 2},
        'total': 750
    },

    {
        'id': 106,
        'customer': 'Fatima',
        'items': {'Rice': 2, 'Milk': 2},
        'total': 1100
    }
]


# ==========================================
# MAIN FUNCTION
# ==========================================

def main():

    logging.info('SMART SUPERMARKET SYSTEM STARTED')

    # Start automatic restocking.
    restocker = RestockingThread()
    restocker.start()

    # Create and start worker threads.
    workers = []

    for i in range(NUM_WORKERS):

        worker = OrderWorker(order_queue)
        worker.name = 'Worker-' + str(i + 1)

        workers.append(worker)
        worker.start()

    # Start order producer.
    producer = OrderProducer(order_queue, orders)
    producer.start()

    # Wait for producer to finish.
    producer.join()

    # Wait until all orders and shutdown signals
    # have been processed.
    order_queue.join()

    # Wait for all workers.
    for worker in workers:
        worker.join()

    # Stop automatic restocking.
    stop_restocking.set()

    # Wake up the restocker if it is waiting.
    with inventory.condition:
        inventory.condition.notify_all()

    restocker.join()

    # Display final report.
    print('\n========== DAILY SALES REPORT ==========')
    print('Total orders completed:', completed_orders)
    print('Total sales: Rs.', total_sales)
    print('Remaining inventory:', inventory.stock)
    print('System shutdown successfully.')
    print('========================================')


if __name__ == '__main__':
    main()
