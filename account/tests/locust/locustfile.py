from locust import HttpUser, task


class User(HttpUser):

    @task(2)
    def get_list_doctor(self):
        self.client.get('/ping', headers={
            'Authorization': f'Bearer {self.token}'
        })

    @task(1)
    def get_me(self):
        self.client.get('/users', headers={
            'Authorization': f'Bearer {self.token}'
        })


    def on_start(self):
        response = self.client.post('/login', json={
            'email': 'legen2a208@gmail.com',
            'password': 'legen2a777'
        })
        self.token = response.json().get('data')['access_token']
