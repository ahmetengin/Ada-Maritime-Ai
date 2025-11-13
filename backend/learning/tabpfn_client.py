"""
Real TabPFN API Client - Production-Ready Integration

Connects to TabPFN-2.5 REST API for few-shot learning predictions.
Falls back to KNN simulation if API is unavailable.

Author: Ada Maritime AI Team
Date: November 2025
"""

import logging
import requests
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import time
import json

from .models import Experience, Prediction

logger = logging.getLogger(__name__)


class TabPFNAPIClient:
    """
    Production TabPFN API Client

    Features:
    - REST API integration with TabPFN-2.5 service
    - Automatic retry with exponential backoff
    - Circuit breaker pattern for fault tolerance
    - Health check monitoring
    - Fallback to KNN simulation
    """

    DEFAULT_API_URL = "https://api.tabpfn.com/v2.5"
    DEFAULT_TIMEOUT = 10.0  # seconds
    MAX_RETRIES = 3
    CIRCUIT_BREAKER_THRESHOLD = 5  # failures before opening circuit
    CIRCUIT_BREAKER_TIMEOUT = 60  # seconds before retry

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        enable_fallback: bool = True
    ):
        """
        Initialize TabPFN API client

        Args:
            api_key: TabPFN API key (from environment or config)
            api_url: TabPFN API endpoint URL
            timeout: Request timeout in seconds
            enable_fallback: Enable KNN fallback if API unavailable
        """
        self.api_key = api_key
        self.api_url = api_url or self.DEFAULT_API_URL
        self.timeout = timeout
        self.enable_fallback = enable_fallback

        # Circuit breaker state
        self.circuit_breaker_open = False
        self.circuit_breaker_failures = 0
        self.circuit_breaker_last_failure = None

        # Statistics
        self.stats = {
            'api_calls': 0,
            'api_successes': 0,
            'api_failures': 0,
            'fallback_uses': 0,
            'avg_latency_ms': 0.0,
        }

        # KNN fallback
        from .tabpfn_adapter import TabPFNAdapter
        self.fallback_adapter = TabPFNAdapter(enable_caching=True) if enable_fallback else None

        logger.info(
            f"TabPFN API client initialized (url={self.api_url}, "
            f"fallback={'enabled' if enable_fallback else 'disabled'})"
        )

    def health_check(self) -> bool:
        """
        Check if TabPFN API is available

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = requests.get(
                f"{self.api_url}/health",
                timeout=5.0
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"TabPFN API health check failed: {e}")
            return False

    def _check_circuit_breaker(self) -> bool:
        """
        Check if circuit breaker is open

        Returns:
            True if requests should be blocked, False otherwise
        """
        if not self.circuit_breaker_open:
            return False

        # Check if timeout has passed
        if self.circuit_breaker_last_failure:
            elapsed = (datetime.now() - self.circuit_breaker_last_failure).total_seconds()
            if elapsed > self.CIRCUIT_BREAKER_TIMEOUT:
                logger.info("Circuit breaker: Attempting half-open state")
                self.circuit_breaker_open = False
                self.circuit_breaker_failures = 0
                return False

        logger.debug("Circuit breaker: Open, blocking request")
        return True

    def _record_failure(self):
        """Record API failure and update circuit breaker"""
        self.circuit_breaker_failures += 1
        self.circuit_breaker_last_failure = datetime.now()
        self.stats['api_failures'] += 1

        if self.circuit_breaker_failures >= self.CIRCUIT_BREAKER_THRESHOLD:
            self.circuit_breaker_open = True
            logger.warning(
                f"Circuit breaker: OPEN after {self.circuit_breaker_failures} failures"
            )

    def _record_success(self):
        """Record API success and reset circuit breaker"""
        self.circuit_breaker_failures = 0
        self.circuit_breaker_open = False
        self.stats['api_successes'] += 1

    def predict(
        self,
        training_data: List[Experience],
        query_experience: Experience,
        target: str = "outcome",
        confidence_threshold: float = 0.6
    ) -> Optional[Prediction]:
        """
        Predict using TabPFN API

        Args:
            training_data: List of training experiences
            query_experience: Experience to predict
            target: Target variable to predict
            confidence_threshold: Minimum confidence threshold

        Returns:
            Prediction object or None if confidence too low
        """
        self.stats['api_calls'] += 1

        # Check circuit breaker
        if self._check_circuit_breaker():
            logger.warning("Circuit breaker open, using fallback")
            return self._fallback_predict(training_data, query_experience, target, confidence_threshold)

        # Check if API key is available
        if not self.api_key:
            logger.warning("No API key provided, using fallback")
            return self._fallback_predict(training_data, query_experience, target, confidence_threshold)

        # Prepare request
        start_time = time.time()

        try:
            # Convert experiences to tabular format
            X_train, y_train = self._experiences_to_arrays(training_data, target)
            X_query, _ = self._experiences_to_arrays([query_experience], target)

            # Make API request with retry
            response = self._make_request_with_retry({
                'X_train': X_train.tolist(),
                'y_train': y_train.tolist(),
                'X_query': X_query.tolist(),
                'confidence_threshold': confidence_threshold,
            })

            if response is None:
                return self._fallback_predict(training_data, query_experience, target, confidence_threshold)

            # Parse response
            prediction = self._parse_response(response, query_experience, target)

            # Record metrics
            latency_ms = (time.time() - start_time) * 1000
            self._update_latency(latency_ms)
            self._record_success()

            logger.debug(f"TabPFN API prediction: {prediction.predicted_value} (confidence: {prediction.confidence:.2f}, latency: {latency_ms:.1f}ms)")

            return prediction

        except Exception as e:
            logger.error(f"TabPFN API error: {e}")
            self._record_failure()
            return self._fallback_predict(training_data, query_experience, target, confidence_threshold)

    def _make_request_with_retry(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make API request with exponential backoff retry

        Args:
            payload: Request payload

        Returns:
            Response JSON or None if all retries failed
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.post(
                    f"{self.api_url}/predict",
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                    time.sleep(wait_time)
                else:
                    logger.error(f"API error: {response.status_code} - {response.text}")
                    return None

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{self.MAX_RETRIES})")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Request error: {e}")
                return None

        return None

    def _experiences_to_arrays(
        self,
        experiences: List[Experience],
        target: str
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert experiences to numpy arrays for API

        Args:
            experiences: List of experiences
            target: Target variable name

        Returns:
            Tuple of (X, y) numpy arrays
        """
        # Extract features from experiences
        X = []
        y = []

        for exp in experiences:
            # Combine context, metrics, and vessel_state as features
            features = {}
            features.update(exp.context)
            features.update(exp.metrics)
            if exp.vessel_state:
                features.update(exp.vessel_state)

            # Convert to numeric features
            feature_vec = []
            for key in sorted(features.keys()):
                val = features[key]
                if isinstance(val, (int, float)):
                    feature_vec.append(val)
                elif isinstance(val, bool):
                    feature_vec.append(1.0 if val else 0.0)
                elif isinstance(val, str):
                    # Simple hash for categorical
                    feature_vec.append(hash(val) % 1000 / 1000.0)

            X.append(feature_vec)

            # Target value
            if target == "outcome":
                y.append(1.0 if exp.outcome == "success" else 0.0)
            elif target == "performance_score":
                y.append(exp.performance_score)
            else:
                y.append(exp.metrics.get(target, 0.0))

        return np.array(X), np.array(y)

    def _parse_response(
        self,
        response: Dict[str, Any],
        experience: Experience,
        target: str
    ) -> Prediction:
        """
        Parse API response into Prediction object

        Args:
            response: API response JSON
            experience: Query experience
            target: Target variable

        Returns:
            Prediction object
        """
        predicted_value = response['prediction']
        confidence = response['confidence']
        probabilities = response.get('probabilities', {})

        # Convert back to outcome string if needed
        if target == "outcome":
            predicted_outcome = "success" if predicted_value > 0.5 else "failure"
        else:
            predicted_outcome = str(predicted_value)

        return Prediction(
            prediction_id=f"tabpfn_{experience.experience_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            experience_id=experience.experience_id,
            predicted_value=predicted_outcome,
            confidence=confidence,
            probabilities=probabilities,
            strategy=LearningStrategy.TABPFN,
            model_version="tabpfn-2.5-api",
            sample_count=response.get('training_samples', 0),
        )

    def _fallback_predict(
        self,
        training_data: List[Experience],
        query_experience: Experience,
        target: str,
        confidence_threshold: float
    ) -> Optional[Prediction]:
        """
        Use KNN fallback for prediction

        Args:
            training_data: Training experiences
            query_experience: Query experience
            target: Target variable
            confidence_threshold: Confidence threshold

        Returns:
            Prediction or None
        """
        if not self.enable_fallback or not self.fallback_adapter:
            logger.error("Fallback disabled and API unavailable")
            return None

        self.stats['fallback_uses'] += 1
        logger.info(f"Using KNN fallback (fallback uses: {self.stats['fallback_uses']})")

        # Add training data to fallback
        for exp in training_data:
            self.fallback_adapter.add_training_sample(exp)

        # Predict using fallback
        return self.fallback_adapter.predict(query_experience, target, confidence_threshold)

    def _update_latency(self, latency_ms: float):
        """Update average latency metric"""
        if self.stats['api_successes'] == 1:
            self.stats['avg_latency_ms'] = latency_ms
        else:
            alpha = 0.1  # Exponential moving average
            self.stats['avg_latency_ms'] = (
                alpha * latency_ms +
                (1 - alpha) * self.stats['avg_latency_ms']
            )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get API client statistics

        Returns:
            Statistics dictionary
        """
        total_calls = self.stats['api_calls']
        if total_calls == 0:
            success_rate = 0.0
            fallback_rate = 0.0
        else:
            success_rate = self.stats['api_successes'] / total_calls
            fallback_rate = self.stats['fallback_uses'] / total_calls

        return {
            **self.stats,
            'success_rate': success_rate,
            'fallback_rate': fallback_rate,
            'circuit_breaker_open': self.circuit_breaker_open,
            'circuit_breaker_failures': self.circuit_breaker_failures,
        }
