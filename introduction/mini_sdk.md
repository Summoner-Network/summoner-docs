# The Mini SDK Concept

This section illustrates how Summoner works by mimicking its core mechanisms using a minimal version of the code — let’s call it ***miniSummoner***.

## Defining an Agent

We begin by defining what an agent should look like in *miniSummoner*. At a minimum, it must be able to **receive** and **send** messages, and it should be customizable by the user.

Here is a simple `Agent` class. It supports:

* `code()` — used to upload a user-defined function into memory (see our [decorator recap](minisdk/decorators.md))
* `receive()` — stores an incoming message
* `send()` — applies the uploaded function to the stored message and returns the result

```python
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
```

To create an agent using this class, we first instantiate the `Agent`, then define its behavior using the `@agent.code()` decorator:

```python
myagent = Agent()

@myagent.code()
def my_agent_behavior(msg):
    print(f"About to send the message: {msg!r}")
    return msg
```

In this example, the agent simply prints the received message and returns it unchanged.

We can now use the `receive()` and `send()` methods to simulate a basic interaction:

```python
msg = "Hello World!"

myagent.receive(msg)

# ... anything can happen here ...

new_msg = myagent.send()

# ... use new_msg as needed ...

print(new_msg)
```

Running the script above (available [here](minisdk/scripts/script1.py)) produces the following output:

```
$ python3 script1.py
About to send the message: 'Hello World!'
Hello World!
```

Note that the `send()` operation can be delayed arbitrarily after `receive()`. In fact, `send` and `receive` do not need to match one-to-one or occur consecutively — this flexibility is essential for asynchronous agent communication.


## Refinement of the `Agent` class



<!-- - mini sdk: Introduction to Summoner SDK
    * **Creating Your First Agent**
    * Defining agent behaviors
    * Message sending and receiving
    * **Creating Your First Server**
    * How to launch a simple local server
    * **Interactive Demo**
    * Short code snippets with immediate feedback
    * Meme to celebrate "It worked!"

    - function
        - decorator
    - multifunctoin
    - signal based: receive(), send()
        - hardcoded
        - autonomous

    - Why use Network:
        - loading a model (word2vec) can take time - loading it once and having it available as an api call is great to work on this
        - Summoner: open to any other context
            - loading model
            - two computers: one with GPUs


- taking care of multiple other agents requires states -->


<p align="center">
  <a href="why5_diff.md">&laquo; Previous: Comparison with Existing Frameworks</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="../---.md">Next: ... &raquo;</a>
</p>