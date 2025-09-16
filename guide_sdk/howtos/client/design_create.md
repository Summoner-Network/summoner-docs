# Design and Create Agents


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
# Configuration
Best practive if unsure

# Structure
- agent.py
- requirements.txt
- folders, etc.. 
- databases

# Plan for crashs and messages not received
 - fsm logic
 - design strategies
    - start simple: travel and function
    - decompose function into task and:
        - valiation 
        - registration 
        - message processing

NOTE: Rely on the agent libraires to give easy examples and then link to the more complex ones


Make remark on starved message: try to account for failure (refer to async_db.md)


I need to refer to `summoner-agent` here -- this is the right place. I would need to describe what agent demonstrate (what feature, and I might also refer to the API reference) -->

 <p align="center">
   <a href="../index.md">&laquo; Previous: How-tos (Intro) </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="id.md">Next: Configure your Agent Identity &raquo;</a>
 </p>

