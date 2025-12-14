#!/usr/bin/env python3
"""
Test xenonit authentication service
"""
from auth_service import XenonitAuthService
from auth_dto import EnrollmentRequestDTO, LoginRequestDTO
from datetime import datetime

def main():
    print("🧪 Testing Xenonit Authentication Service\n")
    
    # Initialize auth service
    auth = XenonitAuthService()
    
    print("1. Testing user registration...")
    enroll_request = EnrollmentRequestDTO(
        email="user@example.com",
        password="SecurePass123",
        full_name="John Doe",
        company="CloudTech Inc.",
        timplanner_code="TIMPLAN2025"
    )
    
    reg_response = auth.register(enroll_request)
    print(f"   Registration Result: {reg_response.message}")
    print(f"   User ID: {reg_response.user_id}")
    
    print("\n2. Testing login (before enrollment)...")
    login_request = LoginRequestDTO(
        email="user@example.com",
        password="SecurePass123",
        timestamp=datetime.now(),
        device_info="Windows PC",
        timplanner_code="TIMPLAN2025"
    )
    
    login_response = auth.login(login_request)
    print(f"   Login Successful: {login_response.success}")
    print(f"   Auth Token: {login_response.auth_token[:20]}...")
    print(f"   Requires Enrollment: {login_response.requires_enrollment}")
    
    if login_response.success and login_response.requires_enrollment:
        print("\n3. Testing enrollment after login...")
        enrollment_data = {
            "subscription_plan": "premium",
            "storage_quota": "1GB",
            "accepted_terms": True,
            "newsletter_opt_in": True
        }
        
        enroll_response = auth.enroll_after_login(
            login_response.auth_token,
            enrollment_data
        )
        print(f"   Enrollment Result: {enroll_response.message}")
        
        print("\n4. Testing login after enrollment...")
        login_request2 = LoginRequestDTO(
            email="user@example.com",
            password="SecurePass123",
            timestamp=datetime.now(),
            device_info="Windows PC"
        )
        
        login_response2 = auth.login(login_request2)
        print(f"   Login Successful: {login_response2.success}")
        print(f"   Requires Enrollment: {login_response2.requires_enrollment}")
    
    print("\n5. Testing token validation...")
    if login_response.success:
        token_valid = auth.validate_token(login_response.auth_token)
        print(f"   Token Valid: {token_valid}")
        
        print("\n6. Testing logout...")
        logout_success = auth.logout(login_response.auth_token)
        print(f"   Logout Successful: {logout_success}")
        
        token_valid_after = auth.validate_token(login_response.auth_token)
        print(f"   Token Valid After Logout: {token_valid_after}")
    
    print("\n✅ Authentication tests completed!")

if __name__ == "__main__":
    main()