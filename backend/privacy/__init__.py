"""
Ada.Sea Privacy-First Architecture
Zero-Trust, Captain-Controlled Data Management

Core Privacy Principles:
1. Zero Trust by Default - No automatic data sharing
2. Explicit Consent - Captain approval required for ALL data transfers
3. Minimal Data - Only essential information shared
4. Complete Audit Trail - Full transparency
5. Captain Control - Delete, rectify, stop rights
6. Edge Computing - Data stays on vessel
7. Zero-Knowledge Cloud - Optional, encrypted, unreadable
8. Regulation Ready - KVKK and GDPR compliant

"Kaptan ne derse o olur. Nokta."
"""

from .privacy_core import AdaSeaPrivacyCore
from .data_policy import DataPolicy, DataClassification, PermissionLevel
from .audit_log import AuditLog, AuditEntry
from .consent_manager import ConsentManager, ConsentRequest, ConsentResponse
from .compliance import KVKKCompliance, GDPRCompliance, ComplianceFramework
from .marina_integration import AdaMarinaIntegration

__all__ = [
    'AdaSeaPrivacyCore',
    'DataPolicy',
    'DataClassification',
    'PermissionLevel',
    'AuditLog',
    'AuditEntry',
    'ConsentManager',
    'ConsentRequest',
    'ConsentResponse',
    'KVKKCompliance',
    'GDPRCompliance',
    'ComplianceFramework',
    'AdaMarinaIntegration',
]

__version__ = '1.0.0'
__author__ = 'Ada.Sea Privacy Team'
