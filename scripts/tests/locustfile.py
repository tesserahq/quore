from locust import HttpUser, task


class HelloWorldUser(HttpUser):
    @task
    def users(self):
        self.client.get("/users")
