import time
from selenium. webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium. webdriver.common.keys import Keys
from faker import Faker
import random
import os
import base64
from PIL import Image
from io import BytesIO

class AWSRegister:
    def __init__(self, driver, capmonster_solver, codesim_api):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)
        self.capmonster = capmonster_solver
        self.codesim = codesim_api
        self.faker = Faker()
        self.gmail94_api = None
        
        os.makedirs('screenshots', exist_ok=True)
    
    def random_delay(self, min_val, max_val):
        return random.randint(int(min_val * 10), int(max_val * 10)) / 10.0
    
    def start_registration(self, account_data):
        """Start AWS registration - OPTIMIZED"""
        try:
            print("Starting AWS registration...")
            print("   Keeping existing cookies/session for natural behavior")
            
            # STEP 1: NAVIGATE (giữ nguyên code cũ nhưng giảm delays)
            print("\n" + "="*70)
            print("STEP 1: NAVIGATE TO AWS SIGNUP PAGE")
            print("="*70)
            
            try:
                print("   Checking current browser state...")
                current_url = self.driver.current_url
                print(f"   Current URL: {current_url}")
                
                if 'chrome-extension://' in current_url or current_url == 'about:blank':
                    print("   ⚠️ Browser on extension/blank page - need to escape!")
                    print("   Opening new tab...")
                    
                    try:
                        self.driver. execute_script("window.open('about:blank', '_blank');")
                        time.sleep(1)  # Reduced
                        
                        if len(self.driver.window_handles) > 1:
                            self.driver.switch_to. window(self.driver.window_handles[-1])
                            print("   ✅ Switched to new tab")
                            
                            if len(self.driver.window_handles) > 1:
                                try:
                                    self.driver.switch_to.window(self.driver.window_handles[0])
                                    self.driver.close()
                                    self.driver.switch_to.window(self.driver.window_handles[0])
                                    print("   ✅ Closed old extension tab")
                                except: 
                                    pass
                    except Exception as tab_error:
                        print(f"   ⚠️ Tab handling error: {str(tab_error)[:100]}")
                
                print("\n   🔍 Method 1: Google Search for 'AWS'...")
                search_success = False
                
                try:
                    print("   Navigating to Google...")
                    self.driver.get("https://www.google.com")
                    time.sleep(2)  # Reduced
                    
                    print(f"   Loaded:  {self.driver.current_url}")
                    
                    try:
                        consent_buttons = self.driver.find_elements(By. XPATH, 
                            "//button[contains(., 'Accept') or contains(., 'Reject') or contains(., 'I agree')]")
                        
                        if consent_buttons:
                            print("   Handling Google consent...")
                            consent_buttons[-1].click()
                            time.sleep(1)  # Reduced
                    except: 
                        pass
                    
                    print("   Looking for search box...")
                    search_box = None
                    search_selectors = [
                        (By.NAME, "q"),
                        (By.CSS_SELECTOR, "input[type='search']"),
                        (By. CSS_SELECTOR, "textarea[name='q']"),
                        (By. XPATH, "//input[@title='Search']"),
                    ]
                    
                    for by, selector in search_selectors: 
                        try:
                            search_box = WebDriverWait(self.driver, 3).until(  # Reduced
                                EC.presence_of_element_located((by, selector))
                            )
                            print("   ✅ Found search box")
                            break
                        except: 
                            continue
                    
                    if not search_box: 
                        raise Exception("No search box found")
                    
                    search_query = "AWS create account"
                    print(f"   Typing:  {search_query}")
                    
                    search_box.click()
                    time.sleep(0.3)  # Reduced
                    search_box.clear()
                    time.sleep(0.2)  # Reduced
                    
                    for char in search_query:
                        search_box.send_keys(char)
                        time. sleep(random.uniform(0.05, 0.1))  # Fast!
                    
                    time.sleep(0.5)  # Reduced
                    
                    print("   Submitting search...")
                    search_box.send_keys(Keys. RETURN)
                    time. sleep(3)  # Reduced
                    
                    print(f"   Search results: {self.driver.current_url}")
                    print("   Looking for AWS signup link...")
                    
                    aws_links = []
                    try:
                        aws_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='aws.amazon.com']")
                        if not aws_links:
                            aws_links = self.driver.find_elements(By. XPATH, "//a[contains(@href, 'aws')]")
                    except:
                        pass
                    
                    if aws_links:
                        best_link = None
                        
                        # Find AWS homepage
                        for link in aws_links[:15]: 
                            try:
                                href = link.get_attribute('href') or ''
                                text = link.text or ''
                                
                                # Look for AWS homepage (not console/signin)
                                if 'aws.amazon.com' in href. lower():
                                    if 'console' not in href and 'signin' not in href:
                                        if '/?' not in href:
                                            best_link = link
                                            print(f"   Found AWS homepage link")
                                            break
                            except:
                                continue
                        
                        if not best_link and aws_links:
                            best_link = aws_links[0]
                        
                        if best_link:
                            result_href = best_link.get_attribute('href')
                            result_text = best_link.text[: 60]
                            
                            print(f"   ✅ Found AWS link:")
                            print(f"      Text: {result_text}")
                            print(f"      URL: {result_href[: 80]}...")
                            print("   Clicking result...")
                            
                            self.driver.execute_script(
                                "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", 
                                best_link
                            )
                            time. sleep(0.5)  # Reduced
                            
                            try:
                                best_link.click()
                            except:
                                self.driver.execute_script("arguments[0].click();", best_link)
                            
                            print("   Clicked! Waiting for page load...")
                            time.sleep(4)  # Reduced
                            
                            current_url = self.driver.current_url
                            print(f"   Navigated to: {current_url}")
                            
                            if 'aws.amazon.com' in current_url or 'signin. aws.amazon.com' in current_url:
                                 print("   ✅ Successfully reached AWS homepage!")
                                                
                            # NOW FIND "Create Account" BUTTON
                            print("\n   Looking for 'Create AWS Account' button...")
                            time.sleep(2)
                            
                            signup_found = False
                            signup_selectors = [
                                "//a[contains(text(), 'Create an AWS Account')]",
                                "//a[contains(text(), 'Tạo tài khoản AWS')]",
                                "//a[contains(text(), 'Sign up')]",
                                "//button[contains(text(), 'Create')]",
                                "//a[contains(@href, 'signup')]",
                                "//a[contains(@href, 'portal. aws.amazon.com/billing/signup')]",
                            ]
                            
                            for selector in signup_selectors:
                                try:
                                    signup_btn = self.driver.find_element(By. XPATH, selector)
                                    
                                    if signup_btn.is_displayed():
                                        btn_text = signup_btn.text[: 40] if signup_btn.text else "No text"
                                        print(f"   Found signup button: {btn_text}")
                                        
                                        # Scroll to button smoothly
                                        self.driver. execute_script(
                                            "arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});",
                                            signup_btn
                                        )
                                        time.sleep(1)
                                        
                                        # Click button
                                        try:
                                            signup_btn. click()
                                        except:
                                            self.driver.execute_script("arguments[0].click();", signup_btn)
                                        
                                        print("   ✅ Clicked 'Create Account' button!")
                                        signup_found = True
                                        time.sleep(3)
                                        break
                                except:
                                    continue
                            
                            if not signup_found: 
                                print("   ⚠️ Signup button not found, navigating directly...")
                                self.driver.get("https://portal.aws.amazon.com/billing/signup#/start/email")
                                time.sleep(3)
                            
                            search_success = True                               
                        else:
                            print(f"   ⚠️ Not on AWS page:  {current_url[: 80]}")
                            raise Exception("Search didn't reach AWS")
                    else:
                        print("   ⚠️ No AWS links found in results")
                        raise Exception("No AWS results")
                
                except Exception as google_error:
                    print(f"   ⚠️ Google search failed: {str(google_error)[:100]}")
                    search_success = False
                
                if not search_success:
                    print("\n   🔗 Method 2: Direct navigation to AWS signup...")
                    signup_url = "https://portal.aws.amazon.com/billing/signup#/start/email"
                    
                    for attempt in range(1, 4):
                        print(f"\n   Attempt {attempt}/3...")
                        
                        try: 
                            print(f"   Navigating to: {signup_url}")
                            
                            if attempt == 1:
                                self.driver.get(signup_url)
                            elif attempt == 2:
                                self.driver.execute_script(f"window.location.href = '{signup_url}';")
                            else:
                                self.driver. execute_script(f"window. open('{signup_url}', '_self');")
                            
                            time.sleep(4)  # Reduced
                            
                            current_url = self.driver.current_url
                            print(f"   Current URL: {current_url}")
                            
                            if current_url != 'about:blank' and 'chrome-extension://' not in current_url:
                                if 'aws.amazon.com' in current_url or 'amazonaws.com' in current_url:
                                    print("   ✅ Successfully navigated to AWS!")
                                    break
                                else:
                                    print(f"   ⚠️ On different page: {current_url[:80]}")
                            else:
                                print("   ❌ Still on blank/extension page")
                            
                            if attempt < 3:
                                print("   Retrying...")
                                time.sleep(1)  # Reduced
                        
                        except Exception as nav_error:
                            print(f"   Error:  {str(nav_error)[:100]}")
                            if attempt < 3:
                                time.sleep(1)  # Reduced
                
                print("\n   Verifying navigation...")
                time.sleep(1)  # Reduced
                
                final_url = self.driver.current_url
                page_title = self.driver.title
                
                print(f"   Final URL: {final_url}")
                print(f"   Page title: {page_title[: 80]}")
                
                if final_url == 'about:blank' or 'chrome-extension://' in final_url:
                    print("\n   ❌ NAVIGATION FAILED!")
                    print("   Still on blank/extension page after all attempts")
                    return False
                
                if 'aws.amazon.com' not in final_url and 'signin.aws' not in final_url and 'amazonaws. com' not in final_url: 
                    print(f"   ⚠️ Warning: May not be on AWS page!")
                    print("   Continuing anyway...")
                else:
                    print("   ✅ STEP 1 COMPLETED - Successfully on AWS")
                
                try:
                    self.driver. save_screenshot("screenshots/step1_completed.png")
                except:
                    pass
            
            except Exception as step1_error:
                print(f"\n   ❌ STEP 1 ERROR: {step1_error}")
                import traceback
                traceback.print_exc()
                return False
            
            # STEP 2: VERIFY PAGE
            print("\n" + "="*70)
            print("STEP 2: VERIFY SIGNUP PAGE LOADED")
            print("="*70)
            
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            print("   Current URL: " + current_url)
            print("   Page title: " + page_title[:60])
            
            if "about:blank" in current_url or current_url == "data:,":
                print("   ERROR: Blank page - navigation failed")
                return False
            
            if "chrome-extension" in current_url: 
                print("   ERROR: Extension page - browser issue")
                return False
            
            if "400" in page_title or "Bad Request" in page_title: 
                print("   ERROR: 400 error - blocked by AWS")
                return False
            
            print("   Waiting for signup form to load...")
            
            email_input_found = False
            email_input = None
            
            email_selectors = [
                (By.ID, "ap_email"),
                (By. NAME, "email"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By. CSS_SELECTOR, "input[placeholder*='email']"),
                (By.CSS_SELECTOR, "input[placeholder*='Email']"),
                (By. XPATH, "//input[contains(@placeholder, 'email')]"),
                (By. XPATH, "//label[contains(text(), 'Root user email')]/following:: input[1]"),
                (By.XPATH, "//label[contains(text(), 'email')]/following::input[1]"),
                (By. XPATH, "//input[@type='email']"),
            ]
            
            for attempt in range(20):
                for i, (by, selector) in enumerate(email_selectors, 1):
                    try: 
                        email_input = self.driver.find_element(by, selector)
                        print("   Signup form found!  (selector #" + str(i) + ":  " + str(by) + ")")
                        email_input_found = True
                        break
                    except:
                        continue
                
                if email_input_found:
                    break
                
                if attempt < 19:
                    print("   Waiting...  (" + str(attempt + 1) + "/20)")
                    time.sleep(2)
            
            if not email_input_found:
                print("   ERROR: Signup form did not appear after 40 seconds")
                self.driver.save_screenshot("screenshots/no_signup_form.png")
                return False
            
            try:
                self.driver.save_screenshot("screenshots/signup_page_ready.png")
            except:
                pass
            
            print("   Signup page ready!")
            
            # STEP 3-9
            print("\n" + "="*70)
            print("STEP 3: FILL SIGNUP FORM (HUMAN-LIKE)")
            print("="*70)
            
            success = self.fill_account_info_humanlike(account_data)
            if not success:
                return False
            
            print("\n" + "="*70)
            print("STEP 4: VERIFY EMAIL")
            print("="*70)
            
            success = self.verify_email_with_otp_humanlike(account_data)
            if not success:
                return False
            
            print("\n" + "="*70)
            print("STEP 5: CREATE PASSWORD")
            print("="*70)
            
            success = self.create_password_humanlike(account_data)
            if not success:
                return False
            
            print("\n" + "="*70)
            print("STEP 6: FILL CONTACT INFO")
            print("="*70)
            
            success = self.fill_contact_info_humanlike(account_data)
            if not success:
                return False
            
            print("\n" + "="*70)
            print("STEP 7: FILL PAYMENT INFO")
            print("="*70)
            
            success = self.fill_payment_info_humanlike(account_data)
            if not success: 
                return False
            
            print("\n" + "="*70)
            print("STEP 8: VERIFY PHONE")
            print("="*70)
            
            success = self.verify_phone()
            if not success:
                return False
            
            print("\n" + "="*70)
            print("STEP 9: SELECT SUPPORT PLAN")
            print("="*70)
            
            success = self.select_support_plan()
            if not success: 
                return False
            
            print("\n" + "="*70)
            print("AWS REGISTRATION COMPLETED!")
            print("="*70 + "\n")
            
            return True
            
        except Exception as e:
            print("\nError during registration:  " + str(e))
            try:
                self.driver.save_screenshot("screenshots/registration_error.png")
            except:
                pass
            import traceback
            traceback.print_exc()
            return False
    
    def fill_account_info_humanlike(self, account_data):
        """Fill account info with AUTO EMAIL RENTAL - OPTIMIZED"""
        try:
            print("Filling account information (human-like typing)...")
            
            thinking_time = self.random_delay(1, 2)  # Reduced! 
            print("   Pausing " + str(round(thinking_time, 1)) + "s before filling form...")
            time.sleep(thinking_time)
            
            # AUTO RENT EMAIL
            print("\n" + "="*70)
            print("   🔑 AUTO-RENTING NEW EMAIL FROM GMAIL94")
            print("="*70)
            
            if not self.gmail94_api: 
                print("   ❌ ERROR: Gmail94 API not configured!")
                return False
            
            print("   Calling Gmail94 rent_email()...")
            rental_result = self.gmail94_api.rent_email(service='aws', rental_time=10)
            
            if not rental_result:
                print("\n   ❌ ERROR:  Failed to rent email from Gmail94!")
                return False
            
            email = rental_result. get('email')
            order_id = rental_result.get('order_id')
            
            if not email or not order_id:
                print("   ❌ ERROR: Invalid rental result from Gmail94")
                return False
            
            account_data['gmail'] = email
            account_data['order_id'] = order_id
            
            print("\n   ✅ EMAIL RENTAL SUCCESS!")
            print(f"      Email: {email}")
            print(f"      Order ID: {order_id}")
            print("      Valid for:  10 minutes")
            print("="*70 + "\n")
            
            time.sleep(1)  # Reduced
            
            # FILL FORM
            print("   Looking for email input...")
            
            email_input = None
            email_selectors = [
                (By.ID, "ap_email"),
                (By.NAME, "email"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.CSS_SELECTOR, "input[placeholder*='email']"),
                (By. XPATH, "//label[contains(text(), 'Root user email')]/following::input[1]"),
                (By. XPATH, "//label[contains(text(), 'email')]/following::input[1]"),
                (By.XPATH, "//input[@type='email']"),
            ]
            
            for i, (by, selector) in enumerate(email_selectors, 1):
                try:
                    email_input = WebDriverWait(self.driver, 2).until(  # Reduced!
                        EC.presence_of_element_located((by, selector))
                    )
                    print("   Found email input!")
                    break
                except: 
                    continue
            
            if not email_input:
                print("   ERROR: Cannot find email input")
                return False
            
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", email_input)
            time.sleep(0.5)  # Reduced
            
            email_input.click()
            time.sleep(0.2)  # Reduced
            
            try:
                email_input.clear()
            except:
                pass
            time.sleep(0.1)  # Reduced
            
            print("   Typing rented email:  " + email)
            for i, char in enumerate(email):
                email_input.send_keys(char)
                
                if char in ['@', '.', '_', '-']:
                    delay = self.random_delay(0.08, 0.15)  # Fast!
                elif i > 0 and email[i-1] == char:
                    delay = self. random_delay(0.02, 0.05)  # Fast!
                else:
                    delay = self.random_delay(0.03, 0.08)  # Fast!
                
                time.sleep(delay)
            
            review_time = self.random_delay(0.5, 1)  # Reduced!
            print("   Reviewing email (" + str(round(review_time, 1)) + "s)...")
            time.sleep(review_time)
            
            print("   Email entered")
            
            # ACCOUNT NAME
            account_name = account_data.get('aws_account_name')
            if not account_name: 
                account_name = "AWS-" + email.split('@')[0][:15]
                account_data['aws_account_name'] = account_name
            
            print("   Looking for account name input...")
            
            name_input = None
            name_selectors = [
                (By.ID, "ap_account_name"),
                (By. NAME, "account_name"),
                (By.NAME, "accountName"),
                (By.CSS_SELECTOR, "input[placeholder*='account name']"),
                (By. XPATH, "//label[contains(text(), 'AWS account name')]/following::input[1]"),
                (By. XPATH, "//label[contains(text(), 'account name')]/following::input[1]"),
            ]
            
            for i, (by, selector) in enumerate(name_selectors, 1):
                try:
                    name_input = WebDriverWait(self.driver, 2).until(  # Reduced!
                        EC.presence_of_element_located((by, selector))
                    )
                    print("   Found account name input!")
                    break
                except:
                    continue
            
            if not name_input:
                print("   ERROR: Cannot find account name input")
                return False
            
            name_input.click()
            time.sleep(0.2)  # Reduced
            
            try:
                name_input.clear()
            except:
                pass
            time.sleep(0.1)  # Reduced
            
            print("   Typing account name: " + account_name)
            for char in account_name:
                name_input.send_keys(char)
                delay = self.random_delay(0.03, 0.1)  # Fast!
                time.sleep(delay)
            
            review_time = self.random_delay(0.5, 1)  # Reduced!
            print("   Reviewing account name (" + str(round(review_time, 1)) + "s)...")
            time.sleep(review_time)
            
            print("   Account name entered")
            
            final_review = self.random_delay(1, 2)  # Reduced!
            print("   Final review before submit (" + str(round(final_review, 1)) + "s)...")
            time.sleep(final_review)
            # ============================================================
            # SUBMIT WITH HUMAN-LIKE BEHAVIOR
            # ============================================================
            print("\n   Preparing to submit...")
            
            # Review time (human-like)
            review_time = random.uniform(1, 2)
            print(f"   Final review ({round(review_time, 1)}s)...")
            time.sleep(review_time)
            
            # Find button
            print("   Looking for Continue button...")
            
            continue_btn = None
            
            continue_selectors = [
                (By.ID, "continue"),
                (By.XPATH, "//button[contains(text(), 'Verify')]"),
                (By.XPATH, "//button[contains(text(), 'Continue')]"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By. XPATH, "//input[@type='submit']"),
            ]
            
            for i, (by, selector) in enumerate(continue_selectors, 1):
                try: 
                    continue_btn = self. driver.find_element(by, selector)
                    
                    if continue_btn.is_displayed():
                        print(f"   Found button (selector #{i})")
                        break
                    else:
                        continue_btn = None
                except: 
                    continue
            
            if not continue_btn:
                print("   ⚠️ Button not found, pressing Enter...")
                account_name_input. send_keys(Keys.RETURN)
                time.sleep(5)
            else:
                # HUMAN-LIKE CLICK
                print("   Performing human-like click...")
                
                # 1. Smooth scroll
                self.driver.execute_script(
                    "arguments[0]. scrollIntoView({behavior: 'smooth', block: 'center'});",
                    continue_btn
                )
                time. sleep(0.8)
                
                # 2. Simulate mouse move
                print("   Moving to button...")
                time.sleep(0.3)
                
                # 3. Hover
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(self.driver)
                    actions. move_to_element(continue_btn).perform()
                    time.sleep(0.2)
                except:
                    pass
                
                # 4. Click (try multiple methods)
                clicked = False
                
                try:
                    continue_btn.click()
                    clicked = True
                    print("   ✅ Clicked (normal)")
                except:
                    pass
                
                if not clicked:
                    try:
                        self.driver.execute_script("arguments[0].click();", continue_btn)
                        clicked = True
                        print("   ✅ Clicked (JavaScript)")
                    except:
                        pass
                
                if not clicked:
                    try:
                        from selenium.webdriver.common.action_chains import ActionChains
                        ActionChains(self.driver).click(continue_btn).perform()
                        clicked = True
                        print("   ✅ Clicked (ActionChains)")
                    except:
                        pass
                
                if not clicked: 
                    print("   ⚠️ All methods failed, pressing Enter...")
                    account_name_input.send_keys(Keys.RETURN)
                
                # 5. Wait for processing
                print("   Waiting for AWS to process...")
                time.sleep(5)
            
            # CHECK CAPTCHA
            print("\n" + "="*70)
            print("DEBUG: Check captcha AFTER submit")
            print("="*70)
            
            try:
                self.check_and_solve_captcha()
                print("DEBUG: check_and_solve_captcha() completed - AFTER submit")
            except Exception as captcha_error:
                print(f"DEBUG: check_and_solve_captcha() failed:  {captcha_error}")
                import traceback
                traceback.print_exc()
            
            print("="*70 + "\n")
            
            print("   Step 3 completed!\n")
            
            return True
            
        except Exception as e:
            print("Error filling account info: " + str(e))
            self.driver.save_screenshot("screenshots/fill_account_error.png")
            import traceback
            traceback.print_exc()
            return False
    def verify_email_with_otp_humanlike(self, account_data):
        """Verify email with OTP - OPTIMIZED + FIXED"""
        try: 
            print("Verifying email with OTP...")
            time.sleep(1)
            
            print("   Current URL:   " + self.driver.current_url)
            print("   Looking for OTP input...")
            
            # Wait for page
            print("   Waiting 3 seconds for page to load...")
            time.sleep(3)
            
            otp_input = None
            
            # ============================================================
            # METHOD 1: JAVASCRIPT (FASTEST - TRY FIRST!)
            # ============================================================
            print("\n   🚀 Method 1: JavaScript (fastest)...")
            
            js_selectors = [
                "document.querySelector('input[name=\"otp\"]')",
                "document.querySelector('input#otp')",
                "document. querySelector('input[id=\"otp\"]')",
                "document.querySelector('input[type=\"text\"]')",
                "document.querySelectorAll('input[type=\"text\"]')[0]",
            ]
            
            for i, js_selector in enumerate(js_selectors, 1):
                try:
                    element = self.driver.execute_script(f"return {js_selector};")
                    
                    if element and element.tag_name == 'input': 
                        elem_id = element.get_attribute('id') or 'N/A'
                        elem_name = element.get_attribute('name') or 'N/A'
                        
                        print(f"   ✅ FOUND!  JS selector #{i}: id={elem_id}, name={elem_name}")
                        
                        otp_input = element
                        break
                
                except: 
                    continue
            
            # ============================================================
            # METHOD 2: SELENIUM TOP 5 (FALLBACK)
            # ============================================================
            if not otp_input: 
                print("\n   ⏳ Method 2: Selenium (slower)...")
                
                top_selectors = [
                    (By.ID, "otp"),
                    (By. NAME, "otp"),
                    (By.ID, "cvf-input-code"),
                    (By.NAME, "code"),
                    (By.CSS_SELECTOR, "input[type='text']"),
                ]
                
                for i, (by, selector) in enumerate(top_selectors, 1):
                    try:
                        otp_input = WebDriverWait(self.driver, 2).until(
                            EC.presence_of_element_located((by, selector))
                        )
                        
                        if otp_input.is_displayed():
                            print(f"   ✅ FOUND! Selenium selector #{i}")
                            break
                        else:
                            otp_input = None
                    
                    except:
                        continue
            
            # ============================================================
            # METHOD 3: JAVASCRIPT ALL INPUTS
            # ============================================================
            if not otp_input:
                print("\n   🔍 Method 3: JavaScript all inputs...")
                
                try:
                    js_code = """
                    var inputs = document.querySelectorAll('input[type="text"], input[type="tel"], input[type="number"]');
                    for(var i=0; i<inputs.length; i++) {
                        if(inputs[i]. offsetWidth > 0 && inputs[i].offsetHeight > 0) {
                            return inputs[i];
                        }
                    }
                    return null;
                    """
                    
                    element = self.driver. execute_script(js_code)
                    
                    if element:
                        elem_id = element.get_attribute('id') or 'N/A'
                        elem_name = element. get_attribute('name') or 'N/A'
                        
                        print(f"   ✅ FOUND! First visible input:  id={elem_id}, name={elem_name}")
                        otp_input = element
                
                except Exception as e:
                    print(f"   ✗ Failed: {str(e)[:50]}")
                        
            
            if not otp_input:
                print("\n   ❌ CANNOT FIND OTP INPUT!")
                
                # Save debug
                try:
                    self.driver.save_screenshot("screenshots/step4_no_input.png")
                    with open("screenshots/step4_page.html", "w", encoding="utf-8") as f:
                        f.write(self.driver.page_source)
                    print("   Debug saved:   step4_no_input.png & step4_page.html")
                except:
                    pass
                
                # Manual fallback
                otp_code = input("\n   Enter AWS verification code:   ").strip()
                
                if otp_code: 
                    try:
                        inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                        for inp in inputs:
                            if inp.is_displayed():
                                inp.click()
                                time.sleep(0.3)
                                inp.send_keys(otp_code)
                                inp.send_keys(Keys. RETURN)
                                time.sleep(2)
                                return True
                    except:
                        pass
                
                return True  # Continue anyway
            
            # ============================================================
            # GET OTP FROM GMAIL94
            # ============================================================
            print("\n   Getting OTP from Gmail94...")
            
            order_id = account_data.  get('order_id')
            otp_code = None
            
            if order_id and self.gmail94_api: 
                print(f"   Order ID: {order_id}")
                print("   Waiting for OTP (up to 120s)...")
                
                otp_code = self.gmail94_api.get_otp_from_gmail(order_id, timeout=120)
            
            if not otp_code:
                print("\n   ⚠️ Cannot get OTP from Gmail94")
                otp_code = input("\n   Enter AWS verification code (6 digits): ").strip()
                
                if not otp_code:
                    return False
            
            print(f"   Got OTP: {otp_code}")
            
            # ============================================================
            # ENTER OTP
            # ============================================================
            print("   Entering OTP...")
            
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", otp_input)
            time.sleep(0.3)
            
            otp_input.click()
            time.sleep(0.2)
            
            try:
                otp_input.  clear()
            except:
                pass
            
            print(f"   Typing:  {otp_code}")
            for char in otp_code:
                otp_input.send_keys(char)
                time.sleep(0.08)
            
            time.sleep(0.5)
            print("   ✅ OTP entered")
            
            try:
                self.driver.save_screenshot("screenshots/step4_otp_entered.png")
            except:
                pass
            
            # ============================================================
            # SUBMIT
            # ============================================================
            print("   Submitting...")
            
            submit_selectors = [
                (By.  XPATH, "//button[contains(text(), 'Verify')]"),
                (By. XPATH, "//button[contains(., 'Verify')]"),
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.ID, "continue"),
            ]
            
            button_found = False
            
            for by, selector in submit_selectors: 
                try:
                    btn = self.driver.find_element(by, selector)
                    if btn.is_displayed():
                        btn.click()
                        button_found = True
                        print("   ✅ Submitted!")
                        break
                except: 
                    continue
            
            if not button_found:
                otp_input. send_keys(Keys.RETURN)
                print("   ✅ Submitted via Enter")
            
            time.sleep(2)
            
            print("   Step 4 completed!\n")
            
            return True
            
        except Exception as e:
            print(f"   ❌ ERROR:   {str(e)}")
            
            try:
                self.driver.save_screenshot("screenshots/step4_error.png")
            except:
                pass
            
            import traceback
            traceback.print_exc()
            
            return False
    
    def create_password_humanlike(self, account_data):
        """Create AWS password - AUTO FILL"""
        try: 
            print("Creating password...")
            time.sleep(2)
            
            # HARDCODE PASSWORD
            password = "Trnhoanganh2002@"
            print(f"   Using password: {password}")
            
            # Save to account_data
            account_data['aws_password'] = password
            
            # ============================================================
            # FIND PASSWORD INPUT (MULTIPLE METHODS)
            # ============================================================
            password_input = None
            
            # Method 1: By ID
            print("\n   Looking for password input...")
            try:
                password_input = self. driver.find_element(By. ID, "ap_password")
                print("   ✅ Found password input (by ID)")
            except:
                pass
            
            # Method 2: By name
            if not password_input:
                try:
                    password_input = self.driver.find_element(By.NAME, "password")
                    print("   ✅ Found password input (by name)")
                except:
                    pass
            
            # Method 3: By type
            if not password_input: 
                try:
                    password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                    print("   ✅ Found password input (by type)")
                except:
                    pass
            
            # Method 4: JavaScript
            if not password_input: 
                try:
                    password_input = self.driver.execute_script("return document.querySelector('input[type=\"password\"]');")
                    if password_input:
                        print("   ✅ Found password input (via JavaScript)")
                except:
                    pass
            
            if not password_input:
                print("   ⚠️ Password input not found - step may be skipped by AWS")
                return True
            
            # ============================================================
            # ENTER PASSWORD (FIRST FIELD)
            # ============================================================
            print(f"\n   Entering password in first field...")
            
            # Scroll to input
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", password_input)
            time.sleep(0.5)
            
            # Click and clear
            password_input.click()
            time.sleep(0.3)
            
            try:
                password_input.clear()
            except:
                pass
            
            # Type password
            for char in password:
                password_input.send_keys(char)
                time.sleep(0.05)  # Fast typing
            
            time.sleep(0.5)
            print("   ✅ Password entered in first field")
            
            # ============================================================
            # FIND CONFIRM PASSWORD INPUT
            # ============================================================
            confirm_input = None
            
            print("\n   Looking for confirm password input...")
            
            # Method 1: By ID
            try:
                confirm_input = self.driver.find_element(By.ID, "ap_password_check")
                print("   ✅ Found confirm input (by ID)")
            except: 
                pass
            
            # Method 2: By name
            if not confirm_input: 
                try:
                    confirm_input = self.driver.find_element(By.NAME, "passwordCheck")
                    print("   ✅ Found confirm input (by name)")
                except:
                    pass
            # Method 3: All password inputs (get 2nd one) - WITH DEBUG
            if not confirm_input: 
                try:
                    all_password_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
                    
                    print(f"\n   🔍 DEBUG: Found {len(all_password_inputs)} password input(s) on page")
                    
                    for idx, inp in enumerate(all_password_inputs):
                        try:
                            inp_id = inp.get_attribute('id') or 'N/A'
                            inp_name = inp.get_attribute('name') or 'N/A'
                            inp_displayed = inp.is_displayed()
                            print(f"      Input[{idx}]: id={inp_id}, name={inp_name}, visible={inp_displayed}")
                        except:
                            pass
                    
                    if len(all_password_inputs) >= 2:
                        confirm_input = all_password_inputs[1]
                        print(f"   ✅ Using Input[1] as confirm password field")
                    elif len(all_password_inputs) == 1:
                        print(f"   ⚠️ Only 1 password field found (may be single-field form)")
                except Exception as e:
                    print(f"   ⚠️ Error finding confirm input: {str(e)[:50]}")
            
            # Method 4: JavaScript
            if not confirm_input:
                try: 
                    js_code = """
                    var inputs = document.querySelectorAll('input[type="password"]');
                    return inputs. length >= 2 ? inputs[1] : null;
                    """
                    confirm_input = self.driver.execute_script(js_code)
                    if confirm_input: 
                        print("   ✅ Found confirm input (via JavaScript)")
                except:
                    pass
                
            
            # Method 5: JavaScript find by label text
            if not confirm_input: 
                print("\n   Method 5: Finding confirm input by label text...")
                try:
                    js_code = """
                    var labels = document.querySelectorAll('label');
                    for(var i=0; i<labels.length; i++) {
                        var text = labels[i].textContent. toLowerCase();
                        if(text. includes('confirm') || text.includes('re-enter') || text.includes('retype')) {
                            // Try next sibling
                            var input = labels[i].nextElementSibling;
                            if(input && input.tagName === 'INPUT' && input.type === 'password') {
                                return input;
                            }
                            // Try parent's input
                            var parent = labels[i].parentElement;
                            input = parent.querySelector('input[type="password"]');
                            if(input) return input;
                        }
                    }
                    return null;
                    """
                    confirm_input = self.driver.execute_script(js_code)
                    if confirm_input: 
                        print("   ✅ Found confirm input (via label text)")
                except Exception as e:
                    print(f"   Method 5 failed: {str(e)[:50]}")
            
            if not confirm_input:
                print("   ⚠️ Confirm password input not found - may be single field only")
                # Try to submit with just one field
                try:
                    password_input.send_keys(Keys.RETURN)
                except:
                    pass
                time.sleep(2)
                return True
            
            # ============================================================
            # ENTER PASSWORD (CONFIRM FIELD)
            # ============================================================
            print(f"\n   Entering password in confirm field...")
            
            # Scroll to input
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", confirm_input)
            time.sleep(0.5)
            
            # Click and clear
            confirm_input.click()
            time.sleep(0.3)
            
            try:
                confirm_input.clear()
            except:
                pass
            
            # Type password
            for char in password:
                confirm_input.send_keys(char)
                time.sleep(0.05)  # Fast typing
            
            time.sleep(0.5)
            print("   ✅ Password entered in confirm field")
            
            # ============================================================
            # SUBMIT
            # ============================================================
            print("\n   Looking for submit button...")
            
            submit_found = False
            
            # Try multiple selectors
            submit_selectors = [
                (By.ID, "continue"),
                (By. XPATH, "//button[contains(text(), 'Continue')]"),
                (By. XPATH, "//input[@type='submit']"),
                (By.CSS_SELECTOR, "button[type='submit']"),
            ]
            
            for by, selector in submit_selectors: 
                try:
                    submit_btn = self.driver.find_element(by, selector)
                    
                    if submit_btn.is_displayed():
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
                        time.sleep(0.5)
                        
                        submit_btn.click()
                        submit_found = True
                        print("   ✅ Clicked Continue button")
                        break
                except:
                    continue
            
            if not submit_found:
                print("   ⚠️ Submit button not found, pressing Enter...")
                confirm_input.send_keys(Keys.RETURN)
            
            time.sleep(3)
            
            print("   Step 5 completed!\n")
            return True
            
        except Exception as e:
            print(f"   ⚠️ Error:  {str(e)}")
            return True  # Continue anyway
    
    def fill_contact_info_humanlike(self, account_data):
        """Fill contact info - OPTIMIZED"""
        try:
            print("Filling contact info...")
            time.sleep(1)  # Reduced from 2-4s
            
            try:
                name_input = self.driver.find_element(By.ID, "ap_customer_name")
                name = account_data.get('card_name', self.faker.name())
                
                name_input.click()
                time.sleep(0.2)  # Reduced
                
                for char in name:
                    name_input.send_keys(char)
                    time. sleep(0.03)  # Fast typing!
                
                time.sleep(0.5)  # Reduced
            except:
                pass
            
            try:
                time.sleep(1)  # Reduced
                continue_btn = self.driver.find_element(By. XPATH, "//button[contains(., 'Continue')]")
                continue_btn.click()
                time.sleep(3)  # Reduced from 5-7s
            except:
                pass
            
            print("   Step 6 completed!\n")
            return True
            
        except: 
            return False
    
    def fill_payment_info_humanlike(self, account_data):
        """Fill payment info - OPTIMIZED"""
        try:
            print("Filling payment info...")
            time.sleep(1)  # Reduced from 2-4s
            
            card_number = account_data.get('card_number', '')
            
            # Handle Excel scientific notation (4. 53E+15)
            if isinstance(card_number, float):
                card_number = f"{card_number:.0f}"
            
            card_number = str(card_number).replace(' ', '').replace('.', '')
            
            if not card_number or len(card_number) < 13:
                print("   ERROR: Invalid card number")
                print(f"   Received: {card_number}")
                return False
            
            try: 
                card_input = self.driver.find_element(By.ID, "card-number")
                card_input. click()
                time.sleep(0.3)  # Reduced
                
                for char in card_number: 
                    card_input.send_keys(char)
                    time.sleep(0.05)  # Fast typing!
                
                time.sleep(0.5)  # Reduced
            except:
                pass
            
            try:
                time.sleep(1)  # Reduced
                continue_btn = self.driver.find_element(By.XPATH, "//button[contains(., 'Continue')]")
                continue_btn.click()
                time.sleep(3)  # Reduced from 5-7s
            except:
                pass
            
            print("   Step 7 completed!\n")
            return True
            
        except:
            return False
    
    def verify_phone(self):
        """Phone verification - OPTIMIZED"""
        try:
            print("Phone verification...")
            time.sleep(2)  # Reduced from 3s
            
            try:
                phone_input = self.driver. find_element(By.ID, "phoneNumber")
            except:
                print("   INFO: Not required")
                return True
            
            if not self.codesim: 
                input("   Press Enter after phone verification...")
                return True
            
            print("   Step 8 completed!\n")
            return True
            
        except:
            return False
    
    def select_support_plan(self):
        """Select support plan - OPTIMIZED"""
        try:
            print("Selecting support plan...")
            time.sleep(2)  # Reduced from 3s
            
            try:
                basic_btn = self.driver.find_element(By. XPATH, "//button[contains(., 'Basic')]")
                time.sleep(1)  # Reduced
                basic_btn.click()
                time.sleep(3)  # Reduced from 5s
            except:
                pass
            
            print("   Step 9 completed!\n")
            return True
            
        except:
            return False
    def check_and_solve_captcha(self):
        """Check and solve AWS captcha using CapMonster - OPTIMIZED"""
        print("\n" + "="*70)
        print("DEBUG: check_and_solve_captcha() METHOD CALLED!")
        print("="*70)
        print(f"   CapMonster object: {self.capmonster}")
        print(f"   CapMonster is None: {self.capmonster is None}")
        
        try:
            print(f"   Current URL: {self.driver.current_url}")
            print(f"   Page title: {self.driver.title[: 50]}")
        except:
            print("   Cannot get URL/title")
        
        print("="*70 + "\n")
        
        try:
            print("\n   Checking for captcha...")
            
            captcha_found = False
            
            try:
                security_dialog = self.driver.find_element(By. XPATH, "//*[contains(text(), 'Security Verification')]")
                captcha_found = True
                print("   WARNING: AWS Security Verification captcha detected!")
                
                print("   Waiting 3 seconds for captcha image to load...")  # Reduced from 5s
                time.sleep(3)
                print("   Wait completed, proceeding to find captcha...")
                
            except:
                print("   INFO: No 'Security Verification' text found")
                pass
            
            if not captcha_found:
                print("   OK: No captcha found")
                return True
            
            if self.capmonster:
                print("\n   AUTO-SOLVING with CapMonster API (with retry)...")
                print("   NOTE: Will retry up to 5 times if solution incorrect")
                
                max_retries = 5
                
                for attempt in range(1, max_retries + 1):
                    try:
                        print(f"\n   {'='*66}")
                        print(f"   ATTEMPT {attempt}/{max_retries}")
                        print(f"   {'='*66}")
                        
                        print("\n      Looking for captcha image...")
                        
                        captcha_img = None
                        image_base64 = None
                        
                        # Check for iframe
                        print("      Checking for iframes...")
                        try:
                            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                            if len(iframes) > 0:
                                print(f"      Found {len(iframes)} iframes, switching to first...")
                                self.driver. switch_to.frame(iframes[0])
                                print(f"      Switched to iframe")
                        except Exception as iframe_error:
                            print(f"      No iframe:  {str(iframe_error)[:50]}")
                        
                        # METHOD 1: Wait for img[alt='captcha']
                        try:
                            print("\n      METHOD 1: Waiting for img[alt='captcha'] (10s)...")  # Reduced from 15s
                            
                            captcha_img = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt='captcha']"))
                            )
                            
                            print(f"      Found img[alt='captcha']!")
                            time.sleep(1)  # Reduced from 2s
                            
                            width = captcha_img.size. get('width', 0)
                            height = captcha_img.size.get('height', 0)
                            
                            print(f"      Size: {width}x{height}px")
                            
                            if width > 0 and height > 0:
                                print(f"      SUCCESS via METHOD 1!")
                            else:
                                captcha_img = None
                                
                        except Exception as wait_error:
                            print(f"      METHOD 1 failed: {str(wait_error)[:80]}")
                            captcha_img = None
                        
                        # METHOD 2: Find by src pattern
                        if not captcha_img:
                            print("\n      METHOD 2: Finding by src pattern...")
                            
                            src_selectors = [
                                "//img[contains(@src, 'amcs-captcha-prod')]",
                                "//img[contains(@src, 's3.dualstack.us-east-1.amazonaws.com')]",
                                "//img[contains(@src, '. jpg') and contains(@src, 'captcha')]",
                            ]
                            
                            for selector in src_selectors:
                                try:
                                    captcha_img = self.driver.find_element(By. XPATH, selector)
                                    width = captcha_img.size. get('width', 0)
                                    height = captcha_img.size.get('height', 0)
                                    
                                    if width > 0 and height > 0:
                                        print(f"      Found!  Size: {width}x{height}px")
                                        print(f"      SUCCESS via METHOD 2!")
                                        break
                                    else:
                                        captcha_img = None
                                except:
                                    continue
                        
                        # METHOD 3: Check for canvas
                        if not captcha_img and not image_base64:
                            print("\n      METHOD 3: Checking for <canvas>...")
                            
                            try:
                                canvas = self. driver.find_element(By. CSS_SELECTOR, "canvas")
                                
                                if canvas. is_displayed():
                                    print(f"      Found <canvas>!  Converting...")
                                    
                                    canvas_base64 = self.driver.execute_script("""
                                        var canvas = arguments[0];
                                        return canvas.toDataURL('image/png').substring(22);
                                    """, canvas)
                                    
                                    if canvas_base64:
                                        image_base64 = canvas_base64
                                        print(f"      Canvas converted!  (length: {len(image_base64)})")
                                        print(f"      SUCCESS via METHOD 3!")
                                    
                            except Exception as canvas_error: 
                                print(f"      No canvas: {str(canvas_error)[:50]}")
                        
                        if not captcha_img and not image_base64:
                            raise Exception("Cannot find captcha image!")
                        
                        # Extract image data
                        if captcha_img and not image_base64:
                            print("\n      Extracting image data...")
                            
                            try:
                                img_src = captcha_img.get_attribute('src')
                                
                                if img_src and img_src.startswith('data:image'):
                                    image_base64 = img_src.split(',')[1]
                                    print(f"      Got base64 from src (length: {len(image_base64)})")
                                    
                                elif img_src and (img_src.startswith('http') or img_src.startswith('//')):
                                    import requests
                                    
                                    if img_src.startswith('//'):
                                        img_src = 'https:' + img_src
                                    
                                    print(f"      Downloading from URL...")
                                    
                                    headers = {
                                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                                        'Referer': 'https://portal.aws.amazon.com/'
                                    }
                                    
                                    response = requests.get(img_src, headers=headers, timeout=10)
                                    if response.status_code == 200:
                                        image_base64 = base64.b64encode(response. content).decode('utf-8')
                                        print(f"      Downloaded (length: {len(image_base64)})")
                                        
                            except Exception as src_error:
                                print(f"      Src failed: {str(src_error)[:50]}")
                            
                            if not image_base64:
                                print("      Taking screenshot...")
                                try:
                                    image_base64 = captcha_img.screenshot_as_base64
                                    print(f"      Screenshot captured (length: {len(image_base64)})")
                                except Exception as screenshot_error:
                                    print(f"      Screenshot failed: {str(screenshot_error)[:50]}")
                                    raise Exception("Cannot capture image")
                        
                        if not image_base64:
                            raise Exception("No image data!")
                        
                        # CROP IMAGE - MINIMAL 5% ONLY! 
                        print("\n      Cropping captcha (MINIMAL 5% borders only)...")
                        
                        try:
                            image_data = base64.b64decode(image_base64)
                            img = Image.open(BytesIO(image_data))
                            
                            width, height = img.size
                            print(f"         Original size: {width}x{height}px")
                            
                            # MINIMAL CROP - Only 5% each side to keep ALL text intact! 
                            crop_left = int(width * 0.05)
                            crop_right = int(width * 0.95)
                            crop_top = int(height * 0.05)
                            crop_bottom = int(height * 0.95)
                            
                            print(f"         Crop:  left={crop_left}, right={crop_right}, top={crop_top}, bottom={crop_bottom}")
                            
                            img_cropped = img.crop((crop_left, crop_top, crop_right, crop_bottom))
                            
                            crop_width, crop_height = img_cropped.size
                            print(f"         Cropped size: {crop_width}x{crop_height}px")
                            
                            # SAVE DEBUG IMAGE
                            try:
                                img_cropped.save('screenshots/captcha_cropped_debug.png')
                                print(f"         ✅ SAVED:  screenshots/captcha_cropped_debug.png")
                                print(f"         📤 This is the image sent to CapMonster!")
                            except: 
                                pass
                            
                            buffered = BytesIO()
                            img_cropped.save(buffered, format="PNG")
                            image_base64_cropped = base64.b64encode(buffered.getvalue()).decode('utf-8')
                            
                            print(f"      Crop completed!")
                            
                        except Exception as crop_error: 
                            print(f"      Crop failed: {str(crop_error)[:50]}")
                            print(f"      Using original image")
                            image_base64_cropped = image_base64
                        
                        # Send to CapMonster
                        print(f"\n      Sending to CapMonster API (attempt {attempt})...")
                        solution = self.capmonster.solve_image_captcha(image_base64_cropped)
                        
                        if not solution:
                            print("      ERROR: No solution from CapMonster")
                            raise Exception("No solution")
                        
                        print(f"      CapMonster solved:  {solution}")
                        
                        # Find input field
                        print("\n      Looking for input field...")
                        
                        captcha_input = None
                        input_selectors = [
                            (By.CSS_SELECTOR, "input[placeholder*='Verification']"),
                            (By.CSS_SELECTOR, "input[placeholder*='answer']"),
                            (By. NAME, "guess"),
                            (By.ID, "captchaGuess"),
                            (By. XPATH, "//input[@type='text']"),
                            (By.XPATH, "//label[contains(text(), 'Type the characters')]/following:: input[1]"),
                        ]
                        
                        for i, (by, selector) in enumerate(input_selectors, 1):
                            try: 
                                captcha_input = self.driver.find_element(by, selector)
                                print(f"      Found input field!")
                                break
                            except:
                                continue
                        
                        if not captcha_input:
                            raise Exception("No input field")
                        
                        # Enter solution
                        print(f"\n      Entering solution:  {solution}")
                        
                        captcha_input.click()
                        time.sleep(0.2)  # Reduced
                        
                        try:
                            captcha_input.clear()
                        except:
                            pass
                        
                        time.sleep(0.1)  # Reduced
                        
                        for char in solution:
                            captcha_input.send_keys(char)
                            time.sleep(random.uniform(0.08, 0.15))  # Fast typing! 
                        
                        print("      Solution entered")
                        
                        # Submit
                        print("\n      Submitting...")
                        
                        submit_found = False
                        submit_selectors = [
                            (By. XPATH, "//button[contains(text(), 'Submit')]"),
                            (By. XPATH, "//button[contains(text(), 'Verify')]"),
                            (By. CSS_SELECTOR, "button[type='submit']"),
                        ]
                        
                        for by, selector in submit_selectors: 
                            try:
                                submit_btn = self.driver.find_element(by, selector)
                                
                                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_btn)
                                time.sleep(0.3)  # Reduced
                                
                                try:
                                    self.driver.execute_script("arguments[0].click();", submit_btn)
                                    print("      Submitted (JS click)")
                                    submit_found = True
                                    break
                                except:
                                    submit_btn.click()
                                    print("      Submitted (normal click)")
                                    submit_found = True
                                    break
                            except:
                                continue
                        
                        if not submit_found:
                            print("      WARNING: No submit button, pressing Enter...")
                            captcha_input.send_keys(Keys. RETURN)
                            print("      Submitted via Enter")
                        
                        # Check result
                        print("\n      Waiting for result...")
                        time.sleep(2)  # Reduced from 3s
                        
                        try:
                            still_there = self.driver.find_element(By. XPATH, "//*[contains(text(), 'Security Verification')]")
                            
                            print(f"\n      ERROR:  ATTEMPT {attempt} FAILED!")
                            print(f"         Solution '{solution}' was INCORRECT")
                            
                            if attempt < max_retries:
                                print(f"\n      Retrying... ({attempt + 1}/{max_retries})")
                                time.sleep(1)
                                continue
                            else:
                                raise Exception(f"Failed after {max_retries} attempts")
                        
                        except: 
                            print(f"\n      SUCCESS: CAPTCHA SOLVED on attempt {attempt}!")
                            print(f"         Correct solution: {solution}")
                            return True
                    
                    except Exception as attempt_error:
                        if attempt >= max_retries:
                            print(f"\n      ERROR: All {max_retries} attempts exhausted")
                            print(f"      Error: {str(attempt_error)[:100]}")
                            print("      Falling back to MANUAL solving...")
                            break
                        else:
                            print(f"      WARNING: Attempt {attempt} error: {str(attempt_error)[:50]}")
                            continue
            
            else:
                print("\n   WARNING: CapMonster not configured!")
            
            # Manual fallback
            print("\n" + "="*70)
            print("WARNING:  CAPTCHA - MANUAL SOLVING REQUIRED")
            print("="*70)
            print("Please solve the captcha in the browser")
            print("Then press Enter to continue...")
            print("="*70 + "\n")
            
            self.driver.save_screenshot("screenshots/captcha_manual_aws.png")
            print("   Screenshot:  screenshots/captcha_manual_aws.png\n")
            
            input("   >>> Press Enter after solving...  ")
            print("\n   Continuing...")
            time.sleep(1)  # Reduced
            
            return True
            
        except Exception as e: 
            print(f"\n   ERROR:  Captcha error: {str(e)[:100]}")
            return True
    
    def navigate_to_ec2_tokyo(self):
        """Navigate to EC2 Tokyo - OPTIMIZED"""
        try:
            print("Navigating to EC2 Tokyo...")
            self.driver.get("https://ap-northeast-1.console.aws.amazon.com/ec2")
            time.sleep(3)  # Reduced from 5s
            return True
        except: 
            return False