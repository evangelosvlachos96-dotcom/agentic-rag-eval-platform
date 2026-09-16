"""Agent: a tool-using loop that decides when and how to retrieve.

Planned responsibilities (Milestone 6):

- an agent loop driven by the LLM provider with a `search` tool
- multi-turn query rewriting and iterative retrieval
- hard step and token limits so runs always terminate
- context management (what stays in the window between steps)
- trajectory logging so every run can be replayed and evaluated
"""
