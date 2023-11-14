import sys
import threading
from queue import Queue
from time import sleep

# Global exception handler 
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        print(f"\nHandled!")
        sys.exit(0)

sys.excepthook = handle_exception

# Thread-safe queue
task_queue = Queue() 

# Helper functions for tasks
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

def find_min_max(numbers):
    return min(numbers), max(numbers)    

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0:
            return False
    return True

# Worker thread
def worker():
    while True:
        task, args = task_queue.get()
        if task == 'fib':
            print(fib(args[0]))
        elif task == 'min_max':
           print(find_min_max(args[0]))
        else:
            print(is_prime(args[0]))
        task_queue.task_done()

# Create worker thread    
threading.Thread(target=worker, daemon=True).start()

def main():
    choices = {
        '1': ('fib', [10]),
        '2': ('min_max', [[1, 5, 2, 20]]),
        '3': ('is_prime', [17])
    }
    
    print("Menu")
    print("\n".join(f"{k}) {v[0]}" for k, v in choices.items()))
    
    while True:
        sleep(0.1)
        choice = input("Enter choice: ").lower()
        if choice in choices:
            task_queue.put(choices[choice])
        else:
            print(f"Not within bounds boi.")

main()