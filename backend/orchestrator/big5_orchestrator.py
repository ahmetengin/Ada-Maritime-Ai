"""Big-5 Super Agent Orchestrator - Refactored"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from anthropic import Anthropic

from ..config import get_config
from ..logger import setup_logger
from ..exceptions import OrchestratorError, SkillExecutionError
from ..learning import ExperienceLearningPipeline, Experience, ExperienceType


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
    Big-5 Super Agent Orchestrator with SEAL v2 Learning

    Coordinates multiple specialized skills for complex marina operations.
    Now includes autonomous learning through SEAL v2 + TabPFN-2.5.
    """

    def __init__(self, api_key: Optional[str] = None, enable_learning: bool = True) -> None:
        """
        Initialize the orchestrator

        Args:
            api_key: Anthropic API key
            enable_learning: Enable SEAL v2 learning capabilities
        """
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

        # SEAL v2 Learning Pipeline
        self.enable_learning = enable_learning
        if enable_learning:
            self.learning_pipeline = ExperienceLearningPipeline(
                enable_tabpfn=True,
                enable_seal=True,
                enable_caching=True
            )
            logger.info("Big5Orchestrator initialized with SEAL v2 learning")
        else:
            self.learning_pipeline = None
            logger.info("Big5Orchestrator initialized (learning disabled)")

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

            # SEAL v2: Record successful experience for learning
            if self.enable_learning and self.learning_pipeline:
                self._record_experience(
                    skill_name=skill_name,
                    params=params,
                    context=context,
                    result=result,
                    success=True
                )

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

            # SEAL v2: Record failure experience for learning
            if self.enable_learning and self.learning_pipeline:
                self._record_experience(
                    skill_name=skill_name,
                    params=params,
                    context=context,
                    result=result,
                    success=False,
                    error=str(e)
                )

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

    # ========================================================================
    # SEAL v2 Learning Methods
    # ========================================================================

    def _record_experience(
        self,
        skill_name: str,
        params: Dict[str, Any],
        context: AgentContext,
        result: SkillResult,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """
        Record skill execution as learning experience

        This is called automatically after each skill execution.
        """
        # Map skill names to experience types
        experience_type_mapping = {
            "berth_management": ExperienceType.BERTH_ASSIGNMENT,
            "pricing": ExperienceType.PRICING,
            "compliance": ExperienceType.COMPLIANCE,
            "maintenance": ExperienceType.MAINTENANCE,
            "analytics": ExperienceType.CUSTOMER_SERVICE,
            "weather": ExperienceType.WEATHER_DECISION,
        }

        exp_type = experience_type_mapping.get(
            skill_name,
            ExperienceType.CUSTOMER_SERVICE  # Default
        )

        # Calculate performance score
        if success:
            # Success: base score 0.8, bonus from execution time
            base_score = 0.8
            # Faster execution = higher score (bonus up to 0.2)
            time_bonus = min(0.2, 0.2 * (1.0 / (result.execution_time + 0.1)))
            performance_score = min(1.0, base_score + time_bonus)
        else:
            # Failure: score based on how far it got
            performance_score = 0.2  # Minimal score for failures

        # Create experience
        experience = Experience(
            experience_type=exp_type,
            context={
                "marina_id": context.marina_id,
                "language": context.language,
                "session_id": context.session_id,
                **params
            },
            action=skill_name,
            action_params=params,
            outcome="success" if success else "failure",
            performance_score=performance_score,
            metrics={
                "execution_time": result.execution_time
            },
            skill_used=skill_name,
            agent_id="big5_orchestrator",
            marina_id=context.marina_id,
            error=error,
            error_category="skill_execution" if error else None
        )

        # Process through learning pipeline
        self.learning_pipeline.process_experience(experience)

        logger.debug(
            f"Recorded learning experience: {skill_name} "
            f"(score: {performance_score:.2f}, outcome: {experience.outcome})"
        )

    def get_learning_statistics(self) -> Optional[Dict[str, Any]]:
        """
        Get SEAL v2 learning statistics

        Returns statistics about learning progress, patterns, and self-edits.
        """
        if not self.enable_learning or not self.learning_pipeline:
            return None

        return self.learning_pipeline.get_combined_statistics()

    def get_learning_patterns(self, min_confidence: float = 0.7) -> List[Dict[str, Any]]:
        """
        Get detected learning patterns

        Args:
            min_confidence: Minimum confidence threshold for patterns

        Returns:
            List of pattern dictionaries
        """
        if not self.enable_learning or not self.learning_pipeline or not self.learning_pipeline.seal:
            return []

        patterns = self.learning_pipeline.seal.get_patterns(min_confidence=min_confidence)

        return [
            {
                "pattern_id": p.pattern_id,
                "description": p.description,
                "confidence": p.confidence,
                "occurrences": p.occurrences,
                "frequency": p.frequency
            }
            for p in patterns
        ]

    def get_pending_self_edits(self) -> List[Dict[str, Any]]:
        """
        Get pending SEAL v2 self-edits

        Returns self-edits that need manual review or approval.
        """
        if not self.enable_learning or not self.learning_pipeline or not self.learning_pipeline.seal:
            return []

        pending = self.learning_pipeline.seal.get_pending_self_edits()

        return [
            {
                "edit_id": edit.edit_id,
                "edit_type": edit.edit_type.value,
                "directive": edit.directive,
                "expected_improvement": edit.expected_improvement,
                "risk_level": edit.risk_level,
                "trigger": edit.trigger
            }
            for edit in pending
        ]

    def apply_self_edit(self, edit_id: str) -> bool:
        """
        Manually apply a pending self-edit

        Args:
            edit_id: ID of self-edit to apply

        Returns:
            True if applied successfully
        """
        if not self.enable_learning or not self.learning_pipeline or not self.learning_pipeline.seal:
            return False

        # Find the self-edit
        pending = self.learning_pipeline.seal.get_pending_self_edits()
        for edit in pending:
            if edit.edit_id == edit_id:
                success = self.learning_pipeline.seal.apply_self_edit(edit)
                if success:
                    logger.info(f"Manually applied self-edit: {edit_id}")
                return success

        logger.warning(f"Self-edit not found: {edit_id}")
        return False

    def get_all_available_skills(self) -> List[Dict[str, Any]]:
        """
        Get detailed information about all available skills

        Includes skill metadata and learning statistics if available.
        """
        skills_info = []

        for name, handler in self.skills.items():
            info = {
                "name": name,
                "description": getattr(handler, 'description', 'No description'),
                "version": getattr(handler, 'version', '1.0.0')
            }

            # Add learning progress if available
            if self.enable_learning and self.learning_pipeline and self.learning_pipeline.seal:
                skill_progress = self.learning_pipeline.seal.get_skill_progress(name)
                if skill_progress:
                    info["learning"] = {
                        "level": skill_progress.level,
                        "xp": skill_progress.current_xp,
                        "total_uses": skill_progress.total_uses,
                        "success_rate": skill_progress.success_rate,
                        "average_performance": skill_progress.average_performance
                    }

            skills_info.append(info)

        return skills_info


# Singleton instance
_orchestrator_instance: Optional[Big5Orchestrator] = None


def get_orchestrator() -> Big5Orchestrator:
    """Get or create global orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = Big5Orchestrator()
    return _orchestrator_instance
