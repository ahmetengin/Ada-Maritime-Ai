"""
SEAL v2 Manager - Self-Adapting Language Models with RL

Ported from Ada repo's TypeScript implementation (core/learning/ExperienceLearningPipeline.ts)

SEAL v2 features:
- Self-edit generation: Models create their own fine-tuning directives
- RL-based learning: Downstream performance as reward signal
- Dynamic hyperparameter optimization
- Pattern detection and knowledge extraction

Reference: SEAL v2 commit fa4ceab (Nov 13, 2025)
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from .models import (
    Experience,
    SelfEdit,
    SelfEditType,
    Pattern,
    SkillProgress,
    ExperienceType,
    LearningStatistics
)

logger = logging.getLogger(__name__)


class SEALv2Manager:
    """
    SEAL v2 Manager for reinforcement learning and self-adaptation

    Key innovations:
    - Self-edit generation based on performance gaps
    - RL-based optimization using downstream metrics
    - Adaptive hyperparameters (learning rate, batch size)
    - Automatic pattern detection
    """

    # RL Configuration
    DEFAULT_LEARNING_RATE = 0.1
    DEFAULT_EXPLORATION_RATE = 0.2
    MIN_LEARNING_RATE = 0.01
    MAX_LEARNING_RATE = 0.5

    # Pattern detection thresholds
    PATTERN_MIN_OCCURRENCES = 3
    PATTERN_CONFIDENCE_THRESHOLD = 0.7

    # Performance thresholds
    HIGH_PERFORMANCE_THRESHOLD = 0.7
    LOW_PERFORMANCE_THRESHOLD = 0.3

    def __init__(
        self,
        learning_rate: float = DEFAULT_LEARNING_RATE,
        exploration_rate: float = DEFAULT_EXPLORATION_RATE
    ):
        """
        Initialize SEAL v2 manager

        Args:
            learning_rate: Initial learning rate for RL
            exploration_rate: Exploration vs exploitation balance (0-1)
        """
        self.learning_rate = learning_rate
        self.exploration_rate = exploration_rate

        # Experience storage
        self.experiences: List[Experience] = []

        # Self-edit tracking
        self.self_edits: List[SelfEdit] = []
        self.pending_self_edits: List[SelfEdit] = []

        # Pattern tracking
        self.patterns: Dict[str, Pattern] = {}

        # Skill progression
        self.skills: Dict[str, SkillProgress] = {}

        # RL state
        self.reward_history: List[float] = []
        self.convergence_velocity: float = 0.0
        self.learning_cycles: int = 0

        # Statistics
        self.stats = LearningStatistics()

        logger.info(
            f"SEAL v2 manager initialized (lr={learning_rate}, "
            f"exploration={exploration_rate})"
        )

    def record_experience(self, experience: Experience):
        """
        Record new experience and trigger learning

        Args:
            experience: Experience to record
        """
        self.experiences.append(experience)
        self.stats.total_experiences += 1

        # Update type counter
        exp_type = experience.experience_type
        if exp_type not in self.stats.experiences_by_type:
            self.stats.experiences_by_type[exp_type] = 0
        self.stats.experiences_by_type[exp_type] += 1

        # Update skill progress
        if experience.skill_used:
            self._update_skill_progress(experience)

        # Extract learnings
        self._extract_learnings(experience)

        # Detect patterns
        self._detect_patterns(experience)

        # Check if self-edit is needed
        self._check_self_edit_trigger(experience)

        logger.debug(
            f"Recorded experience {experience.experience_id} "
            f"(type: {experience.experience_type}, score: {experience.performance_score:.2f})"
        )

    def generate_self_edit(self, trigger_reason: str, performance_gap: float) -> SelfEdit:
        """
        Generate self-edit directive based on performance analysis

        This is the core SEAL v2 innovation: models create their own fine-tuning directives

        Args:
            trigger_reason: Reason for triggering self-edit
            performance_gap: Gap between current and desired performance

        Returns:
            Self-edit directive
        """
        # Determine edit type based on situation
        sample_count = len(self.experiences)
        recent_performance = self._get_recent_performance(window=10)

        if sample_count < 10:
            # Low sample count → Data augmentation
            edit_type = SelfEditType.DATA_AUGMENTATION
            directive = (
                f"Generate synthetic training samples to expand dataset. "
                f"Current samples: {sample_count}. Target: 50 samples."
            )
            parameters = {
                'augmentation_factor': 5.0,
                'noise_level': 0.1,
                'preserve_distribution': True
            }
            expected_improvement = 0.3

        elif self._is_learning_plateaued(recent_performance):
            # Plateaued learning → Hyperparameter adjustment
            edit_type = SelfEditType.HYPERPARAMETER_ADJUSTMENT
            directive = (
                f"Adjust hyperparameters to escape local optimum. "
                f"Current LR: {self.learning_rate:.3f}. "
                f"Convergence velocity: {self.convergence_velocity:.3f}"
            )
            parameters = {
                'new_learning_rate': self.learning_rate * 1.5,
                'new_batch_size': max(8, int(sample_count * 0.1)),
                'momentum': 0.9
            }
            expected_improvement = 0.15

        elif performance_gap > 0.4:
            # High error rate → Knowledge restructuring
            edit_type = SelfEditType.KNOWLEDGE_RESTRUCTURING
            directive = (
                f"Restructure knowledge base due to high error rate. "
                f"Performance gap: {performance_gap:.2f}. "
                f"Review {len(self.patterns)} existing patterns."
            )
            parameters = {
                'prune_low_confidence_patterns': True,
                'confidence_threshold': 0.6,
                'relearn_from_failures': True
            }
            expected_improvement = 0.25

        else:
            # Normal case → Standard gradient update
            edit_type = SelfEditType.GRADIENT_UPDATE
            directive = (
                f"Standard gradient update with performance feedback. "
                f"Recent avg performance: {recent_performance:.2f}"
            )
            parameters = {
                'learning_rate': self.learning_rate,
                'use_momentum': True,
                'clip_gradients': True
            }
            expected_improvement = 0.1

        # Create self-edit
        self_edit = SelfEdit(
            edit_type=edit_type,
            trigger=trigger_reason,
            performance_gap=performance_gap,
            directive=directive,
            parameters=parameters,
            expected_improvement=expected_improvement,
            risk_level=self._assess_risk_level(edit_type, parameters)
        )

        self.self_edits.append(self_edit)
        self.pending_self_edits.append(self_edit)
        self.stats.total_self_edits += 1

        logger.info(
            f"Generated self-edit: {edit_type.value} "
            f"(expected improvement: {expected_improvement:.2%}, "
            f"risk: {self_edit.risk_level})"
        )

        return self_edit

    def apply_self_edit(self, self_edit: SelfEdit) -> bool:
        """
        Apply self-edit directive

        Args:
            self_edit: Self-edit to apply

        Returns:
            True if applied successfully
        """
        try:
            if self_edit.edit_type == SelfEditType.HYPERPARAMETER_ADJUSTMENT:
                # Update learning rate
                new_lr = self_edit.parameters.get('new_learning_rate', self.learning_rate)
                new_lr = max(self.MIN_LEARNING_RATE, min(self.MAX_LEARNING_RATE, new_lr))
                old_lr = self.learning_rate
                self.learning_rate = new_lr
                logger.info(f"Updated learning rate: {old_lr:.3f} → {new_lr:.3f}")

            elif self_edit.edit_type == SelfEditType.KNOWLEDGE_RESTRUCTURING:
                # Prune low-confidence patterns
                if self_edit.parameters.get('prune_low_confidence_patterns'):
                    threshold = self_edit.parameters.get('confidence_threshold', 0.6)
                    self._prune_patterns(threshold)

            elif self_edit.edit_type == SelfEditType.DATA_AUGMENTATION:
                # Data augmentation would happen here
                logger.info("Data augmentation requested (implementation needed)")

            # Mark as applied
            self_edit.applied = True
            self_edit.applied_at = datetime.now()
            self.stats.applied_self_edits += 1

            # Remove from pending
            if self_edit in self.pending_self_edits:
                self.pending_self_edits.remove(self_edit)

            logger.info(f"Applied self-edit {self_edit.edit_id} ({self_edit.edit_type.value})")
            return True

        except Exception as e:
            logger.error(f"Failed to apply self-edit: {e}")
            return False

    def learn_from_reward(self, reward: float):
        """
        RL-based learning using downstream performance as reward signal

        This implements the core SEAL v2 RL loop

        Args:
            reward: Reward signal (-1 to +1, where +1 = perfect performance)
        """
        self.reward_history.append(reward)

        # Update convergence velocity (rate of improvement)
        if len(self.reward_history) >= 2:
            recent_rewards = self.reward_history[-10:]
            if len(recent_rewards) >= 2:
                # Simple derivative
                self.convergence_velocity = recent_rewards[-1] - recent_rewards[-2]

        # Adaptive learning rate based on convergence
        if self.convergence_velocity > 0.1:
            # Fast convergence → Can increase LR
            self.learning_rate = min(self.MAX_LEARNING_RATE, self.learning_rate * 1.1)
        elif self.convergence_velocity < -0.1:
            # Diverging → Reduce LR
            self.learning_rate = max(self.MIN_LEARNING_RATE, self.learning_rate * 0.9)

        self.learning_cycles += 1

        logger.debug(
            f"RL update: reward={reward:.2f}, velocity={self.convergence_velocity:.3f}, "
            f"lr={self.learning_rate:.3f}"
        )

    def detect_pattern(self, experience: Experience) -> Optional[Pattern]:
        """
        Detect patterns from recurring experience contexts

        Args:
            experience: Experience to analyze

        Returns:
            Detected pattern or None
        """
        # This is called by _detect_patterns internally
        # Public method for explicit pattern detection
        return self._detect_patterns(experience)

    def get_skill_progress(self, skill_name: str) -> Optional[SkillProgress]:
        """Get progress for a specific skill"""
        return self.skills.get(skill_name)

    def get_all_skills(self) -> Dict[str, SkillProgress]:
        """Get all skill progressions"""
        return self.skills.copy()

    def get_pending_self_edits(self) -> List[SelfEdit]:
        """Get pending self-edits that need to be applied"""
        return self.pending_self_edits.copy()

    def get_patterns(self, min_confidence: float = 0.0) -> List[Pattern]:
        """
        Get detected patterns

        Args:
            min_confidence: Minimum confidence threshold

        Returns:
            List of patterns meeting confidence threshold
        """
        return [
            pattern for pattern in self.patterns.values()
            if pattern.confidence >= min_confidence
        ]

    def get_statistics(self) -> LearningStatistics:
        """Get learning statistics"""
        # Update dynamic stats
        self.stats.average_performance = self._get_recent_performance(window=50)
        self.stats.total_self_edits = len(self.self_edits)
        self.stats.applied_self_edits = sum(1 for se in self.self_edits if se.applied)
        self.stats.total_patterns = len(self.patterns)
        self.stats.high_confidence_patterns = len([
            p for p in self.patterns.values()
            if p.confidence >= self.PATTERN_CONFIDENCE_THRESHOLD
        ])
        self.stats.last_learning_cycle = datetime.now()

        return self.stats

    # ============================================================================
    # PRIVATE METHODS
    # ============================================================================

    def _update_skill_progress(self, experience: Experience):
        """Update skill progression from experience"""
        skill_name = experience.skill_used

        if skill_name not in self.skills:
            self.skills[skill_name] = SkillProgress(skill_name=skill_name)

        skill = self.skills[skill_name]

        # Update usage counters
        skill.total_uses += 1
        if experience.outcome == "success":
            skill.successful_uses += 1
        else:
            skill.failed_uses += 1

        # Update success rate
        skill.success_rate = skill.calculate_success_rate()

        # Add performance score
        skill.add_performance(experience.performance_score)

        # Calculate XP gain (performance-based)
        xp_gain = experience.performance_score * 10
        if experience.outcome == "success":
            xp_gain *= 1.5  # Bonus for success

        skill.current_xp += xp_gain

        # Level up check
        while skill.current_xp >= skill.xp_for_next_level:
            skill.current_xp -= skill.xp_for_next_level
            skill.level += 1
            skill.xp_for_next_level *= 1.5  # Exponential XP requirements
            logger.info(f"Skill '{skill_name}' leveled up to {skill.level}!")

        skill.last_used = datetime.now()

    def _extract_learnings(self, experience: Experience):
        """Extract learnings from experience"""
        # Success learnings
        if experience.performance_score >= self.HIGH_PERFORMANCE_THRESHOLD:
            learning = f"High performance in {experience.experience_type.value}: {experience.action}"
            if learning not in experience.learnings:
                experience.learnings.append(learning)

        # Failure learnings
        if experience.outcome == "failure" and experience.error:
            learning = f"Avoid {experience.action} when {experience.error_category}: {experience.error}"
            if learning not in experience.learnings:
                experience.learnings.append(learning)

    def _detect_patterns(self, experience: Experience) -> Optional[Pattern]:
        """Detect recurring patterns"""
        # Generate pattern key from context
        pattern_key = self._generate_pattern_key(experience)

        if pattern_key not in self.patterns:
            # New pattern
            self.patterns[pattern_key] = Pattern(
                pattern_type=experience.experience_type.value,
                description=f"Pattern in {experience.experience_type.value}: {pattern_key}",
                conditions=experience.context.copy(),
                occurrences=1,
                total_observations=1,
                frequency=1.0,
                confidence=0.5,  # Low initial confidence
                example_experience_ids=[experience.experience_id]
            )
        else:
            # Existing pattern - update
            pattern = self.patterns[pattern_key]
            pattern.occurrences += 1
            pattern.total_observations += 1
            pattern.frequency = pattern.occurrences / pattern.total_observations
            pattern.confidence = min(1.0, pattern.frequency * (pattern.occurrences / 10))
            pattern.example_experience_ids.append(experience.experience_id)

            # Check if pattern is significant
            if (pattern.occurrences >= self.PATTERN_MIN_OCCURRENCES and
                pattern.confidence >= self.PATTERN_CONFIDENCE_THRESHOLD):

                logger.info(
                    f"Significant pattern detected: {pattern.description} "
                    f"(occurrences: {pattern.occurrences}, confidence: {pattern.confidence:.2f})"
                )
                return pattern

        return None

    def _generate_pattern_key(self, experience: Experience) -> str:
        """Generate pattern key from experience context"""
        # Use key context elements to generate pattern signature
        key_elements = [
            experience.experience_type.value,
            experience.action,
            experience.outcome
        ]

        # Add important context keys
        important_keys = ['season', 'weather', 'occupancy_rate', 'day_of_week']
        for key in important_keys:
            if key in experience.context:
                key_elements.append(f"{key}={experience.context[key]}")

        return "_".join(str(e) for e in key_elements)

    def _check_self_edit_trigger(self, experience: Experience):
        """Check if self-edit should be triggered"""
        # Calculate performance gap
        recent_perf = self._get_recent_performance(window=10)
        target_perf = 0.8  # Target performance
        performance_gap = max(0, target_perf - recent_perf)

        # Trigger conditions
        should_trigger = False
        trigger_reason = ""

        if len(self.experiences) >= 10:
            if performance_gap > 0.2:
                should_trigger = True
                trigger_reason = f"Performance gap: {performance_gap:.2f}"

            elif self._is_learning_plateaued():
                should_trigger = True
                trigger_reason = "Learning plateaued"

            elif len(self.experiences) < 20:
                should_trigger = True
                trigger_reason = "Low sample count"

        # Generate self-edit if triggered
        if should_trigger and performance_gap > 0:
            self.generate_self_edit(trigger_reason, performance_gap)

    def _get_recent_performance(self, window: int = 10) -> float:
        """Get average performance from recent experiences"""
        if not self.experiences:
            return 0.0

        recent = self.experiences[-window:]
        return sum(exp.performance_score for exp in recent) / len(recent)

    def _is_learning_plateaued(self, recent_performance: Optional[List[float]] = None) -> bool:
        """Check if learning has plateaued"""
        if recent_performance is None:
            if len(self.experiences) < 10:
                return False
            recent_performance = [exp.performance_score for exp in self.experiences[-10:]]

        if len(recent_performance) < 5:
            return False

        # Check variance
        avg = sum(recent_performance) / len(recent_performance)
        variance = sum((x - avg) ** 2 for x in recent_performance) / len(recent_performance)

        # Low variance = plateaued
        return variance < 0.01

    def _assess_risk_level(
        self,
        edit_type: SelfEditType,
        parameters: Dict[str, Any]
    ) -> str:
        """Assess risk level of self-edit"""
        if edit_type == SelfEditType.GRADIENT_UPDATE:
            return "low"
        elif edit_type == SelfEditType.DATA_AUGMENTATION:
            return "low"
        elif edit_type == SelfEditType.HYPERPARAMETER_ADJUSTMENT:
            lr_change = parameters.get('new_learning_rate', self.learning_rate) / self.learning_rate
            if lr_change > 2.0 or lr_change < 0.5:
                return "high"
            return "medium"
        elif edit_type == SelfEditType.KNOWLEDGE_RESTRUCTURING:
            return "high"
        return "medium"

    def _prune_patterns(self, confidence_threshold: float):
        """Remove low-confidence patterns"""
        before_count = len(self.patterns)

        self.patterns = {
            key: pattern
            for key, pattern in self.patterns.items()
            if pattern.confidence >= confidence_threshold
        }

        after_count = len(self.patterns)
        pruned = before_count - after_count

        logger.info(f"Pruned {pruned} low-confidence patterns (threshold: {confidence_threshold})")
