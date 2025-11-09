"""Big-5 Super Agent Orchestrator"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from anthropic import Anthropic


@dataclass
class SkillResult:
    skill_name: str
    success: bool
    data: Any
    execution_time: float
    timestamp: str
    error: Optional[str] = None


@dataclass
class AgentContext:
    user_id: str
    session_id: str
    marina_id: Optional[str] = None
    language: str = "tr"
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class Big5Orchestrator:
    """Big-5 Super Agent Orchestrator for Marina Operations"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set")

        self.client = Anthropic(api_key=self.api_key)
        self.skills: Dict[str, Any] = {}
        self.execution_history: List[SkillResult] = []

    def register_skill(self, skill_name: str, skill_handler):
        self.skills[skill_name] = skill_handler
        print(f"✅ Registered skill: {skill_name}")

    def get_available_skills(self) -> List[str]:
        return list(self.skills.keys())

    async def execute_skill(self, skill_name: str, params: Dict, context: AgentContext) -> SkillResult:
        start_time = datetime.now()

        try:
            if skill_name not in self.skills:
                raise ValueError(f"Skill '{skill_name}' not found")

            skill_handler = self.skills[skill_name]
            result_data = await skill_handler.execute(params, context)

            execution_time = (datetime.now() - start_time).total_seconds()

            result = SkillResult(
                skill_name=skill_name,
                success=True,
                data=result_data,
                execution_time=execution_time,
                timestamp=datetime.now().isoformat()
            )

            self.execution_history.append(result)
            return result

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            result = SkillResult(
                skill_name=skill_name,
                success=False,
                data=None,
                execution_time=execution_time,
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )

            self.execution_history.append(result)
            return result

    def process_natural_language(self, user_input: str, context: AgentContext) -> Dict:
        skills_desc = "\n".join([
            f"- {name}: {handler.description}"
            for name, handler in self.skills.items()
        ])

        system_prompt = f"""You are the Big-5 Super Agent for Setur Marina operations.

Available Skills:
{skills_desc}

Your role:
1. Understand user requests in Turkish or English
2. Determine which skill(s) to use
3. Extract parameters from user input
4. Return structured execution plan

Respond in JSON format:
{{
    "intent": "brief description",
    "skills_to_execute": [
        {{
            "skill_name": "skill_name",
            "params": {{}},
            "priority": 1
        }}
    ],
    "response_language": "tr" or "en"
}}
"""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": user_input
            }]
        )

        response_text = message.content[0].text

        try:
            execution_plan = json.loads(response_text)
            return execution_plan
        except json.JSONDecodeError:
            return {
                "intent": "unclear",
                "skills_to_execute": [],
                "response_language": context.language,
                "raw_response": response_text
            }

    async def handle_request(self, user_input: str, context: AgentContext) -> Dict:
        execution_plan = self.process_natural_language(user_input, context)

        results = []
        for skill_spec in execution_plan.get("skills_to_execute", []):
            result = await self.execute_skill(
                skill_name=skill_spec["skill_name"],
                params=skill_spec["params"],
                context=context
            )
            results.append(result)

        return {
            "intent": execution_plan.get("intent"),
            "results": [asdict(r) for r in results],
            "success": all(r.success for r in results),
            "timestamp": datetime.now().isoformat()
        }

    def get_execution_history(self, limit: int = 10) -> List[Dict]:
        return [asdict(r) for r in self.execution_history[-limit:]]


_orchestrator_instance: Optional[Big5Orchestrator] = None


def get_orchestrator() -> Big5Orchestrator:
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = Big5Orchestrator()
    return _orchestrator_instance
