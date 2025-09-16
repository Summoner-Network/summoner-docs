# Define Agent Behavior as Asynchronous Tasks


<style>
  body {
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    margin:0;
    padding:0;
  }

  .center-wrap {
    display:flex;
    align-items:center;
    justify-content:center;
    margin: 3rem 0;
  }

  .wrap{
    text-align:center;
    padding:2rem 3rem;
    border-radius:18px;
    background: rgba(127,127,127,0.06); /* subtle neutral card */
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
    max-width:90%;
  }

  .emoji {
    display:block;
    font-size: clamp(36px, 10vw, 120px);
    margin-bottom:.25rem;
  }

  .text {
    font-size: clamp(22px, 4.5vw, 56px);
    font-weight:700;
    letter-spacing: -0.02em;
  }

  @media (prefers-reduced-motion: no-preference) {
    .emoji {
      animation: float 2.2s ease-in-out infinite;
    }
    @keyframes float {
      0% { transform: translateY(0) scale(1); }
      50% { transform: translateY(-6px) scale(1.03); }
      100% { transform: translateY(0) scale(1); }
    }
  }

  .sub {
    margin-top:.6rem;
    opacity: 0.75;
    font-size: 14px;
  }
</style>

<div class="center-wrap">
  <div class="wrap" role="status" aria-live="polite">
    <span class="emoji" aria-hidden="true">🛠️</span>
    <div class="text">Work in progress</div>
    <div class="sub">Thanks for your patience — we're polishing things up ✨</div>
  </div>
</div>

<br>


<!-- 
What should be async and what should not?

Every thing should be async but things should be divided in block that make sense


Some division would hurt the code more than anything else because they need to be sequential.


`multi` is very useful

`route` communication via the flow. Send sends directly via queue (no wait)


Receive and send are run in parallel (not sequentially)


IMPORTANT HERE: Make remark on starved message: try to account for failure -->



<p align="center">
<a href="state_persist.md">&laquo; Previous: Persist Agent States
 </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="../server/setup_linux.md">Next: Set up a Server on Linux &raquo;</a>
</p>