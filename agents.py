import os
import json
import asyncio
import subprocess
from typing import Dict, Any, List
import requests

# Import our base agent class
from honeycomb import Agent, ContextDB

# You'll need to set your API keys as environment variables
# or replace the os.environ.get calls with your actual keys
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


class WritingAgent(Agent):
    """Agent specialized for writing tasks."""
    
    def __init__(self, name, context_db):
        super().__init__(name, "writing", context_db)
    
    async def process_task(self, task):
        """Process a writing task using OpenAI's API."""
        description = task.get("description", "")
        params = task.get("params", {})
        
        prompt = params.get("prompt", description)
        tone = params.get("tone", "professional")
        length = params.get("length", "medium")
        
        # Fetch context to provide to the model
        context_entries = self.context_db.get_latest_context(5)
        context_text = "\n".join([entry.get("content", "") for entry in context_entries])
        
        # Construct the request to OpenAI
        full_prompt = f"""
Task: {prompt}
Tone: {tone}
Length: {length}

Recent Context:
{context_text}

Please complete the writing task described above, taking into account any relevant context.
"""

        if not OPENAI_API_KEY:
            return "ERROR: OpenAI API key not set. Please set the OPENAI_API_KEY environment variable."
            
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            
            data = {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": full_prompt}],
                "temperature": 0.7
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Add the result to the context for future reference
                self.context_db.add_context({
                    "content": f"Writing task result: {content[:100]}...",
                    "type": "writing_result",
                    "task_id": task["id"]
                })
                
                return content
            else:
                return f"API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error processing writing task: {str(e)}"


class CodingAgent(Agent):
    """Agent specialized for coding tasks."""
    
    def __init__(self, name, context_db):
        super().__init__(name, "coding", context_db)
    
    async def process_task(self, task):
        """Process a coding task using OpenAI's API."""
        description = task.get("description", "")
        params = task.get("params", {})
        
        language = params.get("language", "python")
        file_path = params.get("file_path", "")
        
        # Fetch context to provide to the model
        context_entries = self.context_db.get_latest_context(5)
        context_text = "\n".join([entry.get("content", "") for entry in context_entries])
        
        # Construct the request to OpenAI
        full_prompt = f"""
Task: {description}
Programming Language: {language}
File Path (if applicable): {file_path}

Recent Context:
{context_text}

Please write code that solves the described task, taking into account any relevant context.
Provide clean, efficient, well-documented code that follows best practices.
"""
        
        if not OPENAI_API_KEY:
            return "ERROR: OpenAI API key not set. Please set the OPENAI_API_KEY environment variable."
            
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            
            data = {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": full_prompt}],
                "temperature": 0.2
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Add the result to the context for future reference
                self.context_db.add_context({
                    "content": f"Coding task result: {content[:100]}...",
                    "type": "coding_result",
                    "task_id": task["id"]
                })
                
                # If a file path was provided, save the code to that file
                if file_path:
                    # Extract code from markdown code blocks if present
                    import re
                    code_blocks = re.findall(r'```(?:\w+)?\n([\s\S]+?)\n```', content)
                    
                    if code_blocks:
                        code = code_blocks[0]  # Use the first code block
                    else:
                        code = content  # Use the full content if no code blocks are found
                    
                    try:
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        with open(file_path, 'w') as f:
                            f.write(code)
                        return f"Code saved to {file_path}:\n\n{content}"
                    except Exception as e:
                        return f"Error saving code to file: {str(e)}\n\nCode:\n{content}"
                
                return content
            else:
                return f"API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error processing coding task: {str(e)}"


class ResearchAgent(Agent):
    """Agent specialized for research tasks."""
    
    def __init__(self, name, context_db):
        super().__init__(name, "research", context_db)
    
    async def process_task(self, task):
        """Process a research task using Anthropic's Claude API."""
        description = task.get("description", "")
        params = task.get("params", {})
        
        topic = params.get("topic", description)
        depth = params.get("depth", "medium")
        
        # Fetch context to provide to the model
        context_entries = self.context_db.get_latest_context(5)
        context_text = "\n".join([entry.get("content", "") for entry in context_entries])
        
        # Construct the request to Anthropic
        full_prompt = f"""
Task: Research on {topic}
Depth: {depth}

Recent Context:
{context_text}

Please conduct research on the topic described above, taking into account any relevant context.
Provide a comprehensive summary with key points, insights, and relevant information.
"""
        
        if not ANTHROPIC_API_KEY:
            # Fallback to OpenAI if Anthropic API key is not set
            if not OPENAI_API_KEY:
                return "ERROR: Neither Anthropic nor OpenAI API keys are set. Please set at least one of them."
            
            # Use OpenAI as fallback
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENAI_API_KEY}"
                }
                
                data = {
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": full_prompt}],
                    "temperature": 0.5
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # Add the result to the context for future reference
                    self.context_db.add_context({
                        "content": f"Research task result: {content[:100]}...",
                        "type": "research_result",
                        "task_id": task["id"]
                    })
                    
                    return content
                else:
                    return f"API Error: {response.status_code} - {response.text}"
                    
            except Exception as e:
                return f"Error processing research task: {str(e)}"
        
        try:
            headers = {
                "Content-Type": "application/json",
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-2.1",
                "max_tokens": 4000,
                "prompt": f"\n\nHuman: {full_prompt}\n\nAssistant:",
                "temperature": 0.5
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/complete",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["completion"]
                
                # Add the result to the context for future reference
                self.context_db.add_context({
                    "content": f"Research task result: {content[:100]}...",
                    "type": "research_result",
                    "task_id": task["id"]
                })
                
                return content
            else:
                return f"API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error processing research task: {str(e)}"


class CommandAgent(Agent):
    """Agent specialized for running shell commands."""
    
    def __init__(self, name, context_db):
        super().__init__(name, "command", context_db)
    
    async def process_task(self, task):
        """Execute a shell command and return the result."""
        description = task.get("description", "")
        params = task.get("params", {})
        
        command = params.get("command", description)
        
        if not command:
            return "Error: No command provided."
        
        try:
            # Execute the command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            # Prepare result
            result = {
                "command": command,
                "return_code": process.returncode,
                "stdout": stdout.decode(),
                "stderr": stderr.decode()
            }
            
            # Add the result to the context for future reference
            self.context_db.add_context({
                "content": f"Command executed: {command}",
                "type": "command_result",
                "task_id": task["id"]
            })
            
            return result
                
        except Exception as e:
            return f"Error executing command: {str(e)}"


class ContextSummarizerAgent(Agent):
    """Agent that summarizes context for other agents."""
    
    def __init__(self, name, context_db):
        super().__init__(name, "context_summary", context_db)
    
    async def process_task(self, task):
        """Create a summary of recent context entries."""
        params = task.get("params", {})
        
        # Number of context entries to summarize
        limit = params.get("limit", 20)
        
        # Fetch context to summarize
        context_entries = self.context_db.get_latest_context(limit)
        
        if not context_entries:
            return "No context entries found to summarize."
        
        context_text = "\n".join([
            f"[{entry.get('created_at', '')}] {entry.get('type', 'general')}: {entry.get('content', '')}"
            for entry in context_entries
        ])
        
        # Construct the request to OpenAI
        prompt = f"""
Please provide a concise summary of the following context entries:

{context_text}

Create a clear overview that captures key points and essential information from these entries.
The summary should be comprehensive yet brief, highlighting the most important aspects.
"""
        
        if not OPENAI_API_KEY:
            return "ERROR: OpenAI API key not set. Please set the OPENAI_API_KEY environment variable."
            
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            
            data = {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Add the summary to the context
                self.context_db.add_context({
                    "content": content,
                    "type": "daily_summary",
                    "task_id": task["id"]
                })
                
                return content
            else:
                return f"API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error creating context summary: {str(e)}" 