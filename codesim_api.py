import requests
import time
import re

class CodeSimAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self. base_url = "https://codesim.net/api"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_phone_number(self, service="aws"):
        """
        Thuê số điện thoại
        service: dịch vụ cần thuê số (aws, google, facebook, etc.)
        """
        try:
            endpoint = f"{self.base_url}/phone/order"
            payload = {
                "service": service,
                "country": "US"  # Hoặc country khác
            }
            
            response = requests.post(endpoint, json=payload, headers=self. headers)
            data = response.json()
            
            if data.get("status") == "success":
                return {
                    "session_id": data["data"]["session_id"],
                    "phone_number": data["data"]["phone"],
                    "formatted_phone": data["data"]["formatted_phone"]
                }
            else: 
                print(f"❌ Lỗi thuê số: {data.get('message')}")
                return None
                
        except Exception as e:
            print(f"❌ Lỗi API CodeSim: {e}")
            return None
    
    def get_sms_code(self, session_id, timeout=120):
        """
        Lấy mã SMS
        timeout: thời gian chờ tối đa (giây)
        """
        start_time = time.time()
        endpoint = f"{self.base_url}/phone/sms/{session_id}"
        
        print("📱 Đang chờ SMS...")
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(endpoint, headers=self.headers)
                data = response.json()
                
                if data. get("status") == "success" and data.get("data", {}).get("sms"):
                    sms_list = data["data"]["sms"]
                    if sms_list:
                        # Lấy SMS mới nhất
                        latest_sms = sms_list[-1]
                        message = latest_sms. get("message", "")
                        
                        # Trích xuất mã (thường là 6 số)
                        codes = re.findall(r'\b\d{6}\b', message)
                        if codes:
                            print(f"✅ Nhận được mã:  {codes[0]}")
                            return codes[0]
                
                time.sleep(5)  # Chờ 5 giây trước khi thử lại
                
            except Exception as e:
                print(f"⚠️ Lỗi khi lấy SMS: {e}")
                time. sleep(5)
        
        print("❌ Timeout:  Không nhận được SMS")
        return None
    
    def cancel_session(self, session_id):
        """Hủy phiên thuê số"""
        try: 
            endpoint = f"{self.base_url}/phone/cancel/{session_id}"
            requests.post(endpoint, headers=self.headers)
            print("🗑️ Đã hủy session")
        except: 
            pass