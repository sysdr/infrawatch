#!/usr/bin/env python3
import requests
import json
import time
import sys

class JWTDemo:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
    
    def print_response(self, response, description):
        print(f"\n{'='*50}")
        print(f"📋 {description}")
        print(f"{'='*50}")
        print(f"Status Code: {response.status_code}")
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        except:
            print(f"Response: {response.text}")
    
    def test_health(self):
        """Test health endpoint"""
        response = requests.get(f"{self.base_url}/health")
        self.print_response(response, "Health Check")
        return response.status_code == 200
    
    def register_user(self):
        """Register a test user"""
        user_data = {
            "email": "demo@example.com",
            "password": "DemoPassword123!",
            "first_name": "Demo",
            "last_name": "User",
            "role": "user"
        }
        
        response = requests.post(f"{self.base_url}/auth/register", json=user_data)
        self.print_response(response, "User Registration")
        return response.status_code in [201, 409]  # 409 if user already exists
    
    def login_user(self):
        """Login with test user"""
        login_data = {
            "email": "demo@example.com",
            "password": "DemoPassword123!"
        }
        
        response = requests.post(f"{self.base_url}/auth/login", json=login_data)
        self.print_response(response, "User Login")
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            return True
        return False
    
    def test_protected_endpoint(self):
        """Test accessing protected profile endpoint"""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f"{self.base_url}/auth/profile", headers=headers)
        self.print_response(response, "Protected Profile Endpoint")
        return response.status_code == 200
    
    def test_token_refresh(self):
        """Test token refresh functionality"""
        refresh_data = {"refresh_token": self.refresh_token}
        response = requests.post(f"{self.base_url}/auth/refresh", json=refresh_data)
        self.print_response(response, "Token Refresh")
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            return True
        return False
    
    def test_logout(self):
        """Test logout functionality"""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.post(f"{self.base_url}/auth/logout", headers=headers)
        self.print_response(response, "User Logout")
        return response.status_code == 200
    
    def test_access_after_logout(self):
        """Test accessing protected endpoint after logout"""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f"{self.base_url}/auth/profile", headers=headers)
        self.print_response(response, "Access After Logout (Should Fail)")
        return response.status_code == 401
    
    def run_full_demo(self):
        """Run complete demonstration"""
        print("🚀 Starting JWT Authentication Backend Demo")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health),
            ("User Registration", self.register_user),
            ("User Login", self.login_user),
            ("Protected Endpoint Access", self.test_protected_endpoint),
            ("Token Refresh", self.test_token_refresh),
            ("Updated Token Access", self.test_protected_endpoint),
            ("User Logout", self.test_logout),
            ("Access After Logout", self.test_access_after_logout)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            try:
                result = test_func()
                results.append((test_name, result))
                status = "✅ PASSED" if result else "❌ FAILED"
                print(f"Result: {status}")
            except Exception as e:
                print(f"❌ ERROR: {e}")
                results.append((test_name, False))
            
            time.sleep(1)  # Brief pause between tests
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 DEMO SUMMARY")
        print(f"{'='*60}")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! JWT Authentication is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        return passed == total

if __name__ == "__main__":
    demo = JWTDemo()
    success = demo.run_full_demo()
    sys.exit(0 if success else 1)
