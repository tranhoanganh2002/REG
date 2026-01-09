"""
GPM Browser Manager
Supports both Selenium (legacy) and Playwright
"""

import requests
import logging
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


class GPMBrowser:
    """
    Manage GPM/GoLogin browser profiles
    Works with both Selenium and Playwright
    """
    
    def __init__(self, gpm_api_url='http://127.0.0.1:19995/api/v3', api_token=None):
        """
        Initialize GPM Browser Manager
        
        Args: 
            gpm_api_url:  GPM API endpoint (default: localhost)
            api_token: Optional API token for authentication
        """
        self.gpm_api_url = gpm_api_url
        self.api_token = api_token
        self.active_profiles = {}
        
        logging.debug(f"GPM Browser initialized with API:  {gpm_api_url}")
    
    # ============================================================
    # SELENIUM METHODS (LEGACY - KEEP FOR BACKWARD COMPATIBILITY)
    # ============================================================
    
    def start_profile(self, profile_id):
        """
        Start GPM profile with Selenium (legacy method)
        
        Args: 
            profile_id: Profile name or ID
            
        Returns: 
            WebDriver object or None
        """
        try:
            logging.info(f"   Starting GPM profile: {profile_id}")
            
            # Call GPM API to start profile
            response = self._call_api('POST', '/profiles/start', {
                'profile_id': profile_id
            })
            
            if not response:
                logging.error(f"   Failed to start profile via API")
                return None
            
            # Get WebDriver connection info
            debugger_address = response.get('debugger_address')
            webdriver_path = response.get('webdriver_path')
            
            if not debugger_address: 
                logging.error(f"   No debugger address from GPM")
                return None
            
            # Connect to existing browser
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", debugger_address)
            
            # Create WebDriver
            if webdriver_path and os.path.exists(webdriver_path):
                service = Service(webdriver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                driver = webdriver.Chrome(options=chrome_options)
            
            # Store active profile
            self.active_profiles[profile_id] = {
                'driver': driver,
                'debugger_address': debugger_address
            }
            
            logging. info(f"   ✅ Profile started successfully")
            return driver
            
        except Exception as e:
            logging.error(f"   Error starting profile: {str(e)}")
            return None
    
    def stop_profile(self, profile_id):
        """
        Stop GPM profile (Selenium)
        
        Args:
            profile_id: Profile name or ID
        """
        try:
            if profile_id in self.active_profiles:
                profile_data = self.active_profiles[profile_id]
                
                # Close driver
                try:
                    driver = profile_data. get('driver')
                    if driver:
                        driver.quit()
                except:
                    pass
                
                # Remove from active
                del self.active_profiles[profile_id]
                
                logging.info(f"   Profile {profile_id} stopped")
            
            # Call GPM API to stop profile
            self._call_api('POST', '/profiles/stop', {
                'profile_id': profile_id
            })
            
        except Exception as e:
            logging.warning(f"   Error stopping profile: {str(e)}")
    
    # ============================================================
    # PLAYWRIGHT METHODS (NEW)
    # ============================================================
    
    def get_profile_info(self, profile_id):
        """
        Get profile information for Playwright
        Returns profile path without starting Selenium
        
        Args: 
            profile_id: Profile name or ID
            
        Returns: 
            dict: {'id', 'name', 'profile_path', 'proxy'} or None
        """
        try:
            logging.info(f"   Looking for profile: {profile_id}")
            
            # ========================================================
            # METHOD 1: Search local file system
            # ========================================================
            username = os.getenv('USERNAME') or os.getenv('USER') or 'user'
            
            possible_paths = [
                # GoLogin standard paths
                f"C:\\Users\\{username}\\.gologin\\profiles\\{profile_id}",
                f"C:\\Users\\{username}\\AppData\\Local\\GoLogin\\profiles\\{profile_id}",
                f"C:\\Users\\{username}\\AppData\\Roaming\\GoLogin\\profiles\\{profile_id}",
                
                # GPM Browser paths
                f"C:\\Users\\{username}\\AppData\\Local\\GPM\\profiles\\{profile_id}",
                f"C:\\Users\\{username}\\AppData\\Local\\GPM Browser\\profiles\\{profile_id}",
                f"C:\\Users\\{username}\\Documents\\GPM\\profiles\\{profile_id}",
                
                # Additional GoLogin paths
                f"C:\\Users\\{username}\\.gologin\\browser\\profiles\\{profile_id}",
                
                # Linux/Mac paths (if running on WSL/Mac)
                f"/home/{username}/.gologin/profiles/{profile_id}",
                f"/Users/{username}/.gologin/profiles/{profile_id}",
            ]
            
            # Check each path
            for path in possible_paths:
                if os.path.exists(path):
                    logging.info(f"   ✅ Found profile at: {path}")
                    
                    return {
                        'id':  profile_id,
                        'name': profile_id,
                        'profile_path': path,
                        'proxy': None,  # Will be loaded from profile data
                    }
            
            # ========================================================
            # METHOD 2: Query GPM API
            # ========================================================
            logging.info(f"   Profile not found locally, checking GPM API...")
            
            try:
                # Get all profiles from API
                response = self._call_api('GET', '/profiles')
                
                if response:
                    profiles = response.get('data', []) or response.get('profiles', [])
                    
                    # Search for matching profile
                    for profile in profiles:
                        profile_name = profile.get('name', '')
                        profile_api_id = profile.get('id', '')
                        
                        # Match by name or ID
                        if profile_name == profile_id or profile_api_id == profile_id:
                            logging.info(f"   ✅ Found profile via API")
                            
                            # Get profile path from API response
                            profile_path = (
                                profile.get('profilePath') or 
                                profile. get('profile_path') or
                                profile.get('path')
                            )
                            
                            # If no path in API, construct default
                            if not profile_path:
                                profile_path = f"C:\\Users\\{username}\\AppData\\Local\\GPM\\profiles\\{profile_api_id}"
                            
                            # Get proxy info
                            proxy_data = profile.get('proxy', {})
                            proxy_string = None
                            
                            if proxy_data:
                                proxy_host = proxy_data.get('host')
                                proxy_port = proxy_data.get('port')
                                proxy_user = proxy_data.get('username')
                                proxy_pass = proxy_data.get('password')
                                
                                if proxy_host and proxy_port: 
                                    if proxy_user and proxy_pass: 
                                        proxy_string = f"{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
                                    else:
                                        proxy_string = f"{proxy_host}:{proxy_port}"
                            
                            return {
                                'id': profile_api_id,
                                'name': profile_name,
                                'profile_path': profile_path,
                                'proxy': proxy_string,
                            }
                
            except Exception as api_error: 
                logging.warning(f"   GPM API error: {str(api_error)}")
            
            # ========================================================
            # METHOD 3: Create default profile path
            # ========================================================
            logging.warning(f"   ⚠️ Profile '{profile_id}' not found")
            logging.info(f"   Creating default profile path...")
            
            # Use relative path for new profiles
            default_path = os.path.abspath(f"./profiles/{profile_id}")
            os.makedirs(default_path, exist_ok=True)
            
            logging.info(f"   Created:  {default_path}")
            
            return {
                'id':  profile_id,
                'name': profile_id,
                'profile_path': default_path,
                'proxy': None,
            }
            
        except Exception as e:
            logging.error(f"   ❌ Error getting profile info:  {str(e)}")
            
            # Last resort fallback
            fallback_path = os.path.abspath(f"./profiles/{profile_id}")
            os.makedirs(fallback_path, exist_ok=True)
            
            return {
                'id': profile_id,
                'name': profile_id,
                'profile_path':  fallback_path,
                'proxy': None,
            }
    
    # ============================================================
    # HELPER METHODS
    # ============================================================
    
    def _call_api(self, method, endpoint, data=None):
        """
        Call GPM API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/profiles')
            data: Request data (for POST)
            
        Returns:
            dict: API response or None
        """
        try: 
            url = f"{self.gpm_api_url}{endpoint}"
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            if self.api_token:
                headers['Authorization'] = f'Bearer {self.api_token}'
            
            # Make request
            if method. upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            else:
                logging.error(f"Unsupported HTTP method: {method}")
                return None
            
            # Check response
            if response.status_code == 200:
                return response. json()
            else:
                logging.debug(f"API returned status {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            logging.debug(f"Cannot connect to GPM API at {self.gpm_api_url}")
            return None
        except requests.exceptions.Timeout:
            logging.debug(f"GPM API timeout")
            return None
        except Exception as e:
            logging.debug(f"API call error: {str(e)}")
            return None
    
    def list_profiles(self):
        """
        Get list of all profiles from GPM
        
        Returns:
            list: List of profile dicts
        """
        try: 
            response = self._call_api('GET', '/profiles')
            
            if response:
                profiles = response.get('data', []) or response.get('profiles', [])
                
                logging.info(f"Found {len(profiles)} profiles in GPM")
                
                for profile in profiles:
                    name = profile.get('name', 'N/A')
                    profile_id = profile.get('id', 'N/A')
                    logging.info(f"   - {name} (ID: {profile_id})")
                
                return profiles
            else:
                logging.warning("No profiles found or API not available")
                return []
                
        except Exception as e:
            logging.error(f"Error listing profiles: {str(e)}")
            return []
    
    def cleanup(self):
        """Close all active profiles"""
        try:
            for profile_id in list(self.active_profiles. keys()):
                self.stop_profile(profile_id)
            
            logging.info("All profiles cleaned up")
            
        except Exception as e:
            logging.warning(f"Error during cleanup: {str(e)}")


# ============================================================
# TEST CODE (Optional)
# ============================================================

if __name__ == "__main__": 
    """Test GPM Browser"""
    logging.basicConfig(level=logging. INFO)
    
    gpm = GPMBrowser()
    
    # Test listing profiles
    print("\n=== Testing GPM Browser ===")
    profiles = gpm.list_profiles()
    
    if profiles:
        print(f"\n✅ Found {len(profiles)} profiles")
        
        # Test get_profile_info
        test_profile = profiles[0]. get('name')
        print(f"\nTesting get_profile_info for:  {test_profile}")
        
        info = gpm.get_profile_info(test_profile)
        if info:
            print(f"✅ Profile info:")
            print(f"   ID: {info['id']}")
            print(f"   Name: {info['name']}")
            print(f"   Path: {info['profile_path']}")
            print(f"   Proxy: {info['proxy']}")
    else:
        print("⚠️ No profiles found in GPM")
        print("Testing with default profile...")
        
        info = gpm.get_profile_info("TestProfile")
        if info:
            print(f"✅ Created default profile:")
            print(f"   Path: {info['profile_path']}")