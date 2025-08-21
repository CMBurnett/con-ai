"""
Email Agent API Endpoints

Provides REST API endpoints for email agent configuration, monitoring,
and email data extraction.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr
from typing import Dict, List, Any, Optional
import logging

from orchestra.orchestra_manager import AgentType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email", tags=["email"])


class EmailAccountConfig(BaseModel):
    """Email account configuration model."""
    account_id: str
    email_address: EmailStr
    provider: str = "gmail"  # gmail, outlook, imap
    imap_server: Optional[str] = None
    imap_port: Optional[int] = None
    use_oauth2: bool = True
    monitored_folders: List[str] = ["INBOX"]
    processing_frequency: str = "realtime"  # realtime, hourly, daily


class EmailAgentConfig(BaseModel):
    """Email agent configuration model."""
    agent_id: str
    accounts: List[EmailAccountConfig]
    data_extraction_settings: Dict[str, Any] = {
        "extract_project_data": True,
        "extract_rfi_data": True,
        "extract_budget_data": True,
        "extract_schedule_data": True,
        "process_attachments": True,
        "confidence_threshold": 0.7,
    }
    notification_settings: Dict[str, Any] = {
        "notify_on_rfi": True,
        "notify_on_budget_changes": True,
        "notify_on_schedule_updates": True,
        "email_notifications": True,
        "slack_webhook": None,
    }


class EmailSearchRequest(BaseModel):
    """Email search request model."""
    query: str
    date_range: Optional[Dict[str, str]] = None
    email_types: Optional[List[str]] = None
    project_ids: Optional[List[str]] = None
    limit: int = 50


def get_orchestra_manager(request: Request):
    """Dependency to get Orchestra manager from app state."""
    if not hasattr(request.app.state, "orchestra_manager"):
        raise HTTPException(status_code=500, detail="Orchestra manager not initialized")
    return request.app.state.orchestra_manager


@router.post("/agents/{agent_id}/configure")
async def configure_email_agent(
    agent_id: str,
    config: EmailAgentConfig,
    orchestra_manager=Depends(get_orchestra_manager)
):
    """Configure an email agent with account and processing settings."""
    try:
        # Validate agent exists
        agent_status = await orchestra_manager.get_agent_status(agent_id)
        if not agent_status:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        # Store configuration in agent
        # In a real implementation, this would be saved to the database
        configuration_data = {
            "accounts": [account.dict() for account in config.accounts],
            "data_extraction_settings": config.data_extraction_settings,
            "notification_settings": config.notification_settings,
        }
        
        return {
            "agent_id": agent_id,
            "status": "configured",
            "message": "Email agent configuration updated successfully",
            "accounts_configured": len(config.accounts),
        }
        
    except Exception as e:
        logger.error(f"Email agent configuration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration failed: {str(e)}")


@router.post("/agents/{agent_id}/start-monitoring")
async def start_email_monitoring(
    agent_id: str,
    orchestra_manager=Depends(get_orchestra_manager)
):
    """Start email monitoring for an email agent."""
    try:
        result = await orchestra_manager.start_agent(
            agent_id=agent_id,
            agent_type=AgentType.EMAIL,
            task_type="monitor_emails",
            parameters={"monitoring_mode": "realtime"}
        )
        
        return {
            "agent_id": agent_id,
            "status": "monitoring_started",
            "message": result,
        }
        
    except Exception as e:
        logger.error(f"Failed to start email monitoring for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")


@router.post("/agents/{agent_id}/stop-monitoring")
async def stop_email_monitoring(
    agent_id: str,
    orchestra_manager=Depends(get_orchestra_manager)
):
    """Stop email monitoring for an email agent."""
    try:
        result = await orchestra_manager.stop_agent(agent_id)
        
        return {
            "agent_id": agent_id,
            "status": "monitoring_stopped",
            "message": result,
        }
        
    except Exception as e:
        logger.error(f"Failed to stop email monitoring for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")


@router.post("/agents/{agent_id}/process-emails")
async def trigger_email_processing(
    agent_id: str,
    date_range: Optional[Dict[str, str]] = None,
    folders: Optional[List[str]] = None,
    orchestra_manager=Depends(get_orchestra_manager)
):
    """Trigger manual email processing for a specific date range."""
    try:
        parameters = {
            "processing_mode": "batch",
            "date_range": date_range,
            "folders": folders or ["INBOX"],
        }
        
        result = await orchestra_manager.start_agent(
            agent_id=agent_id,
            agent_type=AgentType.EMAIL,
            task_type="process_emails",
            parameters=parameters
        )
        
        return {
            "agent_id": agent_id,
            "status": "processing_started",
            "message": result,
            "parameters": parameters,
        }
        
    except Exception as e:
        logger.error(f"Failed to trigger email processing for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger processing: {str(e)}")


@router.get("/agents/{agent_id}/emails")
async def get_extracted_emails(
    agent_id: str,
    page: int = 1,
    page_size: int = 20,
    email_type: Optional[str] = None,
    project_id: Optional[str] = None,
    orchestra_manager=Depends(get_orchestra_manager)
):
    """Get extracted email data from an email agent."""
    try:
        # In a real implementation, this would query the knowledge graph
        # or database for extracted email data
        sample_emails = [
            {
                "id": "email_001",
                "sender": "project.manager@construction.com",
                "subject": "RFI Response - Foundation Requirements",
                "timestamp": "2024-01-15T10:30:00Z",
                "email_type": "rfi_response",
                "project_id": "proj_123",
                "confidence_score": 0.95,
                "extracted_data": {
                    "rfi_id": "RFI-001",
                    "response_text": "Foundation depth increased to 8 feet per geological survey",
                    "impact": "Schedule delay of 2 weeks",
                },
            },
            {
                "id": "email_002", 
                "sender": "supplier@materials.com",
                "subject": "Material Delivery Update - Steel Beams",
                "timestamp": "2024-01-15T14:20:00Z",
                "email_type": "material_delivery",
                "project_id": "proj_123",
                "confidence_score": 0.88,
                "extracted_data": {
                    "delivery_date": "2024-01-18",
                    "materials": ["Steel Beams - Grade A", "Concrete Blocks"],
                    "quantity": "50 units",
                },
            },
        ]
        
        # Apply filters
        filtered_emails = sample_emails
        if email_type:
            filtered_emails = [e for e in filtered_emails if e["email_type"] == email_type]
        if project_id:
            filtered_emails = [e for e in filtered_emails if e["project_id"] == project_id]
        
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_emails = filtered_emails[start:end]
        
        return {
            "agent_id": agent_id,
            "emails": paginated_emails,
            "total": len(filtered_emails),
            "page": page,
            "page_size": page_size,
            "total_pages": (len(filtered_emails) + page_size - 1) // page_size,
        }
        
    except Exception as e:
        logger.error(f"Failed to get extracted emails for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get emails: {str(e)}")


@router.post("/agents/{agent_id}/search")
async def search_emails(
    agent_id: str,
    search_request: EmailSearchRequest,
    orchestra_manager=Depends(get_orchestra_manager)
):
    """Search through extracted email data."""
    try:
        # In a real implementation, this would perform a full-text search
        # through the knowledge graph or elasticsearch
        search_results = [
            {
                "id": "email_001",
                "sender": "project.manager@construction.com",
                "subject": "RFI Response - Foundation Requirements",
                "relevance_score": 0.95,
                "match_type": "subject_content",
                "project_id": "proj_123",
                "email_type": "rfi_response",
            }
        ]
        
        return {
            "agent_id": agent_id,
            "query": search_request.query,
            "results": search_results,
            "total_results": len(search_results),
        }
        
    except Exception as e:
        logger.error(f"Email search failed for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/agents/{agent_id}/statistics")
async def get_email_statistics(
    agent_id: str,
    date_range: Optional[Dict[str, str]] = None,
    orchestra_manager=Depends(get_orchestra_manager)
):
    """Get email processing statistics for an agent."""
    try:
        # In a real implementation, this would query actual statistics
        statistics = {
            "total_emails_processed": 1250,
            "emails_this_week": 85,
            "email_types": {
                "rfi_submission": 45,
                "rfi_response": 38,
                "project_update": 125,
                "budget_change": 12,
                "schedule_update": 28,
                "material_delivery": 67,
                "general_communication": 935,
            },
            "average_confidence_score": 0.87,
            "processing_accuracy": 0.92,
            "attachments_processed": 234,
            "last_processing_time": "2024-01-15T16:45:00Z",
        }
        
        return {
            "agent_id": agent_id,
            "statistics": statistics,
            "date_range": date_range,
        }
        
    except Exception as e:
        logger.error(f"Failed to get email statistics for {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.get("/oauth2/gmail/authorize")
async def get_gmail_oauth_url(
    agent_id: str,
    redirect_uri: str = "http://localhost:3000/auth/gmail/callback"
):
    """Get Gmail OAuth2 authorization URL."""
    try:
        # In a real implementation, this would generate the actual OAuth2 URL
        auth_url = f"https://accounts.google.com/oauth2/auth?client_id=demo&redirect_uri={redirect_uri}&scope=https://mail.google.com/&response_type=code&state={agent_id}"
        
        return {
            "agent_id": agent_id,
            "auth_url": auth_url,
            "expires_in": 600,  # 10 minutes
        }
        
    except Exception as e:
        logger.error(f"Failed to generate Gmail OAuth URL: {e}")
        raise HTTPException(status_code=500, detail=f"OAuth URL generation failed: {str(e)}")


@router.post("/oauth2/gmail/callback")
async def handle_gmail_oauth_callback(
    agent_id: str,
    code: str,
    state: str,
    orchestra_manager=Depends(get_orchestra_manager)
):
    """Handle Gmail OAuth2 callback and store tokens."""
    try:
        # In a real implementation, this would exchange the code for tokens
        # and store them securely for the agent
        
        return {
            "agent_id": agent_id,
            "status": "authorized",
            "message": "Gmail account successfully connected",
            "account_email": "demo@gmail.com",  # Would be actual email
        }
        
    except Exception as e:
        logger.error(f"Gmail OAuth callback failed: {e}")
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")