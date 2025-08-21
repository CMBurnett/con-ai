"""
Email Tools for IMAP/OAuth2 Integration

Provides email connectivity, authentication, and message processing capabilities
for the EmailAgent. Supports Gmail, Outlook, and custom IMAP servers.
"""

import imaplib
import email
import base64
import json
import os
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from dataclasses import dataclass
from enum import Enum

try:
    import imapclient
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from msal import ConfidentialClientApplication, PublicClientApplication
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False
    logging.warning("OAuth libraries not available. Email functionality will be limited.")

logger = logging.getLogger(__name__)


class EmailProvider(Enum):
    """Supported email providers."""
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    CUSTOM_IMAP = "custom"


@dataclass
class EmailConfig:
    """Email configuration for different providers."""
    provider: EmailProvider
    email_address: str
    
    # IMAP settings
    imap_server: str
    imap_port: int = 993
    use_ssl: bool = True
    
    # Authentication
    auth_type: str = "oauth2"  # oauth2, password, app_password
    
    # OAuth2 settings
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    redirect_uri: str = "http://localhost:8080/auth/callback"
    
    # Password authentication (fallback)
    password: Optional[str] = None
    
    # Monitoring settings
    folders: List[str] = None
    
    def __post_init__(self):
        if self.folders is None:
            self.folders = ["INBOX"]


class MockEmailTools:
    """Mock email tools for development when OAuth libraries are not available."""
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        logger.warning("Using mock email tools - OAuth libraries not available")
        self.config = config
        return True
    
    async def fetch_emails(self, folder: str = "INBOX", since: datetime = None, limit: int = 10) -> List[Dict[str, Any]]:
        # Return mock email data for development
        mock_emails = [
            {
                "id": f"mock_email_{i}",
                "from": f"contractor{i}@example.com",
                "to": self.config.get("email_address", "user@example.com"),
                "subject": f"Project Update - Mock Email {i}",
                "date": datetime.now() - timedelta(hours=i),
                "body": f"This is a mock construction project update email {i}.",
                "attachments": []
            }
            for i in range(min(limit, 3))
        ]
        
        if since:
            mock_emails = [e for e in mock_emails if e["date"] >= since]
        
        return mock_emails
    
    async def fetch_email_by_id(self, email_id: str) -> Optional[Dict[str, Any]]:
        if email_id.startswith("mock_email_"):
            return {
                "id": email_id,
                "from": "contractor@example.com",
                "to": self.config.get("email_address", "user@example.com"),
                "subject": "Mock Email",
                "date": datetime.now(),
                "body": "This is a mock email for development.",
                "attachments": []
            }
        return None
    
    async def extract_content(self, email_msg: Dict[str, Any]) -> str:
        return email_msg.get("body", "")
    
    async def download_attachment(self, attachment: Dict[str, Any]) -> bytes:
        return b"Mock attachment content"
    
    async def close(self):
        pass


class EmailTools:
    """
    Email tools for IMAP connectivity and OAuth2 authentication.
    
    Supports Gmail, Outlook, and custom IMAP servers with secure authentication.
    """
    
    def __init__(self):
        self.config: Optional[EmailConfig] = None
        self.client: Optional[imapclient.IMAPClient] = None
        self.credentials: Optional[Dict[str, Any]] = None
        self.is_connected: bool = False
        
        # Provider-specific settings
        self.provider_configs = {
            EmailProvider.GMAIL: {
                "imap_server": "imap.gmail.com",
                "imap_port": 993,
                "oauth_scope": ["https://www.googleapis.com/auth/gmail.readonly"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            },
            EmailProvider.OUTLOOK: {
                "imap_server": "outlook.office365.com", 
                "imap_port": 993,
                "oauth_scope": ["https://graph.microsoft.com/IMAP.AccessAsUser.All"],
                "authority": "https://login.microsoftonline.com/common"
            }
        }
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize email tools with configuration.
        
        Args:
            config: Email configuration dictionary
            
        Returns:
            bool: True if initialization successful
        """
        if not OAUTH_AVAILABLE:
            logger.warning("OAuth libraries not available, using mock implementation")
            return True
            
        try:
            # Parse configuration
            provider_str = config.get("email_provider", "gmail")
            provider = EmailProvider(provider_str)
            
            self.config = EmailConfig(
                provider=provider,
                email_address=config["email_address"],
                imap_server=config.get("imap_server") or self.provider_configs[provider]["imap_server"],
                imap_port=config.get("imap_port", 993),
                use_ssl=config.get("use_ssl", True),
                auth_type=config.get("auth_type", "oauth2"),
                client_id=config.get("client_id"),
                client_secret=config.get("client_secret"),
                password=config.get("password"),
                folders=config.get("monitored_folders", ["INBOX"])
            )
            
            # Validate required fields
            if self.config.auth_type == "oauth2":
                if not self.config.client_id:
                    raise ValueError("client_id required for OAuth2 authentication")
            elif self.config.auth_type in ["password", "app_password"]:
                if not self.config.password:
                    raise ValueError("password required for password authentication")
            
            logger.info(f"EmailTools initialized for {self.config.provider.value}: {self.config.email_address}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize EmailTools: {e}")
            return False
    
    async def connect(self) -> bool:
        """
        Connect to the email server with authentication.
        
        Returns:
            bool: True if connection successful
        """
        if not OAUTH_AVAILABLE:
            return True
            
        try:
            # Create IMAP client
            self.client = imapclient.IMAPClient(
                host=self.config.imap_server,
                port=self.config.imap_port,
                ssl=self.config.use_ssl
            )
            
            # Authenticate based on configuration
            if self.config.auth_type == "oauth2":
                success = await self._authenticate_oauth2()
            else:
                success = await self._authenticate_password()
            
            if success:
                self.is_connected = True
                logger.info(f"Connected to {self.config.provider.value} successfully")
                return True
            else:
                logger.error("Authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to email server: {e}")
            return False
    
    async def _authenticate_oauth2(self) -> bool:
        """Authenticate using OAuth2."""
        try:
            if self.config.provider == EmailProvider.GMAIL:
                return await self._authenticate_gmail_oauth2()
            elif self.config.provider == EmailProvider.OUTLOOK:
                return await self._authenticate_outlook_oauth2()
            else:
                logger.error(f"OAuth2 not supported for {self.config.provider.value}")
                return False
                
        except Exception as e:
            logger.error(f"OAuth2 authentication failed: {e}")
            return False
    
    async def _authenticate_gmail_oauth2(self) -> bool:
        """Authenticate with Gmail using OAuth2."""
        try:
            # Load existing credentials or start OAuth flow
            credentials = await self._load_or_refresh_credentials("gmail")
            
            if not credentials:
                logger.info("Starting Gmail OAuth2 flow")
                # This would typically involve redirecting user to OAuth URL
                # For now, we'll use a mock token or require manual setup
                logger.warning("Gmail OAuth2 flow not implemented - using mock credentials")
                return False
            
            # Authenticate with IMAP using OAuth2
            auth_string = self._build_oauth2_string(
                self.config.email_address,
                credentials["access_token"]
            )
            
            self.client.oauth2_login(
                self.config.email_address,
                auth_string
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Gmail OAuth2 authentication failed: {e}")
            return False
    
    async def _authenticate_outlook_oauth2(self) -> bool:
        """Authenticate with Outlook using OAuth2."""
        try:
            # Load existing credentials or start OAuth flow
            credentials = await self._load_or_refresh_credentials("outlook")
            
            if not credentials:
                logger.info("Starting Outlook OAuth2 flow")
                logger.warning("Outlook OAuth2 flow not implemented - using mock credentials")
                return False
            
            # Authenticate with IMAP using OAuth2
            auth_string = self._build_oauth2_string(
                self.config.email_address,
                credentials["access_token"]
            )
            
            self.client.oauth2_login(
                self.config.email_address,
                auth_string
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Outlook OAuth2 authentication failed: {e}")
            return False
    
    async def _authenticate_password(self) -> bool:
        """Authenticate using username/password."""
        try:
            self.client.login(self.config.email_address, self.config.password)
            return True
            
        except Exception as e:
            logger.error(f"Password authentication failed: {e}")
            return False
    
    def _build_oauth2_string(self, email: str, access_token: str) -> str:
        """Build OAuth2 authentication string for IMAP."""
        auth_string = f"user={email}\x01auth=Bearer {access_token}\x01\x01"
        return base64.b64encode(auth_string.encode()).decode()
    
    async def _load_or_refresh_credentials(self, provider: str) -> Optional[Dict[str, Any]]:
        """Load existing credentials or refresh if expired."""
        try:
            # Check for stored credentials
            credentials_file = f".email_credentials_{provider}.json"
            
            if os.path.exists(credentials_file):
                with open(credentials_file, 'r') as f:
                    credentials = json.load(f)
                
                # Check if credentials are still valid
                if self._are_credentials_valid(credentials):
                    return credentials
                else:
                    # Try to refresh
                    refreshed = await self._refresh_credentials(credentials, provider)
                    if refreshed:
                        return refreshed
            
            # No valid credentials found
            return None
            
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            return None
    
    def _are_credentials_valid(self, credentials: Dict[str, Any]) -> bool:
        """Check if credentials are still valid."""
        if "expires_at" not in credentials:
            return False
        
        expires_at = datetime.fromisoformat(credentials["expires_at"])
        return datetime.now() < expires_at - timedelta(minutes=5)  # 5 min buffer
    
    async def _refresh_credentials(self, credentials: Dict[str, Any], provider: str) -> Optional[Dict[str, Any]]:
        """Refresh expired OAuth2 credentials."""
        try:
            if provider == "gmail":
                # Implement Gmail token refresh
                logger.warning("Gmail token refresh not implemented")
                return None
            elif provider == "outlook":
                # Implement Outlook token refresh
                logger.warning("Outlook token refresh not implemented")
                return None
            
        except Exception as e:
            logger.error(f"Failed to refresh credentials: {e}")
            return None
    
    async def fetch_emails(self, folder: str = "INBOX", since: datetime = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch emails from specified folder.
        
        Args:
            folder: Email folder to search
            since: Only fetch emails after this datetime
            limit: Maximum number of emails to fetch
            
        Returns:
            List of email dictionaries
        """
        if not OAUTH_AVAILABLE:
            mock_tools = MockEmailTools()
            await mock_tools.initialize({"email_address": "mock@example.com"})
            return await mock_tools.fetch_emails(folder, since, limit)
        
        if not self.is_connected:
            await self.connect()
        
        try:
            # Select folder
            self.client.select_folder(folder)
            
            # Build search criteria
            search_criteria = ["ALL"]
            if since:
                since_str = since.strftime("%d-%b-%Y")
                search_criteria = ["SINCE", since_str]
            
            # Search for messages
            message_ids = self.client.search(search_criteria)
            
            # Limit results
            if limit:
                message_ids = message_ids[-limit:]
            
            # Fetch email data
            emails = []
            if message_ids:
                fetch_data = self.client.fetch(message_ids, ['ENVELOPE', 'BODY[]', 'FLAGS'])
                
                for msg_id, data in fetch_data.items():
                    try:
                        email_data = await self._parse_email_data(msg_id, data)
                        if email_data:
                            emails.append(email_data)
                    except Exception as e:
                        logger.error(f"Failed to parse email {msg_id}: {e}")
            
            return emails
            
        except Exception as e:
            logger.error(f"Failed to fetch emails: {e}")
            return []
    
    async def fetch_email_by_id(self, email_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific email by ID."""
        if not OAUTH_AVAILABLE:
            mock_tools = MockEmailTools()
            await mock_tools.initialize({"email_address": "mock@example.com"})
            return await mock_tools.fetch_email_by_id(email_id)
        
        if not self.is_connected:
            await self.connect()
        
        try:
            # Fetch specific message
            fetch_data = self.client.fetch([email_id], ['ENVELOPE', 'BODY[]', 'FLAGS'])
            
            if email_id in fetch_data:
                return await self._parse_email_data(email_id, fetch_data[email_id])
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch email {email_id}: {e}")
            return None
    
    async def _parse_email_data(self, msg_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse IMAP email data into standardized format."""
        try:
            envelope = data[b'ENVELOPE']
            body = data[b'BODY[]']
            
            # Parse email message
            msg = email.message_from_bytes(body)
            
            # Extract basic information
            email_data = {
                "id": str(msg_id),
                "from": self._decode_header(envelope.from_[0] if envelope.from_ else ""),
                "to": self._decode_header(envelope.to[0] if envelope.to else ""),
                "subject": self._decode_header(envelope.subject or ""),
                "date": envelope.date or datetime.now(),
                "body": "",
                "attachments": []
            }
            
            # Extract body content
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        email_data["body"] = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    elif part.get_content_type() == "text/html" and not email_data["body"]:
                        email_data["body"] = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                
                # Extract attachments
                for part in msg.walk():
                    if part.get_content_disposition() == "attachment":
                        email_data["attachments"].append({
                            "filename": part.get_filename() or "unknown",
                            "content_type": part.get_content_type(),
                            "size": len(part.get_payload())
                        })
            else:
                email_data["body"] = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            return email_data
            
        except Exception as e:
            logger.error(f"Failed to parse email data: {e}")
            return None
    
    def _decode_header(self, header_value) -> str:
        """Decode email header value."""
        if not header_value:
            return ""
        
        try:
            if hasattr(header_value, 'name') and hasattr(header_value, 'route'):
                # RFC2822 address
                return f"{header_value.name or ''} <{header_value.route or ''}>"
            else:
                # Simple string
                decoded_parts = decode_header(str(header_value))
                return ''.join([
                    part.decode(encoding or 'utf-8') if isinstance(part, bytes) else str(part)
                    for part, encoding in decoded_parts
                ])
        except Exception:
            return str(header_value)
    
    async def extract_content(self, email_msg: Dict[str, Any]) -> str:
        """Extract clean text content from email."""
        body = email_msg.get("body", "")
        
        # Remove HTML tags if present
        if "<html" in body.lower() or "<body" in body.lower():
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(body, 'html.parser')
                body = soup.get_text()
            except ImportError:
                # Fallback: simple HTML tag removal
                import re
                body = re.sub(r'<[^>]+>', '', body)
        
        # Clean up whitespace
        body = '\n'.join(line.strip() for line in body.split('\n') if line.strip())
        
        return body
    
    async def download_attachment(self, attachment: Dict[str, Any]) -> bytes:
        """Download attachment content."""
        if not OAUTH_AVAILABLE:
            return b"Mock attachment content"
        
        # This would fetch the actual attachment content
        # Implementation depends on how attachments are stored in the email data
        logger.warning("Attachment download not fully implemented")
        return b"Placeholder attachment content"
    
    async def close(self):
        """Close email connection and clean up."""
        if self.client and self.is_connected:
            try:
                self.client.logout()
                self.is_connected = False
                logger.info("Email connection closed")
            except Exception as e:
                logger.error(f"Error closing email connection: {e}")


# Export the appropriate class based on availability
if OAUTH_AVAILABLE:
    EmailToolsImpl = EmailTools
else:
    EmailToolsImpl = MockEmailTools
    
# Alias for easier import
EmailTools = EmailToolsImpl