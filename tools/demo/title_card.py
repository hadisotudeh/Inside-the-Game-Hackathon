"""Shared, self-contained opening slide for both demo recordings."""

import base64
from pathlib import Path

ASSETS = Path(__file__).with_name("assets")


def opening_card(historical=True):
    def logo(name, mime):
        encoded = base64.b64encode((ASSETS / name).read_bytes()).decode()
        return f"data:{mime};base64,{encoded}"

    description = "Supporting football fans and commentators."
    detail = "Interactive match statistics · Automatic AI narration · Ask the match"
    return f'''<div id="title-card">
      <div class="event-name">Inside the Game <span>Developer Hackathon</span></div>
      <div class="eyebrow">TOUCHLINE / FOOTBALL INTELLIGENCE</div>
      <h1>Match stats.<br><span>AI insights.</span></h1>
      <div class="rule"></div>
      <p>{description}<br>Follow the match. Explain the action.</p>
      <div class="small">{detail}</div>
      <div class="organizer-logos" aria-label="Hackathon partners">
        <img class="microsoft-logo" src="{logo("microsoft.png", "image/png")}" alt="Microsoft">
        <span class="logo-divider" aria-hidden="true"></span>
        <img class="premier-league-logo"
          src="{logo("premier-league.svg", "image/svg+xml")}" alt="Premier League">
      </div>
    </div>'''


def architecture_card():
    """Summarize the deployed event, analytics and AI paths."""
    return """<div class="eyebrow">TOUCHLINE / APP ARCHITECTURE</div>
    <h1 style="font-size:78px">From events<br><span>to match insight.</span></h1>
    <div class="rule"></div>
    <div style="display:flex;align-items:center;gap:24px;margin-top:45px;
    font-size:27px;line-height:1.6">
      <div id="arch-events" style="padding:28px;border:2px solid #d7dde2;border-radius:14px">
      <strong>Historical events</strong><br>StatsBomb Open Data<br>One event at a time</div>
      <div aria-hidden="true">→</div>
      <div id="arch-server" style="padding:28px;border:2px solid #126347;border-radius:14px">
      <strong>Python / FastAPI</strong><br>Replay + analytics<br>Current match snapshot</div>
      <div aria-hidden="true">→</div>
      <div id="arch-browser" style="padding:28px;border:2px solid #d7dde2;border-radius:14px">
      <strong>Browser / SSE</strong><br>Charts + statistics<br>Narration + questions</div>
    </div>
    <div id="arch-ai" style="margin-top:35px;padding:25px 30px;background:#edf5f1;
    border-radius:14px;font-size:27px;line-height:1.7">
      <strong>AI path:</strong> Match snapshot → Microsoft Agent Framework<br>
      Three evidence tools → <span id="arch-model">Azure GPT-4.1 mini</span> →
      <span id="arch-checks">Response checks</span> → Browser
    </div>
    <div class="small" style="margin-top:24px">
      Hosted on Azure App Service · Model inference via Microsoft Foundry
    </div>"""


def microsoft_card():
    """Show the deployed Microsoft stack and a readable live URL."""
    return """<div class="event-name">Inside the Game <span>Developer Hackathon</span></div>
    <div class="eyebrow">TOUCHLINE / MICROSOFT TECHNOLOGY</div>
    <h1 style="font-size:86px">Already live.<br><span>Hosted on Azure.</span></h1>
    <div class="rule"></div>
    <div class="technology-list">
      <div><strong>Implemented:</strong>
      Microsoft Agent Framework · three evidence tools</div>
      <div><strong>Azure-hosted AI:</strong> GPT-4.1 mini · Microsoft Foundry</div>
      <div><strong>Hosting:</strong> Azure App Service · free Linux plan</div>
      <div style="font-size:30px;color:#126347"><strong>Try it live — no installation:</strong><br>
      https://touchline-inside-the-game.azurewebsites.net</div>
    </div>
    <div class="small">Supporting football fans and commentators
    · Real-time match insights</div>
    <div style="margin-top:18px;font-size:25px;color:#52606d;
    display:flex;align-items:center;gap:12px">Developed by
    <a href="https://www.linkedin.com/in/hadisotudeh"
    style="color:#126347;text-decoration:underline">Hadi Sotudeh</a>
    <a href="https://www.linkedin.com/in/hadisotudeh"
    aria-label="Hadi Sotudeh on LinkedIn" style="display:inline-flex">
      <svg xmlns="http://www.w3.org/2000/svg" width="34" height="34"
      viewBox="0 0 34 34" role="img" aria-label="LinkedIn">
        <rect width="34" height="34" rx="3" fill="#0a66c2"/>
        <text x="6" y="26" fill="white" font-family="Arial,sans-serif"
        font-size="27" font-weight="bold">in</text>
      </svg>
    </a></div>"""
