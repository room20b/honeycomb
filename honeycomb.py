#!/usr/bin/env python3

import os
import sys
import json
import uuid
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any

# ----- Context Database -----
class ContextDB:
    def __init__(self, db_path="context.json"):
        self.db_path = db_path
        self.load_or_create_db()
    
    def load_or_create_db(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as f:
                self.db = json.load(f)
        else:
            self.db = {
                "tasks": [],
                "context": [],
                "agents": []
            }
            self.save_db()
    
    def save_db(self):
        with open(self.db_path, 'w') as f:
            json.dump(self.db, f, indent=2)
    
    def add_task(self, task_data):
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            **task_data
        }
        self.db["tasks"].append(task)
        self.save_db()
        return task_id
    
    def update_task(self, task_id, updates):
        for task in self.db["tasks"]:
            if task["id"] == task_id:
                task.update(updates)
                self.save_db()
                return True
        return False
    
    def get_task(self, task_id):
        for task in self.db["tasks"]:
            if task["id"] == task_id:
                return task
        return None
    
    def get_tasks_by_status(self, status):
        return [task for task in self.db["tasks"] if task["status"] == status]
    
    def add_context(self, context_data):
        context_id = str(uuid.uuid4())
        context = {
            "id": context_id,
            "created_at": datetime.now().isoformat(),
            **context_data
        }
        self.db["context"].append(context)
        self.save_db()
        return context_id
    
    def get_latest_context(self, limit=10):
        return sorted(self.db["context"], key=lambda x: x["created_at"], reverse=True)[:limit]
    
    def register_agent(self, agent_data):
        agent_id = str(uuid.uuid4())
        agent = {
            "id": agent_id,
            "registered_at": datetime.now().isoformat(),
            "status": "idle",
            **agent_data
        }
        self.db["agents"].append(agent)
        self.save_db()
        return agent_id
    
    def update_agent(self, agent_id, updates):
        for agent in self.db["agents"]:
            if agent["id"] == agent_id:
                agent.update(updates)
                self.save_db()
                return True
        return False
    
    def get_all_agents(self):
        return self.db["agents"]

# ----- Base Agent Class -----
class Agent:
    def __init__(self, name, specialty, context_db):
        self.name = name
        self.specialty = specialty
        self.context_db = context_db
        self.agent_id = self._register()
    
    def _register(self):
        return self.context_db.register_agent({
            "name": self.name,
            "specialty": self.specialty
        })
    
    async def process_task(self, task):
        """Process a task and return the result. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement process_task")
    
    def update_status(self, status):
        self.context_db.update_agent(self.agent_id, {"status": status})

# ----- Task Queue -----
class TaskQueue:
    def __init__(self, context_db):
        self.context_db = context_db
    
    def add_task(self, description, task_type, params=None):
        if params is None:
            params = {}
        
        return self.context_db.add_task({
            "description": description,
            "type": task_type,
            "params": params
        })
    
    def get_pending_tasks(self):
        return self.context_db.get_tasks_by_status("pending")
    
    def assign_task(self, task_id, agent_id):
        return self.context_db.update_task(task_id, {
            "status": "assigned",
            "agent_id": agent_id,
            "assigned_at": datetime.now().isoformat()
        })
    
    def complete_task(self, task_id, result):
        return self.context_db.update_task(task_id, {
            "status": "completed",
            "result": result,
            "completed_at": datetime.now().isoformat()
        })

# ----- Task Coordinator -----
class TaskCoordinator:
    def __init__(self, context_db, agents=None):
        self.context_db = context_db
        self.task_queue = TaskQueue(context_db)
        self.agents = agents or []
    
    def register_agent(self, agent):
        self.agents.append(agent)
    
    def find_suitable_agent(self, task):
        # Simple matching by task type to agent specialty
        for agent in self.agents:
            if agent.specialty == task["type"]:
                return agent
        return None
    
    async def process_pending_tasks(self):
        pending_tasks = self.task_queue.get_pending_tasks()
        if not pending_tasks:
            return "No pending tasks."
        
        results = []
        for task in pending_tasks:
            agent = self.find_suitable_agent(task)
            if not agent:
                results.append(f"No suitable agent found for task: {task['id']}")
                continue
            
            # Assign task to agent
            self.task_queue.assign_task(task["id"], agent.agent_id)
            agent.update_status("busy")
            
            # Process task
            try:
                result = await agent.process_task(task)
                self.task_queue.complete_task(task["id"], result)
                results.append(f"Task {task['id']} completed by {agent.name}")
            except Exception as e:
                self.context_db.update_task(task["id"], {
                    "status": "failed",
                    "error": str(e)
                })
                results.append(f"Task {task['id']} failed: {str(e)}")
            finally:
                agent.update_status("idle")
        
        return "\n".join(results)

# ----- UI Functions -----
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("=" * 50)
    print(" " * 15 + "HONEYCOMB AI SWARM" + " " * 15)
    print("=" * 50)
    print()

def print_menu():
    print("1. List Agents")
    print("2. List Tasks")
    print("3. Add Task")
    print("4. Process Pending Tasks")
    print("5. View Latest Context")
    print("6. Generate Daily Summary")
    print("7. Exit")
    print()

def print_agents(context_db):
    agents = context_db.get_all_agents()
    print("\n" + "=" * 50)
    print(" " * 20 + "AGENTS" + " " * 20)
    print("=" * 50)
    
    if not agents:
        print("No agents registered yet.")
        return
    
    for agent in agents:
        print(f"ID: {agent['id'][:8]}...")
        print(f"Name: {agent['name']}")
        print(f"Specialty: {agent['specialty']}")
        print(f"Status: {agent['status']}")
        print("-" * 50)

def print_tasks(context_db):
    tasks = context_db.db["tasks"]
    print("\n" + "=" * 50)
    print(" " * 20 + "TASKS" + " " * 20)
    print("=" * 50)
    
    if not tasks:
        print("No tasks available.")
        return
    
    for task in tasks:
        print(f"ID: {task['id'][:8]}...")
        print(f"Description: {task['description']}")
        print(f"Type: {task['type']}")
        print(f"Status: {task['status']}")
        if task.get("agent_id"):
            print(f"Assigned to: {task['agent_id'][:8]}...")
        if task.get("result"):
            # For dictionary results (like from CommandAgent)
            if isinstance(task["result"], dict):
                print(f"Result: Command executed with return code {task['result'].get('return_code', 'unknown')}")
                if task["result"].get("stdout"):
                    stdout = task["result"]["stdout"]
                    print(f"Output: {stdout[:50]}..." if len(stdout) > 50 else f"Output: {stdout}")
            else:
                # For text results
                result_str = str(task["result"])
                print(f"Result: {result_str[:50]}..." if len(result_str) > 50 else f"Result: {result_str}")
        print("-" * 50)

def print_context(context_db):
    context = context_db.get_latest_context()
    print("\n" + "=" * 50)
    print(" " * 18 + "LATEST CONTEXT" + " " * 18)
    print("=" * 50)
    
    if not context:
        print("No context entries available.")
        return
    
    for entry in context:
        print(f"Created: {entry['created_at']}")
        print(f"Type: {entry.get('type', 'general')}")
        print(f"Content: {entry.get('content', '')[:100]}..." if len(entry.get('content', '')) > 100 else f"Content: {entry.get('content', '')}")
        print("-" * 50)

def parse_json_params(params_str):
    if not params_str:
        return {}
    
    try:
        return json.loads(params_str)
    except json.JSONDecodeError:
        print("Invalid JSON format. Using empty params.")
        return {}

# ----- Main Application -----
async def main():
    context_db = ContextDB()
    coordinator = TaskCoordinator(context_db)
    
    # Import our agent implementations
    from agents import WritingAgent, CodingAgent, ResearchAgent, CommandAgent, ContextSummarizerAgent
    
    # Register agents
    coordinator.register_agent(WritingAgent("WriteBot", context_db))
    coordinator.register_agent(CodingAgent("CodeBot", context_db))
    coordinator.register_agent(ResearchAgent("ResearchBot", context_db))
    coordinator.register_agent(CommandAgent("CommandBot", context_db))
    coordinator.register_agent(ContextSummarizerAgent("SummaryBot", context_db))
    
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        choice = input("Enter your choice (1-7): ")
        
        if choice == '1':
            print_agents(context_db)
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            print_tasks(context_db)
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            print("\nAvailable Task Types:")
            print("- writing: Create written content")
            print("- coding: Generate or modify code")
            print("- research: Research a topic")
            print("- command: Execute a shell command")
            print("- context_summary: Summarize recent context")
            print()
            
            description = input("Enter task description: ")
            task_type = input("Enter task type: ")
            
            # Get specific parameters based on task type
            params = {}
            if task_type == "writing":
                tone = input("Enter tone (casual, professional, formal, etc) [default: professional]: ")
                length = input("Enter desired length (short, medium, long) [default: medium]: ")
                
                if tone:
                    params["tone"] = tone
                if length:
                    params["length"] = length
                    
            elif task_type == "coding":
                language = input("Enter programming language [default: python]: ")
                file_path = input("Enter file path to save code (optional): ")
                
                if language:
                    params["language"] = language
                if file_path:
                    params["file_path"] = file_path
                    
            elif task_type == "research":
                depth = input("Enter research depth (brief, medium, detailed) [default: medium]: ")
                
                if depth:
                    params["depth"] = depth
                    
            elif task_type == "command":
                command = input("Enter shell command to execute: ")
                if command:
                    params["command"] = command
                else:
                    print("Command is required for this task type.")
                    input("\nPress Enter to continue...")
                    continue
                    
            elif task_type == "context_summary":
                limit_str = input("Enter number of entries to summarize [default: 20]: ")
                if limit_str:
                    try:
                        params["limit"] = int(limit_str)
                    except ValueError:
                        print("Invalid number, using default.")
            
            # Allow for custom JSON parameters
            use_custom = input("Do you want to enter custom JSON parameters? (y/n) [default: n]: ").lower() == 'y'
            if use_custom:
                custom_params = input("Enter parameters as JSON: ")
                try:
                    params = json.loads(custom_params)
                except json.JSONDecodeError:
                    print("Invalid JSON. Using previously entered params.")
            
            task_id = coordinator.task_queue.add_task(description, task_type, params)
            print(f"Task added with ID: {task_id}")
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            print("Processing pending tasks...")
            result = await coordinator.process_pending_tasks()
            print(result)
            input("\nPress Enter to continue...")
        
        elif choice == '5':
            print_context(context_db)
            input("\nPress Enter to continue...")
            
        elif choice == '6':
            print("Generating daily summary...")
            # Create a summary task and process it immediately
            task_id = coordinator.task_queue.add_task(
                "Generate daily summary of all context", 
                "context_summary",
                {"limit": 50}
            )
            
            summary_agent = None
            for agent in coordinator.agents:
                if agent.specialty == "context_summary":
                    summary_agent = agent
                    break
            
            if summary_agent:
                task = context_db.get_task(task_id)
                coordinator.task_queue.assign_task(task_id, summary_agent.agent_id)
                summary_agent.update_status("busy")
                
                try:
                    result = await summary_agent.process_task(task)
                    coordinator.task_queue.complete_task(task_id, result)
                    print("\nSummary generated successfully:")
                    print("-" * 50)
                    print(result)
                    print("-" * 50)
                except Exception as e:
                    print(f"Error generating summary: {str(e)}")
                finally:
                    summary_agent.update_status("idle")
            else:
                print("No summary agent found.")
            
            input("\nPress Enter to continue...")
        
        elif choice == '7':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice, please try again.")
            time.sleep(1)

if __name__ == "__main__":
    asyncio.run(main()) 