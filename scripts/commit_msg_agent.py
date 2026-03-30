#!/usr/bin/env python3
"""
Commit-msg agent — vérifie la cohérence commit ↔ ticket Jira.
Appelé par .git/hooks/commit-msg avec le path du fichier message en argument.
"""

import base64
import os
import re
import subprocess
import sys

import httpx
from mistralai.client import Mistral

# ── Config ────────────────────────────────────────────────────────────────────
JIRA_BASE_URL = "https://amaurydreux-1997.atlassian.net"
JIRA_EMAIL = os.environ.get("ATLASSIAN_EMAIL", "")
JIRA_TOKEN = os.environ.get("ATLASSIAN_TOKEN", "")
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "")
MISTRAL_MODEL = "mistral-small-latest"


# ── Git helpers ───────────────────────────────────────────────────────────────
def current_branch() -> str:
    return subprocess.check_output(
        ["git", "symbolic-ref", "--short", "HEAD"], text=True
    ).strip()


def extract_ticket(text: str) -> str | None:
    match = re.search(r"(SCRUM-\d+)", text, re.IGNORECASE)
    return match.group(1).upper() if match else None


def staged_diff_summary() -> str:
    diff = subprocess.check_output(
        ["git", "diff", "--cached", "--stat"], text=True
    ).strip()
    return diff or "Aucun fichier stagé."


# ── Jira helper ───────────────────────────────────────────────────────────────
def fetch_jira_ticket(ticket: str) -> dict:
    token = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_TOKEN}".encode()).decode()
    resp = httpx.get(
        f"{JIRA_BASE_URL}/rest/api/3/issue/{ticket}?fields=summary,status,description",
        headers={"Authorization": f"Basic {token}", "Accept": "application/json"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    return {
        "key": data["key"],
        "summary": data["fields"]["summary"],
        "status": data["fields"]["status"]["name"],
    }


# ── Mistral analysis ──────────────────────────────────────────────────────────
def analyze(ticket: dict, commit_msg: str, diff_stat: str) -> tuple[bool, str]:
    import json

    client = Mistral(api_key=MISTRAL_API_KEY)
    prompt = f"""Tu es un assistant de revue de commit. Analyse la cohérence entre ce commit et son ticket Jira.

Ticket : {ticket['key']} — {ticket['summary']} [{ticket['status']}]

Message de commit : {commit_msg}

Fichiers modifiés :
{diff_stat}

Réponds en JSON strict :
{{
  "coherent": true | false,
  "reason": "explication courte en une phrase"
}}"""

    response = client.chat.complete(
        model=MISTRAL_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content.strip()
    result = json.loads(raw)
    return result["coherent"], result["reason"]


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> int:
    if len(sys.argv) < 2:
        print("[ERR] Usage: commit_msg_agent.py <commit-msg-file>")
        return 1

    commit_msg_file = sys.argv[1]
    with open(commit_msg_file) as f:
        commit_msg = "\n".join(
            line for line in f.read().splitlines() if not line.startswith("#")
        ).strip()

    if not commit_msg:
        return 0

    branch = current_branch()
    ticket_id = extract_ticket(branch) or extract_ticket(commit_msg)

    if not ticket_id:
        print("[SKIP] Aucun ticket SCRUM détecté — commit autorisé.")
        return 0

    if not MISTRAL_API_KEY:
        print("[SKIP] MISTRAL_API_KEY non définie — commit autorisé.")
        return 0

    if not JIRA_EMAIL or not JIRA_TOKEN:
        print("[SKIP] ATLASSIAN_EMAIL / ATLASSIAN_TOKEN non définis — commit autorisé.")
        return 0

    try:
        ticket = fetch_jira_ticket(ticket_id)
    except Exception as e:
        print(f"[SKIP] Jira inaccessible ({e}) — commit autorisé.")
        return 0

    diff_stat = staged_diff_summary()

    try:
        coherent, reason = analyze(ticket, commit_msg, diff_stat)
    except Exception as e:
        print(f"[SKIP] Analyse Mistral échouée ({e}) — commit autorisé.")
        return 0

    status = "[OK]" if coherent else "[WARN]"
    print(f"\n{status} {ticket_id} — {reason}")

    if not coherent:
        answer = input("Continuer quand même ? [y/N] ").strip().lower()
        if answer not in ("y", "o", "oui", "yes"):
            print("Commit annulé. Corrige le message ou le code.")
            return 1

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
