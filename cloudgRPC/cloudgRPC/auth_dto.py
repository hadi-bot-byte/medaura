"""
Data Transfer Objects (DTOs) for xenonit authentication service
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class LoginRequestDTO:
    """DTO for login request to xenonit service"""
    email: str
    password: str
    timestamp: datetime
    device_info: Optional[str] = None
    timplanner_code: Optional[str] = None
    
@dataclass
class LoginResponseDTO:
    """DTO for login response from xenonit service"""
    success: bool
    user_id: Optional[str] = None
    auth_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None
    requires_enrollment: bool = False
    
@dataclass  
class EnrollmentRequestDTO:
    """DTO for user enrollment/registration"""
    email: str
    password: str
    full_name: str
    company: Optional[str] = None
    timplanner_code: Optional[str] = None
    
@dataclass
class EnrollmentResponseDTO:
    """DTO for enrollment response"""
    success: bool
    user_id: Optional[str] = None
    message: Optional[str] = None
    enrollment_date: Optional[datetime] = None
    