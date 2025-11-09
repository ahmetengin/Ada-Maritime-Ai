"""Big-5 Super Agent Orchestrator - Refactored"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from anthropic import Anthropic

from ..config import get_config
from ..logger import setup_logger
from ..exceptions import OrchestratorError, SkillExecutionError


logger = setup_logger(__name__)


@dataclass
class SkillResult:
    """Result from a skill execution"""
    skill_name: str
    success: bool
    data: Any
    execution_time: float
    timestamp: str
    error: Optional[str] = None


@dataclass
class AgentContext:
    """Context for agent execution"""
    user_id: str
    session_id: str
    marina_id: Optional[str] = None
    language: str = "tr"
    metadata: Optional[Dict] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class Big5Orchestrator:
    """
    Big-5 Super Agent Orchestrator
    
    Coordinates multiple specialized skills for complex marina operations.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize the orchestrator"""
        config = get_config()
        
        self.api_key = api_key or config.api.anthropic_api_key
        if not self.api_key:
            raise OrchestratorError("ANTHROPIC_API_KEY is required")

        try:
            self.client = Anthropic(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise OrchestratorError(f"Client initialization failed: {e}")

        self.skills: Dict[str, Any] = {}
        self.execution_history: List[SkillResult] = []
        
        logger.info("Big5Orchestrator initialized")

    def register_skill(self, skill_name: str, skill_handler: Any) -> None:
        """Register a skill handler"""
        if not hasattr(skill_handler, 'execute'):
            raise OrchestratorError(
                f"Skill {skill_name} must have 'execute' method"
            )
        
        self.skills[skill_name] = skill_handler
        logger.info(f"Registered skill: {skill_name}")

    def get_available_skills(self) -> List[str]:
        """Get list of registered skills"""
        return list(self.skills.keys())

    async def execute_skill(
        self,
        skill_name: str,
        params: Dict[str, Any],
        context: AgentContext
    ) -> SkillResult:
        """Execute a specific skill with error handling"""
        start_time = datetime.now()
        
        logger.info(f"Executing skill: {skill_name} with params: {params}")

        try:
            if skill_name not in self.skills:
                raise SkillExecutionError(f"Skill '{skill_name}' not found")

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
            logger.info(
                f"Skill {skill_name} executed successfully "
                f"in {execution_time:.2f}s"
            )
            
            return result

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.error(f"Skill {skill_name} failed: {e}", exc_info=True)
            
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

    def process_natural_language(
        self,
        user_input: str,
        context: AgentContext
    ) -> Dict[str, Any]:
        """Process natural language and determine execution plan"""
        
        logger.info(f"Processing NL input: {user_input[:50]}...")
        
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

        try:
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
            execution_plan = json.loads(response_text)
            
            logger.info(f"Execution plan created: {execution_plan.get('intent')}")
            
            return execution_plan
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return {
                "intent": "unclear",
                "skills_to_execute": [],
                "response_language": context.language,
                "raw_response": response_text
            }
        except Exception as e:
            logger.error(f"NL processing failed: {e}", exc_info=True)
            raise OrchestratorError(f"Failed to process request: {e}")

    async def handle_request(
        self,
        user_input: str,
        context: AgentContext
    ) -> Dict[str, Any]:
        """Main entry point - handle a user request end-to-end"""
        
        logger.info(f"Handling request from user: {context.user_id}")

        try:
            # Understand intent
            execution_plan = self.process_natural_language(user_input, context)

            # Execute skills
            results = []
            for skill_spec in execution_plan.get("skills_to_execute", []):
                result = await self.execute_skill(
                    skill_name=skill_spec["skill_name"],
                    params=skill_spec["params"],
                    context=context
                )
                results.append(result)

            # Aggregate response
            return {
                "intent": execution_plan.get("intent"),
                "results": [asdict(r) for r in results],
                "success": all(r.success for r in results),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Request handling failed: {e}", exc_info=True)
            raise OrchestratorError(f"Failed to handle request: {e}")

    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent execution history"""
        return [asdict(r) for r in self.execution_history[-limit:]]

    def clear_history(self) -> None:
        """Clear execution history"""
        self.execution_history = []
        logger.info("Execution history cleared")


# Singleton instance
_orchestrator_instance: Optional[Big5Orchestrator] = None


def get_orchestrator() -> Big5Orchestrator:
    """Get or create global orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = Big5Orchestrator()
    return _orchestrator_instance
