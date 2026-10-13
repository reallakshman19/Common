#!/usr/bin/env python3
"""SMTP notification for changed observations, not engineering acceptance."""
import json
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from pathlib import Path

def main():
    changes=json.loads(Path(sys.argv[1] if len(sys.argv)>1 else ".state/changes.json").read_text(encoding="utf-8")).get("changes",[])
    if not changes:
        print("No changes; email suppressed")
        return
    host=os.getenv("WF_SMTP_HOST")
    user=os.getenv("WF_SMTP_USER")
    passwd=os.getenv("WF_SMTP_PASSWORD")
    dest=os.getenv("WF_ALERT_TO")
    sender=os.getenv("WF_ALERT_FROM") or user
    if not all((host,user,passwd,dest,sender)):
        raise RuntimeError("SMTP credentials/recipient missing; no email sent")
    port=int(os.getenv("WF_SMTP_PORT") or "465")
    if port not in (465,587):
        raise ValueError("Only TLS ports 465/587 supported")
    message=EmailMessage()
    message["Subject"]="[WF-PROGRESS] GitHub workflow evidence changed"
    message["From"]=sender
    message["To"]=dest
    message.set_content("Read-only GitHub observations changed. No stage was independently certified.\n\n"
                        +json.dumps({"type":"WORKFLOW_EVIDENCE_CHANGED","changes":changes},indent=2))
    if port==465:
        with smtplib.SMTP_SSL(host,port,context=ssl.create_default_context(),timeout=30) as client:
            client.login(user,passwd)
            client.send_message(message)
    else:
        with smtplib.SMTP(host,port,timeout=30) as client:
            client.starttls(context=ssl.create_default_context())
            client.login(user,passwd)
            client.send_message(message)
    print(f"Sent one alert for {len(changes)} changed stage(s)")

if __name__=="__main__":
    main()
