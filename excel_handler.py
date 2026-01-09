import pandas as pd
import os

class ExcelHandler:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        
        # Check if file exists
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"Excel file not found:  {excel_path}")
        
        # Load Excel
        self.df = pd.read_excel(excel_path)
        
        print(f"Excel path: {excel_path}")
        print(f"File exists: {os.path.exists(excel_path)}")
        print(f"Loaded {len(self.df)} rows from Excel")
        
        # Print first row for debugging
        if len(self.df) > 0:
            first_row = self.df.iloc[0]
            profile_id = first_row.get('profile_id', first_row.get('profile_name', 'N/A'))
            email = first_row.get('gmail', first_row.get('email', 'N/A'))
            
            print(f"✅ Profile:  {profile_id}")
            print(f"   Email: {email}")
            
            # Show available columns
            print(f"   Available columns: {', '.join(self.df.columns. tolist())}")
    
    def get_total_accounts(self):
        """Lấy tổng số accounts"""
        return len(self.df)
    
    def get_account_data(self, index):
        """Lấy dữ liệu account từ Excel - SUPPORT PROFILE NAME"""
        try:
            if index >= len(self.df):
                print(f"Index {index} out of range (total: {len(self.df)})")
                return None
            
            row = self.df.iloc[index]
            
            # Helper function to safely get value
            def safe_get(key, default=''):
                try:
                    val = row. get(key, default)
                    if pd.isna(val) or val == '' or val is None:
                        return default
                    return str(val).strip()
                except:
                    return default
            
            # Get profile identifier (support both profile_id and profile_name)
            profile_id = safe_get('profile_id')
            profile_name = safe_get('profile_name')
            
            # Use whichever is available (prefer profile_name if both exist)
            profile_identifier = profile_name if profile_name else profile_id
            
            if not profile_identifier:
                print(f"⚠️ Row {index}: No profile_id or profile_name found")
                return None
            
            # Build account dict with safe gets
            account = {
                # Profile (support both ID and name)
                'profile_id': profile_identifier,
                'profile_name':  profile_identifier,
                
                # Required
                'proxy':  safe_get('proxy'),
                
                # Gmail (optional - will be bought from gmail94)
                'gmail': safe_get('gmail'),
                'gmail_password': safe_get('gmail_password'),
                
                # AWS
                'aws_account_name': safe_get('aws_account_name'),
                'aws_email': safe_get('aws_email'),
                'aws_password': safe_get('aws_password'),
                'aws_account_id': safe_get('aws_account_id'),
                
                # Gmail94 order
                'order_id': safe_get('order_id'),
                
                # Payment info
                'card_number': safe_get('card_number'),
                'card_expiry': safe_get('card_expiry'),
                'card_cvv': safe_get('card_cvv'),
                'card_name': safe_get('card_name'),
                
                # Billing address
                'billing_address': safe_get('billing_address'),
                'city': safe_get('city'),
                'state': safe_get('state', 'CA'),
                'zip_code':  safe_get('zip_code'),
                'country': safe_get('country', 'US'),
                
                # Contact
                'phone': safe_get('phone'),
                'account_type': safe_get('account_type', 'Personal'),
                
                # Status
                'status': safe_get('status'),
            }
            
            return account
            
        except Exception as e: 
            print(f"❌ Error getting account data at index {index}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def update_status(self, index, status, **kwargs):
        """Cập nhật status và các field khác"""
        try: 
            if index >= len(self. df):
                print(f"Cannot update:  index {index} out of range")
                return False
            
            # Update status
            if 'status' in self.df.columns:
                self.df.at[index, 'status'] = status
            else:
                self.df['status'] = ''
                self.df.at[index, 'status'] = status
            
            # Update additional fields
            for key, value in kwargs.items():
                if key in self.df. columns:
                    self.df.at[index, key] = value
                else:
                    # Add new column if doesn't exist
                    self.df[key] = ''
                    self.df.at[index, key] = value
            
            # Save to Excel
            self.df.to_excel(self.excel_path, index=False)
            
            print(f"   Updated status:  {status}")
            
            return True
            
        except Exception as e:
            print(f"Error updating status: {e}")
            return False
    
    def update_account_data(self, index, data_dict):
        """Cập nhật nhiều field cùng lúc"""
        try:
            if index >= len(self.df):
                print(f"Cannot update: index {index} out of range")
                return False
            
            for key, value in data_dict. items():
                if key in self.df.columns:
                    self.df.at[index, key] = value
                else: 
                    # Add new column
                    self.df[key] = ''
                    self.df.at[index, key] = value
            
            # Save
            self.df.to_excel(self.excel_path, index=False)
            
            return True
            
        except Exception as e:
            print(f"Error updating account data: {e}")
            return False