class Agent:

    def __init__(self):
        self.send_behavior = None
        self.receive_behavior = None
        self.memory = []

    def send(self):
        def decorator(fn):
            self.send_behavior = fn
        return decorator

    def receive(self, msg):
        def decorator(fn):
            self.receive_behavior = fn
        return decorator


def server(*agents: Agent):
    while True:

        traffic = []
        for agent in agents:
            msg = agent.send_behavior()
            if msg not in ["", None]:
                traffic.append(msg)
                print(f"{msg!r} sent")

        if traffic == []:
            break

        traffic = [agent.receive_behavior(msg) for agent in agents for msg in traffic]