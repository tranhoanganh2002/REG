import requests
from selenium import webdriver
from selenium. webdriver.chrome.options import Options
from selenium. webdriver.chrome.service import Service
import time
import os

class GPMManager:
    def __init__(self, api_url="http://127.0.0.1:19995/api/v3"):
        self.api_url = api_url
    
    def get_profiles(self, group=None, page=1, per_page=100):
        """Lấy danh sách profiles từ GPM"""
        try: 
            url = f"{self.api_url}/profiles"
            params = {
                'page': page,
                'per_page': per_page
            }
            if group:
                params['group'] = group
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    profiles = result.get('data', [])
                    print(f"Loaded {len(profiles)} profiles from GPM")
                    return profiles
                else:
                    print(f"API returned success=false: {result.get('message')}")
                    return []
            else:
                print(f"Failed to get profiles: {response.status_code}")
                return []
            
        except Exception as e: 
            print(f"Error getting profiles: {e}")
            return []
    
    def get_profile_by_name(self, profile_name):
        """Tìm profile theo tên"""
        try:
            profiles = self.get_profiles()
            
            if not profiles:
                print(f"   ❌ No profiles found in GPM")
                return None
            
            # Exact match
            for profile in profiles: 
                if profile.get('name') == profile_name:
                    profile_id = profile.get('id')
                    print(f"   ✅ Found profile '{profile_name}' -> ID: {profile_id}")
                    return profile
            
            # Case-insensitive match
            profile_name_lower = profile_name.lower()
            for profile in profiles:
                if profile.get('name', '').lower() == profile_name_lower:
                    profile_id = profile.get('id')
                    print(f"   ✅ Found profile '{profile. get('name')}' -> ID: {profile_id}")
                    return profile
            
            # Not found
            print(f"   ❌ Profile '{profile_name}' not found")
            return None
            
        except Exception as e:
            print(f"   ❌ Error:  {e}")
            return None
    
    def get_profile_id(self, profile_identifier):
        """Lấy profile ID từ name hoặc ID"""
        try:
            # Check if already a UUID
            if '-' in profile_identifier and len(profile_identifier) >= 32:
                parts = profile_identifier.split('-')
                if len(parts) == 5:
                    return profile_identifier
            
            # Search by name
            profile = self. get_profile_by_name(profile_identifier)
            if profile:
                return profile.get('id')
            
            return None
            
        except Exception as e:
            print(f"   Error:  {e}")
            return None
    
    def start_profile(self, profile_identifier):
        """Mở profile và connect bằng GPM driver"""
        try:
            print(f"\n{'='*70}")
            print(f"STARTING PROFILE")
            print(f"{'='*70}")
            print(f"Profile:  {profile_identifier}")
            
            # Get profile ID
            profile_id = self.get_profile_id(profile_identifier)
            
            if not profile_id: 
                print(f"❌ Cannot find profile")
                return None
            
            print(f"Profile ID: {profile_id}")
            
            # Call start API
            url = f"{self.api_url}/profiles/start/{profile_id}"
            print(f"API URL: {url}")
            print(f"Calling API...")
            
            try:
                response = requests.get(url, timeout=60)
                
                print(f"Response status: {response.status_code}")
                
                if response. status_code != 200:
                    print(f"❌ HTTP error: {response.status_code}")
                    print(f"Response: {response. text[: 500]}")
                    return None
                
                # Parse JSON response
                try:
                    result = response. json()
                    print(f"✅ Response received")
                except ValueError as json_err:
                    print(f"❌ Invalid JSON response: {json_err}")
                    print(f"Response text: {response.text[:500]}")
                    return None
                
                # Check outer success
                if not result.get('success'):
                    print(f"❌ API returned success=false")
                    print(f"Message: {result.get('message', 'No message')}")
                    return None
                
                # Get data
                data = result.get('data', {})
                
                if not data:
                    print(f"❌ No data in response")
                    return None
                
                # Extract fields
                profile_id_response = data.get('profile_id')
                browser_location = data.get('browser_location')
                remote_debugging_address = data.get('remote_debugging_address')
                driver_path = data.get('driver_path')
                
                print(f"\n{'='*70}")
                print(f"PROFILE START RESPONSE")
                print(f"{'='*70}")
                print(f"Profile ID: {profile_id_response}")
                print(f"Browser:  {browser_location}")
                print(f"Remote debugging: {remote_debugging_address}")
                print(f"Driver path: {driver_path}")
                print(f"{'='*70}\n")
                
                # Check required fields
                if not remote_debugging_address: 
                    print(f"❌ No remote_debugging_address in response")
                    return None
                
                if not driver_path:
                    print(f"⚠️ No driver_path in response, will use system driver")
                
                print(f"✅ Profile started successfully!")
                print(f"Waiting 10 seconds for browser to fully initialize...")
                time.sleep(10)
                
                # Connect to browser using GPM driver
                print(f"Connecting to browser...")
                driver = self.connect_to_browser(remote_debugging_address, driver_path)
                
                if driver:
                    print(f"✅ Successfully connected to browser!")
                    print(f"{'='*70}\n")
                    return driver
                else:
                    print(f"❌ Failed to connect to browser")
                    return None
                
            except requests.exceptions. Timeout:
                print(f"❌ Request timeout (60 seconds)")
                return None
                
            except requests.exceptions.ConnectionError as conn_err:
                print(f"❌ Connection error: {conn_err}")
                print(f"Is GPM Browser running? ")
                return None
                
            except requests.exceptions.RequestException as req_err:
                print(f"❌ Request error: {req_err}")
                return None
            
        except Exception as e: 
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def connect_to_browser(self, remote_debugging_address, driver_path=None):
        """Connect to browser - SIMPLIFIED OPTIONS"""
        try: 
            print(f"   Setting up connection...")
            print(f"   Remote debugging: {remote_debugging_address}")
            
            # MINIMAL OPTIONS - Only debuggerAddress!
            options = Options()
            options.add_experimental_option("debuggerAddress", remote_debugging_address)
            
            driver = None
            
            # Method 1: Try GPM driver
            if driver_path and os. path.exists(driver_path):
                print(f"   [Method 1] Trying GPM driver...")
                print(f"   Driver:  {driver_path}")
                try:
                    service = Service(executable_path=driver_path)
                    driver = webdriver. Chrome(service=service, options=options)
                    
                    # Test connection
                    current_url = driver.current_url
                    page_title = driver.title
                    
                    print(f"   ✅ Connected via GPM driver!")
                    print(f"   URL: {current_url}")
                    print(f"   Title: {page_title[: 50]}")
                    return driver
                    
                except Exception as e1:
                    print(f"   ⚠️ GPM driver failed:")
                    print(f"      Error: {str(e1)[:150]}")
                    driver = None
            else:
                if driver_path:
                    print(f"   ⚠️ GPM driver not found:  {driver_path}")
                else:
                    print(f"   ℹ️ No driver_path provided")
            
            # Method 2: Try webdriver-manager
            if not driver:
                print(f"   [Method 2] Trying webdriver-manager...")
                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    from selenium.webdriver.chrome.service import Service as ChromeService
                    
                    print(f"   Installing/updating ChromeDriver...")
                    service = ChromeService(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                    
                    # Test connection
                    current_url = driver.current_url
                    page_title = driver.title
                    
                    print(f"   ✅ Connected via webdriver-manager!")
                    print(f"   URL: {current_url}")
                    print(f"   Title: {page_title[: 50]}")
                    return driver
                    
                except ImportError:
                    print(f"   ⚠️ webdriver-manager not installed")
                    print(f"   Install with: pip install webdriver-manager")
                except Exception as e2:
                    print(f"   ⚠️ webdriver-manager failed:")
                    print(f"      Error: {str(e2)[:150]}")
                    driver = None
            
            # Method 3: Try system ChromeDriver
            if not driver:
                print(f"   [Method 3] Trying system ChromeDriver...")
                try:
                    driver = webdriver.Chrome(options=options)
                    
                    # Test connection
                    current_url = driver.current_url
                    page_title = driver.title
                    
                    print(f"   ✅ Connected via system driver!")
                    print(f"   URL: {current_url}")
                    print(f"   Title: {page_title[:50]}")
                    return driver
                    
                except Exception as e3:
                    print(f"   ❌ System driver failed:")
                    print(f"      Error:  {str(e3)[:150]}")
                    driver = None
            
            # All methods failed
            if not driver:
                print(f"\n   {'='*70}")
                print(f"   ❌ ALL CONNECTION METHODS FAILED!")
                print(f"   {'='*70}")
                print(f"\n   Possible issues:")
                print(f"   1. ChromeDriver version doesn't match browser version")
                print(f"   2. Browser not actually running on {remote_debugging_address}")
                print(f"   3. Port {remote_debugging_address} is blocked or in use")
                print(f"\n   Troubleshooting steps:")
                print(f"   1. Check browser is running:")
                print(f"      Open in browser: http://{remote_debugging_address}")
                print(f"\n   2. Check Chrome version in GPM browser:")
                print(f"      Navigate to: chrome://version")
                print(f"\n   3. Download matching ChromeDriver:")
                print(f"      https://chromedriver.chromium.org/downloads")
                print(f"\n   4. Or install webdriver-manager:")
                print(f"      pip install webdriver-manager")
                print(f"   {'='*70}\n")
            
            return driver
            
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def stop_profile(self, profile_identifier):
        """Đóng profile"""
        try: 
            print(f"\nStopping profile: {profile_identifier}")
            
            profile_id = self.get_profile_id(profile_identifier)
            
            if not profile_id:
                print(f"   ❌ Cannot find profile ID")
                return False
            
            url = f"{self.api_url}/profiles/stop/{profile_id}"
            
            try:
                response = requests.get(url, timeout=30)
                
                if response. status_code == 200:
                    result = response.json()
                    
                    if result.get('success'):
                        print(f"   ✅ Profile stopped")
                        return True
                    else:
                        print(f"   ⚠️ API returned success=false: {result.get('message')}")
                        return False
                else:
                    print(f"   ⚠️ HTTP error: {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"   ⚠️ Error stopping profile: {e}")
                return False
            
        except Exception as e: 
            print(f"   ❌ Error:  {e}")
            return False