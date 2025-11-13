"""
Learning Module - SEAL v2 and TabPFN-2.5 Integration

This module provides advanced machine learning capabilities for Ada Maritime AI:
- SEAL v2: Self-Adapting Language Models with RL-based optimization
- TabPFN-2.5: Few-shot learning for tabular data
- Experience Learning Pipeline: Intelligent routing and adaptive learning
- GPU Acceleration: PyTorch/CUDA acceleration for batch processing
- Federated Learning: Multi-marina cross-learning with privacy preservation
- A/B Testing: Experiment framework for algorithm comparison
"""

from .models import (
    Experience,
    LearningStrategy,
    Prediction,
    SelfEdit,
    Pattern,
    SkillProgress
)
from .tabpfn_adapter import TabPFNAdapter
from .seal_v2_manager import SEALv2Manager
from .experience_pipeline import ExperienceLearningPipeline

# Q2-Q3 2026 Features
from .tabpfn_client import TabPFNAPIClient
from .gpu_accelerator import GPUAccelerator
from .federated_learning import (
    FederatedLearningCoordinator,
    TenantModel,
    GlobalModel
)
from .ab_testing import (
    ABTestingFramework,
    Experiment,
    Variant,
    VariantMetrics,
    ExperimentResult,
    ExperimentStatus,
    VariantType
)

__all__ = [
    # Core models
    'Experience',
    'LearningStrategy',
    'Prediction',
    'SelfEdit',
    'Pattern',
    'SkillProgress',
    # SEAL v2 & TabPFN
    'TabPFNAdapter',
    'SEALv2Manager',
    'ExperienceLearningPipeline',
    # Q2-Q3 2026 Features
    'TabPFNAPIClient',
    'GPUAccelerator',
    'FederatedLearningCoordinator',
    'TenantModel',
    'GlobalModel',
    'ABTestingFramework',
    'Experiment',
    'Variant',
    'VariantMetrics',
    'ExperimentResult',
    'ExperimentStatus',
    'VariantType',
]

__version__ = '2.5.0'
