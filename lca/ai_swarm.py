import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
import time
import sys

DB_FILE = "contextdb.sqlite"
MAX_WORKERS = 5

db_lock = threading.Lock()

def init_db():
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS tasks
                     (id INTEGER PRIMARY KEY, type TEXT, description TEXT, status TEXT, result TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS context
                     (id INTEGER PRIMARY KEY, summary TEXT)''')
        c.execute("INSERT OR IGNORE INTO context (id, summary) VALUES (1, '')")
        conn.commit()
        conn.close()

def add_task(type, description, executor):
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO tasks (type, description, status) VALUES (?, ?, 'pending')", (type, description))
        task_id = c.lastrowid
        conn.commit()
        conn.close()
    executor.submit(process_task, task_id)

def process_task(task_id):
    time.sleep(2)  # Simulate processing time
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT type, description FROM tasks WHERE id=?", (task_id,))
        type, description = c.fetchone()
        if type == 'write':
            result = f"This is a dummy writing result for: {description}"
        elif type == 'code':
            result = f"def dummy_function(): pass  # Dummy code for: {description}"
        elif type == 'research':
            result = f"Research findings on: {description}"
        else:
            result = "Unsupported task type"
        c.execute("UPDATE tasks SET status='completed', result=? WHERE id=?", (result, task_id))
        conn.commit()
        conn.close()

def view_tasks():
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, type, description, status, result FROM tasks")
        tasks = c.fetchall()
        conn.close()
    for task in tasks:
        print(f"ID: {task[0]}, Type: {task[1]}, Description: {task[2]}, Status: {task[3]}")
        if task[4]:
            print(f"Result: {task[4]}\n")

def review_task(task_id, approve=False):
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT status, result FROM tasks WHERE id=?", (task_id,))
        row = c.fetchone()
        if row:
            status, result = row
            if status == 'completed':
                print(f"Result: {result}")
                if approve:
                    update_context(result)
                    print("Context updated.")
            else:
                print("Task not completed yet.")
        else:
            print("Task not found.")
        conn.close()

def get_context():
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT summary FROM context WHERE id=1")
        summary = c.fetchone()[0]
        conn.close()
    return summary

def update_context(new_info):
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        current = get_context()
        updated = f"{current}\n{new_info}" if current else new_info
        c.execute("UPDATE context SET summary=? WHERE id=1", (updated,))
        conn.commit()
        conn.close()

def main():
    init_db()
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)
    print("AI Assistant Swarm CLI. Type 'help' for commands.")
    while True:
        cmd = input("> ").strip().split()
        if not cmd:
            continue
        action = cmd[0].lower()
        if action == "add":
            if len(cmd) < 3:
                print("Usage: add <type> <description>")
            else:
                task_type = cmd[1].lower()
                description = " ".join(cmd[2:])
                add_task(task_type, description, executor)
                print("Task added.")
        elif action == "view":
            view_tasks()
        elif action == "review":
            if len(cmd) < 2:
                print("Usage: review <task_id> [approve]")
            else:
                task_id = int(cmd[1])
                approve = len(cmd) > 2 and cmd[2].lower() == "approve"
                review_task(task_id, approve)
        elif action == "context":
            print(f"Current Context: {get_context()}")
        elif action == "help":
            print("Commands: add <type> <description>, view, review <task_id> [approve], context, exit")
        elif action == "exit":
            print("Exiting...")
            break
        else:
            print("Unknown command. Type 'help' for commands.")

if __name__ == "__main__":
    main()