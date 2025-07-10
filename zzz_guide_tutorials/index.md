# Tutorials

- [ ] Keep having in mind: chat agent <--> agent
- [ ] Explain core versus sdk



- config
- send None does not send (escape the loop)
- travel and quit:

    This will dominate if self.host/port is None or null:
    ```
    def run(
                self, 
                host: str = '127.0.0.1', 
                port: int = 8888, 
                config_path = ""
            )
    ```
    self.host/port are logical intents
    default is safe place to fall back to