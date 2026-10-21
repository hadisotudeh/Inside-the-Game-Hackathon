"""Shared, self-contained opening slide for both demo recordings."""

import base64
from pathlib import Path

ASSETS = Path(__file__).with_name("assets")


def opening_card(historical=True):
    def logo(name, mime):
        encoded = base64.b64encode((ASSETS / name).read_bytes()).decode()
        return f"data:{mime};base64,{encoded}"

    description = "Designed for fans watching live TV and streaming."
    detail = "Real-time match insights · Interactive stats · Ask the match via <strong>AI</strong>"
    return f'''<div id="title-card">
      <div class="event-name">Inside the Game <span>Developer Hackathon</span></div>
      <div class="eyebrow">TOUCHLINE / FOOTBALL INTELLIGENCE</div>
      <h1>See the game.<br><span>Understand the story.</span></h1>
      <div class="rule"></div>
      <p>The story behind the score.<br>{description}</p>
      <div class="small">{detail}</div>
      <div class="organizer-logos" aria-label="Hackathon partners">
        <img class="microsoft-logo" src="{logo('microsoft.png', 'image/png')}" alt="Microsoft">
        <span class="logo-divider" aria-hidden="true"></span>
        <img class="premier-league-logo" src="{logo('premier-league.svg', 'image/svg+xml')}" alt="Premier League">
      </div>
    </div>'''


def microsoft_card():
    """Show implemented Microsoft technology and the proposed deployment path."""
    return '''<div class="event-name">Inside the Game <span>Developer Hackathon</span></div>
    <div class="eyebrow">TOUCHLINE / MICROSOFT TECHNOLOGY</div>
    <h1 style="font-size:86px">Built with Microsoft<br><span>Agent Framework.</span></h1>
    <div class="rule"></div>
    <p style="font-size:32px;line-height:1.6"><strong>Implemented:</strong> Three evidence tools → orchestration → Gemini explanation<br>
    <strong>Adapter ready; verification pending:</strong> Microsoft Foundry explanations<br>
    <strong>Proposed:</strong> Azure Container Apps hosting + Web PubSub shared updates<br>
    <strong>Proposed:</strong> Application Insights monitoring + Key Vault secrets</p>
    <div class="small">Designed for fans watching live TV and streaming · Real-time match insights</div>'''
