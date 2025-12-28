from locust import HttpUser, task, between

class TronwallUser(HttpUser):
    wait_time = between(0.1, 0.5) # 100-500 kullanıcı simülasyonu için düşük bekleme

    @task
    def visit(self):
        self.client.get("/")
