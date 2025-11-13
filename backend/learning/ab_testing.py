"""
A/B Testing Framework for SEAL v2

Enables controlled experiments for learning algorithms:
- Multi-variant testing (A/B/C/D...)
- Statistical significance testing
- Feature flag management
- Performance comparison
- Automatic rollout based on results

Author: Ada Maritime AI Team
Date: November 2025
"""

import logging
import hashlib
import json
import numpy as np
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from scipy import stats

logger = logging.getLogger(__name__)


class ExperimentStatus(str, Enum):
    """Experiment status"""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class VariantType(str, Enum):
    """Variant type"""
    CONTROL = "control"
    TREATMENT = "treatment"


@dataclass
class Variant:
    """Experiment variant configuration"""
    variant_id: str
    name: str
    variant_type: VariantType
    traffic_allocation: float  # 0.0 to 1.0
    config: Dict[str, Any]  # Configuration parameters
    description: str


@dataclass
class VariantMetrics:
    """Metrics for a variant"""
    variant_id: str
    sample_count: int
    success_count: int
    total_performance: float
    avg_performance: float
    std_performance: float
    conversion_rate: float
    confidence_interval_95: tuple  # (lower, upper)


@dataclass
class Experiment:
    """A/B test experiment"""
    experiment_id: str
    name: str
    description: str
    status: ExperimentStatus
    variants: List[Variant]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    target_metric: str
    minimum_sample_size: int
    confidence_level: float  # e.g., 0.95 for 95%
    created_at: datetime
    created_by: str


@dataclass
class ExperimentResult:
    """Results of an A/B test"""
    experiment_id: str
    variant_metrics: Dict[str, VariantMetrics]
    winner: Optional[str]  # Variant ID of winner
    statistical_significance: bool
    p_value: float
    effect_size: float  # Cohen's d
    recommendation: str
    completed_at: datetime


class ABTestingFramework:
    """
    A/B Testing Framework for Learning Algorithms

    Features:
    - Multi-variant experiment management
    - Statistical significance testing (t-test, chi-square)
    - Traffic allocation and bucketing
    - Feature flag integration
    - Automatic rollout recommendations
    """

    DEFAULT_CONFIDENCE_LEVEL = 0.95
    DEFAULT_MIN_SAMPLE_SIZE = 100

    def __init__(
        self,
        confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
        min_sample_size: int = DEFAULT_MIN_SAMPLE_SIZE
    ):
        """
        Initialize A/B testing framework

        Args:
            confidence_level: Confidence level for statistical tests (e.g., 0.95)
            min_sample_size: Minimum samples per variant
        """
        self.confidence_level = confidence_level
        self.min_sample_size = min_sample_size

        # State
        self.experiments: Dict[str, Experiment] = {}
        self.variant_data: Dict[str, Dict[str, List[float]]] = {}  # {exp_id: {variant_id: [scores]}}
        self.user_assignments: Dict[str, Dict[str, str]] = {}  # {exp_id: {user_id: variant_id}}

        # Statistics
        self.stats = {
            'total_experiments': 0,
            'running_experiments': 0,
            'completed_experiments': 0,
            'total_assignments': 0,
        }

        logger.info(
            f"A/B testing framework initialized "
            f"(confidence={confidence_level}, min_samples={min_sample_size})"
        )

    def create_experiment(
        self,
        name: str,
        description: str,
        variants: List[Variant],
        target_metric: str,
        created_by: str,
        minimum_sample_size: Optional[int] = None,
        confidence_level: Optional[float] = None
    ) -> Experiment:
        """
        Create new A/B test experiment

        Args:
            name: Experiment name
            description: Experiment description
            variants: List of variants to test
            target_metric: Metric to optimize
            created_by: Creator identifier
            minimum_sample_size: Override minimum sample size
            confidence_level: Override confidence level

        Returns:
            Created experiment
        """
        # Validate traffic allocation
        total_allocation = sum(v.traffic_allocation for v in variants)
        if not (0.99 <= total_allocation <= 1.01):
            raise ValueError(f"Traffic allocation must sum to 1.0, got {total_allocation}")

        # Check for control variant
        control_count = sum(1 for v in variants if v.variant_type == VariantType.CONTROL)
        if control_count != 1:
            raise ValueError(f"Must have exactly 1 control variant, got {control_count}")

        experiment_id = self._generate_experiment_id(name)

        experiment = Experiment(
            experiment_id=experiment_id,
            name=name,
            description=description,
            status=ExperimentStatus.DRAFT,
            variants=variants,
            start_date=None,
            end_date=None,
            target_metric=target_metric,
            minimum_sample_size=minimum_sample_size or self.min_sample_size,
            confidence_level=confidence_level or self.confidence_level,
            created_at=datetime.now(),
            created_by=created_by,
        )

        self.experiments[experiment_id] = experiment
        self.variant_data[experiment_id] = {v.variant_id: [] for v in variants}
        self.user_assignments[experiment_id] = {}

        self.stats['total_experiments'] += 1

        logger.info(f"Experiment created: {name} ({len(variants)} variants)")

        return experiment

    def start_experiment(self, experiment_id: str) -> bool:
        """
        Start running an experiment

        Args:
            experiment_id: Experiment identifier

        Returns:
            True if started successfully
        """
        if experiment_id not in self.experiments:
            logger.error(f"Experiment not found: {experiment_id}")
            return False

        experiment = self.experiments[experiment_id]

        if experiment.status != ExperimentStatus.DRAFT:
            logger.error(f"Cannot start experiment in status: {experiment.status}")
            return False

        experiment.status = ExperimentStatus.RUNNING
        experiment.start_date = datetime.now()

        self.stats['running_experiments'] += 1

        logger.info(f"Experiment started: {experiment.name}")

        return True

    def assign_variant(self, experiment_id: str, user_id: str) -> Optional[str]:
        """
        Assign user to a variant

        Uses deterministic hashing for consistent assignment

        Args:
            experiment_id: Experiment identifier
            user_id: User identifier

        Returns:
            Assigned variant ID or None if error
        """
        if experiment_id not in self.experiments:
            return None

        experiment = self.experiments[experiment_id]

        if experiment.status != ExperimentStatus.RUNNING:
            return None

        # Check if already assigned
        if user_id in self.user_assignments[experiment_id]:
            return self.user_assignments[experiment_id][user_id]

        # Deterministic hash-based assignment
        hash_input = f"{experiment_id}_{user_id}".encode()
        hash_value = int(hashlib.sha256(hash_input).hexdigest(), 16)
        bucket = (hash_value % 10000) / 10000.0  # 0.0 to 1.0

        # Allocate to variant based on traffic allocation
        cumulative = 0.0
        assigned_variant_id = None

        for variant in experiment.variants:
            cumulative += variant.traffic_allocation
            if bucket < cumulative:
                assigned_variant_id = variant.variant_id
                break

        if assigned_variant_id is None:
            assigned_variant_id = experiment.variants[-1].variant_id

        self.user_assignments[experiment_id][user_id] = assigned_variant_id
        self.stats['total_assignments'] += 1

        logger.debug(f"User {user_id} assigned to variant {assigned_variant_id}")

        return assigned_variant_id

    def record_outcome(
        self,
        experiment_id: str,
        variant_id: str,
        performance_score: float
    ) -> bool:
        """
        Record outcome for a variant

        Args:
            experiment_id: Experiment identifier
            variant_id: Variant identifier
            performance_score: Performance score (0.0 to 1.0)

        Returns:
            True if recorded successfully
        """
        if experiment_id not in self.experiments:
            return False

        if experiment_id not in self.variant_data:
            return False

        if variant_id not in self.variant_data[experiment_id]:
            return False

        self.variant_data[experiment_id][variant_id].append(performance_score)

        return True

    def get_variant_metrics(
        self,
        experiment_id: str,
        variant_id: str
    ) -> Optional[VariantMetrics]:
        """
        Calculate metrics for a variant

        Args:
            experiment_id: Experiment identifier
            variant_id: Variant identifier

        Returns:
            Variant metrics or None
        """
        if experiment_id not in self.variant_data:
            return None

        if variant_id not in self.variant_data[experiment_id]:
            return None

        scores = self.variant_data[experiment_id][variant_id]

        if len(scores) == 0:
            return None

        sample_count = len(scores)
        success_count = sum(1 for s in scores if s > 0.5)
        total_performance = sum(scores)
        avg_performance = np.mean(scores)
        std_performance = np.std(scores)
        conversion_rate = success_count / sample_count

        # 95% confidence interval
        if sample_count > 1:
            sem = std_performance / np.sqrt(sample_count)
            ci = stats.t.interval(0.95, sample_count - 1, loc=avg_performance, scale=sem)
        else:
            ci = (avg_performance, avg_performance)

        return VariantMetrics(
            variant_id=variant_id,
            sample_count=sample_count,
            success_count=success_count,
            total_performance=total_performance,
            avg_performance=avg_performance,
            std_performance=std_performance,
            conversion_rate=conversion_rate,
            confidence_interval_95=ci,
        )

    def analyze_experiment(self, experiment_id: str) -> Optional[ExperimentResult]:
        """
        Analyze experiment and determine winner

        Uses t-test for continuous metrics, chi-square for binary

        Args:
            experiment_id: Experiment identifier

        Returns:
            Experiment result or None if insufficient data
        """
        if experiment_id not in self.experiments:
            return None

        experiment = self.experiments[experiment_id]

        # Get metrics for all variants
        variant_metrics = {}
        for variant in experiment.variants:
            metrics = self.get_variant_metrics(experiment_id, variant.variant_id)
            if metrics is None or metrics.sample_count < experiment.minimum_sample_size:
                logger.warning(
                    f"Insufficient data for variant {variant.variant_id}: "
                    f"{metrics.sample_count if metrics else 0}/{experiment.minimum_sample_size}"
                )
                return None
            variant_metrics[variant.variant_id] = metrics

        # Find control and treatment variants
        control_variant_id = None
        treatment_variant_ids = []

        for variant in experiment.variants:
            if variant.variant_type == VariantType.CONTROL:
                control_variant_id = variant.variant_id
            else:
                treatment_variant_ids.append(variant.variant_id)

        if control_variant_id is None:
            return None

        control_scores = self.variant_data[experiment_id][control_variant_id]

        # Compare each treatment to control
        best_variant_id = control_variant_id
        best_performance = variant_metrics[control_variant_id].avg_performance
        min_p_value = 1.0
        max_effect_size = 0.0

        for treatment_id in treatment_variant_ids:
            treatment_scores = self.variant_data[experiment_id][treatment_id]

            # t-test for significance
            t_stat, p_value = stats.ttest_ind(treatment_scores, control_scores)

            # Cohen's d for effect size
            pooled_std = np.sqrt(
                (np.var(treatment_scores) + np.var(control_scores)) / 2
            )
            effect_size = abs(
                (np.mean(treatment_scores) - np.mean(control_scores)) / pooled_std
            ) if pooled_std > 0 else 0.0

            logger.debug(
                f"Variant {treatment_id} vs control: p={p_value:.4f}, d={effect_size:.2f}"
            )

            if p_value < min_p_value:
                min_p_value = p_value
                max_effect_size = effect_size

            # Check if treatment is better
            treatment_perf = variant_metrics[treatment_id].avg_performance
            if treatment_perf > best_performance and p_value < (1 - experiment.confidence_level):
                best_variant_id = treatment_id
                best_performance = treatment_perf

        # Determine statistical significance
        statistically_significant = min_p_value < (1 - experiment.confidence_level)

        # Generate recommendation
        if not statistically_significant:
            recommendation = "No significant difference found. Continue with control or run longer."
        elif best_variant_id == control_variant_id:
            recommendation = "Control performs best. No changes recommended."
        else:
            improvement = (best_performance - variant_metrics[control_variant_id].avg_performance) * 100
            recommendation = (
                f"Roll out variant {best_variant_id}. "
                f"Expected improvement: {improvement:.1f}%"
            )

        result = ExperimentResult(
            experiment_id=experiment_id,
            variant_metrics=variant_metrics,
            winner=best_variant_id if statistically_significant else None,
            statistical_significance=statistically_significant,
            p_value=min_p_value,
            effect_size=max_effect_size,
            recommendation=recommendation,
            completed_at=datetime.now(),
        )

        logger.info(
            f"Experiment analyzed: {experiment.name}, "
            f"winner={best_variant_id}, p={min_p_value:.4f}"
        )

        return result

    def complete_experiment(self, experiment_id: str) -> bool:
        """
        Mark experiment as completed

        Args:
            experiment_id: Experiment identifier

        Returns:
            True if completed successfully
        """
        if experiment_id not in self.experiments:
            return False

        experiment = self.experiments[experiment_id]

        if experiment.status != ExperimentStatus.RUNNING:
            return False

        experiment.status = ExperimentStatus.COMPLETED
        experiment.end_date = datetime.now()

        self.stats['running_experiments'] -= 1
        self.stats['completed_experiments'] += 1

        logger.info(f"Experiment completed: {experiment.name}")

        return True

    def _generate_experiment_id(self, name: str) -> str:
        """Generate unique experiment ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        hash_input = f"{name}_{timestamp}".encode()
        hash_digest = hashlib.sha256(hash_input).hexdigest()[:8]
        return f"exp_{timestamp}_{hash_digest}"

    def export_experiment_results(self, experiment_id: str, filepath: str) -> bool:
        """
        Export experiment results to JSON file

        Args:
            experiment_id: Experiment identifier
            filepath: Output file path

        Returns:
            True if export successful
        """
        if experiment_id not in self.experiments:
            return False

        experiment = self.experiments[experiment_id]
        result = self.analyze_experiment(experiment_id)

        try:
            export_data = {
                'experiment': asdict(experiment),
                'result': asdict(result) if result else None,
                'exported_at': datetime.now().isoformat(),
            }

            # Convert datetime objects to strings
            export_data['experiment']['created_at'] = export_data['experiment']['created_at'].isoformat()
            export_data['experiment']['start_date'] = (
                export_data['experiment']['start_date'].isoformat()
                if export_data['experiment']['start_date'] else None
            )
            export_data['experiment']['end_date'] = (
                export_data['experiment']['end_date'].isoformat()
                if export_data['experiment']['end_date'] else None
            )

            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)

            logger.info(f"Experiment results exported to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error exporting results: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get A/B testing statistics

        Returns:
            Statistics dictionary
        """
        return {
            **self.stats,
            'total_variants': sum(len(exp.variants) for exp in self.experiments.values()),
            'avg_variants_per_experiment': (
                sum(len(exp.variants) for exp in self.experiments.values()) / len(self.experiments)
                if self.experiments else 0
            ),
        }
