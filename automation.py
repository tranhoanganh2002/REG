import pandas as pd
import logging
import time
from src.gpm_browser_playwright import GPMBrowserPlaywright as GPMBrowser
from src.aws_register import AWSRegister
from src.capmonster_solver import CapMonsterSolver
from src.codesim_api import CodeSimAPI
from src.gmail94_api import Gmail94API
from src.aws_register_playwright import AWSRegisterPlaywright

class AWSAutomation: 
    def __init__(self, excel_path, capmonster_key, codesim_key, gmail94_token, gpm_config=None):
        """
        Initialize AWS Automation
        
        Args:
            excel_path:  Path to Excel file with account data
            capmonster_key: CapMonster API key (optional)
            codesim_key: CodeSim API key (optional)
            gmail94_token:  Gmail94 API token (required)
            gpm_config: GPM configuration dict (optional)
        """
        self. excel_path = excel_path
        self.capmonster_key = capmonster_key
        self.codesim_key = codesim_key
        self.gmail94_token = gmail94_token
        
        # Initialize Gmail94 API object
        if gmail94_token:
            logging.info("   Initializing Gmail94 API...")
            
            gmail94_config = {
                'api_key': gmail94_token,
                'api_token': gmail94_token,  # Support both key names
                'api_url': 'https://gmail94.com/api',
                'service': 'aws'  # ← Changed from 'amazon' to 'aws'! 
            }
            
            self.gmail94_api = Gmail94API(gmail94_config)
            logging.info("   ✅ Gmail94 API initialized successfully")
        else:
            self.gmail94_api = None
            logging.warning("   ⚠️ Gmail94 not configured - OTP will be manual")
        
        # Initialize CapMonster if key provided
        if capmonster_key:
            self.capmonster = CapMonsterSolver(capmonster_key)
            logging.info("   ✅ CapMonster initialized")
        else:
            self.capmonster = None
            logging.warning("   ⚠️ CapMonster not configured - captcha will be manual")
        
        # Initialize CodeSim if key provided
        if codesim_key: 
            self.codesim = CodeSimAPI(codesim_key)
            logging.info("   ✅ CodeSim initialized")
        else:
            self.codesim = None
            logging.warning("   ⚠️ CodeSim not configured")
        
        # Initialize GPM Browser with config
        if gpm_config:
            gpm_api_url = gpm_config.get('api_url', 'http://127.0.0.1:19995/api/v3')
            gpm_api_token = gpm_config.get('api_token')  # May be None (GPM doesn't use token)
            
            if gpm_api_token:
                self.gpm = GPMBrowser(gpm_api_url=gpm_api_url, api_token=gpm_api_token)
            else:
                self.gpm = GPMBrowser(gpm_api_url=gpm_api_url)
            
            logging.info(f"   ✅ GPM Browser initialized")
            logging.info(f"      API URL: {gpm_api_url}")
        else:
            self.gpm = GPMBrowser()
            logging.info("   ✅ GPM Browser initialized with defaults")
        
        # ============================================================
        # CHOOSE AUTOMATION ENGINE
        # ============================================================
        self.use_playwright = True  # ← SET TRUE TO USE PLAYWRIGHT! 
        
        engine_name = "PLAYWRIGHT (Stable)" if self.use_playwright else "SELENIUM (Legacy)"
        logging.info(f"\n   🤖 Automation Engine: {engine_name}")
        
        if self.use_playwright:
            logging.info("      ✅ Using Playwright - More stable, auto-wait, better selectors")
        else:
            logging.info("      ⚠️  Using Selenium - May have timeout issues")
        
    def load_accounts(self):
        """Load accounts from Excel file"""
        try: 
            logging.info(f"\n📂 Loading accounts from:  {self.excel_path}")
            
            df = pd.read_excel(self.excel_path)
            
            logging.info(f"   ✅ Loaded {len(df)} accounts")
            logging.info(f"   Columns: {', '. join(df.columns. tolist())}")
            
            return df
            
        except FileNotFoundError:
            logging. error(f"   ❌ Excel file not found: {self.excel_path}")
            return None
        except Exception as e:  
            logging.error(f"   ❌ Error loading Excel: {e}")
            return None
    
    def process_account(self, account_data):
        """
        Process a single account registration
        
        Args: 
            account_data: Dictionary with account information
        
        Returns: 
            bool: True if successful, False otherwise
        """
        # Get profile identifier
        profile_id = (account_data.get('profile_name') or
                     account_data. get('profile_id') or
                     account_data.get('proxy') or
                     'Unknown')
        
        if not profile_id or profile_id == 'Unknown':  
            logging.error(f"\n   ❌ NO VALID PROFILE IDENTIFIER!")
            logging.error(f"      Excel must have 'profile_name' or 'profile_id'")
            return False
        
        logging.info("\n" + "="*70)
        logging.info(f"🔄 PROCESSING ACCOUNT: {profile_id}")
        logging.info("="*70)
        
        # ============================================================
        # PLAYWRIGHT PATH
        # ============================================================
        if self.use_playwright:
            return self._process_with_playwright(profile_id, account_data)
        
        # ============================================================
        # SELENIUM PATH (LEGACY)
        # ============================================================
        else:
            return self._process_with_selenium(profile_id, account_data)
    
    def _process_with_playwright(self, profile_id, account_data):
        """Process account using Playwright - FIXED VERSION"""
        logging.info("   🎭 Using Playwright engine")
        
        aws_register = None
        
        try:
            # ============================================================
            # GET PROFILE INFO
            # ============================================================
            logging.info("   Getting profile info...")
            
            try:
                profile_info = self.gpm.get_profile_info(profile_id)
            except Exception as gpm_error:
                logging. error(f"   GPM error: {str(gpm_error)}")
                profile_info = None
            
            # Validate profile_info
            if not profile_info or not isinstance(profile_info, dict):
                logging.warning(f"   ⚠️ Could not get profile from GPM")
                logging.info(f"   Creating default profile path...")
                
                import os
                profile_path = os.path.abspath(f"./playwright_profiles/{profile_id}")
                os.makedirs(profile_path, exist_ok=True)
                
                logging.info(f"   Using:  {profile_path}")
            else:
                # Extract profile path from dict
                profile_path = profile_info.get('profile_path')
                
                if not profile_path: 
                    logging.warning(f"   ⚠️ No profile_path in response")
                    
                    import os
                    profile_path = os.path.abspath(f"./playwright_profiles/{profile_id}")
                    os.makedirs(profile_path, exist_ok=True)
                    
                    logging.info(f"   Using default:  {profile_path}")
                else:
                    logging.info(f"   ✅ Profile path: {profile_path}")
                    
                    # Check if path exists, if not create it
                    import os
                    if not os. path.exists(profile_path):
                        logging.warning(f"   Path doesn't exist, creating...")
                        os.makedirs(profile_path, exist_ok=True)
            
            # ============================================================
            # INITIALIZE PLAYWRIGHT
            # ============================================================
            logging.info("   Initializing Playwright...")
            
            config = {
                'gmail94_api_token': self.gmail94_token,
                'profile_path': profile_path,
            }
            
            aws_register = AWSRegisterPlaywright(config, self.gmail94_api)
            
            # ============================================================
            # SETUP BROWSER
            # ============================================================
            logging.info("   Setting up Playwright browser...")
            
            if not aws_register.setup_browser(profile_path):
                logging.error("   ❌ Failed to setup browser")
                return False
            
            logging.info("   ✅ Browser started successfully")
            time.sleep(2)
            
            # ============================================================
            # RUN REGISTRATION STEPS
            # ============================================================
            logging.info("\n   Starting AWS registration flow...")
            
            # Step 1: Navigate to AWS signup
            logging.info("\n   → Step 1: Navigate to signup page")
            if not aws_register.start_registration(account_data):
                logging.error("   ❌ Step 1 failed (Navigation)")
                return False
            
            logging.info("   ✅ Step 1 completed")
            
            # Step 2: Fill account info (email + account name)
            logging.info("\n   → Step 2: Fill account information")
            if not aws_register.fill_account_info(account_data):
                logging.error("   ❌ Step 2 failed (Fill form)")
                return False
            
            logging.info("   ✅ Step 2 completed")
            
            # Step 3:  Verify email with OTP
            logging.info("\n   → Step 3: Verify email")
            if not aws_register. verify_email_with_otp(account_data):
                logging.error("   ❌ Step 3 failed (Email verification)")
                return False
            
            logging.info("   ✅ Step 3 completed")
            
            # Step 4: Create password
            logging.info("\n   → Step 4: Create password")
            if not aws_register. create_password(account_data):
                logging.error("   ❌ Step 4 failed (Password)")
                return False
            
            logging.info("   ✅ Step 4 completed")
            
            # ============================================================
            # SUCCESS
            # ============================================================
            logging.info(f"\n{'='*70}")
            logging.info(f"✅ SUCCESS: Account {profile_id} registered!")
            logging.info(f"{'='*70}")
            
            return True
            
        except Exception as e:
            logging.error(f"\n❌ Error processing {profile_id}: {str(e)}")
            
            import traceback
            traceback.print_exc()
            
            return False
            
        finally:
            # ============================================================
            # CLEANUP
            # ============================================================
            if aws_register:
                try:
                    logging.info(f"\n   Closing browser...")
                    aws_register.close()
                    logging.info("   ✅ Browser closed")
                except Exception as close_error:
                    logging. warning(f"   ⚠️ Error closing browser:  {str(close_error)}")
            
            # Small delay before next account
            time.sleep(2)
    
    def _process_with_selenium(self, profile_id, account_data):
        """Process account using Selenium (legacy)"""
        logging.info("   🔧 Using Selenium engine (legacy)")
        
        driver = None
        
        try: 
            # Start GPM browser
            logging.info("   Starting GPM browser...")
            driver = self.gpm.start_profile(profile_id)
            
            if not driver:  
                logging.error("   ❌ Failed to start browser")
                return False
            
            logging.info("   ✅ Browser started successfully")
            time.sleep(3)
            
            # Initialize AWS Register (Selenium)
            aws_register = AWSRegister(driver, self.capmonster, self. codesim)
            aws_register.gmail94_api = self.gmail94_api
            
            if self.gmail94_api:
                logging.info("   ✅ Gmail94 API passed to AWSRegister")
            
            # Start registration
            success = aws_register.start_registration(account_data)
            
            if success: 
                logging.info(f"\n✅ SUCCESS:  Account {profile_id} registered!")
                return True
            else:  
                logging.error(f"\n❌ FAILED:  Registration failed")
                return False
                
        except Exception as e: 
            logging.error(f"\n❌ Error:  {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            # Close browser
            if driver:
                try:
                    logging.info(f"\n   Closing browser...")
                    self.gpm. stop_profile(profile_id)
                    logging.info("   ✅ Browser closed")
                except Exception as close_error: 
                    logging.warning(f"   ⚠️ Error closing: {close_error}")
    
    def run_all(self):
        """Process all accounts from Excel"""
        # Load accounts
        df = self.load_accounts()
        
        if df is None or df.empty:
            logging. error("❌ No accounts to process")
            return
        
        total = len(df)
        success_count = 0
        failed_count = 0
        
        logging.info("\n" + "="*70)
        logging.info(f"🚀 STARTING BATCH REGISTRATION - {total} ACCOUNTS")
        logging.info("="*70)
        
        # Process each account
        for index, row in df.iterrows():
            account_num = index + 1
            
            logging.info(f"\n\n{'='*70}")
            logging.info(f"📋 ACCOUNT {account_num}/{total}")
            logging.info(f"{'='*70}")
            
            # Convert row to dict
            account_data = row.to_dict()
            
            # Process account
            success = self.process_account(account_data)
            
            if success: 
                success_count += 1
            else:
                failed_count += 1
            
            # Wait between accounts
            if account_num < total:
                wait_time = 10
                logging.info(f"\n   ⏳ Waiting {wait_time}s before next account...")
                time.sleep(wait_time)
        
        # Summary
        logging.info("\n\n" + "="*70)
        logging.info("📊 BATCH REGISTRATION SUMMARY")
        logging.info("="*70)
        logging.info(f"   Total accounts:  {total}")
        logging.info(f"   ✅ Successful: {success_count}")
        logging.info(f"   ❌ Failed: {failed_count}")
        logging.info(f"   Success rate:  {(success_count/total*100):.1f}%")
        logging.info("="*70)