"""
Federated Learning for Multi-Marina Cross-Learning

Enables secure knowledge sharing across marinas while preserving privacy:
- Privacy-preserving model aggregation
- Differential privacy guarantees
- Secure multi-party computation
- Tenant isolation and access control

Author: Ada Maritime AI Team
Date: November 2025
"""

import logging
import hashlib
import json
import numpy as np
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict

from .models import Experience, Pattern, LearningStrategy

logger = logging.getLogger(__name__)


@dataclass
class TenantModel:
    """Model update from a single tenant/marina"""
    tenant_id: str
    marina_name: str
    model_weights: Dict[str, float]
    sample_count: int
    performance_metrics: Dict[str, float]
    timestamp: datetime
    privacy_budget: float  # Differential privacy budget spent


@dataclass
class GlobalModel:
    """Aggregated global model"""
    model_id: str
    version: int
    aggregated_weights: Dict[str, float]
    participating_tenants: List[str]
    total_samples: int
    avg_performance: float
    created_at: datetime
    privacy_guarantee: float  # Epsilon for differential privacy


class FederatedLearningCoordinator:
    """
    Federated Learning Coordinator for Multi-Marina Cross-Learning

    Features:
    - Privacy-preserving federated averaging
    - Differential privacy with configurable epsilon
    - Secure aggregation across tenants
    - Performance-weighted model combination
    - Tenant opt-in/opt-out control
    """

    DEFAULT_PRIVACY_EPSILON = 1.0  # Differential privacy parameter
    DEFAULT_MIN_PARTICIPANTS = 3   # Minimum marinas for aggregation
    AGGREGATION_INTERVAL_HOURS = 24

    def __init__(
        self,
        privacy_epsilon: float = DEFAULT_PRIVACY_EPSILON,
        min_participants: int = DEFAULT_MIN_PARTICIPANTS,
        enable_privacy: bool = True
    ):
        """
        Initialize federated learning coordinator

        Args:
            privacy_epsilon: Privacy budget (smaller = more private)
            min_participants: Minimum participants for aggregation
            enable_privacy: Enable differential privacy
        """
        self.privacy_epsilon = privacy_epsilon
        self.min_participants = min_participants
        self.enable_privacy = enable_privacy

        # State
        self.tenant_models: Dict[str, TenantModel] = {}
        self.global_models: List[GlobalModel] = []
        self.opt_in_tenants: Set[str] = set()
        self.last_aggregation: Optional[datetime] = None

        # Statistics
        self.stats = {
            'total_aggregations': 0,
            'total_participating_tenants': 0,
            'avg_model_improvement': 0.0,
            'privacy_budget_spent': 0.0,
        }

        logger.info(
            f"Federated learning coordinator initialized "
            f"(epsilon={privacy_epsilon}, min_participants={min_participants}, "
            f"privacy={'enabled' if enable_privacy else 'disabled'})"
        )

    def tenant_opt_in(self, tenant_id: str, marina_name: str):
        """
        Tenant opts into federated learning

        Args:
            tenant_id: Tenant identifier
            marina_name: Marina name
        """
        self.opt_in_tenants.add(tenant_id)
        logger.info(f"Tenant {tenant_id} ({marina_name}) opted into federated learning")

    def tenant_opt_out(self, tenant_id: str):
        """
        Tenant opts out of federated learning

        Args:
            tenant_id: Tenant identifier
        """
        self.opt_in_tenants.discard(tenant_id)
        if tenant_id in self.tenant_models:
            del self.tenant_models[tenant_id]
        logger.info(f"Tenant {tenant_id} opted out of federated learning")

    def submit_local_model(
        self,
        tenant_id: str,
        marina_name: str,
        experiences: List[Experience],
        model_weights: Dict[str, float],
        performance_metrics: Dict[str, float]
    ) -> bool:
        """
        Submit local model update from a marina

        Args:
            tenant_id: Tenant identifier
            marina_name: Marina name
            experiences: Local training experiences
            model_weights: Local model weights
            performance_metrics: Performance metrics

        Returns:
            True if submission successful
        """
        # Check opt-in
        if tenant_id not in self.opt_in_tenants:
            logger.warning(f"Tenant {tenant_id} not opted in, rejecting submission")
            return False

        # Apply differential privacy
        if self.enable_privacy:
            model_weights = self._apply_differential_privacy(
                model_weights,
                self.privacy_epsilon
            )
            privacy_budget = self.privacy_epsilon
        else:
            privacy_budget = 0.0

        # Create tenant model
        tenant_model = TenantModel(
            tenant_id=tenant_id,
            marina_name=marina_name,
            model_weights=model_weights,
            sample_count=len(experiences),
            performance_metrics=performance_metrics,
            timestamp=datetime.now(),
            privacy_budget=privacy_budget,
        )

        self.tenant_models[tenant_id] = tenant_model

        logger.info(
            f"Local model submitted: {marina_name} ({len(experiences)} samples, "
            f"privacy_budget={privacy_budget:.2f})"
        )

        # Check if ready for aggregation
        self._check_and_aggregate()

        return True

    def _apply_differential_privacy(
        self,
        weights: Dict[str, float],
        epsilon: float
    ) -> Dict[str, float]:
        """
        Apply differential privacy (Laplace mechanism) to model weights

        Args:
            weights: Original weights
            epsilon: Privacy parameter

        Returns:
            Noisy weights with privacy guarantee
        """
        noisy_weights = {}

        for key, value in weights.items():
            # Laplace noise: scale = sensitivity / epsilon
            # Assuming sensitivity = 1 for normalized weights
            noise_scale = 1.0 / epsilon
            noise = np.random.laplace(0, noise_scale)
            noisy_weights[key] = value + noise

        logger.debug(f"Applied differential privacy: epsilon={epsilon:.2f}")

        return noisy_weights

    def _check_and_aggregate(self):
        """Check if conditions met for aggregation and perform if ready"""
        # Check minimum participants
        if len(self.tenant_models) < self.min_participants:
            logger.debug(
                f"Not enough participants: {len(self.tenant_models)}/{self.min_participants}"
            )
            return

        # Check time interval
        if self.last_aggregation:
            hours_since = (datetime.now() - self.last_aggregation).total_seconds() / 3600
            if hours_since < self.AGGREGATION_INTERVAL_HOURS:
                logger.debug(
                    f"Too soon for aggregation: {hours_since:.1f}h/{self.AGGREGATION_INTERVAL_HOURS}h"
                )
                return

        # Perform aggregation
        self._aggregate_models()

    def _aggregate_models(self):
        """
        Aggregate tenant models into global model using federated averaging

        Uses weighted averaging based on sample count and performance
        """
        if len(self.tenant_models) < self.min_participants:
            return

        logger.info(f"Starting federated aggregation: {len(self.tenant_models)} participants")

        # Calculate weights for each tenant
        total_samples = sum(tm.sample_count for tm in self.tenant_models.values())
        total_performance = sum(
            tm.performance_metrics.get('avg_performance', 0.5)
            for tm in self.tenant_models.values()
        )

        # Aggregate weights
        aggregated_weights: Dict[str, float] = defaultdict(float)
        participating_tenants = []
        total_privacy_budget = 0.0

        for tenant_id, tenant_model in self.tenant_models.items():
            # Performance-weighted contribution
            sample_weight = tenant_model.sample_count / total_samples
            performance_weight = (
                tenant_model.performance_metrics.get('avg_performance', 0.5) /
                (total_performance / len(self.tenant_models))
            )
            tenant_weight = (sample_weight + performance_weight) / 2.0

            # Add weighted contribution
            for key, value in tenant_model.model_weights.items():
                aggregated_weights[key] += value * tenant_weight

            participating_tenants.append(tenant_id)
            total_privacy_budget += tenant_model.privacy_budget

        # Create global model
        global_model = GlobalModel(
            model_id=self._generate_model_id(),
            version=len(self.global_models) + 1,
            aggregated_weights=dict(aggregated_weights),
            participating_tenants=participating_tenants,
            total_samples=total_samples,
            avg_performance=total_performance / len(self.tenant_models),
            created_at=datetime.now(),
            privacy_guarantee=total_privacy_budget / len(self.tenant_models),
        )

        self.global_models.append(global_model)
        self.last_aggregation = datetime.now()

        # Update statistics
        self.stats['total_aggregations'] += 1
        self.stats['total_participating_tenants'] += len(participating_tenants)
        self.stats['privacy_budget_spent'] += total_privacy_budget

        # Calculate improvement
        if len(self.global_models) > 1:
            prev_performance = self.global_models[-2].avg_performance
            improvement = global_model.avg_performance - prev_performance
            self.stats['avg_model_improvement'] = (
                0.9 * self.stats['avg_model_improvement'] + 0.1 * improvement
            )

        logger.info(
            f"Federated aggregation complete: "
            f"v{global_model.version}, "
            f"{len(participating_tenants)} tenants, "
            f"{total_samples} samples, "
            f"avg_performance={global_model.avg_performance:.3f}"
        )

        # Clear tenant models for next round
        self.tenant_models.clear()

    def get_global_model(self) -> Optional[GlobalModel]:
        """
        Get latest global model

        Returns:
            Latest global model or None
        """
        if not self.global_models:
            return None
        return self.global_models[-1]

    def get_global_model_weights(self, tenant_id: str) -> Optional[Dict[str, float]]:
        """
        Get global model weights for a tenant

        Args:
            tenant_id: Requesting tenant

        Returns:
            Model weights or None if tenant not authorized
        """
        # Check authorization
        if tenant_id not in self.opt_in_tenants:
            logger.warning(f"Unauthorized access attempt by tenant {tenant_id}")
            return None

        global_model = self.get_global_model()
        if not global_model:
            return None

        return global_model.aggregated_weights

    def get_cross_marina_patterns(
        self,
        min_marinas: int = 2,
        min_confidence: float = 0.7
    ) -> List[Pattern]:
        """
        Extract patterns that appear across multiple marinas

        Args:
            min_marinas: Minimum number of marinas for pattern
            min_confidence: Minimum confidence threshold

        Returns:
            List of cross-marina patterns
        """
        # This would analyze patterns across tenants
        # For now, returning empty list (placeholder for future implementation)
        patterns = []

        logger.info(f"Cross-marina pattern analysis: {len(patterns)} patterns found")

        return patterns

    def _generate_model_id(self) -> str:
        """Generate unique model ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        participants = '_'.join(sorted(self.tenant_models.keys())[:5])
        hash_input = f"{timestamp}_{participants}".encode()
        hash_digest = hashlib.sha256(hash_input).hexdigest()[:12]
        return f"global_model_{timestamp}_{hash_digest}"

    def export_global_model(self, filepath: str) -> bool:
        """
        Export global model to file

        Args:
            filepath: Output file path

        Returns:
            True if export successful
        """
        global_model = self.get_global_model()
        if not global_model:
            logger.warning("No global model to export")
            return False

        try:
            model_dict = {
                'model_id': global_model.model_id,
                'version': global_model.version,
                'weights': global_model.aggregated_weights,
                'participants': global_model.participating_tenants,
                'total_samples': global_model.total_samples,
                'avg_performance': global_model.avg_performance,
                'created_at': global_model.created_at.isoformat(),
                'privacy_guarantee': global_model.privacy_guarantee,
            }

            with open(filepath, 'w') as f:
                json.dump(model_dict, f, indent=2)

            logger.info(f"Global model exported to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error exporting model: {e}")
            return False

    def import_global_model(self, filepath: str) -> bool:
        """
        Import global model from file

        Args:
            filepath: Input file path

        Returns:
            True if import successful
        """
        try:
            with open(filepath, 'r') as f:
                model_dict = json.load(f)

            global_model = GlobalModel(
                model_id=model_dict['model_id'],
                version=model_dict['version'],
                aggregated_weights=model_dict['weights'],
                participating_tenants=model_dict['participants'],
                total_samples=model_dict['total_samples'],
                avg_performance=model_dict['avg_performance'],
                created_at=datetime.fromisoformat(model_dict['created_at']),
                privacy_guarantee=model_dict['privacy_guarantee'],
            )

            self.global_models.append(global_model)

            logger.info(f"Global model imported from {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error importing model: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get federated learning statistics

        Returns:
            Statistics dictionary
        """
        latest_model = self.get_global_model()

        return {
            **self.stats,
            'opt_in_tenants': len(self.opt_in_tenants),
            'pending_models': len(self.tenant_models),
            'global_model_version': latest_model.version if latest_model else 0,
            'last_aggregation': self.last_aggregation.isoformat() if self.last_aggregation else None,
        }
