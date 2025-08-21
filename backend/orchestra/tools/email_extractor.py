"""
AI-Powered Email Data Extractor

Uses OpenAI/Anthropic APIs to classify construction emails and extract structured data
including project information, RFIs, budget updates, schedule changes, and more.
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

try:
    import openai
    from anthropic import Anthropic
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    logging.warning("AI libraries not available. Email extraction will use rule-based fallback.")

logger = logging.getLogger(__name__)


class EmailClassification(Enum):
    """Types of construction emails that can be classified."""
    PROJECT_UPDATE = "project_update"
    RFI_SUBMISSION = "rfi_submission"
    RFI_RESPONSE = "rfi_response"
    BUDGET_CHANGE = "budget_change"
    SCHEDULE_UPDATE = "schedule_update"
    MATERIAL_DELIVERY = "material_delivery"
    INSPECTION_REPORT = "inspection_report"
    CHANGE_ORDER = "change_order"
    SAFETY_INCIDENT = "safety_incident"
    GENERAL_COMMUNICATION = "general_communication"
    NON_CONSTRUCTION = "non_construction"


@dataclass
class ExtractionResult:
    """Result of email classification and data extraction."""
    email_type: str
    confidence: float
    summary: str
    extracted_data: Dict[str, Any]
    project_id: Optional[str] = None
    processing_time: float = 0.0


class MockEmailDataExtractor:
    """Mock email data extractor for development when AI libraries are not available."""
    
    async def initialize(self, config: Dict[str, Any]):
        logger.warning("Using mock email data extractor - AI libraries not available")
        self.config = config
    
    async def classify_and_extract(self, subject: str, content: str, sender: str) -> Dict[str, Any]:
        """Mock classification and extraction using rule-based approach."""
        
        # Simple keyword-based classification
        content_lower = (subject + " " + content).lower()
        
        # Determine email type based on keywords
        if any(keyword in content_lower for keyword in ['rfi', 'request for information']):
            email_type = EmailClassification.RFI_SUBMISSION.value
        elif any(keyword in content_lower for keyword in ['budget', 'cost', 'payment']):
            email_type = EmailClassification.BUDGET_CHANGE.value
        elif any(keyword in content_lower for keyword in ['schedule', 'timeline', 'delay']):
            email_type = EmailClassification.SCHEDULE_UPDATE.value
        elif any(keyword in content_lower for keyword in ['delivery', 'material', 'supply']):
            email_type = EmailClassification.MATERIAL_DELIVERY.value
        elif any(keyword in content_lower for keyword in ['inspection', 'quality']):
            email_type = EmailClassification.INSPECTION_REPORT.value
        elif any(keyword in content_lower for keyword in ['project', 'construction', 'site']):
            email_type = EmailClassification.PROJECT_UPDATE.value
        else:
            email_type = EmailClassification.NON_CONSTRUCTION.value
        
        # Extract basic data
        extracted_data = {
            "keywords": self._extract_keywords(content_lower),
            "dates": self._extract_dates(content),
            "numbers": self._extract_numbers(content),
            "urgency": "medium" if any(word in content_lower for word in ['urgent', 'asap', 'immediate']) else "normal"
        }
        
        # Simple project ID extraction
        project_id = self._extract_project_id(content)
        
        return {
            "email_type": email_type,
            "confidence": 0.7,  # Mock confidence
            "summary": f"Mock classification: {email_type}",
            "extracted_data": extracted_data,
            "project_id": project_id
        }
    
    def _extract_keywords(self, content: str) -> List[str]:
        construction_keywords = [
            'project', 'construction', 'building', 'site', 'schedule', 'budget',
            'rfi', 'change order', 'material', 'inspection', 'safety'
        ]
        return [kw for kw in construction_keywords if kw in content]
    
    def _extract_dates(self, content: str) -> List[str]:
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
        return re.findall(date_pattern, content)
    
    def _extract_numbers(self, content: str) -> List[str]:
        number_pattern = r'\$[\d,]+(?:\.\d{2})?'
        return re.findall(number_pattern, content)
    
    def _extract_project_id(self, content: str) -> Optional[str]:
        project_pattern = r'(?:project|prj|job)\s*[#:-]?\s*(\w+[-]?\d+)'
        match = re.search(project_pattern, content, re.IGNORECASE)
        return match.group(1) if match else None


class EmailDataExtractor:
    """
    AI-powered email classification and data extraction for construction projects.
    
    Uses large language models to analyze email content and extract structured data
    relevant to construction project management including RFIs, schedules, budgets, etc.
    """
    
    def __init__(self):
        self.openai_client: Optional[openai.OpenAI] = None
        self.anthropic_client: Optional[Anthropic] = None
        self.ai_provider = "openai"  # Default to OpenAI
        self.model_config = {
            "openai": {
                "model": "gpt-4",
                "temperature": 0.1,
                "max_tokens": 1000
            },
            "anthropic": {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1000
            }
        }
        
        # Prompts for different analysis tasks
        self.classification_prompt = """
You are an AI assistant specialized in analyzing construction project emails. 
Classify this email into one of the following categories and extract relevant data.

Email Categories:
- project_update: General project status updates
- rfi_submission: Request for Information submissions
- rfi_response: Responses to RFIs
- budget_change: Budget modifications, cost changes, payment requests
- schedule_update: Schedule changes, timeline updates, delays
- material_delivery: Material deliveries, supply notifications
- inspection_report: Quality inspections, safety reports
- change_order: Change orders, modifications to work scope
- safety_incident: Safety incidents, accidents, violations
- general_communication: General project communication
- non_construction: Not related to construction projects

Email Subject: {subject}
Email Content: {content}
Sender: {sender}

Please respond with a JSON object containing:
{{
    "email_type": "category_name",
    "confidence": 0.0-1.0,
    "summary": "brief summary of the email content",
    "project_id": "extracted project identifier or null",
    "extracted_data": {{
        "key_points": ["list of important points"],
        "deadlines": ["any mentioned deadlines"],
        "costs": ["any mentioned costs or budget items"],
        "people": ["mentioned people or roles"],
        "locations": ["mentioned locations or sites"],
        "urgency": "low/medium/high",
        "action_required": true/false,
        "next_steps": ["any mentioned next steps"]
    }}
}}
"""
        
        self.rfi_analysis_prompt = """
You are analyzing an RFI (Request for Information) email. Extract detailed information.

Email Content: {content}

Please extract the following information and respond with JSON:
{{
    "rfi_number": "RFI identifier if mentioned",
    "trade": "relevant trade or discipline",
    "description": "description of the information requested",
    "due_date": "response due date if mentioned",
    "priority": "low/medium/high",
    "referenced_drawings": ["any drawing numbers mentioned"],
    "referenced_specs": ["any specification sections mentioned"],
    "contact_person": "person to contact for response",
    "cost_impact": "potential cost impact if mentioned",
    "schedule_impact": "potential schedule impact if mentioned"
}}
"""
        
        self.budget_analysis_prompt = """
You are analyzing a budget or cost-related construction email. Extract financial information.

Email Content: {content}

Please extract the following information and respond with JSON:
{{
    "cost_items": [
        {{
            "description": "description of cost item",
            "amount": "cost amount",
            "type": "original/change/additional"
        }}
    ],
    "total_amount": "total cost impact",
    "budget_category": "category of budget impact",
    "approval_required": true/false,
    "justification": "reason for cost change",
    "effective_date": "when cost change takes effect"
}}
"""
    
    async def initialize(self, config: Dict[str, Any]):
        """
        Initialize the email data extractor with AI configuration.
        
        Args:
            config: Configuration including API keys and model preferences
        """
        if not AI_AVAILABLE:
            logger.warning("AI libraries not available, using mock implementation")
            return
        
        try:
            # Initialize AI clients based on configuration
            if config.get("openai_api_key"):
                self.openai_client = openai.OpenAI(api_key=config["openai_api_key"])
                self.ai_provider = "openai"
                logger.info("OpenAI client initialized for email extraction")
            
            if config.get("anthropic_api_key"):
                self.anthropic_client = Anthropic(api_key=config["anthropic_api_key"])
                if not self.openai_client:  # Use Anthropic if OpenAI not available
                    self.ai_provider = "anthropic"
                logger.info("Anthropic client initialized for email extraction")
            
            # Update model configuration if provided
            if config.get("model_config"):
                self.model_config.update(config["model_config"])
            
            if not self.openai_client and not self.anthropic_client:
                logger.warning("No AI API keys provided, using rule-based fallback")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI clients: {e}")
    
    async def classify_and_extract(self, subject: str, content: str, sender: str) -> Dict[str, Any]:
        """
        Classify email type and extract relevant construction data.
        
        Args:
            subject: Email subject line
            content: Email body content
            sender: Email sender address
            
        Returns:
            Dictionary with classification and extracted data
        """
        if not AI_AVAILABLE or (not self.openai_client and not self.anthropic_client):
            # Fall back to mock implementation
            mock_extractor = MockEmailDataExtractor()
            await mock_extractor.initialize({})
            return await mock_extractor.classify_and_extract(subject, content, sender)
        
        try:
            start_time = datetime.now()
            
            # Prepare prompt with email content
            prompt = self.classification_prompt.format(
                subject=subject[:200],  # Limit subject length
                content=content[:4000],  # Limit content length for token efficiency
                sender=sender
            )
            
            # Get AI analysis
            if self.ai_provider == "openai" and self.openai_client:
                result = await self._analyze_with_openai(prompt)
            elif self.ai_provider == "anthropic" and self.anthropic_client:
                result = await self._analyze_with_anthropic(prompt)
            else:
                raise Exception("No AI client available")
            
            # Parse AI response
            try:
                parsed_result = json.loads(result)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI response: {result}")
                # Fall back to mock
                mock_extractor = MockEmailDataExtractor()
                await mock_extractor.initialize({})
                return await mock_extractor.classify_and_extract(subject, content, sender)
            
            # Enhance with specialized analysis if needed
            email_type = parsed_result.get("email_type")
            if email_type in ["rfi_submission", "rfi_response"]:
                rfi_data = await self._analyze_rfi_details(content)
                parsed_result["extracted_data"].update(rfi_data)
            elif email_type == "budget_change":
                budget_data = await self._analyze_budget_details(content)
                parsed_result["extracted_data"].update(budget_data)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            parsed_result["processing_time"] = processing_time
            
            logger.info(f"Email classified as {email_type} with {parsed_result.get('confidence', 0):.2f} confidence")
            return parsed_result
            
        except Exception as e:
            logger.error(f"Email classification failed: {e}")
            # Fall back to mock implementation
            mock_extractor = MockEmailDataExtractor()
            await mock_extractor.initialize({})
            return await mock_extractor.classify_and_extract(subject, content, sender)
    
    async def _analyze_with_openai(self, prompt: str) -> str:
        """Analyze email using OpenAI API."""
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model_config["openai"]["model"],
                messages=[
                    {"role": "system", "content": "You are a construction project management AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.model_config["openai"]["temperature"],
                max_tokens=self.model_config["openai"]["max_tokens"]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
    
    async def _analyze_with_anthropic(self, prompt: str) -> str:
        """Analyze email using Anthropic API."""
        try:
            response = await self.anthropic_client.messages.create(
                model=self.model_config["anthropic"]["model"],
                max_tokens=self.model_config["anthropic"]["max_tokens"],
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API call failed: {e}")
            raise
    
    async def _analyze_rfi_details(self, content: str) -> Dict[str, Any]:
        """Perform detailed RFI analysis."""
        try:
            prompt = self.rfi_analysis_prompt.format(content=content[:3000])
            
            if self.ai_provider == "openai" and self.openai_client:
                result = await self._analyze_with_openai(prompt)
            elif self.ai_provider == "anthropic" and self.anthropic_client:
                result = await self._analyze_with_anthropic(prompt)
            else:
                return {}
            
            rfi_data = json.loads(result)
            return {"rfi_details": rfi_data}
            
        except Exception as e:
            logger.error(f"RFI detail analysis failed: {e}")
            return {}
    
    async def _analyze_budget_details(self, content: str) -> Dict[str, Any]:
        """Perform detailed budget analysis."""
        try:
            prompt = self.budget_analysis_prompt.format(content=content[:3000])
            
            if self.ai_provider == "openai" and self.openai_client:
                result = await self._analyze_with_openai(prompt)
            elif self.ai_provider == "anthropic" and self.anthropic_client:
                result = await self._analyze_with_anthropic(prompt)
            else:
                return {}
            
            budget_data = json.loads(result)
            return {"budget_details": budget_data}
            
        except Exception as e:
            logger.error(f"Budget detail analysis failed: {e}")
            return {}
    
    async def analyze_batch(self, emails: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple emails in batch for efficiency.
        
        Args:
            emails: List of email dictionaries with subject, content, sender
            
        Returns:
            List of analysis results
        """
        results = []
        
        for email in emails:
            try:
                result = await self.classify_and_extract(
                    subject=email.get("subject", ""),
                    content=email.get("content", ""),
                    sender=email.get("sender", "")
                )
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to analyze email in batch: {e}")
                results.append({
                    "email_type": "error",
                    "confidence": 0.0,
                    "summary": f"Analysis failed: {str(e)}",
                    "extracted_data": {}
                })
        
        return results
    
    def get_classification_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics from a batch of classification results."""
        if not results:
            return {}
        
        # Count classifications
        type_counts = {}
        total_confidence = 0
        construction_emails = 0
        
        for result in results:
            email_type = result.get("email_type", "unknown")
            type_counts[email_type] = type_counts.get(email_type, 0) + 1
            total_confidence += result.get("confidence", 0)
            
            if email_type != "non_construction":
                construction_emails += 1
        
        return {
            "total_emails": len(results),
            "construction_emails": construction_emails,
            "non_construction_emails": len(results) - construction_emails,
            "average_confidence": total_confidence / len(results),
            "type_distribution": type_counts,
            "construction_percentage": (construction_emails / len(results)) * 100
        }


# Export the appropriate class based on availability
if AI_AVAILABLE:
    EmailDataExtractorImpl = EmailDataExtractor
else:
    EmailDataExtractorImpl = MockEmailDataExtractor

# Alias for easier import
EmailDataExtractor = EmailDataExtractorImpl