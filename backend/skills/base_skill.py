"""Base Skill Class"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class SkillMetadata:
    name: str
    description: str
    version: str
    author: str
    requires_mcp: bool = False
    requires_database: bool = False


class BaseSkill(ABC):
    def __init__(self):
        self.metadata = self.get_metadata()

    @abstractmethod
    def get_metadata(self) -> SkillMetadata:
        pass

    @abstractmethod
    async def execute(self, params: Dict[str, Any], context: Any) -> Dict[str, Any]:
        pass

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def description(self) -> str:
        return self.metadata.description

    def validate_params(self, params: Dict[str, Any], required_keys: list) -> None:
        missing = [key for key in required_keys if key not in params]
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")
