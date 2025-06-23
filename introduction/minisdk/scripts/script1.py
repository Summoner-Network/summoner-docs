class Agent:

    def __init__(self):
        self.behavior = None
        self.memory = None

    def send(self):
        return self.behavior(self.memory)

    def receive(self, msg):
        self.memory = msg
    
    def code(self):
        def decorator(fn):
            self.behavior = fn
        return decorator
    
myagent = Agent()

@myagent.code()
def my_agent_behavior(msg):
    print(f"About to send the message: {msg!r}")
    return msg

if __name__ == "__main__":
    
    msg = "Hello World!"

    myagent.receive(msg)

    # ... anything can happen here ...

    new_msg = myagent.send()

    # ... use new_msg as desired ...

    print(new_msg)