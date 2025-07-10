# Define Agent Behavior as Asynchronous Tasks


What should be async and what should not?

Every thing should be async but things should be divided in block that make sense


Some division would hurt the code more than anything else because they need to be sequential.


`multi` is very useful

`route` communication via the flow. Send sends directly via queue (no wait)


Receive and send are run in parallel (not sequentially)


IMPORTANT HERE: Make remark on starved message: try to account for failure



<p align="center">
<a href="state_persist.md">&laquo; Previous: Persist Agent States
 </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="../server/setup_linux.md">Next: Set up a Server on Linux &raquo;</a>
</p>