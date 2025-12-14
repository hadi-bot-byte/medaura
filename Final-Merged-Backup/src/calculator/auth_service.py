"""
Xenonit Authentication Service
Implements authentication with enrollment after login
"""
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
from auth_dto import LoginRequestDTO, LoginResponseDTO, EnrollmentRequestDTO, EnrollmentResponseDTO

class XenonitAuthService:
    """Mock xenonit authentication service with enrollment"""
    
    def __init__(self, storage_file="users.json", config_file="cloudtemplate.json"):
        self.storage_file = storage_file
        self.config_file = config_file
        self.users: Dict = {}
        self.sessions: Dict = {}
        self.load_users()
        self.load_config()
        
    def load_config(self):
        """Load configuration from cloudtemplate.json"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "authentication": {
                    "session_timeout_minutes": 60,
                    "max_login_attempts": 5
                }
            }
            
    def load_users(self):
        """Load users from storage"""
        try:
            with open(self.storage_file, 'r') as f:
                self.users = json.load(f)
        except FileNotFoundError:
            self.users = {}
            
    def save_users(self):
        """Save users to storage"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.users, f, indent=2)
            
    def hash_password(self, password: str) -> str:
        """Simple password hashing"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_token(self, email: str) -> str:
        """Generate authentication token"""
        return hashlib.sha256(f"{email}{datetime.now()}{uuid.uuid4()}".encode()).hexdigest()[:32]
    
    def login(self, login_request: LoginRequestDTO) -> LoginResponseDTO:
        """Authenticate user with xenonit service"""
        email = login_request.email
        
        if email not in self.users:
            return LoginResponseDTO(
                success=False,
                error_message="User not found. Please register first.",
                requires_enrollment=True
            )
            
        user = self.users[email]
        
        # Check if user is locked
        if user.get('login_attempts', 0) >= self.config['authentication']['max_login_attempts']:
            return LoginResponseDTO(
                success=False,
                error_message="Account locked due to too many failed attempts"
            )
        
        # Verify password
        hashed_password = self.hash_password(login_request.password)
        
        if user['password_hash'] != hashed_password:
            # Increment failed attempts
            user['login_attempts'] = user.get('login_attempts', 0) + 1
            self.save_users()
            
            return LoginResponseDTO(
                success=False,
                error_message="Invalid password",
                requires_enrollment=False
            )
        
        # Reset login attempts on successful login
        user['login_attempts'] = 0
        user['last_login'] = datetime.now().isoformat()
        self.save_users()
        
        # Generate auth token
        auth_token = self.generate_token(email)
        expires_at = datetime.now() + timedelta(minutes=self.config['authentication']['session_timeout_minutes'])
        
        # Store session
        self.sessions[auth_token] = {
            'user_id': user['user_id'],
            'email': email,
            'expires_at': expires_at.isoformat(),
            'login_time': datetime.now().isoformat()
        }
        
        # Check if enrollment is required
        requires_enrollment = not user.get('enrolled', False)
        
        return LoginResponseDTO(
            success=True,
            user_id=user['user_id'],
            auth_token=auth_token,
            expires_at=expires_at,
            requires_enrollment=requires_enrollment
        )
    
    def enroll_after_login(self, auth_token: str, enrollment_data: dict) -> EnrollmentResponseDTO:
        """Allow enrollment after successful login"""
        # Verify token
        if auth_token not in self.sessions:
            return EnrollmentResponseDTO(
                success=False,
                message="Invalid or expired session"
            )
        
        session = self.sessions[auth_token]
        email = session['email']
        
        if email not in self.users:
            return EnrollmentResponseDTO(
                success=False,
                message="User not found"
            )
        
        # Update user with enrollment data
        user = self.users[email]
        user.update(enrollment_data)
        user['enrolled'] = True
        user['enrolled_at'] = datetime.now().isoformat()
        user['enrollment_data'] = enrollment_data
        
        self.save_users()
        
        return EnrollmentResponseDTO(
            success=True,
            user_id=user['user_id'],
            message="Enrollment successful",
            enrollment_date=datetime.now()
        )
    
    def register(self, enrollment_request: EnrollmentRequestDTO) -> EnrollmentResponseDTO:
        """Register new user"""
        email = enrollment_request.email
        
        # Check if user already exists
        if email in self.users:
            return EnrollmentResponseDTO(
                success=False,
                message="User already exists"
            )
        
        # Validate password length
        if len(enrollment_request.password) < self.config['authentication']['password_min_length']:
            return EnrollmentResponseDTO(
                success=False,
                message=f"Password must be at least {self.config['authentication']['password_min_length']} characters"
            )
        
        # Create user
        user_id = str(uuid.uuid4())
        
        self.users[email] = {
            'user_id': user_id,
            'email': email,
            'password_hash': self.hash_password(enrollment_request.password),
            'full_name': enrollment_request.full_name,
            'company': enrollment_request.company,
            'timplanner_code': enrollment_request.timplanner_code,
            'registered_at': datetime.now().isoformat(),
            'enrolled': False,
            'login_attempts': 0
        }
        
        self.save_users()
        
        return EnrollmentResponseDTO(
            success=True,
            user_id=user_id,
            message="Registration successful. Please login to complete enrollment."
        )
    
    def validate_token(self, auth_token: str) -> bool:
        """Validate authentication token"""
        if auth_token not in self.sessions:
            return False
        
        session = self.sessions[auth_token]
        expires_at = datetime.fromisoformat(session['expires_at'])
        
        if datetime.now() > expires_at:
            # Token expired
            del self.sessions[auth_token]
            return False
        
        return True
    
    def logout(self, auth_token: str) -> bool:
        """Logout user"""
        if auth_token in self.sessions:
            del self.sessions[auth_token]
            return True
        return False