import requests
import time
import logging
import os
from selenium import webdriver
from selenium. webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class GPMBrowser:
    def __init__(self, gpm_api_url="http://127.0.0.1:19995/api/v3"):
        """
        Initialize GPM Browser Manager
        
        Args:
            gpm_api_url: GPM API endpoint (default: http://127.0.0.1:19995/api/v3)
        """
        self.api_url = gpm_api_url
        logging.info(f"   GPM API URL: {self.api_url}")
    
    def get_all_profiles(self):
        """
        Lấy danh sách tất cả profiles
        
        API:  GET /api/v3/profiles
        
        Returns:
            list: Danh sách profiles hoặc []
        """
        try: 
            url = f"{self.api_url}/profiles"
            
            logging.info(f"      Getting profiles list from: {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    profiles = result.get('data', [])
                    logging. info(f"      ✅ Found {len(profiles)} profiles")
                    return profiles
                else:
                    logging.error(f"      ❌ API returned success=false:  {result.get('message')}")
                    return []
            else:
                logging.error(f"      ❌ HTTP error: {response.status_code}")
                return []
        
        except Exception as e:
            logging.error(f"      ❌ Error getting profiles: {e}")
            return []
    
    def get_profile_id_by_name(self, profile_name):
        """
        Tìm profile ID theo tên
        
        Args:
            profile_name:  Tên profile
        
        Returns:
            str: Profile ID hoặc None
        """
        try:
            profiles = self.get_all_profiles()
            
            if not profiles:
                logging.error(f"      ❌ No profiles found in GPM")
                return None
            
            # Tìm profile theo tên (exact match)
            for profile in profiles:
                if profile.get('name') == profile_name:
                    profile_id = profile.get('id')
                    logging.info(f"      ✅ Found '{profile_name}' → ID: {profile_id}")
                    return profile_id
            
            # Tìm profile theo tên (case-insensitive)
            profile_name_lower = profile_name.lower()
            for profile in profiles: 
                if profile.get('name', '').lower() == profile_name_lower:
                    profile_id = profile.get('id')
                    logging.info(f"      ✅ Found '{profile. get('name')}' → ID: {profile_id}")
                    return profile_id
            
            logging.error(f"      ❌ Profile '{profile_name}' not found")
            logging.info(f"      Available profiles:")
            for profile in profiles[: 5]:  # Show first 5
                logging.info(f"         - {profile.get('name')}")
            
            return None
        
        except Exception as e: 
            logging.error(f"      ❌ Error:  {e}")
            return None
    
    def start_profile(self, profile_identifier):
        """
        Khởi động profile
        
        API: POST /api/v3/profiles/start/{id}
        
        Args: 
            profile_identifier: Profile name hoặc ID
        
        Returns:
            WebDriver instance hoặc None
        """
        try:
            logging.info(f"      Starting GPM profile: {profile_identifier}")
            
            # Xác định profile ID
            profile_id = profile_identifier
            
            # Nếu không phải UUID → tìm theo name
            if '-' not in profile_identifier or len(profile_identifier) < 30:
                logging.info(f"      Looking up profile ID by name...")
                profile_id = self. get_profile_id_by_name(profile_identifier)
                
                if not profile_id: 
                    return None
            
            logging.info(f"      Profile ID: {profile_id}")
            
            # Gọi API start theo docs:  POST /api/v3/profiles/start/{id}
            url = f"{self.api_url}/profiles/start/{profile_id}"
            
            logging.info(f"      Calling:  POST {url}")
            
            response = requests.post(url, json={}, timeout=60)
            
            logging.info(f"      Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                logging.info(f"      Response: {result}")
                
                if result.get('success'):
                    data = result.get('data', {})
                    
                    # Lấy thông tin kết nối
                    remote_debugging = data.get('remote_debugging_address')
                    debug_port = None
                    driver_path = data.get('driver_path')
                    
                    # Parse debug port
                    if remote_debugging:
                        logging.info(f"      Remote debugging: {remote_debugging}")
                        
                        # Format: 127.0.0.1:PORT
                        if ':' in remote_debugging:
                            debug_port = remote_debugging.split(':')[-1]
                        else:
                            debug_port = remote_debugging
                    
                    if not debug_port:
                        logging.error(f"      ❌ No debug port in response")
                        logging.error(f"         Data keys: {list(data.keys())}")
                        return None
                    
                    logging.info(f"      ✅ Profile started!")
                    logging.info(f"         Debug port: {debug_port}")
                    logging.info(f"         Driver path: {driver_path}")
                    
                    # Đợi browser khởi động hoàn toàn
                    time.sleep(3)
                    
                    # Kết nối tới browser
                    return self._connect_to_browser(debug_port, driver_path)
                else:
                    logging.error(f"      ❌ API returned success=false")
                    logging.error(f"         Message: {result.get('message')}")
                    return None
            else:
                logging.error(f"      ❌ HTTP error: {response.status_code}")
                logging.error(f"         Response: {response.text[: 300]}")
                return None
        
        except Exception as e: 
            logging.error(f"      ❌ Error:  {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _connect_to_browser(self, debug_port, driver_path=None):
        """
        Kết nối tới browser qua Chrome DevTools Protocol
        
        SIMPLIFIED - CHỈ DÙNG debuggerAddress, KHÔNG THÊM OPTIONS KHÁC! 
        
        Args:
            debug_port: Chrome debugging port
            driver_path:  Đường dẫn tới chromedriver (optional)
        
        Returns: 
            WebDriver instance
        """
        try:
            logging. info(f"      Connecting to browser on port {debug_port}...")
            
            # CRITICAL: CHỈ DÙNG debuggerAddress, KHÔNG THÊM GÌ KHÁC!
            # Các options khác có thể gây lỗi "cannot parse capability"
            
            driver = None
            
            # === METHOD 1: GPM Driver từ response ===
            if driver_path: 
                try:
                    # Check file exists
                    if not os. path.exists(driver_path):
                        logging.warning(f"      Driver not found: {driver_path}")
                        
                        # Try fix path (GPM sometimes returns wrong slashes)
                        fixed_paths = [
                            driver_path.replace('\\', '/'),
                            driver_path.replace('/', '\\'),
                            driver_path.replace('chrome.exe\\', ''),  # Remove chrome.exe from path
                        ]
                        
                        for fixed_path in fixed_paths: 
                            if os.path.exists(fixed_path):
                                driver_path = fixed_path
                                logging.info(f"      ✅ Found at: {fixed_path}")
                                break
                    
                    if os.path.exists(driver_path):
                        logging.info(f"      [Method 1] Trying GPM driver...")
                        logging.info(f"         Path: {driver_path}")
                        
                        # MINIMAL OPTIONS
                        options = Options()
                        options. add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
                        
                        service = Service(executable_path=driver_path)
                        driver = webdriver.Chrome(service=service, options=options)
                        
                        # Test connection
                        _ = driver.current_url
                        
                        logging.info(f"      ✅ Connected via GPM driver!")
                        
                        # Set timeouts
                        driver.set_page_load_timeout(60)
                        driver.implicitly_wait(10)
                        
                        return driver
                
                except Exception as e1:
                    logging.warning(f"      Method 1 failed: {str(e1)[:150]}")
                    if driver:
                        try:
                            driver.quit()
                        except:
                            pass
                    driver = None
            
            # === METHOD 2: webdriver-manager ===
            if not driver:
                try:
                    logging.info(f"      [Method 2] Trying webdriver-manager...")
                    
                    from webdriver_manager. chrome import ChromeDriverManager
                    from selenium.webdriver.chrome.service import Service as ChromeService
                    
                    # MINIMAL OPTIONS
                    options = Options()
                    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
                    
                    # Auto-download matching ChromeDriver
                    logging.info(f"         Installing/updating ChromeDriver...")
                    service = ChromeService(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                    
                    # Test connection
                    _ = driver. current_url
                    
                    logging.info(f"      ✅ Connected via webdriver-manager!")
                    
                    # Set timeouts
                    driver.set_page_load_timeout(60)
                    driver.implicitly_wait(10)
                    
                    return driver
                
                except ImportError:
                    logging.warning(f"      webdriver-manager not installed")
                    logging.info(f"         Install:  pip install webdriver-manager")
                except Exception as e2:
                    logging.warning(f"      Method 2 failed: {str(e2)[:150]}")
                    if driver: 
                        try:
                            driver.quit()
                        except:
                            pass
                    driver = None
            
            # === METHOD 3: System ChromeDriver ===
            if not driver:
                try:
                    logging.info(f"      [Method 3] Trying system chromedriver...")
                    
                    # MINIMAL OPTIONS
                    options = Options()
                    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
                    
                    driver = webdriver.Chrome(options=options)
                    
                    # Test connection
                    _ = driver.current_url
                    
                    logging.info(f"      ✅ Connected via system driver!")
                    
                    # Set timeouts
                    driver. set_page_load_timeout(60)
                    driver.implicitly_wait(10)
                    
                    return driver
                
                except Exception as e3:
                    logging.error(f"      Method 3 failed: {str(e3)[:150]}")
                    if driver:
                        try:
                            driver.quit()
                        except:
                            pass
                    driver = None
            
            # === ALL METHODS FAILED ===
            if not driver:
                logging.error(f"\n      {'='*60}")
                logging.error(f"      ❌ ALL CONNECTION METHODS FAILED!")
                logging.error(f"      {'='*60}")
                logging.error(f"\n      Troubleshooting:")
                logging. error(f"      1. Browser is running on port {debug_port}")
                logging.error(f"      2. Try manual test:")
                logging.error(f"         Open:  http://127.0.0.1:{debug_port}")
                logging.error(f"\n      3. ChromeDriver version mismatch")
                logging. error(f"         Solution:")
                logging.error(f"         pip install --upgrade webdriver-manager")
                logging.error(f"         pip install --upgrade selenium")
                logging.error(f"\n      4. Or download ChromeDriver manually:")
                logging.error(f"         https://chromedriver.chromium.org/downloads")
                logging. error(f"      {'='*60}\n")
            
            return driver
        
        except Exception as e: 
            logging.error(f"      ❌ Connection error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def stop_profile(self, profile_identifier):
        """
        Dừng profile
        
        API: POST /api/v3/profiles/stop/{id}
        
        Args:
            profile_identifier: Profile name hoặc ID
        """
        try:
            logging. info(f"      Stopping profile: {profile_identifier}")
            
            # Get profile ID
            profile_id = profile_identifier
            
            if '-' not in profile_identifier or len(profile_identifier) < 30:
                profile_id = self.get_profile_id_by_name(profile_identifier)
                
                if not profile_id:
                    logging.warning(f"      ⚠️ Cannot find profile ID")
                    return
            
            # Call API stop
            url = f"{self.api_url}/profiles/stop/{profile_id}"
            
            response = requests.post(url, json={}, timeout=10)
            
            if response. status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    logging.info(f"      ✅ Profile stopped")
                else:
                    logging.warning(f"      ⚠️ Stop failed: {result.get('message')}")
            else:
                logging.warning(f"      ⚠️ HTTP error: {response.status_code}")
        
        except Exception as e: 
            logging.warning(f"      ⚠️ Error:  {e}")