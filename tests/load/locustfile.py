from locust import HttpUser, task, between
from faker import Faker

fake = Faker()

class ShortLinkUser(HttpUser):
    def on_start(self):
        email = fake.email()  # Генерирует случайный email
        password = "test123"
        
        # Регистрация
        self.client.post(
            "/register",
            json={"email": email, "password": password}
        )


    @task
    def create_link(self):
        self.client.post(
            "/links/shorten",
            json={"original_url": "https://example.com"},
        )
