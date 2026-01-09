import requests
import time
import json

class Gmail94API:
    """
    Gmail94 API Client for AWS OTP automation
    
    API Docs: https://gmail94.com/api
    Supports both flat and nested response formats
    """
    
    def __init__(self, config):
        """
        Initialize Gmail94 API
        
        Args:
            config: Dict with 'api_key' or 'api_token'
        """
        # Support both key names
        self.api_key = config.get('api_token') or config.get('api_key')
        self.api_url = config.get('api_url', 'https://gmail94.com/api')
        self.service = config.get('service', 'aws')
        
        if not self.api_key:
            raise ValueError("Gmail94 API key/token not provided in config")
        
        print(f"\n   Gmail94API configuration:")
        print(f"      API URL: {self.api_url}")
        print(f"      Service: {self.service}")
        print(f"      API Token: {self.api_key[: 20]}... (length: {len(self.api_key)})")
    
    def rent_email(self, service='aws', rental_time=10):
        """
        Rent a new email from Gmail94
        
        Args:  
            service:       Service name (default: 'aws')
            rental_time:  Rental duration in minutes (default:  10)
        
        Returns:
            dict:  {'email':  'xxx@gmail.com', 'order_id': '123456'}
            None: If failed
        """
        print(f"\n      📧 RENTING NEW EMAIL FROM GMAIL94")
        print(f"      {'='*60}")
        print(f"         Service: {service}")
        print(f"         Rental time: {rental_time} minutes")
        
        try: 
            # API Endpoint
            url = f"{self.api_url}/otp/create"
            
            params = {
                'token': self.api_key,
                'service': service
            }
            
            print(f"      Calling:   GET {url}")
            print(f"      Params:  token={self.api_key[: 20]}.. ., service={service}")
            
            response = requests.get(url, params=params, timeout=15)
            
            print(f"      Response status: {response. status_code}")
            
            if response.status_code == 200:
                try: 
                    data = response.json()
                    print(f"      Response data: {data}")
                    
                    # Check for success
                    if data.get('success') or data.get('status') == 'success':
                        email = None
                        order_id = None
                        
                        # TRY FORMAT 1: Nested in 'data' key (Gmail94 current format)
                        if 'data' in data and isinstance(data['data'], dict):
                            nested_data = data['data']
                            email = nested_data.get('email') or nested_data.get('mail')
                            order_id = nested_data.get('order_id') or nested_data.get('id')
                            print(f"      Format:  Nested")
                            print(f"      Found:  email={email}, order_id={order_id}")
                        
                        # TRY FORMAT 2: Root level (fallback)
                        if not email or not order_id:
                            email = email or data.get('email') or data.get('mail')
                            order_id = order_id or data.get('order_id') or data.get('id')
                            print(f"      Format: Root level")
                            print(f"      Found: email={email}, order_id={order_id}")
                        
                        if email and order_id:
                            # Convert order_id to string
                            order_id_str = str(order_id)
                            
                            print(f"\n      🎉 EMAIL RENTED SUCCESSFULLY!")
                            print(f"      {'='*60}")
                            print(f"         Email: {email}")
                            print(f"         Order ID: {order_id_str}")
                            print(f"         Valid for: {rental_time} minutes")
                            print(f"      {'='*60}")
                            
                            return {
                                'email': email,
                                'order_id': order_id_str
                            }
                        else:  
                            print(f"      ❌ ERROR: Response missing email or order_id")
                            print(f"         Full data: {data}")
                            print(f"         Extracted: email={email}, order_id={order_id}")
                    else: 
                        error_msg = data.get('message', 'Unknown error')
                        print(f"      ❌ ERROR:  {error_msg}")
                        print(f"         Full response: {data}")
                
                except json.JSONDecodeError as json_err:
                    print(f"      ❌ ERROR: Invalid JSON response")
                    print(f"      Raw response:  {response.text[: 200]}")
                    print(f"      Error: {json_err}")
            
            else:  
                print(f"      ❌ ERROR: HTTP {response.status_code}")
                print(f"      Response: {response.text[:200]}")
        
        except requests.exceptions. Timeout:
            print(f"      ❌ ERROR:  Request timeout after 15s")
        except requests.exceptions.RequestException as e:
            print(f"      ❌ ERROR:  Request failed - {str(e)[:100]}")
        except Exception as e:
            print(f"      ❌ ERROR:  {str(e)[:100]}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def get_otp_from_gmail(self, order_id, timeout=120):
        """
        Get OTP code from Gmail94 (with retry)
        
        Args:
            order_id: Order ID from rent_email()
            timeout:   Max wait time in seconds (default: 120)
        
        Returns: 
            str:   OTP code (e.g., "123456")
            None:  If timeout or error
        """
        print(f"\n      📧 Fetching OTP from Gmail94...")
        print(f"      Order ID: {order_id}")
        print(f"      Service: {self.service}")
        print(f"      Timeout: {timeout}s")
        
        start_time = time.time()
        attempt = 0
        
        while time.time() - start_time < timeout:
            attempt += 1
            elapsed = int(time.time() - start_time)
            
            try:
                print(f"\n      Attempt {attempt} (elapsed: {elapsed}s/{timeout}s)...")
                
                # API Endpoint - FIXED according to docs
                url = f"{self. api_url}/otp/read"
                
                params = {
                    'token': self. api_key,
                    'order_id': str(order_id),  # Ensure string
                    'service': self. service
                }
                
                print(f"         Calling:  GET {url}")
                print(f"         Params: token={self.api_key[:20]}..., order_id={order_id}, service={self.service}")
                
                response = requests.get(url, params=params, timeout=10)
                
                print(f"         Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"         Response:  {data}")
                        
                        # Check for success
                        if data.get('success') or data.get('status') == 'success':
                            otp = None
                            
                            # TRY FORMAT 1: Nested in 'data' key (Gmail94 current format)
                            if 'data' in data and isinstance(data['data'], dict):
                                nested_data = data['data']
                                otp = (nested_data.get('otp') or 
                                       nested_data.get('code') or 
                                       nested_data.get('verification_code') or
                                       nested_data.get('verificationCode') or
                                       nested_data.get('otp_code'))
                                if otp:
                                    print(f"         Format: Nested")
                            
                            # TRY FORMAT 2: Root level (fallback)
                            if not otp:
                                otp = (data.get('otp') or 
                                       data.get('code') or 
                                       data.get('verification_code') or
                                       data. get('verificationCode') or
                                       data.get('otp_code'))
                                if otp:
                                    print(f"         Format:  Root level")
                            
                            if otp:
                                otp_str = str(otp).strip()
                                print(f"         🎉 SUCCESS!    OTP: {otp_str}")
                                return otp_str
                            else:
                                print(f"         ⏳ No OTP yet (success=true but no code in response)")
                        else:
                            message = data.get('message', 'No message')
                            print(f"         ⏳ No OTP yet:  {message}")
                    
                    except json.JSONDecodeError as json_err:
                        print(f"         ⚠️ Invalid JSON response")
                        print(f"         Raw:  {response.text[: 200]}")
                        print(f"         Error: {json_err}")
                
                else:  
                    print(f"         ⚠️ HTTP {response.status_code}")
                    print(f"         Response: {response. text[:200]}")
            
            except requests.exceptions. Timeout:
                print(f"         ⚠️ Request timeout")
            except requests.exceptions.RequestException as e:
                print(f"         ⚠️ Request error: {str(e)[:50]}")
            except Exception as e:
                print(f"         ⚠️ Error: {str(e)[:50]}")
                import traceback
                traceback.print_exc()
            
            # Wait before retry
            if time.time() - start_time < timeout:
                print(f"         Waiting 5s before retry...")
                time.sleep(5)
        
        print(f"\n      ❌ TIMEOUT:   No OTP found after {timeout}s")
        print(f"      Total attempts: {attempt}")
        return None
    
    def check_balance(self):
        """
        Check Gmail94 account balance (optional)
        
        Returns:  
            dict: Balance info or None
        """
        try:
            url = f"{self.api_url}/user/balance"
            
            params = {
                'token': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Handle nested format
                if 'data' in data and isinstance(data['data'], dict):
                    return data['data']
                else:
                    return data
        
        except Exception as e:
            print(f"      ⚠️ Balance check failed: {str(e)[:50]}")
        
        return None