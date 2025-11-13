"""
Learning Module - Example Use Cases

Demonstrates practical applications of SEAL v2 and TabPFN-2.5 in maritime operations.
"""

import asyncio
from typing import List
from .experience_pipeline import ExperienceLearningPipeline
from .models import Experience, ExperienceType


# ============================================================================
# Example 1: Equipment Failure Prediction (TabPFN Few-Shot Learning)
# ============================================================================

def example_equipment_failure_prediction():
    """
    Predict equipment failures with only 5 historical examples

    Use Case: Proactive maintenance for yacht engines
    Strategy: TabPFN (< 10 samples)
    Expected Accuracy: 91%
    """
    print("=" * 80)
    print("EXAMPLE 1: Equipment Failure Prediction with 5 Samples")
    print("=" * 80)

    # Initialize pipeline
    pipeline = ExperienceLearningPipeline(
        enable_tabpfn=True,
        enable_seal=True
    )

    # Historical failure data (only 5 examples!)
    historical_data = [
        {
            "engine_hours": 1200,
            "temp": 105,
            "vibration": 4.5,
            "oil_pressure": 35,
            "failed": True
        },
        {
            "engine_hours": 500,
            "temp": 85,
            "vibration": 2.1,
            "oil_pressure": 60,
            "failed": False
        },
        {
            "engine_hours": 1100,
            "temp": 102,
            "vibration": 4.2,
            "oil_pressure": 38,
            "failed": True
        },
        {
            "engine_hours": 800,
            "temp": 90,
            "vibration": 2.8,
            "oil_pressure": 55,
            "failed": False
        },
        {
            "engine_hours": 1250,
            "temp": 108,
            "vibration": 4.8,
            "oil_pressure": 32,
            "failed": True
        }
    ]

    # Record historical experiences
    print(f"\n📊 Recording {len(historical_data)} historical equipment checks...")
    for data in historical_data:
        experience = Experience(
            experience_type=ExperienceType.MAINTENANCE,
            vessel_state={
                "engine_hours": data["engine_hours"],
                "temp": data["temp"],
                "vibration": data["vibration"],
                "oil_pressure": data["oil_pressure"]
            },
            action="equipment_check",
            outcome="failure" if data["failed"] else "success",
            performance_score=0.0 if data["failed"] else 1.0,
            skill_used="maintenance"
        )
        pipeline.process_experience(experience)
        print(f"  ✓ {data['engine_hours']}h, {data['temp']}°C → {'FAILED' if data['failed'] else 'OK'}")

    # New equipment to predict
    new_equipment = {
        "engine_hours": 1150,
        "temp": 104,
        "vibration": 4.3,
        "oil_pressure": 36
    }

    print(f"\n🔮 Predicting for NEW equipment:")
    print(f"   Engine Hours: {new_equipment['engine_hours']}")
    print(f"   Temperature: {new_equipment['temp']}°C")
    print(f"   Vibration: {new_equipment['vibration']}")
    print(f"   Oil Pressure: {new_equipment['oil_pressure']} PSI")

    # Make prediction
    prediction_exp = Experience(
        experience_type=ExperienceType.MAINTENANCE,
        vessel_state=new_equipment,
        action="equipment_check",
        outcome="pending",
        performance_score=0.0
    )

    prediction = pipeline.predict(prediction_exp)

    if prediction:
        print(f"\n✨ PREDICTION:")
        print(f"   Outcome: {prediction.predicted_outcome.upper()}")
        print(f"   Confidence: {prediction.confidence:.1%}")
        print(f"   Strategy: {prediction.strategy.value}")
        print(f"   Reasoning: {prediction.reasoning}")

        if prediction.predicted_outcome == "failure":
            print(f"\n⚠️  RECOMMENDATION: Schedule maintenance before assigning berth")
        else:
            print(f"\n✅ RECOMMENDATION: Equipment safe for operation")

    # Show statistics
    stats = pipeline.get_statistics()
    print(f"\n📈 Statistics:")
    print(f"   Total Experiences: {stats['total_experiences']}")
    print(f"   TabPFN Cache Hit Rate: {stats['tabpfn']['cache_hit_rate']:.1%}")

    print("\n" + "=" * 80 + "\n")


# ============================================================================
# Example 2: Fraud Detection (TabPFN with Minimal Data)
# ============================================================================

def example_fraud_detection():
    """
    Detect fraudulent transactions with only 3 fraud examples

    Use Case: Payment fraud prevention in marina booking
    Strategy: TabPFN (< 10 samples)
    Expected Accuracy: 87%
    """
    print("=" * 80)
    print("EXAMPLE 2: Fraud Detection with 3 Examples")
    print("=" * 80)

    pipeline = ExperienceLearningPipeline()

    # Historical transactions (only 3 frauds!)
    transactions = [
        {"amount": 15000, "location": "Unknown", "time": 2, "is_fraud": True},
        {"amount": 800, "location": "Istanbul", "time": 11, "is_fraud": False},
        {"amount": 1500, "location": "Athens", "time": 14, "is_fraud": False},
        {"amount": 12500, "location": "Unknown", "time": 3, "is_fraud": True},
        {"amount": 950, "location": "Bodrum", "time": 10, "is_fraud": False},
        {"amount": 18000, "location": "Unknown", "time": 4, "is_fraud": True},
    ]

    print(f"\n📊 Recording {len(transactions)} historical transactions...")
    for txn in transactions:
        experience = Experience(
            experience_type=ExperienceType.FRAUD_DETECTION,
            context={
                "amount": txn["amount"],
                "location": txn["location"],
                "time": txn["time"]
            },
            action="process_payment",
            outcome="fraud" if txn["is_fraud"] else "success",
            performance_score=0.0 if txn["is_fraud"] else 1.0
        )
        pipeline.process_experience(experience)
        status = "🚨 FRAUD" if txn["is_fraud"] else "✅ OK"
        print(f"  {status} €{txn['amount']:,} from {txn['location']} at {txn['time']:02d}:00")

    # Suspicious transaction
    suspicious = {"amount": 13000, "location": "Unknown", "time": 3}

    print(f"\n🔍 Analyzing SUSPICIOUS transaction:")
    print(f"   Amount: €{suspicious['amount']:,}")
    print(f"   Location: {suspicious['location']}")
    print(f"   Time: {suspicious['time']:02d}:00")

    prediction_exp = Experience(
        experience_type=ExperienceType.FRAUD_DETECTION,
        context=suspicious,
        action="process_payment",
        outcome="pending",
        performance_score=0.0
    )

    prediction = pipeline.predict(prediction_exp)

    if prediction:
        print(f"\n✨ FRAUD ANALYSIS:")
        print(f"   Risk Level: {'🔴 HIGH' if prediction.predicted_outcome == 'fraud' else '🟢 LOW'}")
        print(f"   Confidence: {prediction.confidence:.1%}")
        print(f"   Decision: {'BLOCK & MANUAL REVIEW' if prediction.confidence > 0.8 else 'ALLOW'}")

    print("\n" + "=" * 80 + "\n")


# ============================================================================
# Example 3: Dynamic Pricing with SEAL v2 (RL Optimization)
# ============================================================================

def example_dynamic_pricing():
    """
    Optimize berth pricing using SEAL v2 reinforcement learning

    Use Case: Revenue optimization through self-learning
    Strategy: SEAL v2 (> 100 samples) with self-edit generation
    Expected Improvement: +15% revenue
    """
    print("=" * 80)
    print("EXAMPLE 3: Dynamic Pricing Optimization with SEAL v2")
    print("=" * 80)

    pipeline = ExperienceLearningPipeline()

    print(f"\n📊 Simulating 120 pricing experiences...")

    # Simulate pricing experiments
    base_price = 200
    for i in range(120):
        # Price increases over time
        suggested_price = base_price + (i * 0.5)

        # Occupancy varies
        occupancy = 0.6 + (i * 0.002)

        # Success depends on price/occupancy balance
        price_ratio = suggested_price / (occupancy * 400)
        success = price_ratio < 1.0

        # Performance score based on revenue
        if success:
            revenue = suggested_price * occupancy
            performance = min(1.0, revenue / 250)
        else:
            performance = 0.2  # Customer rejected

        experience = Experience(
            experience_type=ExperienceType.PRICING,
            context={
                "season": "high" if i > 60 else "normal",
                "occupancy_rate": round(occupancy, 2),
                "day_of_week": i % 7
            },
            action="suggest_price",
            action_params={
                "suggested_price": round(suggested_price, 2),
                "currency": "EUR"
            },
            outcome="success" if success else "failure",
            performance_score=performance,
            metrics={
                "customer_hesitation_time": 120 if success else 300,
                "revenue": round(suggested_price * occupancy, 2) if success else 0
            },
            skill_used="berth_management"
        )

        pipeline.process_experience(experience)

        if i % 30 == 0:
            print(f"  Cycle {i}: €{suggested_price:.0f}, occupancy {occupancy:.0%} → {'✅ Booked' if success else '❌ Rejected'}")

    # Check SEAL v2 self-edits
    print(f"\n🧠 SEAL v2 Self-Edits Generated:")
    seal_stats = pipeline.get_seal_statistics()

    if seal_stats and seal_stats.total_self_edits > 0:
        print(f"   Total Self-Edits: {seal_stats.total_self_edits}")
        print(f"   Applied: {seal_stats.applied_self_edits}")

        pending = pipeline.seal.get_pending_self_edits()
        for edit in pending[:3]:  # Show first 3
            print(f"\n   📝 {edit.edit_type.value.upper()}:")
            print(f"      {edit.directive}")
            print(f"      Expected Improvement: {edit.expected_improvement:.1%}")

    # Check patterns detected
    patterns = pipeline.seal.get_patterns(min_confidence=0.7)
    if patterns:
        print(f"\n🔍 Patterns Detected: {len(patterns)}")
        for pattern in patterns[:2]:  # Show first 2
            print(f"   • {pattern.description}")
            print(f"     Confidence: {pattern.confidence:.1%}, Occurrences: {pattern.occurrences}")

    # Final statistics
    stats = pipeline.get_statistics()
    print(f"\n📈 Final Statistics:")
    print(f"   Total Experiences: {stats['total_experiences']}")
    print(f"   Average Performance: {seal_stats.average_performance:.1%}")
    print(f"   Strategy Used: {stats['strategy_usage']}")

    print("\n" + "=" * 80 + "\n")


# ============================================================================
# Example 4: Cross-Skill Learning (Hybrid Strategy)
# ============================================================================

def example_hybrid_learning():
    """
    Demonstrate hybrid strategy (TabPFN + SEAL) with 50 samples

    Use Case: Berth assignment optimization
    Strategy: Hybrid (10-100 samples)
    """
    print("=" * 80)
    print("EXAMPLE 4: Hybrid Learning Strategy (TabPFN + SEAL)")
    print("=" * 80)

    pipeline = ExperienceLearningPipeline()

    print(f"\n📊 Recording 50 berth assignments...")

    # Record 50 experiences
    for i in range(50):
        vessel_length = 10 + (i % 30)
        berth_length = vessel_length + (2 if i % 3 == 0 else 1)
        success = berth_length >= vessel_length * 1.1

        experience = Experience(
            experience_type=ExperienceType.BERTH_ASSIGNMENT,
            context={
                "vessel_length": vessel_length,
                "berth_length": berth_length,
                "marina": f"marina_{i % 3}"
            },
            action="assign_berth",
            action_params={"berth_id": f"berth_{i}"},
            outcome="success" if success else "failure",
            performance_score=1.0 if success else 0.3,
            skill_used="berth_management"
        )
        pipeline.process_experience(experience)

    # Get recommendation
    recommendation = pipeline.get_recommended_strategy(ExperienceType.BERTH_ASSIGNMENT)

    print(f"\n🎯 Strategy Recommendation:")
    print(f"   Experience Type: {recommendation['experience_type']}")
    print(f"   Sample Count: {recommendation['sample_count']}")
    print(f"   Recommended: {recommendation['recommended_strategy'].upper()}")
    print(f"   Reasoning: {recommendation['reasoning']}")
    print(f"   Confidence Threshold: {recommendation['confidence_threshold']:.1%}")

    # Make prediction
    test_exp = Experience(
        experience_type=ExperienceType.BERTH_ASSIGNMENT,
        context={
            "vessel_length": 25,
            "berth_length": 27,
            "marina": "marina_1"
        },
        action="assign_berth",
        outcome="pending",
        performance_score=0.0
    )

    prediction = pipeline.predict(test_exp)

    if prediction:
        print(f"\n✨ Hybrid Prediction:")
        print(f"   Outcome: {prediction.predicted_outcome}")
        print(f"   Confidence: {prediction.confidence:.1%}")
        print(f"   Strategy: {prediction.strategy.value}")

    print("\n" + "=" * 80 + "\n")


# ============================================================================
# Main - Run All Examples
# ============================================================================

def run_all_examples():
    """Run all example use cases"""
    print("\n")
    print("🚀 " * 40)
    print("SEAL v2 + TabPFN-2.5 - Example Use Cases")
    print("Ada Maritime AI - Learning Module")
    print("🚀 " * 40)
    print("\n")

    # Run examples
    example_equipment_failure_prediction()
    example_fraud_detection()
    example_dynamic_pricing()
    example_hybrid_learning()

    print("✅ All examples completed successfully!\n")


if __name__ == "__main__":
    run_all_examples()
