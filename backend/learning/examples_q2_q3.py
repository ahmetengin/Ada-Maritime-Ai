"""
Q2-Q3 2026 Features Examples

Demonstrates usage of new features:
1. Real TabPFN API Integration
2. GPU Acceleration
3. Multi-Marina Cross-Learning (Federated Learning)
4. A/B Testing Framework

Author: Ada Maritime AI Team
Date: November 2025
"""

import logging
from datetime import datetime
from typing import List

from .models import Experience, ExperienceType
from .tabpfn_client import TabPFNAPIClient
from .gpu_accelerator import GPUAccelerator
from .federated_learning import FederatedLearningCoordinator, Variant as FLVariant
from .ab_testing import (
    ABTestingFramework,
    Variant,
    VariantType,
    ExperimentStatus
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_1_tabpfn_api():
    """
    Example 1: Real TabPFN API Integration

    Shows how to use TabPFN API with automatic fallback to KNN simulation
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Real TabPFN API Integration")
    print("=" * 60)

    # Initialize client (with fallback enabled)
    client = TabPFNAPIClient(
        api_key=None,  # Set to your TabPFN API key
        enable_fallback=True
    )

    # Check health
    is_healthy = client.health_check()
    print(f"API Health: {'✓ Healthy' if is_healthy else '✗ Unhealthy (using fallback)'}")

    # Create training data
    training_data = []
    for i in range(10):
        exp = Experience(
            experience_type=ExperienceType.PRICING,
            context={"season": "high", "occupancy": 0.7 + i * 0.02},
            action="suggest_price",
            outcome="success" if i > 3 else "failure",
            performance_score=0.5 + i * 0.05,
            metrics={"revenue": 100 + i * 10},
        )
        training_data.append(exp)

    # Make prediction
    query_exp = Experience(
        experience_type=ExperienceType.PRICING,
        context={"season": "high", "occupancy": 0.85},
        action="suggest_price",
        outcome="unknown",
        performance_score=0.0,
        metrics={},
    )

    prediction = client.predict(training_data, query_exp)

    if prediction:
        print(f"\nPrediction: {prediction.predicted_value}")
        print(f"Confidence: {prediction.confidence:.2%}")
        print(f"Strategy: {prediction.strategy.value}")
    else:
        print("\nPrediction failed")

    # Show statistics
    stats = client.get_statistics()
    print(f"\nAPI Statistics:")
    print(f"  Total calls: {stats['api_calls']}")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    print(f"  Fallback rate: {stats['fallback_rate']:.1%}")
    print(f"  Avg latency: {stats['avg_latency_ms']:.1f}ms")


def example_2_gpu_acceleration():
    """
    Example 2: GPU Acceleration with PyTorch

    Shows how to use GPU acceleration for batch processing
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 2: GPU Acceleration (PyTorch/CUDA)")
    print("=" * 60)

    # Initialize GPU accelerator
    accelerator = GPUAccelerator(
        enable_gpu=True,
        batch_size=32,
        learning_rate=0.001
    )

    print(f"Device: {accelerator.device}")
    print(f"GPU Available: {accelerator.is_gpu_available()}")

    # Create batch of experiences
    experiences = []
    for i in range(100):
        exp = Experience(
            experience_type=ExperienceType.MAINTENANCE,
            context={"engine_hours": 1000 + i * 10, "temp": 95 + i * 0.5},
            action="predict_failure",
            outcome="success" if i % 3 == 0 else "failure",
            performance_score=0.6 + (i % 10) * 0.04,
            metrics={"accuracy": 0.7 + i * 0.002},
        )
        experiences.append(exp)

    # Batch compute rewards (GPU-accelerated)
    print(f"\nProcessing {len(experiences)} experiences...")
    rewards = accelerator.batch_compute_rewards(experiences)
    print(f"Computed rewards: {len(rewards)} values")
    print(f"Avg reward: {rewards.mean():.3f}")

    # Initialize and train value network
    print("\nInitializing value network...")
    accelerator.initialize_value_network(input_dim=10, hidden_dim=64)

    print("Training value network...")
    metrics = accelerator.train_value_network(experiences, epochs=10)
    print(f"Training loss: {metrics['loss']:.4f}")

    # Show statistics
    stats = accelerator.get_statistics()
    print(f"\nGPU Statistics:")
    print(f"  Batch operations: {stats['batch_operations']}")
    print(f"  GPU time: {stats['gpu_time_ms']:.1f}ms")
    print(f"  Speedup factor: {stats['speedup_factor']:.2f}x")


def example_3_federated_learning():
    """
    Example 3: Multi-Marina Cross-Learning

    Shows how multiple marinas can share knowledge while preserving privacy
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Multi-Marina Cross-Learning (Federated)")
    print("=" * 60)

    # Initialize coordinator
    coordinator = FederatedLearningCoordinator(
        privacy_epsilon=1.0,
        min_participants=3,
        enable_privacy=True
    )

    print(f"Privacy epsilon: {coordinator.privacy_epsilon}")
    print(f"Min participants: {coordinator.min_participants}")

    # Three marinas opt in
    marinas = [
        ("wim_001", "West Istanbul Marina"),
        ("setur_bodrum", "Setur Bodrum Marina"),
        ("dmarin_turgutreis", "D-Marin Turgutreis")
    ]

    for tenant_id, marina_name in marinas:
        coordinator.tenant_opt_in(tenant_id, marina_name)
        print(f"✓ {marina_name} opted in")

    # Each marina submits local model
    print("\nMarinas submitting local models...")

    for i, (tenant_id, marina_name) in enumerate(marinas):
        # Generate local training data
        local_experiences = []
        for j in range(50):
            exp = Experience(
                experience_type=ExperienceType.PRICING,
                context={"season": "high", "berth_size": 15 + j},
                action="dynamic_pricing",
                outcome="success" if j > 20 else "failure",
                performance_score=0.6 + i * 0.1 + j * 0.005,
                metrics={"revenue": 500 + i * 100 + j * 10},
            )
            local_experiences.append(exp)

        # Local model weights (simulated)
        model_weights = {
            f"weight_{k}": 0.5 + i * 0.1 + k * 0.05
            for k in range(10)
        }

        performance_metrics = {
            "avg_performance": 0.7 + i * 0.05,
            "accuracy": 0.8 + i * 0.03,
        }

        success = coordinator.submit_local_model(
            tenant_id=tenant_id,
            marina_name=marina_name,
            experiences=local_experiences,
            model_weights=model_weights,
            performance_metrics=performance_metrics
        )

        print(f"  {marina_name}: {'✓ Submitted' if success else '✗ Failed'}")

    # Get global model
    global_model = coordinator.get_global_model()

    if global_model:
        print(f"\n✓ Global model aggregated!")
        print(f"  Model ID: {global_model.model_id}")
        print(f"  Version: {global_model.version}")
        print(f"  Participants: {len(global_model.participating_tenants)}")
        print(f"  Total samples: {global_model.total_samples}")
        print(f"  Avg performance: {global_model.avg_performance:.3f}")
        print(f"  Privacy guarantee: ε={global_model.privacy_guarantee:.2f}")
    else:
        print("\n✗ Global model not yet ready")

    # Show statistics
    stats = coordinator.get_statistics()
    print(f"\nFederated Learning Statistics:")
    print(f"  Total aggregations: {stats['total_aggregations']}")
    print(f"  Opt-in tenants: {stats['opt_in_tenants']}")
    print(f"  Privacy budget spent: {stats['privacy_budget_spent']:.2f}")


def example_4_ab_testing():
    """
    Example 4: A/B Testing Framework

    Shows how to run experiments comparing different learning algorithms
    """
    print("\n" + "=" * 60)
    print("EXAMPLE 4: A/B Testing Framework")
    print("=" * 60)

    # Initialize framework
    framework = ABTestingFramework(
        confidence_level=0.95,
        min_sample_size=100
    )

    print(f"Confidence level: {framework.confidence_level}")
    print(f"Min sample size: {framework.min_sample_size}")

    # Create experiment: TabPFN vs SEAL v2
    print("\nCreating experiment: TabPFN vs SEAL v2...")

    variants = [
        Variant(
            variant_id="control_tabpfn",
            name="TabPFN (Control)",
            variant_type=VariantType.CONTROL,
            traffic_allocation=0.5,
            config={"strategy": "tabpfn", "k_neighbors": 5},
            description="TabPFN few-shot learning"
        ),
        Variant(
            variant_id="treatment_seal",
            name="SEAL v2 (Treatment)",
            variant_type=VariantType.TREATMENT,
            traffic_allocation=0.5,
            config={"strategy": "seal", "learning_rate": 0.1},
            description="SEAL v2 RL-based learning"
        )
    ]

    experiment = framework.create_experiment(
        name="TabPFN vs SEAL v2 Performance",
        description="Compare TabPFN and SEAL v2 for dynamic pricing",
        variants=variants,
        target_metric="performance_score",
        created_by="ada_maritime_ai"
    )

    print(f"✓ Experiment created: {experiment.name}")
    print(f"  ID: {experiment.experiment_id}")
    print(f"  Variants: {len(variants)}")

    # Start experiment
    framework.start_experiment(experiment.experiment_id)
    print(f"✓ Experiment started")

    # Simulate user assignments and outcomes
    print(f"\nSimulating {200} user interactions...")

    for user_id in range(200):
        # Assign to variant
        variant_id = framework.assign_variant(experiment.experiment_id, f"user_{user_id}")

        # Simulate outcome based on variant
        if variant_id == "control_tabpfn":
            # TabPFN: 75% avg performance
            performance = 0.75 + (user_id % 10 - 5) * 0.02
        else:  # treatment_seal
            # SEAL v2: 80% avg performance (5% improvement)
            performance = 0.80 + (user_id % 10 - 5) * 0.02

        # Clamp to [0, 1]
        performance = max(0.0, min(1.0, performance))

        # Record outcome
        framework.record_outcome(experiment.experiment_id, variant_id, performance)

    print(f"✓ Recorded {200} outcomes")

    # Analyze results
    print(f"\nAnalyzing experiment...")
    result = framework.analyze_experiment(experiment.experiment_id)

    if result:
        print(f"\n{'=' * 60}")
        print("EXPERIMENT RESULTS")
        print(f"{'=' * 60}")

        for variant_id, metrics in result.variant_metrics.items():
            variant_name = next(v.name for v in variants if v.variant_id == variant_id)
            print(f"\n{variant_name}:")
            print(f"  Samples: {metrics.sample_count}")
            print(f"  Avg Performance: {metrics.avg_performance:.3f}")
            print(f"  Std Dev: {metrics.std_performance:.3f}")
            print(f"  95% CI: [{metrics.confidence_interval_95[0]:.3f}, {metrics.confidence_interval_95[1]:.3f}]")
            print(f"  Conversion Rate: {metrics.conversion_rate:.1%}")

        print(f"\n{'=' * 60}")
        print(f"Winner: {result.winner}")
        print(f"Statistically Significant: {'Yes' if result.statistical_significance else 'No'}")
        print(f"P-value: {result.p_value:.4f}")
        print(f"Effect Size (Cohen's d): {result.effect_size:.2f}")
        print(f"\nRecommendation:")
        print(f"  {result.recommendation}")
        print(f"{'=' * 60}")
    else:
        print("✗ Insufficient data for analysis")

    # Complete experiment
    framework.complete_experiment(experiment.experiment_id)
    print(f"\n✓ Experiment completed")

    # Show statistics
    stats = framework.get_statistics()
    print(f"\nA/B Testing Statistics:")
    print(f"  Total experiments: {stats['total_experiments']}")
    print(f"  Completed: {stats['completed_experiments']}")
    print(f"  Total assignments: {stats['total_assignments']}")


def run_all_examples():
    """Run all Q2-Q3 2026 feature examples"""
    print("\n" + "=" * 60)
    print("ADA MARITIME AI - Q2-Q3 2026 FEATURES DEMO")
    print("=" * 60)
    print("\nDemonstrating 4 new features:")
    print("1. Real TabPFN API Integration")
    print("2. GPU Acceleration (PyTorch/CUDA)")
    print("3. Multi-Marina Cross-Learning (Federated)")
    print("4. A/B Testing Framework")

    try:
        example_1_tabpfn_api()
    except Exception as e:
        logger.error(f"Example 1 failed: {e}")

    try:
        example_2_gpu_acceleration()
    except Exception as e:
        logger.error(f"Example 2 failed: {e}")

    try:
        example_3_federated_learning()
    except Exception as e:
        logger.error(f"Example 3 failed: {e}")

    try:
        example_4_ab_testing()
    except Exception as e:
        logger.error(f"Example 4 failed: {e}")

    print("\n" + "=" * 60)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    run_all_examples()
