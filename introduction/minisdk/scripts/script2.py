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
agent1_memory = None

@agent1.receive()
def behavior(msg):
    global agent1_memory
    print(f"Agent 1 remembers: {msg!r}")
    agent1_memory = msg

@agent1.send()
def behavior():
    if isinstance(agent1_memory, dict) and "for" in agent1_memory and "data" in agent1_memory:
        task = agent1_memory["for"]
        data = agent1_memory["data"]
        print(f"Agent 1 sorts data using {task!r}")
    else:
        return None

    if task == "sort_alpha":
        return sorted(data)
    elif task == "sort_length":
        return sorted(data, key=len)
    else:
        return None
    
import random
agent2 = Agent()
agent2_memory = []

@agent2.receive()
def behavior(msg):
    global agent2_memory
    if msg is not None:
        print(f"Agent 2 stores: {msg!r}")
        agent2_memory.append(msg)

@agent2.send()
def behavior():
    for_value = random.choice(["sort_alpha", "sort_length"])
    print(f"Agent 2 requests: {for_value}")
    return {"for": for_value, "data": ["banana", "apple", "cherry"]}

# Round 1
print("\n-> Agent 1 sends None and Agent 2 sends sort request")
msg1 = agent1.send_behavior()
msg2 = agent2.send_behavior()

print("\n-> Agent 1 receives request and Agent 2 receives None")
agent1.receive_behavior(msg2)
agent2.receive_behavior(msg1)

# Round 2
print("\n-> Agent 1 sends sorted data and Agent 2 sends new sort request")
msg1 = agent1.send_behavior()
msg2 = agent2.send_behavior()

print("\n-> Agent 1 receives new request and Agent 2 receives sorted data")
agent1.receive_behavior(msg2)
agent2.receive_behavior(msg1)

# Round 3
print("\n-> Agent 1 sends sorted data and Agent 2 sends new sort request")
msg1 = agent1.send_behavior()
msg2 = agent2.send_behavior()

print("\n-> Agent 1 receives new request and Agent 2 receives sorted data")
agent1.receive_behavior(msg2)
agent2.receive_behavior(msg1)
