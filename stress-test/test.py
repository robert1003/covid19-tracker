from locust import HttpUser, TaskSet, task
from random import randint, seed
import json, time


class WebsiteTasks(TaskSet):
    
    types, idx, token = 0, 0, 0
    idx_list = []
    user_phonenum = []
    user_password = []
    store_phonenum = []
    store_password = []
    store_store_id = []

    def on_start(self):
        self._signup()
        self._login()

    def _signup(self):
        self.type, self.idx = len(self.idx_list) % 2, len(self.idx_list) // 2
        self.idx_list.append(0)
        if self.type == 0:   # user
            self.user_phonenum.append(0)
            self.user_password.append(0)
            while 1:
                try:
                    self.user_phonenum[self.idx] = str(randint(0, 1000000000000000))
                    self.user_password[self.idx] = str(randint(0, 1000000000000000))
                    ph, ps, val = self.user_phonenum[self.idx], self.user_password[self.idx], {}
                    val['phone'], val['password'] = ph, ps
                    res = self.client.post('/auth/user/signup', data=json.dumps(val))
                    print(val)
                    print('user sign up', res.status_code)
                    if res.status_code == 200:
                        res=res.json()
                        print('user sign up', res, flush=True)
                        break
                    else:
                        print(self.idx, res.text)
                except Exception as e:
                    print('User Signup Error', e, flush=True)
        else:
            self.store_phonenum.append(0)
            self.store_password.append(0)
            self.store_store_id.append(0)
            while 1:
                try:
                    self.store_phonenum[self.idx] = str(randint(0, 1000000000000000))
                    self.store_password[self.idx] = str(randint(0, 1000000000000000))
                    ph, ps, val = self.store_phonenum[self.idx], self.store_password[self.idx], {}
                    val['phone'], val['password'] = ph, ps
                    val['name'], val['address'] = 'giver', 'taiwan'
                    res = self.client.post('/auth/store/signup', data=json.dumps(val))
                    print(val)
                    print('store sign up', res.status_code)
                    if res.status_code == 200:
                        res=res.json()
                        print('Store Sign up', res, flush=True)
                        break
                    else:
                        print(self.idx, res.text)
                except Exception as e:
                    print('Store Signup Error', e, flush=True)

    def _login(self):
        print('self.idx: ', self.type, self.idx)
        if self.type == 0: # user
            while 1:
                try:
                    ph, ps, val = self.user_phonenum[self.idx], self.user_password[self.idx], {}
                    val['phone'], val['password'] = ph, ps
                    res = self.client.post('/auth/user/login', data=json.dumps(val)).json()
                    self.token = res['token']
                    print('User login: ', res, flush=True)
                    break
                except Exception as e:
                    print('User Login Error', e, flush=True)
                    pass
        else:
            while 1:
                try:
                    ph, ps, val = self.store_phonenum[self.idx], self.store_password[self.idx], {}
                    val['phone'], val['password'] = ph, ps
                    res = self.client.post('/auth/store/login', data=json.dumps(val)).json()
                    print('Store login: ', res)
                    self.token = res['token']
                    break
                except Exception as e:
                    print('Store Login Error', e, flush=True)
                    pass
            while 1:
                try: 
                    headers = {'Authorization': 'Bearer ' + self.token}
                    print(headers)
                    res = self.client.get('/auth/store/profile', headers=headers).json()
                    print('res: ', res, flush=True)
                    self.store_store_id[self.idx] = res['qrcode']
                    break
                except Exception as e:
                    print('Get Qrcode Error', e, flush=True)
                    pass

    @task(1)
    def _recode(self):
        if self.type == 0: # User
            the_store_id = randint(0, len(self.store_phonenum) - 1)
            if self.store_store_id[the_store_id] == 0:
                return
            val1 = {'Authorization': 'Bearer ' + self.token}
            val2 = {'store_id': self.store_store_id[the_store_id]}
            res = {}
            try:
                res = self.client.post('/records', headers=val1, data=json.dumps(val2))
            except:
                print('Error res: ', res)


class WebsiteUser(HttpUser):
    tasks = [WebsiteTasks]
#    host = "http://linux5.csie.ntu.edu.tw:8888"
    host = 'http://autoscale-covid-tracker.default.52.203.67.181.sslip.io'
    port = 80
    min_wait = 5000
    max_wait = 15000


# curl -X POST http://linux5.csie.ntu.edu.tw:8888/auth/user/signup -d '{"phone": "0912345678", "password": "878787"}'
# curl -X POST http://linux5.csie.ntu.edu.tw:8888/auth/user/login -d '{"phone": "0912345678", "password": "878787"}'
# curl -X POST http://linux5.csie.ntu.edu.tw:8888/auth/store/signup -d '{"phone": "0987654321", "password": "87878787", "name": "giver", "address": "taiwan"}'
# curl -X POST http://linux5.csie.ntu.edu.tw:8888/auth/store/login -d '{"phone": "0987654321", "password": "87878787"}'
# curl -X GET http://linux5.csie.ntu.edu.tw:8888/auth/store/profile -H 'Authorization: Bearer <store's jwt token>'
# curl -X POST http://linux5.csie.ntu.edu.tw:8888/records -H 'Authorization: Bearer <user's jwt token>' -d '{"store_id": "0987654321"}'

