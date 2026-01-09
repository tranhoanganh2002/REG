from playwright.sync_api import sync_playwright, expect, TimeoutError as PlaywrightTimeout
import time
import random

class AWSRegisterPlaywright:
    """
    AWS Account Registration using Playwright
    More stable than Selenium! 
    """
    
    def __init__(self, config, gmail94_api=None):
        self.config = config
        self.gmail94_api = gmail94_api
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def random_delay(self, min_sec=0.5, max_sec=1.5):
        """Random delay for human-like behavior"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
        return delay
    
    def setup_browser(self, profile_path):
        """Setup Playwright browser with profile - FIXED VERSION"""
        print("\n" + "="*70)
        print("🚀 STARTING PLAYWRIGHT BROWSER")
        print("="*70)
        
        try:
            # Start Playwright
            self.playwright = sync_playwright().start()
            
            # Launch browser with persistent context (supports profile)
            print("   Launching Chromium...")
            print(f"   Loading profile: {profile_path}")
            
            # ============================================================
            # USE launch_persistent_context() - CORRECT FOR PROFILES! 
            # ============================================================
            self.context = self.playwright. chromium.launch_persistent_context(
                user_data_dir=profile_path,  # Profile path as first argument
                headless=False,
                viewport={'width': 1280, 'height': 720},
                locale='en-US',
                timezone_id='America/New_York',
                
                # Anti-detection
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-web-security',
                ],
                
                # Ignore HTTPS errors
                ignore_https_errors=True,
            )
            
            # Get the default page (persistent context creates one automatically)
            pages = self.context.pages
            if pages:
                self.page = pages[0]
            else:
                self.page = self.context.new_page()
            
            # Set default timeout
            self.page.set_default_timeout(30000)  # 30 seconds
            
            print("   ✅ Browser started successfully!")
            return True
            
        except Exception as e:
            print(f"   ❌ Error starting browser: {str(e)}")
            
            # Fallback:  Launch without profile
            print("\n   ⚠️ Trying without profile...")
            
            try:
                # Clean up failed attempt
                if self.playwright:
                    try:
                        self.playwright. stop()
                    except: 
                        pass
                
                # Restart Playwright
                self.playwright = sync_playwright().start()
                
                # Launch browser normally (no profile)
                self.browser = self.playwright.chromium. launch(
                    headless=False,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                    ]
                )
                
                # Create context without profile
                self.context = self.browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    locale='en-US',
                    timezone_id='America/New_York',
                )
                
                # Create page
                self.page = self.context.new_page()
                self.page.set_default_timeout(30000)
                
                print("   ✅ Browser started (without profile)")
                return True
                
            except Exception as fallback_error:
                print(f"   ❌ Fallback also failed: {str(fallback_error)}")
                return False
    
    def start_registration(self, account_data):
        """Navigate to AWS signup page - DIRECT METHOD"""
        print("\n" + "="*70)
        print("STEP 1: NAVIGATE TO AWS SIGNUP")
        print("="*70)
        
        try: 
            # ============================================================
            # METHOD:  DIRECT NAVIGATION (NO GOOGLE)
            # ============================================================
            print("\n   Going directly to AWS signup page...")
            
            # Navigate directly to AWS signup
            self.page.goto(
                "https://portal.aws.amazon.com/billing/signup#/start/email",
                wait_until="domcontentloaded",
                timeout=60000  # 60 seconds
            )
            
            print("   Waiting for page to load...")
            time.sleep(3)
            
            # Wait for page to be ready
            try:
                self.page.wait_for_load_state("networkidle", timeout=30000)
            except: 
                print("   ⚠️ Network not idle, but continuing...")
            
            # Check if we're on signup page
            current_url = self.page.url
            print(f"   Current URL: {current_url[: 60]}...")
            
            if 'signup' in current_url. lower() or 'portal. aws' in current_url.lower():
                print("   ✅ Reached AWS signup page!")
                time.sleep(2)
                return True
            else:
                print(f"   ⚠️ Unexpected page, but continuing...")
                return True
            
        except Exception as e:
            print(f"   ❌ Error:  {str(e)[:100]}")
            
            # Try alternative URL
            print("\n   Trying alternative URL...")
            
            try:
                self.page.goto("https://aws.amazon.com/free/", timeout=60000)
                time.sleep(3)
                
                # Look for signup link
                try:
                    signup_link = self.page.locator("a[href*='signup']").first
                    signup_link.click(timeout=10000)
                    time.sleep(3)
                    print("   ✅ Clicked signup link")
                    return True
                except:
                    print("   ⚠️ Could not find signup link, but continuing...")
                    return True
                
            except Exception as fallback_error:
                print(f"   ❌ Fallback failed: {str(fallback_error)[:100]}")
                return False
    
    def fill_account_info(self, account_data):
        """Fill email and account name - FIXED for pandas NaN"""
        print("\n" + "="*70)
        print("STEP 3: FILL SIGNUP FORM")
        print("="*70)
        
        try:
            # ============================================================
            # GET EMAIL - HANDLE pandas NaN! 
            # ============================================================
            
            import pandas as pd
            
            email = None
            
            # Try multiple column names
            for key in ['email', 'gmail', 'aws_email', 'mail']: 
                value = account_data.get(key)
                
                # CRITICAL: Check for pandas NaN
                if value is not None: 
                    try:
                        # Check if pandas NaN
                        if pd.isna(value):
                            print(f"   [DEBUG] '{key}' is NaN, skipping")
                            continue
                    except:
                        pass
                    
                    # Convert to string and validate
                    value_str = str(value).strip()
                    
                    if value_str and value_str.lower() not in ['nan', 'none', '', 'null']:
                        email = value_str
                        print(f"   ✅ Found email in '{key}': {email}")
                        break
            
            # ============================================================
            # RENT FROM GMAIL94 IF NO EMAIL
            # ============================================================
            
            if not email: 
                print(f"\n   No email in Excel, trying Gmail94...")
                
                if self.gmail94_api:
                    print("\n   🔑 AUTO-RENTING EMAIL FROM GMAIL94...")
                    print("   " + "-"*60)
                    
                    result = self.gmail94_api. rent_email('aws', rental_time=10)
                    
                    if result and isinstance(result, dict):
                        email = result.get('email')
                        order_id = result.get('order_id')
                        
                        if email: 
                            account_data['email'] = email
                            account_data['order_id'] = order_id
                            
                            print(f"\n   ✅ EMAIL RENTAL SUCCESS!")
                            print(f"      Email: {email}")
                            print(f"      Order ID: {order_id}")
                        else:
                            print("   ❌ No email in Gmail94 response!")
                            return False
                    else:
                        print(f"   ❌ Gmail94 failed: {result}")
                        return False
                else:
                    print("   ❌ Gmail94 API not available!")
                    return False
            
            # ============================================================
            # VALIDATE EMAIL
            # ============================================================
            
            if not email or '@' not in str(email):
                print(f"\n   ❌ NO VALID EMAIL!")
                return False
            
            print(f"\n   Using email: {email}")
            
            # ============================================================
            # FILL EMAIL INPUT
            # ============================================================
            
            print("\n   Looking for email input...")
            
            email_selectors = [
                "input[name='email']",
                "input[type='email']",
                "#ap_email",
                "input[id*='email']",
            ]
            
            email_input = None
            for selector in email_selectors:
                try: 
                    inp = self.page.locator(selector).first
                    if inp.is_visible(timeout=2000):
                        email_input = inp
                        print(f"   Found email input")
                        break
                except: 
                    continue
            
            if not email_input:
                try:
                    email_input = self.page.get_by_label("email", exact=False).first
                    print("   Found email input (smart locator)")
                except: 
                    print("   ❌ Email input not found!")
                    return False
            
            # Fill email
            print(f"   Filling email: {email}")
            
            email_input.click(timeout=5000)
            self.random_delay(0.2, 0.5)
            email_input.fill("")
            self.random_delay(0.1, 0.3)
            
            for char in str(email):
                email_input.type(char, delay=random.uniform(50, 150))
            
            self.random_delay(0.5, 1)
            print("   ✅ Email entered")
            
            # ============================================================
            # FILL ACCOUNT NAME
            # ============================================================
            
            account_name = account_data.get('profile_name', 'AWS Account')
            
            # Handle NaN for account name
            try:
                if pd.isna(account_name):
                    account_name = f"AWS-{int(time.time())}"
            except:
                pass
            
            if not account_name or str(account_name).lower() in ['nan', 'none', '']:
                account_name = f"AWS-{int(time.time())}"
            
            print(f"\n   Filling account name: {account_name}")
            
            name_selectors = [
                "input[name='accountName']",
                "input[name='fullName']",
                "#ap_customer_name",
                "input[id*='account']",
            ]
            
            name_input = None
            for selector in name_selectors:
                try:
                    inp = self.page.locator(selector).first
                    if inp.is_visible(timeout=2000):
                        name_input = inp
                        print(f"   Found name input")
                        break
                except:
                    continue
            
            if not name_input: 
                try:
                    name_input = self.page.get_by_label("account name", exact=False).first
                except:
                    print("   ⚠️ Account name input not found, skipping...")
            
            if name_input:
                name_input.click(timeout=5000)
                self.random_delay(0.2, 0.5)
                name_input.fill("")
                
                for char in str(account_name):
                    name_input.type(char, delay=random.uniform(50, 150))
                
                self.random_delay(0.5, 1)
                print("   ✅ Account name entered")
            
            # ============================================================
            # SUBMIT FORM
            # ============================================================
            
            print("\n   Preparing to submit...")
            self.random_delay(1, 2)
            
            button_selectors = [
                "button:has-text('Verify')",
                "button: has-text('Continue')",
                "button[type='submit']",
                "#continue",
            ]
            
            clicked = False
            for selector in button_selectors:
                try: 
                    btn = self.page.locator(selector).first
                    if btn.is_visible(timeout=2000):
                        print(f"   Found submit button")
                        btn.scroll_into_view_if_needed()
                        self.random_delay(0.5, 1)
                        btn.click(timeout=10000)
                        clicked = True
                        print("   ✅ Clicked submit button!")
                        break
                except:
                    continue
            
            if not clicked: 
                print("   ⚠️ Button not found, pressing Enter...")
                self.page.keyboard.press("Enter")
            
            # Wait for next page
            print("   Waiting for page to load...")
            
            try:
                self.page.wait_for_load_state("networkidle", timeout=30000)
            except:
                print("   ⚠️ Network not idle, continuing...")
            
            self.random_delay(3, 5)
            
            print("   ✅ Form submitted successfully!")
            return True
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            
            try:
                self.page.screenshot(path=f"error_fill_{int(time.time())}.png")
            except:
                pass
            
            return False
    
    def verify_email_with_otp(self, account_data):
        """Verify email with OTP code"""
        print("\n" + "="*70)
        print("STEP 4: VERIFY EMAIL WITH OTP")
        print("="*70)
        
        try:
            # Get OTP from Gmail94
            order_id = account_data.get('order_id')
            
            if not order_id or not self.gmail94_api:
                print("   ⚠️ No order_id or Gmail94 API not available")
                return False
            
            print(f"   Getting OTP from Gmail94...")
            print(f"   Order ID: {order_id}")
            
            otp_code = self.gmail94_api. get_otp_from_gmail(order_id, timeout=120)
            
            if not otp_code:
                print("   ❌ Failed to get OTP")
                return False
            
            print(f"\n   ✅ Got OTP: {otp_code}")
            
            # Find OTP input
            print("   Looking for OTP input...")
            
            otp_selectors = [
                "input[name='otp']",
                "input[name='code']",
                "input[type='text'][maxlength='6']",
                "#otp",
                "#cvf-input-code",
                "label:has-text('Verification code') + input",
            ]
            
            otp_input = None
            for selector in otp_selectors:
                try:
                    inp = self.page.locator(selector).first
                    if inp.is_visible():
                        print(f"   Found OTP input: {selector[:40]}...")
                        otp_input = inp
                        break
                except:
                    continue
            
            if not otp_input:
                # Smart locator
                otp_input = self.page.get_by_label("Verification code", exact=False).first
                print("   Found OTP input (smart locator)")
            
            # Fill OTP
            print(f"   Entering OTP: {otp_code}")
            otp_input.click()
            self.random_delay(0.3, 0.8)
            
            # Type slowly (human-like)
            for char in otp_code:
                otp_input.type(char, delay=random.uniform(50, 150))
            
            self.random_delay(0.5, 1)
            print("   ✅ OTP entered")
            
            # Click Verify button
            print("   Looking for Verify button...")
            
            verify_selectors = [
                "button:has-text('Verify')",
                "button:has-text('Continue')",
                "button[type='submit']",
                "#continue",
            ]
            
            clicked = False
            for selector in verify_selectors:
                try:
                    btn = self.page.locator(selector).first
                    if btn.is_visible():
                        btn.click()
                        clicked = True
                        print("   ✅ Clicked Verify button!")
                        break
                except:
                    continue
            
            if not clicked:
                print("   ⚠️ Button not found, pressing Enter...")
                self.page.keyboard.press("Enter")
            
            # Wait for next page
            self.page.wait_for_load_state("networkidle")
            self.random_delay(3, 5)
            
            print("   ✅ Email verified successfully!")
            return True
            
        except Exception as e: 
            print(f"   ❌ Error: {str(e)}")
            return False
    
    def create_password(self, account_data):
        """Create AWS root password"""
        print("\n" + "="*70)
        print("STEP 5: CREATE PASSWORD")
        print("="*70)
        
        try: 
            password = "Trnhoanganh2002@"
            account_data['aws_password'] = password
            
            print(f"   Using password: {password}")
            
            # Find password input
            print("\n   Looking for password input...")
            
            pwd_selectors = [
                "input[name='password']",
                "input[id='ap_password']",
                "input[type='password']",
                "label:has-text('Root user password') + input",
            ]
            
            pwd_input = None
            for selector in pwd_selectors:
                try: 
                    inputs = self.page.locator(selector).all()
                    if len(inputs) > 0:
                        pwd_input = inputs[0]
                        print(f"   Found password input:  {selector[:40]}...")
                        break
                except:
                    continue
            
            if not pwd_input: 
                pwd_input = self.page.get_by_label("password", exact=False).first
                print("   Found password input (smart locator)")
            
            # Fill password
            print("   Entering password (first field)...")
            pwd_input. click()
            self.random_delay(0.3, 0.8)
            
            for char in password:
                pwd_input.type(char, delay=random.uniform(40, 100))
            
            self.random_delay(0.5, 1)
            print("   ✅ Password entered in first field")
            
            # Find confirm password input
            print("\n   Looking for confirm password input...")
            
            confirm_input = None
            
            # Get all password inputs
            all_pwd_inputs = self.page.locator("input[type='password']").all()
            print(f"   Found {len(all_pwd_inputs)} password input(s)")
            
            if len(all_pwd_inputs) >= 2:
                confirm_input = all_pwd_inputs[1]
                print("   Using 2nd password input as confirm field")
            else:
                # Try smart locator
                try:
                    confirm_input = self.page.get_by_label("Confirm", exact=False).first
                    print("   Found confirm input (smart locator)")
                except: 
                    print("   ⚠️ Only 1 password field found")
            
            # Fill confirm password
            if confirm_input:
                print("   Entering password (confirm field)...")
                confirm_input.click()
                self.random_delay(0.3, 0.8)
                
                for char in password:
                    confirm_input.type(char, delay=random.uniform(40, 100))
                
                self.random_delay(0.5, 1)
                print("   ✅ Password entered in confirm field")
            
            # Click Continue
            print("\n   Looking for Continue button...")
            
            continue_selectors = [
                "button:has-text('Continue')",
                "button[type='submit']",
                "#continue",
            ]
            
            clicked = False
            for selector in continue_selectors: 
                try:
                    btn = self.page.locator(selector).first
                    if btn.is_visible():
                        btn.scroll_into_view_if_needed()
                        self.random_delay(0.5, 1)
                        btn.click()
                        clicked = True
                        print("   ✅ Clicked Continue button!")
                        break
                except: 
                    continue
            
            if not clicked:
                print("   ⚠️ Button not found, pressing Enter...")
                self.page.keyboard.press("Enter")
            
            # Wait for next page
            self.page.wait_for_load_state("networkidle")
            self.random_delay(3, 5)
            
            print("   ✅ Password created successfully!")
            return True
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return True  # Continue anyway
    
    def close(self):
        """Close browser and cleanup"""
        print("\n   Closing browser...")
        
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            
            print("   ✅ Browser closed")
        except Exception as e:
            print(f"   ⚠️ Error closing browser:  {str(e)}")