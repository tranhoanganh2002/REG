from capmonster_python import RecaptchaV2Task
import time
import requests

class CapMonsterSolver: 
    def __init__(self, api_key):
        self.api_key = api_key
    
    def solve_recaptcha_v2(self, website_url, website_key):
        """Giai reCAPTCHA v2"""
        try:
            print("   🤖 Dang giai reCAPTCHA v2...")
            
            capmonster = RecaptchaV2Task(self.api_key)
            task_id = capmonster.create_task(
                website_url=website_url,
                website_key=website_key
            )
            
            print(f"   ⏳ Task ID: {task_id}, dang cho ket qua...")
            result = capmonster.join_task_result(task_id)
            
            print("   ✅ Da giai captcha thanh cong!")
            return result. get("gRecaptchaResponse")
            
        except Exception as e:
            print(f"   ❌ Loi giai captcha: {e}")
            return None
    
    def solve_hcaptcha(self, website_url, website_key):
        """Giai hCaptcha - Dung RecaptchaV2 thay the"""
        try:
            print("   🤖 Dang giai hCaptcha (dung RecaptchaV2 API)...")
            return self.solve_recaptcha_v2(website_url, website_key)
        except Exception as e:
            print(f"   ❌ Loi:  {e}")
            return None
    
    def solve_image_captcha(self, image_base64):
        """Giai image/text captcha - AWS captcha"""
        try:
            print("      🤖 Dang gui captcha den CapMonster API...")
            
            # Create task via API
            create_url = "https://api.capmonster.cloud/createTask"
            create_data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "ImageToTextTask",
                    "body": image_base64,
                    "case": False,
                    "minLength": 4,
                    "maxLength":  8
                }
            }
            
            response = requests.post(create_url, json=create_data, timeout=30)
            result = response.json()
            
            if result.get('errorId') != 0:
                error_desc = result.get('errorDescription', 'Unknown error')
                print(f"      ❌ Loi API: {error_desc}")
                return None
            
            task_id = result.get('taskId')
            print(f"      ⏳ Task ID: {task_id}, dang cho ket qua...")
            
            # Get result
            get_url = "https://api.capmonster.cloud/getTaskResult"
            
            for attempt in range(30):  # Max 60 seconds
                time.sleep(2)
                
                get_data = {
                    "clientKey": self.api_key,
                    "taskId": task_id
                }
                
                response = requests.post(get_url, json=get_data, timeout=30)
                result = response.json()
                
                status = result.get('status')
                
                if status == 'ready':
                    solution = result.get('solution', {}).get('text')
                    if solution:
                        print(f"      ✅ Captcha da giai:  {solution}")
                        return solution
                    else:
                        print("      ❌ Khong co solution")
                        return None
                
                elif status == 'processing': 
                    print(f"      Dang xu ly...  ({attempt + 1}/30)")
                else:
                    error_desc = result.get('errorDescription', 'Unknown')
                    print(f"      ❌ Loi:  {error_desc}")
                    return None
            
            print("      ❌ Timeout - qua 60 giay")
            return None
            
        except Exception as e: 
            print(f"      ❌ Loi CapMonster:  {str(e)[:100]}")
            return None