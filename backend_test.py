import requests
import sys
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

class EventReminderAPITester:
    def __init__(self, base_url="https://931e0b94-0fa4-4ded-900d-ea29c15ce294.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.created_contact_id = None
        self.created_event_id = None
        self.subscription_id = None

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> tuple:
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    return False, error_data
                except:
                    print(f"   Error: {response.text}")
                    return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic health endpoints"""
        print("\n" + "="*50)
        print("TESTING BASIC HEALTH ENDPOINTS")
        print("="*50)
        
        # Test root endpoint
        self.run_test("Root endpoint", "GET", "", 200)
        
        # Test health endpoint
        self.run_test("Health check", "GET", "health", 200)

    def test_authentication_flow(self):
        """Test authentication with a mock Firebase token"""
        print("\n" + "="*50)
        print("TESTING AUTHENTICATION")
        print("="*50)
        
        # Note: For real testing, we would need a valid Firebase token
        # For now, we'll test the endpoint structure
        success, response = self.run_test(
            "Auth verification (without token)", 
            "POST", 
            "auth/verify", 
            401  # Expected to fail without token
        )
        
        # Test getting current user without token
        self.run_test(
            "Get current user (without token)", 
            "GET", 
            "auth/me", 
            401  # Expected to fail without token
        )

    def test_dashboard_endpoints(self):
        """Test dashboard endpoints (will fail without auth)"""
        print("\n" + "="*50)
        print("TESTING DASHBOARD ENDPOINTS")
        print("="*50)
        
        # These will fail without authentication, but we can test the endpoint structure
        self.run_test("Dashboard stats", "GET", "dashboard/stats", 401)
        self.run_test("Next event", "GET", "dashboard/next-event", 401)
        self.run_test("Recent activity", "GET", "dashboard/recent-activity", 401)

    def test_contact_endpoints(self):
        """Test contact CRUD endpoints (will fail without auth)"""
        print("\n" + "="*50)
        print("TESTING CONTACT ENDPOINTS")
        print("="*50)
        
        # Test get contacts
        self.run_test("Get contacts", "GET", "contacts", 401)
        
        # Test create contact
        contact_data = {
            "name": "Test Contact",
            "email": "test@example.com",
            "phone": "+1234567890",
            "notes": "Test contact for API testing"
        }
        self.run_test("Create contact", "POST", "contacts", 401, data=contact_data)

    def test_event_endpoints(self):
        """Test event CRUD endpoints (will fail without auth)"""
        print("\n" + "="*50)
        print("TESTING EVENT ENDPOINTS")
        print("="*50)
        
        # Test get events
        self.run_test("Get events", "GET", "events", 401)
        
        # Test create event
        event_data = {
            "title": "Test Event",
            "description": "Test event for API testing",
            "event_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "location": "Test Location",
            "reminder_intervals": [
                {"value": 1, "unit": "days"},
                {"value": 2, "unit": "hours"}
            ]
        }
        self.run_test("Create event", "POST", "events", 401, data=event_data)

    def test_notification_endpoints(self):
        """Test notification endpoints (will fail without auth)"""
        print("\n" + "="*50)
        print("TESTING NOTIFICATION ENDPOINTS")
        print("="*50)
        
        # Test get notifications
        self.run_test("Get notifications", "GET", "notifications", 401)
        self.run_test("Get pending notifications", "GET", "notifications?status=pending", 401)
        self.run_test("Get sent notifications", "GET", "notifications?status=sent", 401)

    def test_cors_and_options(self):
        """Test CORS configuration"""
        print("\n" + "="*50)
        print("TESTING CORS CONFIGURATION")
        print("="*50)
        
        try:
            # Test OPTIONS request
            response = requests.options(f"{self.base_url}/api/health", timeout=10)
            print(f"🔍 Testing CORS OPTIONS request...")
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            # Check for CORS headers
            cors_headers = [
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Methods',
                'Access-Control-Allow-Headers'
            ]
            
            for header in cors_headers:
                if header in response.headers:
                    print(f"✅ {header}: {response.headers[header]}")
                else:
                    print(f"❌ Missing CORS header: {header}")
                    
        except Exception as e:
            print(f"❌ CORS test failed: {str(e)}")

    def test_scheduler_status(self):
        """Check if the scheduler is running by looking for recent activity"""
        print("\n" + "="*50)
        print("TESTING SCHEDULER STATUS")
        print("="*50)
        
        print("📋 Scheduler status check:")
        print("   - APScheduler should be running in the background")
        print("   - Processing notifications every minute")
        print("   - Check backend logs for scheduler activity")
        print("   - Notifications with scheduled_at <= current time should be processed")

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Event Reminder System API Tests")
        print(f"📍 Base URL: {self.base_url}")
        print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Run all test suites
            self.test_health_check()
            self.test_authentication_flow()
            self.test_dashboard_endpoints()
            self.test_contact_endpoints()
            self.test_event_endpoints()
            self.test_notification_endpoints()
            self.test_cors_and_options()
            self.test_scheduler_status()
            
        except KeyboardInterrupt:
            print("\n⚠️ Tests interrupted by user")
        except Exception as e:
            print(f"\n💥 Unexpected error during testing: {str(e)}")
        
        # Print final results
        print("\n" + "="*60)
        print("📊 FINAL TEST RESULTS")
        print("="*60)
        print(f"✅ Tests passed: {self.tests_passed}")
        print(f"❌ Tests failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Total tests: {self.tests_run}")
        
        if self.tests_run > 0:
            success_rate = (self.tests_passed / self.tests_run) * 100
            print(f"🎯 Success rate: {success_rate:.1f}%")
        
        print("\n📝 NOTES:")
        print("   - Most tests expected to fail with 401 (authentication required)")
        print("   - This validates API endpoint structure and error handling")
        print("   - For full testing, valid Firebase authentication tokens are needed")
        print("   - Scheduler runs in background - check supervisor logs for activity")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = EventReminderAPITester()
    success = tester.run_all_tests()
    
    # Return appropriate exit code
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())