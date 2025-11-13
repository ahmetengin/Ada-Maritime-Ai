"""
Learning Module - SEAL v2 and TabPFN-2.5 Integration

This module provides advanced machine learning capabilities for Ada Maritime AI:
- SEAL v2: Self-Adapting Language Models with RL-based optimization
- TabPFN-2.5: Few-shot learning for tabular data
- Experience Learning Pipeline: Intelligent routing and adaptive learning
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

__all__ = [
    'Experience',
    'LearningStrategy',
    'Prediction',
    'SelfEdit',
    'Pattern',
    'SkillProgress',
    'TabPFNAdapter',
    'SEALv2Manager',
    'ExperienceLearningPipeline',
]

__version__ = '2.0.0'
