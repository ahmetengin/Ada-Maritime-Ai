"""
TabPFN-2.5 Adapter - Few-Shot Learning for Tabular Data

Ported from Ada repo's TypeScript implementation (core/learning/TabPFNAdapter.ts)

TabPFN-2.5 achieves 100% win rate vs XGBoost on datasets with ≤10,000 samples.
Uses zero-training in-context learning for immediate predictions.

Reference: "Advancing the State of the Art in Tabular Foundation Models"
           arXiv:2511.08667v1, November 2025
"""

import math
import logging
from typing import Dict, List, Optional, Any, Tuple, Literal
from datetime import datetime, timedelta
from collections import defaultdict

from .models import Experience, Prediction, LearningStrategy

logger = logging.getLogger(__name__)


class TabPFNAdapter:
    """
    TabPFN-2.5 Adapter for few-shot learning on tabular data

    Features:
    - K-nearest neighbor simulation (production would use actual TabPFN API)
    - Intelligent caching for performance
    - Model distillation support (MLP, XGBoost, Random Forest)
    - Automatic confidence thresholds based on sample count
    """

    # Configuration
    FEW_SHOT_THRESHOLD = 10  # < 10 samples = TabPFN only
    HYBRID_THRESHOLD = 100   # 10-100 samples = Hybrid mode
    MAX_SAMPLES = 10000      # Maximum training samples
    MAX_FEATURES = 2000      # Maximum features
    K_NEIGHBORS = 5          # K for KNN simulation

    def __init__(self, enable_caching: bool = True):
        """
        Initialize TabPFN adapter

        Args:
            enable_caching: Enable prediction caching for performance
        """
        self.training_data: List[Experience] = []
        self.enable_caching = enable_caching
        self.prediction_cache: Dict[str, Tuple[Prediction, datetime]] = {}
        self.cache_ttl_seconds = 300  # 5 minutes

        # Statistics
        self.stats = {
            'predictions': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'training_samples': 0,
        }

        # Distillation state
        self.distilled_model: Optional[Dict[str, Any]] = None
        self.distilled_model_type: Optional[Literal['mlp', 'xgboost', 'random_forest']] = None

        logger.info(
            f"TabPFN adapter initialized (caching={'enabled' if enable_caching else 'disabled'}, "
            f"K={self.K_NEIGHBORS})"
        )

    def add_training_sample(self, experience: Experience):
        """
        Add training sample to TabPFN training set

        Args:
            experience: Experience to add as training data
        """
        self.training_data.append(experience)
        self.stats['training_samples'] = len(self.training_data)

        # Limit training data size (FIFO removal)
        if len(self.training_data) > self.MAX_SAMPLES:
            removed = self.training_data.pop(0)
            logger.debug(f"Removed oldest sample {removed.experience_id} (max samples reached)")

        logger.debug(f"Added training sample {experience.experience_id} (total: {len(self.training_data)})")

    def predict(
        self,
        experience: Experience,
        target: str = "outcome",
        confidence_threshold: float = 0.6
    ) -> Optional[Prediction]:
        """
        Predict outcome using TabPFN few-shot learning

        Args:
            experience: Experience to predict
            target: Target variable to predict
            confidence_threshold: Minimum confidence threshold

        Returns:
            Prediction object or None if insufficient data
        """
        self.stats['predictions'] += 1

        # Check cache
        if self.enable_caching:
            cache_key = self._generate_cache_key(experience, target)
            cached = self._check_cache(cache_key)
            if cached:
                self.stats['cache_hits'] += 1
                return cached

        self.stats['cache_misses'] += 1

        # Check if we have enough training data
        if len(self.training_data) < 1:
            logger.warning("Insufficient training data for prediction (need at least 1 sample)")
            return None

        # Convert experience to feature vector
        features = self._extract_features(experience)

        # Find K-nearest neighbors
        neighbors = self._find_k_nearest_neighbors(features, self.K_NEIGHBORS)

        if not neighbors:
            logger.warning("No neighbors found for prediction")
            return None

        # Predict using weighted voting
        predicted_outcome, confidence, probabilities = self._weighted_voting(neighbors, target)

        # Check confidence threshold
        if confidence < confidence_threshold:
            logger.debug(
                f"Prediction confidence {confidence:.2f} below threshold {confidence_threshold}"
            )
            return None

        # Create prediction object
        prediction = Prediction(
            predicted_outcome=predicted_outcome,
            confidence=confidence,
            probabilities=probabilities,
            strategy=LearningStrategy.TABPFN,
            sample_count=len(self.training_data),
            reasoning=f"Based on {len(neighbors)} similar experiences (K={self.K_NEIGHBORS})",
            contributing_factors=self._extract_contributing_factors(neighbors),
            from_cache=False
        )

        # Cache prediction
        if self.enable_caching:
            self._cache_prediction(cache_key, prediction)

        logger.info(
            f"TabPFN prediction: {predicted_outcome} (confidence: {confidence:.2f}, "
            f"samples: {len(self.training_data)})"
        )

        return prediction

    def _extract_features(self, experience: Experience) -> Dict[str, Any]:
        """Extract feature vector from experience"""
        features = {}

        # Context features
        for key, value in experience.context.items():
            features[f"context_{key}"] = value

        # Vessel state features
        if experience.vessel_state:
            for key, value in experience.vessel_state.items():
                features[f"vessel_{key}"] = value

        # Action parameters
        for key, value in experience.action_params.items():
            features[f"action_{key}"] = value

        # Metrics
        for key, value in experience.metrics.items():
            features[f"metric_{key}"] = value

        # Categorical features
        features['experience_type'] = experience.experience_type.value
        features['action'] = experience.action

        # Temporal features
        features['hour'] = experience.timestamp.hour
        features['day_of_week'] = experience.timestamp.weekday()

        return features

    def _find_k_nearest_neighbors(
        self,
        query_features: Dict[str, Any],
        k: int
    ) -> List[Tuple[Experience, float]]:
        """
        Find K-nearest neighbors using Euclidean distance

        Args:
            query_features: Query feature vector
            k: Number of neighbors

        Returns:
            List of (experience, distance) tuples
        """
        distances = []

        for training_exp in self.training_data:
            training_features = self._extract_features(training_exp)
            distance = self._calculate_distance(query_features, training_features)
            distances.append((training_exp, distance))

        # Sort by distance and return top K
        distances.sort(key=lambda x: x[1])
        return distances[:k]

    def _calculate_distance(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any]
    ) -> float:
        """
        Calculate Euclidean distance between two feature vectors

        Handles mixed data types (numeric, categorical, boolean)
        """
        distance = 0.0
        all_keys = set(features1.keys()) | set(features2.keys())

        for key in all_keys:
            val1 = features1.get(key)
            val2 = features2.get(key)

            # Handle missing values
            if val1 is None or val2 is None:
                distance += 1.0  # Penalty for missing value
                continue

            # Numeric distance
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                distance += (val1 - val2) ** 2

            # Categorical/string distance
            elif isinstance(val1, str) and isinstance(val2, str):
                distance += 0.0 if val1 == val2 else 1.0

            # Boolean distance
            elif isinstance(val1, bool) and isinstance(val2, bool):
                distance += 0.0 if val1 == val2 else 1.0

            # Type mismatch
            else:
                distance += 1.0

        return math.sqrt(distance)

    def _weighted_voting(
        self,
        neighbors: List[Tuple[Experience, float]],
        target: str
    ) -> Tuple[str, float, Dict[str, float]]:
        """
        Weighted voting for classification

        Args:
            neighbors: List of (experience, distance) tuples
            target: Target variable

        Returns:
            (predicted_outcome, confidence, probabilities)
        """
        votes: Dict[str, float] = defaultdict(float)
        total_weight = 0.0

        for experience, distance in neighbors:
            # Weight = 1 / (distance + epsilon)
            weight = 1.0 / (distance + 1e-6)

            # Get outcome
            if target == "outcome":
                outcome = experience.outcome
            else:
                outcome = experience.context.get(target, "unknown")

            votes[outcome] += weight
            total_weight += weight

        # Normalize to probabilities
        probabilities = {
            outcome: weight / total_weight
            for outcome, weight in votes.items()
        }

        # Get prediction (highest probability)
        predicted_outcome = max(probabilities, key=probabilities.get)
        confidence = probabilities[predicted_outcome]

        return predicted_outcome, confidence, probabilities

    def _extract_contributing_factors(
        self,
        neighbors: List[Tuple[Experience, float]]
    ) -> List[str]:
        """Extract contributing factors from nearest neighbors"""
        factors = []

        # Get common patterns from neighbors
        if neighbors:
            closest_exp, _ = neighbors[0]

            # Experience type
            factors.append(f"Similar to {closest_exp.experience_type.value} experiences")

            # Performance
            avg_performance = sum(exp.performance_score for exp, _ in neighbors) / len(neighbors)
            factors.append(f"Avg neighbor performance: {avg_performance:.2f}")

            # Context patterns
            common_contexts = self._find_common_context(neighbors)
            if common_contexts:
                factors.append(f"Common context: {common_contexts}")

        return factors

    def _find_common_context(
        self,
        neighbors: List[Tuple[Experience, float]]
    ) -> str:
        """Find common context patterns in neighbors"""
        if not neighbors:
            return ""

        # Count context keys
        context_counts: Dict[str, int] = defaultdict(int)
        for exp, _ in neighbors:
            for key in exp.context.keys():
                context_counts[key] += 1

        # Find most common (appears in >50% of neighbors)
        threshold = len(neighbors) / 2
        common = [key for key, count in context_counts.items() if count > threshold]

        return ", ".join(common[:3]) if common else ""

    def _generate_cache_key(self, experience: Experience, target: str) -> str:
        """Generate cache key for prediction"""
        features = self._extract_features(experience)
        # Simple hash of features
        feature_str = "_".join(f"{k}:{v}" for k, v in sorted(features.items())[:5])
        return f"{target}_{hash(feature_str)}"

    def _check_cache(self, cache_key: str) -> Optional[Prediction]:
        """Check if prediction is in cache"""
        if cache_key in self.prediction_cache:
            prediction, cached_at = self.prediction_cache[cache_key]

            # Check TTL
            age = (datetime.now() - cached_at).total_seconds()
            if age < self.cache_ttl_seconds:
                prediction.from_cache = True
                prediction.cache_age_seconds = age
                logger.debug(f"Cache hit: {cache_key} (age: {age:.1f}s)")
                return prediction
            else:
                # Expired
                del self.prediction_cache[cache_key]
                logger.debug(f"Cache expired: {cache_key}")

        return None

    def _cache_prediction(self, cache_key: str, prediction: Prediction):
        """Cache prediction"""
        self.prediction_cache[cache_key] = (prediction, datetime.now())
        logger.debug(f"Cached prediction: {cache_key}")

    def is_suitable_for_tabpfn(self, sample_count: Optional[int] = None) -> bool:
        """
        Check if current dataset is suitable for TabPFN

        Args:
            sample_count: Override sample count (uses training_data length if None)

        Returns:
            True if TabPFN is suitable
        """
        count = sample_count if sample_count is not None else len(self.training_data)
        return count < self.FEW_SHOT_THRESHOLD

    def get_recommended_confidence_threshold(self, sample_count: Optional[int] = None) -> float:
        """
        Get recommended confidence threshold based on sample count

        Args:
            sample_count: Override sample count

        Returns:
            Recommended confidence threshold (0.6-0.85)
        """
        count = sample_count if sample_count is not None else len(self.training_data)

        if count < 5:
            return 0.85  # High threshold for very few samples
        elif count < 10:
            return 0.75
        elif count < 50:
            return 0.70
        else:
            return 0.60  # Lower threshold for more samples

    def distill_model(
        self,
        model_type: Literal['mlp', 'xgboost', 'random_forest'] = 'xgboost'
    ) -> Dict[str, Any]:
        """
        Distill TabPFN model to faster alternative

        Note: This is a simulation. Production would train actual models.

        Args:
            model_type: Type of model to distill to

        Returns:
            Distilled model metadata
        """
        logger.info(f"Distilling TabPFN model to {model_type}...")

        # Simulated distillation results
        distillation_info = {
            'mlp': {'accuracy': 0.93, 'speedup': '50x', 'size_mb': 2.5},
            'xgboost': {'accuracy': 0.95, 'speedup': '100x', 'size_mb': 5.0},
            'random_forest': {'accuracy': 0.92, 'speedup': '75x', 'size_mb': 8.0},
        }

        info = distillation_info[model_type]

        self.distilled_model = {
            'type': model_type,
            'accuracy': info['accuracy'],
            'speedup': info['speedup'],
            'size_mb': info['size_mb'],
            'training_samples': len(self.training_data),
            'created_at': datetime.now().isoformat()
        }
        self.distilled_model_type = model_type

        logger.info(
            f"Model distilled: {model_type} "
            f"(accuracy: {info['accuracy']:.2%}, speedup: {info['speedup']})"
        )

        return self.distilled_model

    def get_statistics(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        cache_hit_rate = 0.0
        if self.stats['predictions'] > 0:
            cache_hit_rate = self.stats['cache_hits'] / self.stats['predictions']

        return {
            'training_samples': len(self.training_data),
            'cache_size': len(self.prediction_cache),
            'predictions': self.stats['predictions'],
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'cache_hit_rate': cache_hit_rate,
            'distilled_model': self.distilled_model_type,
            'max_samples': self.MAX_SAMPLES,
            'max_features': self.MAX_FEATURES,
        }

    def reset(self):
        """Reset adapter state"""
        self.training_data.clear()
        self.prediction_cache.clear()
        self.stats = {
            'predictions': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'training_samples': 0,
        }
        self.distilled_model = None
        self.distilled_model_type = None
        logger.info("TabPFN adapter reset")
