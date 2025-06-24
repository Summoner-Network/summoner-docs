from typing import Callable, Optional

class Agent:

    def __init__(self):
        self.send_behaviors: dict[str, Callable] = {}
        self.receive_behaviors: dict[str, Callable] = {}

        self._upload_state = None
        self._download_state = None

    def send(self, route: Optional[str] = None):
        def decorator(fn):
            self.send_behaviors[route] = fn
        return decorator

    def receive(self, route: Optional[str] = None):
        def decorator(fn):
            self.receive_behaviors[route] = fn
        return decorator
    
    def upload_state(self):
        def decorator(fn):
            self._upload_state = fn
        return decorator
    
    def download_state(self):
        def decorator(fn):
            self._download_state = fn
        return decorator

state_graph = {
    "Start":    {"elements": "Ready", "function": "Waiting"},
    "Waiting":  {"elements": "Ready"},
    "Ready":    {"elements": "Ready", "function": "Waiting"},
    } 

agent1 = Agent()
agent1_memory = {}
agent1_state = "Start"

def raw_behavior(msg, state):
    global agent1_memory
    if agent1_memory is None:
        agent1_memory = {}
    if msg["purpose"] not in agent1_memory:
        print(f"[{state} - receive] Agent 1 remembers: {msg!r}")
        agent1_memory[msg["purpose"]] = msg
        return msg["purpose"]

@agent1.receive(route = "Start")
def behavior(msg: dict):
    if "purpose" in msg:
        return raw_behavior(msg, "Start")
        
@agent1.receive(route = "Waiting")
def behavior(msg: dict):
    if "purpose" in msg and msg["purpose"] == "elements":
        return raw_behavior(msg, "Waiting")

@agent1.receive(route = "Ready")
def behavior(msg: dict):
    global agent1_memory
    agent1_memory = {}
    return raw_behavior(msg, "Ready")

@agent1.send(route="Ready")
def send_ready():
    global agent1_memory
    task = agent1_memory.get("function", {}).get("for", "sort_alpha")
    data = agent1_memory["elements"]["data"]
    print(f"[Ready - send] Agent 1 sorts data using {task!r}")
    if task == "sort_alpha":
        return {"purpose": "response", "data": sorted(data)}
    elif task == "sort_length":
        return {"purpose": "response", "data": sorted(data, key=len)}
    return None

@agent1.upload_state()
def upload():
    global agent1_state
    return agent1_state

@agent1.download_state()
def download(next_states):
    global agent1_state
    # pick the highest-priority transition if multiple events occurred
    for state in ["Ready", "Waiting", "Start"]:
        if state in next_states:
            agent1_state = state
            break

import random
agent2 = Agent()
agent2_memory = []
agent2_state = None

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

@agent2.download_state()
def dowload(state):
    global agent2_state
    agent2_state = state

@agent2.upload_state()
def upload():
    global agent2_state
    return agent2_state

agent3 = Agent()
agent3_memory = []
agent3_state = None

@agent3.receive()
def behavior(msg):
    global agent3_memory
    if msg is not None and msg.get("purpose") == "response":
        print(f"Agent 3 stores: {msg!r}")
        agent3_memory.append(msg)

@agent3.send()
def behavior():
    print(f"Agent 3 requests for given data")
    return {"purpose": "elements", "data": ["banana", "apple", "kiwi"]}

@agent3.download_state()
def dowload(state):
    global agent3_state
    agent3_state = state

@agent3.upload_state()
def upload():
    global agent3_state
    return agent3_state


def server_protocol(*agents: Agent):
    previous_states = [None for _ in agents]

    for round in range(1,4):
        print(f"\n-> Round {round}")

        msgs = []
        for i, agent in enumerate(agents):
            msg = [fn() for route, fn in agent.send_behaviors.items() if route is None or route == agent._upload_state()]
            msgs.append(None if msg == [] else msg[0])

        exchanges = [(agents[i], msgs[:i]+msgs[i+1:]) for i in range(len(agents))]

        for i, (agent, msgs) in enumerate(exchanges):
            current_state = agent._upload_state()
            next_states = []
            
            for msg in msgs:
                for route, fn in agent.receive_behaviors.items():
                    if route is None or route == current_state:
                        result = fn(msg)
                        if route is not None:
                            next_state = state_graph[route].get(result)
                            if next_state is None:
                                next_state = route

                            next_states.append(next_state)

            agent._download_state(next_states)

server_protocol(agent1, agent2, agent3)