class Agent:

    def __init__(self):
        self.send_behavior = None
        self.receive_behavior = None

    def send(self):
        def decorator(fn):
            self.send_behavior = fn
        return decorator

    def receive(self):
        def decorator(fn):
            self.receive_behavior = fn
        return decorator

    
agent1 = Agent()
agent1_memory = {}

@agent1.receive()
def behavior(msg):
    global agent1_memory
    if "purpose" in msg:
        if agent1_memory is None:
            agent1_memory = {}
        if msg["purpose"] not in agent1_memory:
            print(f"Agent 1 remembers: {msg!r}")
            agent1_memory[msg["purpose"]] = msg

@agent1.send()
def behavior():
    global agent1_memory
    if not isinstance(agent1_memory, dict):
        return None

    if "function" in agent1_memory and "for" in agent1_memory["function"]:
        task = agent1_memory["function"]["for"]
    else:
        task = "sort_alpha"

    if "elements" in agent1_memory and "data" in agent1_memory["elements"]:
        data = agent1_memory["elements"]["data"]
    else:
        return None

    print(f"Agent 1 sorts data using {task!r}")
    agent1_memory = {}

    if task == "sort_alpha":
        return {"purpose": "response", "data": sorted(data)}

    elif task == "sort_length":
        return {"purpose": "response", "data": sorted(data, key=len)}

    else:
        return None
    
import random
agent2 = Agent()
agent2_memory = []

@agent2.receive()
def behavior(msg):
    global agent2_memory
    if msg is not None and msg.get("purpose") == "response":
        print(f"Agent 2 stores: {msg!r}")
        agent2_memory.append(msg)

@agent2.send()
def behavior():
    for_value = random.choice(["sort_alpha", "sort_length"])
    print(f"Agent 2 requests: {for_value}")
    return {"purpose": "function", "for": for_value}

agent3 = Agent()
agent3_memory = []

@agent3.receive()
def behavior(msg):
    global agent3_memory
    if msg is not None and msg.get("purpose") == "response":
        print(f"Agent 3 stores: {msg!r}")
        agent3_memory.append(msg)

@agent3.send()
def behavior():
    print(f"Agent 3 requests for given data")
    return {"purpose": "elements", "data": ["banana", "apple", "cherry"]}

for round in range(1,4):
    print(f"\n-> Round {round}")
    agents = [agent1, agent2, agent3]
    msgs = [agent.send_behavior() for agent in agents]
    exchanges = [(agents[i], msgs[:i]+msgs[i+1:]) for i in range(len(agents))]

    for agent, msgs in exchanges:
        for msg in msgs:
            agent.receive_behavior(msg)
