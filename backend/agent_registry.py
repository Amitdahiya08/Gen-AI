from typing import Dict, Callable

class AgentRegistry:
    """Registry to hold agent classes and workflows."""

    def __init__(self):
        self._agents: Dict[str, Callable] = {}

    def register(self, name: str, agent_cls: Callable):
        self._agents[name] = agent_cls

    def get(self, name: str):
        if name not in self._agents:
            raise ValueError(f"Agent {name} not found in registry")
        return self._agents[name]
