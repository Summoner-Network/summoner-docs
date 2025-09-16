# Set up an Asynchronous Database


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

<!-- queues, asqlite, etc.

use the agent examples in the library

# Set up
This page should explain how to set up and rely use these

# Principles of use
Give an alternative using some global list variable
asqlite and queue run in parallel


Make remark on starved message: try to account for failure -->



<p align="center">
<a href="id.md">&laquo; Previous: Configure your Agent Identity </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="state_persist.md">Next: Persist Agent States &raquo;</a>
</p>