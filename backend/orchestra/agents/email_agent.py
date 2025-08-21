"""
Email Agent for Construction Intelligence

This agent monitors email accounts, extracts construction-related data from emails
and attachments, and integrates with the Orchestra framework for multi-agent coordination.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from orchestra.agents.construction_agent import ConstructionAgent
from orchestra.tools.email_tools import EmailTools
from orchestra.tools.attachment_processor import AttachmentProcessor
from orchestra.tools.email_extractor import EmailDataExtractor

logger = logging.getLogger(__name__)


class EmailType(Enum):
    """Types of construction emails that can be processed."""
    PROJECT_UPDATE = "project_update"
    RFI_SUBMISSION = "rfi_submission"
    RFI_RESPONSE = "rfi_response"
    BUDGET_CHANGE = "budget_change"
    SCHEDULE_UPDATE = "schedule_update"
    MATERIAL_DELIVERY = "material_delivery"
    INSPECTION_REPORT = "inspection_report"
    CHANGE_ORDER = "change_order"
    GENERAL_COMMUNICATION = "general_communication"
    NON_CONSTRUCTION = "non_construction"


@dataclass
class EmailData:
    """Structured data extracted from construction emails."""
    email_id: str
    sender: str
    recipient: str
    subject: str
    timestamp: datetime
    email_type: EmailType
    project_id: Optional[str] = None
    content_summary: str = ""
    extracted_data: Dict[str, Any] = None
    attachments: List[Dict[str, Any]] = None
    confidence_score: float = 0.0
    
    def __post_init__(self):
        if self.extracted_data is None:
            self.extracted_data = {}
        if self.attachments is None:
            self.attachments = []


class EmailAgent(ConstructionAgent):
    """
    Email processing agent that monitors email accounts and extracts construction data.
    
    This agent extends the base ConstructionAgent to provide email-specific functionality
    including IMAP monitoring, attachment processing, and AI-powered content extraction.
    """
    
    def __init__(self, name: str = "Email Agent", agent_id: str = None):
        super().__init__(name=name, platform="email", agent_id=agent_id)
        
        # Initialize email processing tools
        self.email_tools = EmailTools()
        self.attachment_processor = AttachmentProcessor()
        self.data_extractor = EmailDataExtractor()
        
        # Email monitoring configuration
        self.email_config: Dict[str, Any] = {}
        self.monitored_folders: List[str] = ["INBOX"]
        self.processing_interval: int = 300  # 5 minutes default
        self.last_check: Optional[datetime] = None
        
        # Processing state
        self.is_monitoring: bool = False
        self.processed_emails: set = set()
        self.monitoring_task: Optional[asyncio.Task] = None
        
        logger.info(f"EmailAgent initialized: {self.name}")
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the email agent with configuration.
        
        Args:
            config: Email configuration including provider, authentication, etc.
            
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            self.email_config = config
            
            # Extract configuration
            self.monitored_folders = config.get("monitored_folders", ["INBOX"])
            self.processing_interval = config.get("processing_interval", 300)
            
            # Initialize email tools with configuration
            success = await self.email_tools.initialize(config)
            if not success:
                logger.error("Failed to initialize email tools")
                return False
            
            # Initialize attachment processor
            await self.attachment_processor.initialize()
            
            # Initialize data extractor
            await self.data_extractor.initialize(config.get("ai_config", {}))
            
            logger.info(f"EmailAgent initialized successfully for {config.get('email_provider', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize EmailAgent: {e}")
            return False
    
    async def execute_task(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute email processing task.
        
        Args:
            task_context: Task configuration and parameters
            
        Returns:
            Dict containing task results and extracted data
        """
        task_type = task_context.get("task_type", "monitor_emails")
        logger.info(f"Executing email task: {task_type}")
        
        try:
            if task_type == "monitor_emails":
                return await self._monitor_emails(task_context)
            elif task_type == "process_single_email":
                return await self._process_single_email(task_context)
            elif task_type == "sync_historical_emails":
                return await self._sync_historical_emails(task_context)
            elif task_type == "stop_monitoring":
                return await self._stop_monitoring()
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
        except Exception as e:
            logger.error(f"Email task execution failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "extracted_data": {}
            }
    
    async def _monitor_emails(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Start continuous email monitoring."""
        if self.is_monitoring:
            return {
                "status": "already_running",
                "message": "Email monitoring is already active"
            }
        
        self.is_monitoring = True
        
        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        return {
            "status": "started",
            "message": "Email monitoring started successfully",
            "config": {
                "folders": self.monitored_folders,
                "interval": self.processing_interval
            }
        }
    
    async def _monitoring_loop(self):
        """Main monitoring loop for email processing."""
        logger.info("Starting email monitoring loop")
        
        while self.is_monitoring:
            try:
                # Process new emails
                results = await self._process_new_emails()
                
                if results["new_emails"] > 0:
                    logger.info(f"Processed {results['new_emails']} new emails")
                    
                    # Trigger Orchestra coordination if significant data found
                    if results.get("construction_emails", 0) > 0:
                        await self._trigger_orchestra_coordination(results)
                
                # Wait for next check
                await asyncio.sleep(self.processing_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _process_new_emails(self) -> Dict[str, Any]:
        """Process new emails since last check."""
        try:
            # Calculate time range for new emails
            since_time = self.last_check or (datetime.now() - timedelta(hours=1))
            
            # Fetch new emails from all monitored folders
            all_emails = []
            for folder in self.monitored_folders:
                emails = await self.email_tools.fetch_emails(
                    folder=folder,
                    since=since_time,
                    limit=100
                )
                all_emails.extend(emails)
            
            # Process each email
            processed_emails = []
            construction_emails = 0
            
            for email_msg in all_emails:
                if email_msg["id"] in self.processed_emails:
                    continue
                
                # Extract and analyze email content
                email_data = await self._process_single_email_data(email_msg)
                
                if email_data and email_data.email_type != EmailType.NON_CONSTRUCTION:
                    processed_emails.append(email_data)
                    construction_emails += 1
                
                # Mark as processed
                self.processed_emails.add(email_msg["id"])
            
            # Update last check time
            self.last_check = datetime.now()
            
            return {
                "status": "success",
                "new_emails": len(all_emails),
                "construction_emails": construction_emails,
                "processed_data": [email.__dict__ for email in processed_emails]
            }
            
        except Exception as e:
            logger.error(f"Failed to process new emails: {e}")
            return {
                "status": "error",
                "message": str(e),
                "new_emails": 0,
                "construction_emails": 0
            }
    
    async def _process_single_email(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a specific email by ID."""
        email_id = task_context.get("email_id")
        if not email_id:
            raise ValueError("email_id required for single email processing")
        
        # Fetch specific email
        email_msg = await self.email_tools.fetch_email_by_id(email_id)
        if not email_msg:
            return {
                "status": "not_found",
                "message": f"Email {email_id} not found"
            }
        
        # Process the email
        email_data = await self._process_single_email_data(email_msg)
        
        if email_data:
            return {
                "status": "success",
                "message": "Email processed successfully",
                "extracted_data": email_data.__dict__
            }
        else:
            return {
                "status": "no_data",
                "message": "No construction data found in email"
            }
    
    async def _process_single_email_data(self, email_msg: Dict[str, Any]) -> Optional[EmailData]:
        """Process a single email message and extract construction data."""
        try:
            # Basic email information
            email_data = EmailData(
                email_id=email_msg["id"],
                sender=email_msg["from"],
                recipient=email_msg["to"],
                subject=email_msg["subject"],
                timestamp=email_msg["date"]
            )
            
            # Extract email content
            content = await self.email_tools.extract_content(email_msg)
            
            # Classify email type and extract data using AI
            classification_result = await self.data_extractor.classify_and_extract(
                subject=email_data.subject,
                content=content,
                sender=email_data.sender
            )
            
            email_data.email_type = EmailType(classification_result["email_type"])
            email_data.content_summary = classification_result["summary"]
            email_data.extracted_data = classification_result["extracted_data"]
            email_data.confidence_score = classification_result["confidence"]
            email_data.project_id = classification_result.get("project_id")
            
            # Process attachments if any
            if email_msg.get("attachments"):
                email_data.attachments = await self._process_attachments(
                    email_msg["attachments"], 
                    email_data.project_id
                )
            
            # Only return if it's construction-related
            if email_data.email_type != EmailType.NON_CONSTRUCTION:
                logger.info(f"Extracted construction data from email: {email_data.subject}")
                return email_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to process email {email_msg.get('id', 'unknown')}: {e}")
            return None
    
    async def _process_attachments(self, attachments: List[Dict], project_id: str = None) -> List[Dict[str, Any]]:
        """Process email attachments and extract relevant data."""
        processed_attachments = []
        
        for attachment in attachments:
            try:
                # Download attachment content
                attachment_data = await self.email_tools.download_attachment(attachment)
                
                # Process based on file type
                processed = await self.attachment_processor.process_attachment(
                    filename=attachment["filename"],
                    content=attachment_data,
                    project_id=project_id
                )
                
                if processed:
                    processed_attachments.append({
                        "filename": attachment["filename"],
                        "file_type": processed["file_type"],
                        "extracted_data": processed["data"],
                        "processing_status": "success"
                    })
                
            except Exception as e:
                logger.error(f"Failed to process attachment {attachment.get('filename', 'unknown')}: {e}")
                processed_attachments.append({
                    "filename": attachment.get("filename", "unknown"),
                    "processing_status": "error",
                    "error": str(e)
                })
        
        return processed_attachments
    
    async def _sync_historical_emails(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """Sync historical emails from specified time range."""
        days_back = task_context.get("days_back", 30)
        since_time = datetime.now() - timedelta(days=days_back)
        
        logger.info(f"Syncing emails from last {days_back} days")
        
        try:
            total_processed = 0
            construction_emails = 0
            
            for folder in self.monitored_folders:
                emails = await self.email_tools.fetch_emails(
                    folder=folder,
                    since=since_time,
                    limit=1000  # Higher limit for historical sync
                )
                
                for email_msg in emails:
                    if email_msg["id"] not in self.processed_emails:
                        email_data = await self._process_single_email_data(email_msg)
                        
                        if email_data and email_data.email_type != EmailType.NON_CONSTRUCTION:
                            construction_emails += 1
                        
                        self.processed_emails.add(email_msg["id"])
                        total_processed += 1
            
            return {
                "status": "success",
                "message": f"Historical sync completed",
                "total_emails": total_processed,
                "construction_emails": construction_emails,
                "days_synced": days_back
            }
            
        except Exception as e:
            logger.error(f"Historical sync failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _stop_monitoring(self) -> Dict[str, Any]:
        """Stop email monitoring."""
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None
        
        return {
            "status": "stopped",
            "message": "Email monitoring stopped successfully"
        }
    
    async def _trigger_orchestra_coordination(self, email_results: Dict[str, Any]):
        """Trigger Orchestra coordination based on email analysis."""
        try:
            # Analyze extracted data for triggers
            for email_data in email_results.get("processed_data", []):
                email_type = email_data.get("email_type")
                project_id = email_data.get("project_id")
                
                # Trigger appropriate agents based on email content
                if email_type == "schedule_update" and project_id:
                    # Trigger MS Project agent to sync latest schedule
                    await self._trigger_agent("msproject", {
                        "task_type": "sync_project_schedule",
                        "project_id": project_id,
                        "triggered_by": "email_update"
                    })
                
                elif email_type == "rfi_submission":
                    # Notify relevant stakeholders
                    await self._send_notification({
                        "type": "rfi_received",
                        "project_id": project_id,
                        "email_data": email_data
                    })
                
                elif email_type == "budget_change":
                    # Update financial tracking
                    await self._trigger_agent("financial", {
                        "task_type": "update_budget",
                        "project_id": project_id,
                        "email_data": email_data
                    })
            
        except Exception as e:
            logger.error(f"Orchestra coordination failed: {e}")
    
    async def _trigger_agent(self, agent_type: str, task_context: Dict[str, Any]):
        """Trigger another Orchestra agent."""
        # This would integrate with the Orchestra manager
        logger.info(f"Triggering {agent_type} agent with context: {task_context}")
        # Implementation depends on Orchestra framework integration
    
    async def _send_notification(self, notification: Dict[str, Any]):
        """Send notification via WebSocket."""
        # This would integrate with the WebSocket manager
        logger.info(f"Sending notification: {notification}")
        # Implementation depends on WebSocket integration
    
    async def stop(self):
        """Stop the email agent and clean up resources."""
        await self._stop_monitoring()
        
        # Clean up tools
        if hasattr(self.email_tools, 'close'):
            await self.email_tools.close()
        
        logger.info(f"EmailAgent {self.name} stopped successfully")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "name": self.name,
            "platform": self.platform,
            "is_monitoring": self.is_monitoring,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "processed_emails": len(self.processed_emails),
            "monitored_folders": self.monitored_folders,
            "processing_interval": self.processing_interval
        }