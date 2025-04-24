# Honeycomb AI Swarm

A multi-agent AI system that enables collaborative task execution with a shared context database. Honeycomb allows specialized AI agents to work together, share knowledge, and tackle a variety of tasks efficiently.

## Features

- **Multiple Specialized Agents**: Writing, coding, research, command execution, and context summarization
- **Shared Context Database**: All agents share and reference the same knowledge base
- **Task Assignment**: Tasks are automatically routed to the most suitable agent
- **Task Queue**: Manage and track tasks through their lifecycle
- **Context Persistence**: Knowledge and decisions are preserved across tasks
- **Terminal UI**: Simple, clean interface for interaction

## Setup

1. Clone this repository:
```
git clone https://github.com/yourusername/honeycomb.git
cd honeycomb
```

2. Install required packages:
```
pip install requests
```

3. Set up your API keys as environment variables:
```
# For macOS/Linux
export OPENAI_API_KEY="your_openai_api_key"
export ANTHROPIC_API_KEY="your_anthropic_api_key"  # Optional

# For Windows
set OPENAI_API_KEY=your_openai_api_key
set ANTHROPIC_API_KEY=your_anthropic_api_key  # Optional
```

## Usage

Run the main application:
```
python honeycomb.py
```

The terminal interface will guide you through the following options:

1. **List Agents**: View all registered AI agents
2. **List Tasks**: View all tasks and their statuses
3. **Add Task**: Create a new task and assign it to an agent
4. **Process Pending Tasks**: Execute all pending tasks
5. **View Latest Context**: See the most recent context entries
6. **Generate Daily Summary**: Create a summary of recent context
7. **Exit**: Close the application

### Task Types

- **writing**: Create written content with specified tone and length
- **coding**: Generate code in various languages, optionally save to file
- **research**: Research a topic and provide a comprehensive summary
- **command**: Execute shell commands and capture output
- **context_summary**: Summarize recent context entries for other agents

## Architecture

- **ContextDB**: Simple JSON-based database for storing tasks, context, and agent information
- **Agent**: Base class for all specialized agents
- **TaskQueue**: Manages task creation and status updates
- **TaskCoordinator**: Assigns tasks to appropriate agents and manages execution

## Custom Parameters

Each task type accepts specific parameters:

- **writing**:
  - `tone`: Casual, professional, formal, etc.
  - `length`: Short, medium, long
  
- **coding**:
  - `language`: Python, JavaScript, etc.
  - `file_path`: Path to save the generated code
  
- **research**:
  - `depth`: Brief, medium, detailed
  
- **command**:
  - `command`: Shell command to execute
  
- **context_summary**:
  - `limit`: Number of context entries to summarize

## Future Enhancements

- Web interface for better visualization
- Concurrent task processing
- More agent types and specializations
- Advanced context management with vector databases
- Integration with external tools and platforms