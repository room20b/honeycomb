#!/usr/bin/env python3
import asyncio
import os
import json
from honeycomb import ContextDB, TaskCoordinator
from agents import WritingAgent, CodingAgent, ResearchAgent, CommandAgent, ContextSummarizerAgent

async def run_example():
    """Run a demonstration of the Honeycomb AI Swarm system."""
    print("=" * 50)
    print(" " * 15 + "HONEYCOMB AI SWARM DEMO" + " " * 15)
    print("=" * 50)
    print()
    
    # Initialize ContextDB with a demo database file
    context_db = ContextDB("demo_context.json")
    
    # Set up the coordinator and agents
    coordinator = TaskCoordinator(context_db)
    
    # Register agents
    print("Registering agents...")
    coordinator.register_agent(WritingAgent("WriteBot", context_db))
    coordinator.register_agent(CodingAgent("CodeBot", context_db))
    coordinator.register_agent(ResearchAgent("ResearchBot", context_db))
    coordinator.register_agent(CommandAgent("CommandBot", context_db))
    coordinator.register_agent(ContextSummarizerAgent("SummaryBot", context_db))
    print("All agents registered successfully!\n")
    
    # Add example tasks
    print("Adding example tasks...")
    
    # Add a writing task
    writing_task_id = coordinator.task_queue.add_task(
        "Write a short paragraph about AI collaboration",
        "writing",
        {
            "tone": "enthusiastic",
            "length": "short"
        }
    )
    print(f"Added writing task with ID: {writing_task_id}")
    
    # Add a coding task
    coding_task_id = coordinator.task_queue.add_task(
        "Write a Python function to calculate Fibonacci numbers",
        "coding",
        {
            "language": "python",
            "file_path": "fibonacci.py"
        }
    )
    print(f"Added coding task with ID: {coding_task_id}")
    
    # Add a research task
    research_task_id = coordinator.task_queue.add_task(
        "Research the benefits of multi-agent AI systems",
        "research",
        {
            "depth": "brief"
        }
    )
    print(f"Added research task with ID: {research_task_id}")
    
    # Add a command task to list files
    command_task_id = coordinator.task_queue.add_task(
        "List files in the current directory",
        "command",
        {
            "command": "ls -la"
        }
    )
    print(f"Added command task with ID: {command_task_id}")
    
    print("\nProcessing all tasks...")
    result = await coordinator.process_pending_tasks()
    print(result)
    
    print("\nGenerating context summary...")
    summary_task_id = coordinator.task_queue.add_task(
        "Summarize all recent context",
        "context_summary",
        {
            "limit": 20
        }
    )
    
    # Find the summary agent
    summary_agent = None
    for agent in coordinator.agents:
        if agent.specialty == "context_summary":
            summary_agent = agent
            break
    
    if summary_agent:
        task = context_db.get_task(summary_task_id)
        coordinator.task_queue.assign_task(summary_task_id, summary_agent.agent_id)
        summary_agent.update_status("busy")
        
        try:
            result = await summary_agent.process_task(task)
            coordinator.task_queue.complete_task(summary_task_id, result)
            print("\nContext Summary:")
            print("-" * 50)
            print(result)
            print("-" * 50)
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
        finally:
            summary_agent.update_status("idle")
    
    print("\nDemonstration completed!")
    print("\nYou can explore the full app by running:")
    print("python honeycomb.py")

if __name__ == "__main__":
    # Check for API keys
    if not os.environ.get("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY environment variable is not set!")
        print("Some features may not work without API keys.")
        print("Set your API keys with:")
        print("export OPENAI_API_KEY=your_api_key")
        choice = input("Continue anyway? (y/n): ")
        if choice.lower() != 'y':
            exit(1)
    
    asyncio.run(run_example()) 