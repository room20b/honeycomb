# honeycomb

## Overview

The **honeycomb** is a context-aware system that enables multiple AI agents to collaborate on a variety of tasks, such as writing, coding, research, and more. Unlike traditional AI tools focused on single tasks, this system allows a swarm of agents to work simultaneously, sharing a common context to provide more cohesive and efficient results. The initial version is designed as a minimal viable product (MVP) with a focus on simplicity, scalability, and future extensibility.

### Features

- **Multi-Agent Collaboration**: Specialized agents handle different tasks (e.g., writing, coding, creative idea gen) and can work concurrently.
- **Shared Context**: A local database (ContextDB) maintains a shared context across all agents, ensuring they stay aligned.
- **Task Queue**: A simple task queue manages concurrent task processing.
- **Command-Line Interface (CLI)**: Users can easily interact with the system via a CLI to add, view, and manage tasks.
- **Modular Design**: The system is built to be extended with more agents, tasks, and features over time.

### Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-repo/ai-assistant-swarm.git
   cd ai-assistant-swarm
   ```

2. **Install Dependencies**:

   - Ensure you have Python 3.x installed.
   - Install required packages:

     ```bash
     pip install requests
     ```

3. **Set Up the Database**:

   - The system uses a local SQLite database (`contextdb.sqlite`), which is automatically created when you run the script for the first time.

4. **Run the System**:

   - Start the CLI by running:

     ```bash
     python ai_swarm.py
     ```

### Usage

Once the system is running, you can interact with it via the CLI using the following commands:

- `add <type> <description>`: Add a new task.
  - Example: `add write Summarize the benefits of AI`
  - Supported types: `write`, `code`, `research`
- `view`: List all tasks and their statuses.
- `review <task_id> [approve]`: Review a task's result. Use `approve` to add the result to the shared context.
  - Example: `review 1 approve`
- `context`: View the current shared context.
- `exit`: Quit the CLI.

### Configuration

- **Database**: The system uses a local SQLite database by default. You can modify the database path in `ai_swarm.py` if needed.
- **Agents**: The system currently supports basic agents for writing and coding. You can extend this by adding more agents in the `agents` directory.

### Troubleshooting

- **Database Errors**: Ensure the database file (`contextdb.sqlite`) is not locked or corrupted. Delete the file to reset the database.
- **Task Processing Issues**: Check if the task type is supported. Only `write`, `code`, and `research` are currently available.

### Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. For major updates, open an issue first to discuss your ideas.

---

This project is licensed under the MIT License. See the LICENSE file for details.