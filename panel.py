import requests
import uuid
import random
import json
from utils import load_config, get_timestamp
from datetime import datetime
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

class Panel():
    def __init__(self, url, max_users, email, password):
        self.max_users = max_users
        self.email = email
        self.password = password
        self.logger = logging.getLogger("Panel")
        self.url = url 
        r = self.login()
        if r['is_admin']:
            self.logger.info('Loggin to panel was successful.')


    def login(self):
        payload = {'email': self.email, 'password': self.password}
        url = f"{self.url}/api/v1/passport/auth/login"
        r = requests.post(url, data=payload, verify=False)
        if r.status_code!=200:
            self.logger.error('Could not login to panel.')
        return r.json()['data']
    
    def add_user(self,id,username,expiry_date,password,plan_id):
        url = f"{self.url}/api/v1/admin/user/generate"
        payload = {'email_prefix': id, 'email_suffix': username, 'expired_at':expiry_date, 'password': password, 'plan_id':plan_id}
        r = self.login()
        r = requests.post(url, data=payload, headers={'authorization':r['auth_data']}, verify=False)
        if 'data' in r.json() and r.json()['data']:
            return True, "ثبت نام با موفقیت انجام شد."
        else:
            if r.json()['message'] == "邮箱已存在于系统中":
                return False, "شما قبلا ثبت نام کرده اید."
            else:
                self.logger.info(r.json())
                return False, "مشکلی در ارتباط با سرور پیش آمده. لطفا دوباره امتحان فرمایید."

    def get_sub(self,id,username):    
        user = self.search_user_by_email_prefix(id, page_size=50)
        if user is None:
            return False, "مشکلی در ارتباط با سرور پیش آمده. لطفا بعدا امتحان فرمایید."
        return True, user['subscribe_url']
    
    def get_usage(self,id):
        user = self.search_user_by_email_prefix(id, page_size=150)
        if user is None:
            return False, "مشکلی در ارتباط با سرور پیش آمده. لطفا بعدا امتحان فرمایید."
        return True, f"{int(user['total_used'])/ 1024**3}"

    
    def search_user_by_email_prefix(self,email_prefix, page_size=50):
        current_page = 1
        r = self.login()

        while True:
            link = f"{self.url}/api/v1/admin/user/fetch?page_size={page_size}&current={current_page}"
            response = requests.get(link, headers={'authorization':r['auth_data']}, verify=False)
            users_in_page = response.json()['data']

            for user in users_in_page:
                if user['email'].split("@")[0] == email_prefix:
                    return user

            if len(users_in_page) < page_size:
                break

            current_page += 1
        
        return None

if __name__=="__main__":
    config = load_config('config.yaml')

    panel_config = config['panel']
    
    panel = Panel(**panel_config)
    panel.add_user('123','testgp',1706686371,'123',1)
