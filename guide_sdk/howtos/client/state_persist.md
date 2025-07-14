# Persist Agent States


Explain very well how to properly use upload_states and download_states


Explain that there may be confusion if not used well

```
The issue is that the code we are examining operates on a single payload, which is associated with either 90da6f92-... or 190b6470-....

Currently, the code fetches the entire tape for both negotiators, and the activation is computed over the full tape. This means that when we build the batch, we extract functions for both 90da6f92-... and 190b6470-..., and run each of these functions on the same payload—regardless of whether it originated from 90da6f92-... or 190b6470-.... As a result, we create unintended intersections.

The core issue is that activations are reused later based on key attributes, without accounting for these intersections. A single message (e.g., from agent A) may trigger functions associated with either agent A or B. If agent A's message activates a function for agent B first, then local_tape will compute the next states for B instead of A—and that is where the inconsistency arises.

I am considering specializing _upload_state by adding a payload argument to restrict the relevant states in the tape. However, I wonder if you have a better idea?

```

<p align="center">
<a href="async_db.md">&laquo; Previous: Set up an Asynchronous Database
 </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="async_task.md">Next: Define Agent Behavior as Asynchronous Tasks &raquo;</a>
</p>