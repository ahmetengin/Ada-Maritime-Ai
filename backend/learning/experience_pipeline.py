"""
Experience Learning Pipeline - SEAL v2 + TabPFN Integration

Ported from Ada repo's TypeScript implementation (core/learning/ExperienceLearningPipeline.ts)

Intelligent routing strategy:
- < 10 samples: TabPFN only (few-shot learning)
- 10-100 samples: Hybrid (TabPFN + SEAL combined)
- > 100 samples: SEAL only (RL optimization excels)

This is the main entry point for the learning system.
"""

import logging
from typing import Dict, Optional, Any, Tuple
from datetime import datetime

from .models import (
    Experience,
    Prediction,
    LearningStrategy,
    LearningStatistics,
    ExperienceType
)
from .tabpfn_adapter import TabPFNAdapter
from .seal_v2_manager import SEALv2Manager

logger = logging.getLogger(__name__)


class ExperienceLearningPipeline:
    """
    Unified learning pipeline combining SEAL v2 and TabPFN-2.5

    This class implements intelligent routing between three strategies:
    1. TabPFN-only: For datasets with < 10 samples
    2. Hybrid: For datasets with 10-100 samples
    3. SEAL-only: For datasets with > 100 samples

    Features:
    - Automatic strategy selection
    - Cross-strategy learning
    - Performance tracking
    - Self-optimization
    """

    def __init__(
        self,
        enable_tabpfn: bool = True,
        enable_seal: bool = True,
        enable_caching: bool = True
    ):
        """
        Initialize experience learning pipeline

        Args:
            enable_tabpfn: Enable TabPFN few-shot learning
            enable_seal: Enable SEAL v2 RL-based learning
            enable_caching: Enable prediction caching
        """
        self.enable_tabpfn = enable_tabpfn
        self.enable_seal = enable_seal

        # Initialize components
        self.tabpfn = TabPFNAdapter(enable_caching=enable_caching) if enable_tabpfn else None
        self.seal = SEALv2Manager() if enable_seal else None

        # Experience tracking by type
        self.experiences_by_type: Dict[ExperienceType, list] = {}

        # Strategy usage tracking
        self.strategy_usage = {
            LearningStrategy.TABPFN: 0,
            LearningStrategy.HYBRID: 0,
            LearningStrategy.SEAL: 0
        }

        logger.info(
            f"Experience learning pipeline initialized "
            f"(TabPFN: {'enabled' if enable_tabpfn else 'disabled'}, "
            f"SEAL: {'enabled' if enable_seal else 'disabled'})"
        )

    def process_experience(self, experience: Experience):
        """
        Process new experience through the learning pipeline

        This is the main entry point for recording experiences

        Args:
            experience: Experience to process
        """
        # Store experience by type
        exp_type = experience.experience_type
        if exp_type not in self.experiences_by_type:
            self.experiences_by_type[exp_type] = []
        self.experiences_by_type[exp_type].append(experience)

        # Add to TabPFN training data
        if self.tabpfn:
            self.tabpfn.add_training_sample(experience)

        # Record in SEAL
        if self.seal:
            self.seal.record_experience(experience)

            # RL learning: Use performance as reward signal
            reward = self._calculate_reward(experience)
            self.seal.learn_from_reward(reward)

        # Apply pending self-edits
        if self.seal:
            self._apply_pending_self_edits()

        logger.debug(
            f"Processed experience {experience.experience_id} "
            f"(type: {experience.experience_type}, strategy: {self._get_strategy(exp_type)})"
        )

    def predict(
        self,
        experience: Experience,
        target: str = "outcome"
    ) -> Optional[Prediction]:
        """
        Predict outcome using intelligent strategy selection

        Args:
            experience: Experience to predict
            target: Target variable to predict

        Returns:
            Prediction or None if unable to predict
        """
        # Get sample count for this experience type
        sample_count = self._get_sample_count(experience.experience_type)

        # Select strategy
        strategy = self._select_strategy(sample_count)

        logger.info(
            f"Predicting with {strategy.value} strategy "
            f"(samples: {sample_count}, type: {experience.experience_type})"
        )

        # Route to appropriate method
        if strategy == LearningStrategy.TABPFN:
            prediction = self._predict_with_tabpfn(experience, target)
        elif strategy == LearningStrategy.HYBRID:
            prediction = self._predict_with_hybrid(experience, target)
        elif strategy == LearningStrategy.SEAL:
            prediction = self._predict_with_seal(experience, target)
        else:
            logger.warning(f"Unknown strategy: {strategy}")
            return None

        # Track strategy usage
        if prediction:
            self.strategy_usage[strategy] += 1

        return prediction

    def get_recommended_strategy(self, experience_type: ExperienceType) -> Dict[str, Any]:
        """
        Get recommended strategy for experience type

        Args:
            experience_type: Type of experience

        Returns:
            Strategy recommendation with details
        """
        sample_count = self._get_sample_count(experience_type)
        strategy = self._select_strategy(sample_count)

        recommendation = {
            'experience_type': experience_type.value,
            'sample_count': sample_count,
            'recommended_strategy': strategy.value,
            'reasoning': self._get_strategy_reasoning(strategy, sample_count),
            'confidence_threshold': self._get_confidence_threshold(strategy, sample_count)
        }

        return recommendation

    def get_statistics(self) -> Dict[str, Any]:
        """Get combined statistics from all components"""
        stats = {
            'total_experiences': sum(len(exps) for exps in self.experiences_by_type.values()),
            'experiences_by_type': {
                exp_type.value: len(exps)
                for exp_type, exps in self.experiences_by_type.items()
            },
            'strategy_usage': {
                strategy.value: count
                for strategy, count in self.strategy_usage.items()
            }
        }

        # Add TabPFN stats
        if self.tabpfn:
            stats['tabpfn'] = self.tabpfn.get_statistics()

        # Add SEAL stats
        if self.seal:
            seal_stats = self.seal.get_statistics()
            stats['seal'] = {
                'total_experiences': seal_stats.total_experiences,
                'total_self_edits': seal_stats.total_self_edits,
                'applied_self_edits': seal_stats.applied_self_edits,
                'total_patterns': seal_stats.total_patterns,
                'high_confidence_patterns': seal_stats.high_confidence_patterns,
                'average_performance': seal_stats.average_performance
            }

        return stats

    def get_tabpfn_statistics(self) -> Optional[Dict[str, Any]]:
        """Get TabPFN-specific statistics"""
        if self.tabpfn:
            return self.tabpfn.get_statistics()
        return None

    def get_seal_statistics(self) -> Optional[LearningStatistics]:
        """Get SEAL-specific statistics"""
        if self.seal:
            return self.seal.get_statistics()
        return None

    def get_combined_statistics(self) -> Dict[str, Any]:
        """
        Get unified statistics across both approaches

        This is the main statistics endpoint for monitoring
        """
        return self.get_statistics()

    # ============================================================================
    # PRIVATE METHODS - Strategy Selection & Routing
    # ============================================================================

    def _get_sample_count(self, experience_type: ExperienceType) -> int:
        """Get sample count for experience type"""
        return len(self.experiences_by_type.get(experience_type, []))

    def _select_strategy(self, sample_count: int) -> LearningStrategy:
        """
        Select appropriate learning strategy based on sample count

        < 10 samples: TabPFN only
        10-100 samples: Hybrid
        > 100 samples: SEAL only
        """
        if sample_count < TabPFNAdapter.FEW_SHOT_THRESHOLD:
            return LearningStrategy.TABPFN if self.enable_tabpfn else LearningStrategy.SEAL

        elif sample_count < TabPFNAdapter.HYBRID_THRESHOLD:
            if self.enable_tabpfn and self.enable_seal:
                return LearningStrategy.HYBRID
            elif self.enable_tabpfn:
                return LearningStrategy.TABPFN
            else:
                return LearningStrategy.SEAL

        else:
            return LearningStrategy.SEAL if self.enable_seal else LearningStrategy.TABPFN

    def _get_strategy(self, experience_type: ExperienceType) -> LearningStrategy:
        """Get current strategy for experience type"""
        sample_count = self._get_sample_count(experience_type)
        return self._select_strategy(sample_count)

    def _get_strategy_reasoning(self, strategy: LearningStrategy, sample_count: int) -> str:
        """Get human-readable reasoning for strategy selection"""
        if strategy == LearningStrategy.TABPFN:
            return (
                f"Few-shot learning optimal for {sample_count} samples. "
                f"TabPFN achieves 91% accuracy with just 5 samples."
            )
        elif strategy == LearningStrategy.HYBRID:
            return (
                f"Hybrid approach combines TabPFN speed with SEAL depth for {sample_count} samples. "
                f"Dual validation improves confidence."
            )
        elif strategy == LearningStrategy.SEAL:
            return (
                f"RL-based optimization excels with {sample_count} samples. "
                f"Self-adapting models achieve best performance at scale."
            )
        return "Unknown strategy"

    def _get_confidence_threshold(self, strategy: LearningStrategy, sample_count: int) -> float:
        """Get recommended confidence threshold"""
        if strategy == LearningStrategy.TABPFN and self.tabpfn:
            return self.tabpfn.get_recommended_confidence_threshold(sample_count)
        elif strategy == LearningStrategy.HYBRID:
            return 0.7  # Higher threshold for hybrid
        else:
            return 0.6  # Standard threshold for SEAL

    # ============================================================================
    # PRIVATE METHODS - Prediction Strategies
    # ============================================================================

    def _predict_with_tabpfn(
        self,
        experience: Experience,
        target: str
    ) -> Optional[Prediction]:
        """Predict using TabPFN only"""
        if not self.tabpfn:
            logger.warning("TabPFN not enabled")
            return None

        prediction = self.tabpfn.predict(experience, target)

        if prediction:
            logger.info(
                f"TabPFN prediction: {prediction.predicted_outcome} "
                f"(confidence: {prediction.confidence:.2f})"
            )

        return prediction

    def _predict_with_hybrid(
        self,
        experience: Experience,
        target: str
    ) -> Optional[Prediction]:
        """
        Predict using hybrid approach (TabPFN + SEAL)

        Combines TabPFN's few-shot capability with SEAL's analytical depth
        """
        if not self.tabpfn or not self.seal:
            logger.warning("Hybrid mode requires both TabPFN and SEAL")
            return self._predict_with_tabpfn(experience, target) or self._predict_with_seal(experience, target)

        # Get TabPFN prediction
        tabpfn_pred = self.tabpfn.predict(experience, target)

        if not tabpfn_pred:
            # Fallback to SEAL
            return self._predict_with_seal(experience, target)

        # Enhance with SEAL insights
        seal_patterns = self.seal.get_patterns(min_confidence=0.6)

        # Check if any patterns apply
        applicable_patterns = [
            pattern for pattern in seal_patterns
            if self._pattern_matches_experience(pattern, experience)
        ]

        # Adjust confidence based on SEAL patterns
        adjusted_confidence = tabpfn_pred.confidence

        if applicable_patterns:
            # Boost confidence if patterns agree
            pattern_agreement = sum(
                1 for p in applicable_patterns
                if p.description.find(tabpfn_pred.predicted_outcome) >= 0
            ) / len(applicable_patterns)

            adjusted_confidence = (tabpfn_pred.confidence * 0.7) + (pattern_agreement * 0.3)

            # Add pattern insights to reasoning
            tabpfn_pred.reasoning += f" Enhanced by {len(applicable_patterns)} SEAL patterns."
            tabpfn_pred.contributing_factors.extend([
                f"Pattern: {p.description}" for p in applicable_patterns[:2]
            ])

        tabpfn_pred.confidence = adjusted_confidence
        tabpfn_pred.strategy = LearningStrategy.HYBRID

        logger.info(
            f"Hybrid prediction: {tabpfn_pred.predicted_outcome} "
            f"(confidence: {adjusted_confidence:.2f}, patterns: {len(applicable_patterns)})"
        )

        return tabpfn_pred

    def _predict_with_seal(
        self,
        experience: Experience,
        target: str
    ) -> Optional[Prediction]:
        """
        Predict using SEAL only

        Uses pattern matching and historical performance
        """
        if not self.seal:
            logger.warning("SEAL not enabled")
            return None

        # Get relevant patterns
        patterns = self.seal.get_patterns(min_confidence=0.7)

        # Find matching patterns
        matching_patterns = [
            pattern for pattern in patterns
            if self._pattern_matches_experience(pattern, experience)
        ]

        if not matching_patterns:
            logger.debug("No matching SEAL patterns for prediction")
            return None

        # Use pattern with highest confidence
        best_pattern = max(matching_patterns, key=lambda p: p.confidence)

        # Extract predicted outcome from pattern
        # (Simplified - production would use more sophisticated pattern matching)
        predicted_outcome = "success"  # Default
        confidence = best_pattern.confidence

        prediction = Prediction(
            predicted_outcome=predicted_outcome,
            confidence=confidence,
            probabilities={predicted_outcome: confidence, "failure": 1 - confidence},
            strategy=LearningStrategy.SEAL,
            sample_count=len(self.seal.experiences),
            reasoning=f"Based on SEAL pattern: {best_pattern.description}",
            contributing_factors=[
                f"Pattern confidence: {best_pattern.confidence:.2f}",
                f"Pattern occurrences: {best_pattern.occurrences}"
            ]
        )

        logger.info(
            f"SEAL prediction: {predicted_outcome} "
            f"(confidence: {confidence:.2f}, pattern: {best_pattern.pattern_id})"
        )

        return prediction

    # ============================================================================
    # PRIVATE METHODS - Utilities
    # ============================================================================

    def _calculate_reward(self, experience: Experience) -> float:
        """
        Calculate reward signal for RL

        Maps performance score and outcome to reward (-1 to +1)
        """
        # Base reward from performance score
        reward = experience.performance_score * 2 - 1  # Map [0,1] to [-1,1]

        # Bonus/penalty for outcome
        if experience.outcome == "success":
            reward = max(reward, 0.5)  # Minimum 0.5 for success
        elif experience.outcome == "failure":
            reward = min(reward, -0.5)  # Maximum -0.5 for failure

        return reward

    def _pattern_matches_experience(self, pattern, experience: Experience) -> bool:
        """Check if pattern matches experience context"""
        if pattern.pattern_type != experience.experience_type.value:
            return False

        # Check if pattern conditions match experience context
        matches = 0
        total_conditions = len(pattern.conditions)

        if total_conditions == 0:
            return False

        for key, value in pattern.conditions.items():
            if key in experience.context and experience.context[key] == value:
                matches += 1

        # Require at least 50% match
        return (matches / total_conditions) >= 0.5

    def _apply_pending_self_edits(self):
        """Apply pending self-edits from SEAL"""
        if not self.seal:
            return

        pending = self.seal.get_pending_self_edits()

        for self_edit in pending:
            # Apply low-risk edits automatically
            if self_edit.risk_level == "low":
                self.seal.apply_self_edit(self_edit)
                logger.info(f"Auto-applied low-risk self-edit: {self_edit.edit_id}")

            # Medium-risk edits require manual review (log only)
            elif self_edit.risk_level == "medium":
                logger.warning(
                    f"Medium-risk self-edit pending manual review: {self_edit.edit_id} "
                    f"({self_edit.edit_type.value})"
                )

            # High-risk edits require explicit approval
            elif self_edit.risk_level == "high":
                logger.warning(
                    f"High-risk self-edit requires approval: {self_edit.edit_id} "
                    f"({self_edit.edit_type.value})"
                )
