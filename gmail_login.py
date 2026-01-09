from selenium. webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

class GmailLogin:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)
    
    def login(self, email, password):
        """Login vào Gmail - FULL FIX"""
        try:
            print(f"\n{'='*70}")
            print(f"🔐 GMAIL LOGIN")
            print(f"{'='*70}\n")
            
            print(f"📧 Email: {email}")
            
            # === FORCE NAVIGATE ===
            print(f"🌐 Navigating to Google login...")
            
            target_url = "https://accounts.google.com/signin"
            max_retries = 3
            
            for attempt in range(max_retries):
                print(f"\n   Attempt {attempt + 1}/{max_retries}")
                
                self.driver.get(target_url)
                time.sleep(8)
                
                current_url = self.driver.current_url
                print(f"   Current URL: {current_url}")
                
                if "accounts.google.com" in current_url:
                    print(f"   ✅ Navigation successful!")
                    break
                elif "google.com" in current_url and "accounts" not in current_url:
                    print(f"   ⚠️ On Google homepage, trying again...")
                    continue
                else:
                    print(f"   ⚠️ Unexpected URL, trying again...")
                    continue
            else:
                print(f"\n❌ Cannot navigate to Google Accounts!")
                print(f"   Final URL: {self.driver.current_url}")
                self.driver.save_screenshot("navigation_failed.png")
                return False
            
            print(f"\n📍 Current URL: {self.driver.current_url}")
            print(f"📄 Page title: {self.driver.title}")
            
            # === NHẬP EMAIL ===
            print(f"\n📧 Step 1: Entering email...")
            
            try:
                email_input = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
                )
            except: 
                print(f"❌ Email input not found!")
                self.driver.save_screenshot("email_input_not_found. png")
                return False
            
            print(f"   ✅ Found email input!")
            
            # Scroll to view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", email_input)
            time.sleep(2)
            
            # Wait until clickable
            try:
                email_input = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By. CSS_SELECTOR, "input[type='email']"))
                )
            except:
                pass
            
            # Click multiple times to ensure focus
            print(f"   Clicking email input...")
            for _ in range(3):
                try:
                    email_input.click()
                except:
                    self.driver.execute_script("arguments[0].click();", email_input)
                time.sleep(0.5)
            
            # Clear using multiple methods
            print(f"   Clearing input...")
            try:
                email_input.clear()
            except:
                pass
            
            # Clear with Ctrl+A + Delete
            try: 
                email_input.send_keys(Keys.CONTROL + "a")
                email_input. send_keys(Keys.DELETE)
            except:
                pass
            
            time.sleep(1)
            
            # Type email - VERY SLOW
            print(f"   Typing:  {email}")
            for i, char in enumerate(email):
                email_input.send_keys(char)
                time.sleep(0.15)  # 150ms per character
                
                # Every 5 characters, check if still there
                if (i + 1) % 5 == 0:
                    current_value = email_input.get_attribute('value')
                    if not current_value:
                        print(f"   ⚠️ Input cleared! Re-focusing...")
                        email_input.click()
                        time.sleep(0.5)
            
            time.sleep(2)
            
            # Verify email was entered
            final_value = email_input.get_attribute('value')
            print(f"   Input value: '{final_value}'")
            
            if not final_value or email not in final_value: 
                print(f"   ⚠️ Email not in input! Trying JavaScript...")
                
                # Use JavaScript to set value
                self.driver.execute_script(f"arguments[0].value = '{email}';", email_input)
                time.sleep(1)
                
                # Trigger input events
                self.driver.execute_script("""
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('blur', { bubbles:  true }));
                """, email_input)
                time.sleep(1)
                
                final_value = email_input.get_attribute('value')
                print(f"   After JS: '{final_value}'")
            
            if not final_value: 
                print(f"   ❌ Cannot enter email!")
                self.driver.save_screenshot("cannot_enter_email.png")
                return False
            
            print(f"   ✅ Email entered successfully!")
            
            # Wait before clicking Next
            time.sleep(3)
            
            # Find and click Next button
            print(f"   Looking for Next button...")
            
            try:
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "identifierNext"))
                )
            except:
                # Try XPath
                try:
                    next_button = self.driver.find_element(By. XPATH, "//button[@type='button' and . //span[text()='Tiếp theo' or text()='Next']]")
                except: 
                    print(f"   ❌ Next button not found!")
                    self.driver. save_screenshot("next_button_not_found.png")
                    return False
            
            print(f"   ✅ Found Next button, clicking...")
            
            # Scroll to button
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(1)
            
            # Click
            try: 
                next_button.click()
            except:
                self. driver.execute_script("arguments[0].click();", next_button)
            
            print(f"   Waiting for password page...")
            time.sleep(15)  # Wait 15 seconds
            
            current_url = self.driver.current_url
            print(f"\n📍 After email: {current_url}")
            
            # Check if still on email page
            if "identifier" in current_url and "challenge" not in current_url:
                print(f"⚠️ Still on email page!")
                
                # Check for error message
                try:
                    error_elem = self.driver.find_element(By.CSS_SELECTOR, "[role='alert'], . error-msg, [aria-live='assertive']")
                    error_text = error_elem.text
                    print(f"   Error message: {error_text}")
                except:
                    print(f"   No error message found")
                
                self.driver.save_screenshot("stuck_on_email_page.png")
                
                with open("stuck_email_page_source.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                
                return False
            
            # === NHẬP PASSWORD ===
            print(f"\n🔑 Step 2: Entering password...")
            
            try:
                password_input = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
                )
            except: 
                print(f"❌ Password input not found!")
                print(f"   URL: {self.driver.current_url}")
                self.driver. save_screenshot("password_input_not_found.png")
                
                with open("password_page_source.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                
                return False
            
            print(f"   ✅ Found password input!")
            
            # Scroll to input
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", password_input)
            time.sleep(2)
            
            # Wait until clickable
            try:
                password_input = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By. CSS_SELECTOR, "input[type='password']"))
                )
            except:
                pass
            
            # Click to focus
            print(f"   Clicking password input...")
            for _ in range(3):
                try:
                    password_input.click()
                except:
                    self. driver.execute_script("arguments[0].click();", password_input)
                time.sleep(0.5)
            
            # Clear
            print(f"   Clearing input...")
            try:
                password_input.clear()
            except:
                pass
            
            try:
                password_input.send_keys(Keys.CONTROL + "a")
                password_input.send_keys(Keys.DELETE)
            except:
                pass
            
            time.sleep(1)
            
            # Type password - VERY SLOW
            print(f"   Typing password...")
            for i, char in enumerate(password):
                password_input.send_keys(char)
                time.sleep(0.12)  # 120ms per character
                
                # Every 5 characters, check
                if (i + 1) % 5 == 0:
                    current_value = password_input.get_attribute('value')
                    if not current_value:
                        print(f"   ⚠️ Input cleared! Re-focusing...")
                        password_input.click()
                        time.sleep(0.5)
            
            time. sleep(2)
            
            # Verify password entered
            final_value = password_input.get_attribute('value')
            
            if not final_value: 
                print(f"   ⚠️ Password not in input!  Trying JavaScript...")
                
                self.driver.execute_script(f"arguments[0].value = '{password}';", password_input)
                time.sleep(1)
                
                self.driver.execute_script("""
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                """, password_input)
                time.sleep(1)
            
            print(f"   ✅ Password entered!")
            
            # Wait before Next
            time.sleep(3)
            
            # Find Next button
            print(f"   Looking for Next button...")
            
            try:
                next_button = WebDriverWait(self. driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "passwordNext"))
                )
            except:
                try:
                    next_button = self.driver.find_element(By.XPATH, "//button[@type='button' and .//span[text()='Tiếp theo' or text()='Next']]")
                except: 
                    print(f"   ❌ Next button not found!")
                    self.driver.save_screenshot("password_next_not_found.png")
                    return False
            
            print(f"   ✅ Found Next button, clicking...")
            
            # Scroll & click
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(1)
            
            try:
                next_button.click()
            except:
                self.driver. execute_script("arguments[0]. click();", next_button)
            
            # Wait for login
            print(f"   Waiting for login...")
            time.sleep(15)
            
            # Check result
            current_url = self. driver.current_url
            print(f"\n📍 Final URL: {current_url}")
            print(f"📄 Final title: {self.driver.title}")
            
            # Success
            if any(domain in current_url for domain in ["myaccount.google.com", "mail.google.com", "ManageAccount"]):
                print(f"\n{'='*70}")
                print(f"✅ GMAIL LOGIN SUCCESSFUL!")
                print(f"{'='*70}\n")
                return True
            
            # Verification needed
            elif any(keyword in current_url for keyword in ["challenge", "verify", "signin/v2/challenge"]):
                print(f"\n{'='*70}")
                print(f"⚠️ VERIFICATION REQUIRED!")
                print(f"   (2FA, phone verification, or security check)")
                print(f"{'='*70}\n")
                self.driver.save_screenshot("verification_required.png")
                return False
            
            # Error
            elif "error" in current_url or "denied" in current_url:
                print(f"\n{'='*70}")
                print(f"❌ LOGIN FAILED!")
                print(f"   Google blocked or rejected login")
                print(f"{'='*70}\n")
                self.driver.save_screenshot("login_failed.png")
                return False
            
            # Uncertain
            else:
                print(f"\n{'='*70}")
                print(f"⚠️ LOGIN STATUS UNCERTAIN")
                print(f"{'='*70}\n")
                self.driver.save_screenshot("login_uncertain.png")
                
                # Check for error messages
                try:
                    error_elem = self.driver.find_element(By.CSS_SELECTOR, "[role='alert'], . error-msg")
                    print(f"   Error:  {error_elem.text}")
                except:
                    pass
                
                return False
                
        except Exception as e: 
            print(f"\n{'='*70}")
            print(f"❌ EXCEPTION DURING LOGIN!")
            print(f"{'='*70}")
            print(f"{e}\n")
            
            try:
                self.driver.save_screenshot("gmail_exception.png")
                print(f"Screenshot:  gmail_exception.png")
                
                with open("exception_page_source.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print(f"Page source:  exception_page_source.html")
            except:
                pass
            
            import traceback
            traceback.print_exc()
            
            return False