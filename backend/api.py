"""
Ada Maritime AI - REST API

FastAPI REST API for marina management operations and compliance.

Endpoints:
- /api/v1/verify/insurance - Insurance verification
- /api/v1/verify/permit - Hot work permits
- /api/v1/verify/compliance - Compliance checking
- /api/v1/verify/audit - Compliance audits
- /api/v1/verify/violations - Violation management
- /api/v1/dashboard - Real-time dashboard
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .main import AdaMaritimeAI
from .logger import setup_logger


logger = setup_logger(__name__)


# Initialize FastAPI app
app = FastAPI(
    title="Ada Maritime AI API",
    description="Complete marina management system with operations and compliance",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize Ada Maritime AI
ada_system: Optional[AdaMaritimeAI] = None


def get_ada_system() -> AdaMaritimeAI:
    """Get Ada Maritime AI system instance"""
    global ada_system
    if ada_system is None:
        ada_system = AdaMaritimeAI()
    return ada_system


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class VesselVerificationRequest(BaseModel):
    """Request model for vessel verification"""
    vessel_name: str = Field(..., description="Name of the vessel")
    vessel_registration: str = Field(..., description="Vessel registration number")
    marina_id: str = Field(..., description="Marina ID")
    booking_id: Optional[str] = Field(None, description="Booking ID if applicable")


class HotWorkPermitRequest(BaseModel):
    """Request model for hot work permit"""
    work_description: str = Field(..., description="Description of work to be performed")
    work_location: str = Field(..., description="Location where work will be performed")
    scheduled_start: str = Field(..., description="Start time (ISO format)")
    scheduled_end: str = Field(..., description="End time (ISO format)")
    requested_by: str = Field(..., description="Name of requester")
    requester_email: str = Field(..., description="Email of requester")
    requester_phone: str = Field(..., description="Phone of requester")
    marina_id: str = Field(..., description="Marina ID")
    vessel_name: Optional[str] = None
    vessel_registration: Optional[str] = None
    berth_id: Optional[str] = None


class ComplianceAuditRequest(BaseModel):
    """Request model for compliance audit"""
    marina_id: str = Field(..., description="Marina ID")
    scope: Optional[List[str]] = Field(None, description="Specific articles to check")
    include_recommendations: bool = Field(True, description="Include recommendations")


class ViolationResolutionRequest(BaseModel):
    """Request model for resolving violation"""
    violation_id: str = Field(..., description="Violation ID")
    resolved_by: str = Field(..., description="Who resolved the violation")
    resolution_notes: str = Field(..., description="Notes about resolution")


# ============================================================================
# HEALTH & INFO ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - system information"""
    return {
        "system": "Ada Maritime AI",
        "version": "1.0.0",
        "status": "operational",
        "capabilities": [
            "Insurance Verification (Article E.2.1)",
            "Hot Work Permits (Article E.5.5)",
            "176-Article Compliance System",
            "Violation Detection & Management",
            "Security Incident Tracking",
            "Real-time Monitoring"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/skills")
async def get_available_skills(ada: AdaMaritimeAI = Depends(get_ada_system)):
    """Get all available skills"""
    return ada.orchestrator.get_all_available_skills()


# ============================================================================
# VESSEL VERIFICATION ENDPOINTS
# ============================================================================

@app.post("/api/v1/verify/vessel")
async def verify_vessel(
    request: VesselVerificationRequest,
    ada: AdaMaritimeAI = Depends(get_ada_system)
):
    """
    Verify vessel compliance for marina entry

    Checks:
    - Insurance validity (Article E.2.1)
    - Outstanding violations
    - Security incidents

    Returns authorization decision
    """
    try:
        result = await ada.verify_vessel_entry(
            vessel_name=request.vessel_name,
            vessel_registration=request.vessel_registration,
            marina_id=request.marina_id,
            booking_id=request.booking_id
        )
        return result

    except Exception as e:
        logger.error(f"Vessel verification failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# INSURANCE ENDPOINTS
# ============================================================================

@app.get("/api/v1/verify/insurance/status")
async def get_insurance_status(
    vessel_registration: Optional[str] = None,
    marina_id: Optional[str] = None,
    ada: AdaMaritimeAI = Depends(get_ada_system)
):
    """Get insurance status for vessel or marina"""
    try:
        insurance_skill = ada.orchestrator.verify.skills.get("insurance_verification")
        if not insurance_skill:
            raise HTTPException(status_code=500, detail="Insurance skill not available")

        result = await insurance_skill.execute({
            "operation": "get_status",
            "vessel_registration": vessel_registration,
            "marina_id": marina_id
        })

        return result

    except Exception as e:
        logger.error(f"Insurance status check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/verify/insurance/expiring")
async def get_expiring_insurance(
    marina_id: str,
    days_threshold: int = 30,
    ada: AdaMaritimeAI = Depends(get_ada_system)
):
    """Get insurance policies expiring soon"""
    try:
        insurance_skill = ada.orchestrator.verify.skills.get("insurance_verification")
        if not insurance_skill:
            raise HTTPException(status_code=500, detail="Insurance skill not available")

        result = await insurance_skill.execute({
            "operation": "check_expiry",
            "marina_id": marina_id,
            "days_threshold": days_threshold
        })

        return result

    except Exception as e:
        logger.error(f"Insurance expiry check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HOT WORK PERMIT ENDPOINTS
# ============================================================================

@app.post("/api/v1/verify/permit/request")
async def request_hot_work_permit(
    request: HotWorkPermitRequest,
    ada: AdaMaritimeAI = Depends(get_ada_system)
):
    """Request a hot work permit (Article E.5.5)"""
    try:
        result = await ada.request_hot_work_permit(
            work_description=request.work_description,
            work_location=request.work_location,
            scheduled_start=request.scheduled_start,
            scheduled_end=request.scheduled_end,
            requested_by=request.requested_by,
            requester_email=request.requester_email,
            requester_phone=request.requester_phone,
            marina_id=request.marina_id,
            vessel_name=request.vessel_name,
            vessel_registration=request.vessel_registration,
            berth_id=request.berth_id
        )

        return result

    except Exception as e:
        logger.error(f"Hot work permit request failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/verify/permit/active")
async def get_active_permits(
    marina_id: str,
    ada: AdaMaritimeAI = Depends(get_ada_system)
):
    """Get all active hot work permits"""
    try:
        permit_skill = ada.orchestrator.verify.skills.get("hot_work_monitoring")
        if not permit_skill:
            raise HTTPException(status_code=500, detail="Permit skill not available")

        result = await permit_skill.execute({
            "operation": "check_active",
            "marina_id": marina_id
        })

        return result

    except Exception as e:
        logger.error(f"Active permits check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/verify/permit/{permit_id}/monitor")
async def monitor_permit(
    permit_id: str,
    ada: AdaMaritimeAI = Depends(get_ada_system)
):
    """Monitor hot work permit compliance"""
    try:
        permit_skill = ada.orchestrator.verify.skills.get("hot_work_monitoring")
        if not permit_skill:
            raise HTTPException(status_code=500, detail="Permit skill not available")

        result = await permit_skill.execute({
            "operation": "monitor",
            "permit_id": permit_id
        })

        return result

    except Exception as e:
        logger.error(f"Permit monitoring failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# COMPLIANCE ENDPOINTS
# ============================================================================

@app.post("/api/v1/verify/audit")
async def run_compliance_audit(
    request: ComplianceAuditRequest,
    ada: AdaMaritimeAI = Depends(get_ada_system)
):
    """Run comprehensive compliance audit"""
    try:
        result = await ada.run_compliance_audit(request.marina_id)
        return result

    except Exception as e:
        logger.error(f"Compliance audit failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/verify/compliance/rules")
async def get_compliance_rules(
    category: Optional[str] = None,
    article_number: Optional[str] = None,
    ada: AdaMaritimeAI = Depends(get_ada_system)
):
    """Get compliance rules"""
    try:
        compliance_skill = ada.orchestrator.verify.skills.get("compliance_checking")
        if not compliance_skill:
            raise HTTPException(status_code=500, detail="Compliance skill not available")

        result = await compliance_skill.execute({
            "operation": "get_rules",
            "category": category,
            "article_number": article_number
        })

        return result

    except Exception as e:
        logger.error(f"Get rules failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# VIOLATION ENDPOINTS
# ============================================================================

@app.get("/api/v1/verify/violations")
async def get_violations(
    marina_id: str,
    severity: Optional[str] = None,
    ada: AdaMaritimeAI = Depends(get_ada_system)
):
    """Get active violations"""
    try:
        violations = ada.orchestrator.verify.get_active_violations(
            marina_id=marina_id,
            severity=severity
        )

        return {
            "marina_id": marina_id,
            "count": len(violations),
            "violations": [
                {
                    "id": v.violation_id,
                    "article": v.article_number,
                    "type": v.violation_type,
                    "severity": v.severity,
                    "description": v.description,
                    "detected_at": v.detected_at,
                    "status": v.status,
                    "vessel_name": v.vessel_name
                }
                for v in violations
            ]
        }

    except Exception as e:
        logger.error(f"Get violations failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/verify/violations/{violation_id}/resolve")
async def resolve_violation(
    violation_id: str,
    request: ViolationResolutionRequest,
    ada: AdaMaritimeAI = Depends(get_ada_system)
):
    """Resolve a violation"""
    try:
        success = ada.orchestrator.verify.resolve_violation(
            violation_id=violation_id,
            resolved_by=request.resolved_by,
            resolution_notes=request.resolution_notes
        )

        if not success:
            raise HTTPException(status_code=404, detail="Violation not found")

        return {
            "success": True,
            "violation_id": violation_id,
            "message": "Violation resolved successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resolve violation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DASHBOARD ENDPOINT
# ============================================================================

@app.get("/api/v1/dashboard/{marina_id}")
async def get_dashboard(
    marina_id: str,
    ada: AdaMaritimeAI = Depends(get_ada_system)
):
    """Get real-time dashboard data"""
    try:
        dashboard = ada.get_dashboard(marina_id)
        return dashboard

    except Exception as e:
        logger.error(f"Dashboard fetch failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# APPLICATION STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    global ada_system
    logger.info("Starting Ada Maritime AI API...")
    ada_system = AdaMaritimeAI()
    logger.info("Ada Maritime AI API ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Ada Maritime AI API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
