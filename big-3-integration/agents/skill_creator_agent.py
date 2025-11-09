"""SkillCreatorAgent - Autonomous Skill Creation"""

import os
import json
from pathlib import Path
from datetime import datetime
from anthropic import Anthropic


class SkillCreatorAgent:
    """Autonomous Skill Creator Agent - 6-Phase Workflow"""

    PHASES = ["research", "design", "implement", "validate", "package", "document"]

    def __init__(self, agent_name: str, skill_type: str, description: str,
                 workspace_dir: str = "apps/content-gen"):
        self.agent_name = agent_name
        self.skill_type = skill_type
        self.description = description

        self.workspace = Path(workspace_dir)
        self.skills_dir = self.workspace / "skills"
        self.skill_dir = self.skills_dir / agent_name
        self.registry_file = self.skills_dir / "registry.json"

        self.skills_dir.mkdir(parents=True, exist_ok=True)

        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        self.current_phase = 0
        self.phase_results = []
        self.status = "initialized"

    async def execute_task(self, task: dict) -> dict:
        operation = task.get("operation", "create_skill")

        if operation == "create_skill":
            return await self._create_skill()
        elif operation == "get_status":
            return self._get_status()
        else:
            return {"error": f"Unknown operation: {operation}"}

    async def _create_skill(self) -> dict:
        print(f"[SkillCreator] Creating skill: {self.agent_name}")
        self.status = "in_progress"

        for phase in self.PHASES:
            print(f"[SkillCreator] Phase {self.current_phase + 1}/6: {phase}")

            result = await self._execute_phase(phase)
            self.phase_results.append(result)

            if not result.get("success"):
                print(f"[SkillCreator] ❌ Phase {phase} failed")
                self.status = "failed"
                break

            self.current_phase += 1

        if self.current_phase == len(self.PHASES):
            self.status = "completed"
            print(f"[SkillCreator] ✅ Skill creation completed!")

        self._update_registry()

        return {
            "agent_name": self.agent_name,
            "status": self.status,
            "phases_completed": self.current_phase,
            "total_phases": len(self.PHASES),
            "skill_path": str(self.skill_dir),
            "results": self.phase_results
        }

    async def _execute_phase(self, phase: str) -> dict:
        start_time = datetime.now()

        try:
            prompt = self._get_phase_prompt(phase)

            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                system=prompt,
                messages=[{
                    "role": "user",
                    "content": f"Execute {phase} phase for {self.skill_type} skill: {self.agent_name}\n\n{self.description}"
                }]
            )

            output = message.content[0].text

            if phase == "implement":
                self._create_skill_files(output)
            elif phase == "package":
                self._create_skill_package(output)

            duration = (datetime.now() - start_time).total_seconds()

            return {
                "phase": phase,
                "success": True,
                "output": output[:500],
                "duration": duration
            }

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            return {
                "phase": phase,
                "success": False,
                "error": str(e),
                "duration": duration
            }

    def _get_phase_prompt(self, phase: str) -> str:
        base = f"""You are a Claude skill creation expert.

Skill: {self.agent_name}
Type: {self.skill_type}
Description: {self.description}

Phase: {phase}
"""

        prompts = {
            "research": base + "Research requirements and analyze similar skills.",
            "design": base + "Design skill architecture and workflow.",
            "implement": base + "Create skill files (custom_instructions.md, skill.json, README.md).",
            "validate": base + "Validate implementation and test use cases.",
            "package": base + "Package skill for distribution.",
            "document": base + "Create comprehensive documentation."
        }

        return prompts.get(phase, base)

    def _create_skill_files(self, output: str):
        self.skill_dir.mkdir(parents=True, exist_ok=True)
        # Simplified file creation
        (self.skill_dir / "README.md").write_text(f"# {self.agent_name}\n\n{self.description}")

    def _create_skill_package(self, output: str):
        package_file = self.skill_dir / f"{self.agent_name}.skill"
        metadata = {
            "name": self.agent_name,
            "type": self.skill_type,
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "description": self.description
        }
        package_file.write_text(json.dumps(metadata, indent=2))

    def _update_registry(self):
        registry = {}
        if self.registry_file.exists():
            registry = json.loads(self.registry_file.read_text())

        registry[self.agent_name] = {
            "name": self.agent_name,
            "type": self.skill_type,
            "status": self.status,
            "phases_completed": self.current_phase,
            "created": datetime.now().isoformat(),
            "path": str(self.skill_dir)
        }

        self.registry_file.write_text(json.dumps(registry, indent=2))

    def _get_status(self) -> dict:
        return {
            "agent_name": self.agent_name,
            "status": self.status,
            "current_phase": self.PHASES[self.current_phase] if self.current_phase < len(self.PHASES) else "completed",
            "phases_completed": self.current_phase,
            "total_phases": len(self.PHASES),
            "progress": (self.current_phase / len(self.PHASES)) * 100
        }
