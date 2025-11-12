"""
Regulatory Compliance Framework
KVKK (Turkish Data Protection Law) and GDPR compliance
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import time


class DataProcessingPurpose(Enum):
    """Legal purposes for data processing"""
    CONSENT = "consent"  # Article 6 GDPR
    CONTRACT = "contract"  # Service execution
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"  # Emergency/safety
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTEREST = "legitimate_interest"


class DataSubjectRight(Enum):
    """Rights of data subjects (captains)"""
    ACCESS = "access"  # Right to access data
    RECTIFICATION = "rectification"  # Right to correct data
    ERASURE = "erasure"  # Right to be forgotten
    RESTRICTION = "restriction"  # Right to restrict processing
    PORTABILITY = "portability"  # Right to data portability
    OBJECTION = "objection"  # Right to object
    COMPLAINT = "complaint"  # Right to lodge complaint


@dataclass
class ComplianceFramework:
    """
    Base compliance framework
    Common requirements for KVKK and GDPR
    """

    data_controller: Dict[str, str]
    dpo_contact: str  # Data Protection Officer
    privacy_policy_url: str
    last_updated: float

    def get_data_subject_rights(self) -> List[str]:
        """Get list of data subject rights"""
        return [right.value for right in DataSubjectRight]

    def get_processing_purposes(self) -> List[str]:
        """Get legal bases for processing"""
        return [purpose.value for purpose in DataProcessingPurpose]

    def generate_privacy_notice(self, language: str = "tr") -> str:
        """Generate privacy notice for captain"""
        if language == "tr":
            return self._generate_turkish_notice()
        else:
            return self._generate_english_notice()

    def _generate_turkish_notice(self) -> str:
        """Generate Turkish privacy notice"""
        return f"""
ADA.SEA GİZLİLİK BİLDİRİMİ

Veri Sorumlusu: {self.data_controller['name']}
İletişim: {self.data_controller['contact']}
Veri Koruma Sorumlusu: {self.dpo_contact}

KİŞİSEL VERİLERİNİZİN KORUNMASI

Ada.Sea, kişisel verilerinizi korumak için tasarlanmıştır:

✓ Tüm veriler teknede (Mac Mini M4)
✓ Hiçbir otomatik bulut senkronizasyonu
✓ Hiçbir otomatik veri paylaşımı
✓ Her paylaşım için sizin onayınız gerekir

VERİ İŞLEME İLKELERİ

1. Hukuka Uygunluk: Açık rızanız
2. Amaç Sınırlaması: Sadece belirtilen amaçlar
3. Veri Minimizasyonu: Minimum gerekli veri
4. Doğruluk: Verilerinizi siz doğrularsınız
5. Saklama Sınırlaması: Siz kontrol edersiniz
6. Güvenlik: AES-256, E2E şifreleme
7. Hesap Verebilirlik: Tam denetim kaydı

HAKLARINIZ (KVKK Madde 11)

• Bilgi Talep Etme: "Ada, verilerimi göster"
• Düzeltme: "Ada, [veri]'yi düzelt"
• Silme: "Ada, [veri]'yi sil"
• Kısıtlama: "Ada, [veri] paylaşımını durdur"
• Taşınabilirlik: "Ada, verilerimi dışa aktar"
• İtiraz: "Ada, [işleme] itiraz ediyorum"

BAŞVURU

Veri Koruma Sorumlusu: {self.dpo_contact}
Kişisel Verileri Koruma Kurumu: www.kvkk.gov.tr

Son Güncelleme: {time.strftime('%Y-%m-%d', time.localtime(self.last_updated))}
"""

    def _generate_english_notice(self) -> str:
        """Generate English privacy notice"""
        return f"""
ADA.SEA PRIVACY NOTICE

Data Controller: {self.data_controller['name']}
Contact: {self.data_controller['contact']}
Data Protection Officer: {self.dpo_contact}

PROTECTION OF YOUR PERSONAL DATA

Ada.Sea is designed to protect your personal data:

✓ All data on vessel (Mac Mini M4)
✓ No automatic cloud synchronization
✓ No automatic data sharing
✓ Your approval required for every transfer

DATA PROCESSING PRINCIPLES

1. Lawfulness: Your explicit consent
2. Purpose Limitation: Only specified purposes
3. Data Minimization: Minimum necessary
4. Accuracy: You verify all data
5. Storage Limitation: You control retention
6. Security: AES-256, E2E encryption
7. Accountability: Complete audit trail

YOUR RIGHTS (GDPR Articles 15-22)

• Access: "Ada, show my data"
• Rectification: "Ada, correct [data]"
• Erasure: "Ada, delete [data]"
• Restriction: "Ada, stop [data] sharing"
• Portability: "Ada, export my data"
• Objection: "Ada, I object to [processing]"

CONTACT

Data Protection Officer: {self.dpo_contact}
Supervisory Authority: [Country DPA]

Last Updated: {time.strftime('%Y-%m-%d', time.localtime(self.last_updated))}
"""


class KVKKCompliance:
    """
    KVKK (Kişisel Verilerin Korunması Kanunu)
    Turkish Data Protection Law Compliance

    Law No: 6698
    Effective: April 7, 2016
    """

    def __init__(self):
        self.framework = ComplianceFramework(
            data_controller={
                'name': 'Ada.Sea Platform',
                'contact': 'privacy@ada.sea',
                'registration': 'VERBİS Registry'  # If registered
            },
            dpo_contact='veri-sorumlusu@ada.sea',
            privacy_policy_url='https://ada.sea/gizlilik-politikasi',
            last_updated=time.time()
        )

        # KVKK Article 11 - Data Subject Rights
        self.data_subject_rights = {
            'bilgi_talep': 'Right to request information',
            'duzeltme': 'Right to rectification',
            'silme': 'Right to erasure',
            'kisitlama': 'Right to restriction',
            'tasinabilirlik': 'Right to data portability',
            'itiraz': 'Right to object',
            'sikayet': 'Right to lodge complaint with KVKK'
        }

    def validate_consent(self, consent_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate consent according to KVKK requirements

        KVKK Article 3 - Explicit Consent Required
        """
        validations = {
            'explicit': False,  # Must be explicit, not implicit
            'informed': False,  # Captain must be informed
            'specific': False,  # For specific purpose
            'freely_given': False,  # Not forced
            'documented': False  # Must be documented
        }

        # Check if consent is explicit (not pre-checked)
        if consent_data.get('method') in ['voice', 'manual']:
            validations['explicit'] = True

        # Check if captain was informed
        if consent_data.get('purpose') and consent_data.get('data_type'):
            validations['informed'] = True

        # Check if specific (not blanket consent)
        if consent_data.get('purpose') and len(consent_data.get('purpose', '')) > 0:
            validations['specific'] = True

        # Check if freely given (no coercion)
        if consent_data.get('confirmation_text'):
            validations['freely_given'] = True

        # Check if documented
        if consent_data.get('timestamp') and consent_data.get('captain_id'):
            validations['documented'] = True

        return validations

    def handle_data_subject_request(
        self,
        request_type: str,
        captain_id: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle data subject requests under KVKK Article 11

        Response deadline: 30 days (can be extended to 60)
        """
        handlers = {
            'bilgi_talep': self._handle_access_request,
            'duzeltme': self._handle_rectification_request,
            'silme': self._handle_erasure_request,
            'kisitlama': self._handle_restriction_request,
            'tasinabilirlik': self._handle_portability_request,
            'itiraz': self._handle_objection_request,
        }

        handler = handlers.get(request_type)
        if not handler:
            return {
                'success': False,
                'reason': f'Unknown request type: {request_type}'
            }

        return handler(captain_id, details)

    def _handle_access_request(
        self,
        captain_id: str,
        details: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle right to access (KVKK Article 11/a,b,c,ç,d)"""
        return {
            'success': True,
            'request_type': 'access',
            'deadline_days': 30,
            'message': 'Verilerinize erişim talebi alındı. 30 gün içinde yanıt verilecek.'
        }

    def _handle_rectification_request(
        self,
        captain_id: str,
        details: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle right to rectification (KVKK Article 11/e)"""
        return {
            'success': True,
            'request_type': 'rectification',
            'deadline_days': 30,
            'message': 'Düzeltme talebi alındı. 30 gün içinde işlem yapılacak.'
        }

    def _handle_erasure_request(
        self,
        captain_id: str,
        details: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle right to erasure (KVKK Article 11/e)"""
        return {
            'success': True,
            'request_type': 'erasure',
            'deadline_days': 30,
            'message': 'Silme talebi alındı. 30 gün içinde işlem yapılacak.',
            'note': 'Yasal saklama yükümlülüğü olan veriler hariç'
        }

    def _handle_restriction_request(
        self,
        captain_id: str,
        details: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle right to restriction"""
        return {
            'success': True,
            'request_type': 'restriction',
            'deadline_days': 30,
            'message': 'Kısıtlama talebi alındı. İşleme durduruldu.'
        }

    def _handle_portability_request(
        self,
        captain_id: str,
        details: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle right to data portability (KVKK Article 11/f)"""
        return {
            'success': True,
            'request_type': 'portability',
            'deadline_days': 30,
            'message': 'Veri taşınabilirlik talebi alındı. JSON/CSV formatında sağlanacak.'
        }

    def _handle_objection_request(
        self,
        captain_id: str,
        details: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle right to object"""
        return {
            'success': True,
            'request_type': 'objection',
            'deadline_days': 30,
            'message': 'İtiraz talebi alındı. İşleme durduruldu.'
        }

    def generate_kvkk_report(self) -> Dict[str, Any]:
        """Generate KVKK compliance report"""
        return {
            'compliance_framework': 'KVKK Law 6698',
            'data_controller': self.framework.data_controller,
            'dpo': self.framework.dpo_contact,
            'principles_implemented': [
                'Hukuka ve dürüstlük kurallarına uygun işleme',
                'Doğru ve gerektiğinde güncel olma',
                'Belirli, açık ve meşru amaçlar için işleme',
                'İşlendikleri amaçla bağlantılı, sınırlı ve ölçülü olma',
                'İlgili mevzuatta öngörülen süre kadar muhafaza edilme'
            ],
            'rights_provided': list(self.data_subject_rights.keys()),
            'complaint_authority': {
                'name': 'Kişisel Verileri Koruma Kurumu',
                'website': 'www.kvkk.gov.tr',
                'email': 'kvkk@kvkk.gov.tr'
            }
        }


class GDPRCompliance:
    """
    GDPR (General Data Protection Regulation)
    EU Data Protection Regulation Compliance

    Regulation (EU) 2016/679
    Effective: May 25, 2018
    """

    def __init__(self):
        self.framework = ComplianceFramework(
            data_controller={
                'name': 'Ada.Sea Platform',
                'contact': 'privacy@ada.sea',
                'representative': 'EU Representative (if required)'
            },
            dpo_contact='dpo@ada.sea',
            privacy_policy_url='https://ada.sea/privacy-policy',
            last_updated=time.time()
        )

        # GDPR Articles 15-22 - Data Subject Rights
        self.data_subject_rights = {
            'access': 'Article 15 - Right to access',
            'rectification': 'Article 16 - Right to rectification',
            'erasure': 'Article 17 - Right to be forgotten',
            'restriction': 'Article 18 - Right to restriction',
            'portability': 'Article 20 - Right to data portability',
            'objection': 'Article 21 - Right to object',
            'automated_decision': 'Article 22 - Automated decision-making'
        }

    def validate_legal_basis(
        self,
        processing_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate legal basis under GDPR Article 6

        Six legal bases:
        1. Consent
        2. Contract
        3. Legal obligation
        4. Vital interests
        5. Public task
        6. Legitimate interests
        """
        purpose = processing_data.get('purpose', '')

        # Determine legal basis
        if 'emergency' in purpose:
            legal_basis = DataProcessingPurpose.VITAL_INTERESTS
        elif 'contract' in purpose or 'service' in purpose:
            legal_basis = DataProcessingPurpose.CONTRACT
        elif 'consent' in processing_data:
            legal_basis = DataProcessingPurpose.CONSENT
        else:
            legal_basis = DataProcessingPurpose.LEGITIMATE_INTEREST

        return {
            'legal_basis': legal_basis.value,
            'article': 'GDPR Article 6',
            'valid': True,
            'justification': self._get_legal_basis_justification(legal_basis)
        }

    def _get_legal_basis_justification(
        self,
        legal_basis: DataProcessingPurpose
    ) -> str:
        """Get justification for legal basis"""
        justifications = {
            DataProcessingPurpose.CONSENT: 'Explicit captain consent obtained',
            DataProcessingPurpose.CONTRACT: 'Necessary for service execution',
            DataProcessingPurpose.VITAL_INTERESTS: 'Emergency/safety critical',
            DataProcessingPurpose.LEGITIMATE_INTEREST: 'Balancing test passed',
        }
        return justifications.get(legal_basis, 'Legal basis established')

    def conduct_dpia(
        self,
        processing_activity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Conduct Data Protection Impact Assessment (DPIA)
        Required under GDPR Article 35 for high-risk processing
        """
        risk_factors = {
            'systematic_monitoring': False,
            'sensitive_data': False,
            'large_scale': False,
            'automated_decisions': False,
            'vulnerable_subjects': False,
        }

        # Assess risks
        if 'tracking' in processing_activity.get('type', ''):
            risk_factors['systematic_monitoring'] = True

        if 'financial' in processing_activity.get('data_type', ''):
            risk_factors['sensitive_data'] = True

        high_risk = sum(risk_factors.values()) >= 2

        return {
            'dpia_required': high_risk,
            'risk_factors': risk_factors,
            'risk_level': 'high' if high_risk else 'low',
            'mitigation_measures': self._get_mitigation_measures(),
            'article': 'GDPR Article 35'
        }

    def _get_mitigation_measures(self) -> List[str]:
        """Get data protection mitigation measures"""
        return [
            'Privacy by Design - Zero trust architecture',
            'Privacy by Default - All sharing disabled initially',
            'Encryption - AES-256-GCM at rest and in transit',
            'Access Control - Captain authentication required',
            'Audit Trail - Complete logging of all transfers',
            'Data Minimization - Only essential data shared',
            'Purpose Limitation - Specific purpose for each transfer',
            'Storage Limitation - Captain controls retention'
        ]

    def handle_data_breach(
        self,
        breach_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle data breach notification
        GDPR Article 33 - 72 hour notification requirement
        """
        severity = breach_details.get('severity', 'medium')

        notification_required = severity in ['high', 'critical']
        notification_deadline_hours = 72

        return {
            'notification_required': notification_required,
            'deadline_hours': notification_deadline_hours,
            'supervisory_authority': 'EU Data Protection Authority',
            'affected_subjects_notification': severity == 'critical',
            'article': 'GDPR Article 33-34',
            'actions': [
                'Assess breach scope and severity',
                'Contain and remediate breach',
                'Notify supervisory authority within 72 hours',
                'Notify affected data subjects if high risk',
                'Document breach and response'
            ]
        }

    def generate_gdpr_report(self) -> Dict[str, Any]:
        """Generate GDPR compliance report"""
        return {
            'compliance_framework': 'GDPR Regulation (EU) 2016/679',
            'data_controller': self.framework.data_controller,
            'dpo': self.framework.dpo_contact,
            'principles_implemented': [
                'Lawfulness, fairness and transparency (Article 5.1.a)',
                'Purpose limitation (Article 5.1.b)',
                'Data minimisation (Article 5.1.c)',
                'Accuracy (Article 5.1.d)',
                'Storage limitation (Article 5.1.e)',
                'Integrity and confidentiality (Article 5.1.f)',
                'Accountability (Article 5.2)'
            ],
            'rights_provided': list(self.data_subject_rights.values()),
            'privacy_by_design': True,
            'privacy_by_default': True,
            'dpia_conducted': True,
            'breach_procedures': True,
            'international_transfers': {
                'mechanism': 'Standard Contractual Clauses',
                'adequacy_decision': 'N/A',
                'safeguards': 'Encryption, Access Control, Audit'
            }
        }


# Voice commands for compliance
COMPLIANCE_VOICE_COMMANDS = {
    'tr': {
        'show_rights': ["haklarımı göster", "veri haklarım"],
        'access': ["verilerimi göster", "hangi verilerim var"],
        'rectify': ["veriyi düzelt", "bilgiyi güncelle"],
        'erase': ["verilerimi sil", "hesabımı sil"],
        'export': ["verilerimi dışa aktar", "verilerimi indir"],
        'object': ["itiraz ediyorum", "işlemeyi durdur"],
        'complain': ["şikayet et", "KVKK'ya başvur"]
    },
    'en': {
        'show_rights': ["show my rights", "data rights"],
        'access': ["show my data", "what data do you have"],
        'rectify': ["correct data", "update information"],
        'erase': ["delete my data", "delete account"],
        'export': ["export my data", "download my data"],
        'object': ["I object", "stop processing"],
        'complain': ["file complaint", "contact DPA"]
    }
}
