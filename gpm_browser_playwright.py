import requests
import logging
import time

class GPMBrowserPlaywright: 
    """
    GPM Browser Manager for Playwright
    Manages profiles without Selenium dependency
    """
    
    def __init__(self, gpm_api_url='http://127.0.0.1:19995/api/v3', api_token=None):
        self.gpm_api_url = gpm_api_url
        self. api_token = api_token
        self.active_profiles = {}
    
    def get_profile_info(self, profile_id):
        """Get profile information from GPM"""
        try: 
            # Try to get profile by name
            url = f"{self.gpm_api_url}/profiles"
            
            headers = {}
            if self.api_token:
                headers['Authorization'] = f'Bearer {self.api_token}'
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                profiles = response.json()
                
                # Search for profile by name or ID
                for profile in profiles: 
                    if (profile.get('name') == profile_id or 
                        profile.get('id') == profile_id):
                        
                        # Get profile path
                        profile_path = profile.get('profile_path') or profile.get('profilePath')
                        
                        return {
                            'id': profile.get('id'),
                            'name': profile.get('name'),
                            'profile_path': profile_path or f"./gpm_profiles/{profile_id}",
                            'proxy': profile.get('proxy'),
                        }
                
                logging.warning(f"   Profile '{profile_id}' not found in GPM")
                return None
            else:
                logging. error(f"   GPM API error: {response.status_code}")
                return None
                
        except Exception as e: 
            logging.error(f"   Error getting profile info: {str(e)}")
            return None
    
    def start_profile(self, profile_id):
        """
        Start GPM profile (for Playwright, just return profile info)
        Playwright will manage the browser itself
        """
        try: 
            logging.info(f"   Getting profile info for:  {profile_id}")
            
            profile_info = self.get_profile_info(profile_id)
            
            if not profile_info:
                logging.error(f"   Profile '{profile_id}' not found")
                return None
            
            # Store profile info
            self.active_profiles[profile_id] = profile_info
            
            logging.info(f"   ✅ Profile ready: {profile_info['name']}")
            
            return profile_info
            
        except Exception as e:
            logging.error(f"   Error starting profile: {str(e)}")
            return None
    
    def stop_profile(self, profile_id):
        """Stop profile (cleanup)"""
        try:
            if profile_id in self.active_profiles:
                del self. active_profiles[profile_id]
                logging.info(f"   Profile {profile_id} stopped")
        except Exception as e:
            logging.warning(f"   Error stopping profile: {str(e)}")