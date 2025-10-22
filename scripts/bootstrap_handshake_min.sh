#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo .)"
mkdir -p "$ROOT/.github/workflows" "$ROOT/docs"

# ensure plan doc exists so the workflow has content to parse
[ -f "$ROOT/docs/15_MINUTE_WORKFLOW.md" ] || cat > "$ROOT/docs/15_MINUTE_WORKFLOW.md" <<'MD'
# 15-Minute Workflow (placeholder)
- Task A
- Task B
- Task C
MD

# minimal every-15m workflow (Slack optional, email hourly max)
cat > "$ROOT/.github/workflows/handshake-status.yml" <<'YAML'
name: handshake-status
on:
  schedule: [ { cron: "*/15 * * * *" } ]
  workflow_dispatch:
jobs:
  status:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-python@v5
        with: { python-version: "3.10" }
      - run: python -m pip install --upgrade pip && pip install requests
      - id: build
        env:
          WINDOW_MINUTES: ${{ vars.STATUS_WINDOW_MINUTES || '15' }}
          PLAN_FILE: ${{ vars.STATUS_PLAN_FILE || 'docs/START_HERE_EXACT_PLAN.md' }}
          ALT_PLAN_FILE: ${{ vars.STATUS_ALT_PLAN_FILE || 'docs/15_MINUTE_WORKFLOW.md' }}
        run: |
          python - << 'PY'
          import os, subprocess, pathlib, datetime
          win=int(os.getenv('WINDOW_MINUTES','15'))
          def sh(a): return subprocess.check_output(a, text=True).strip()
          try: log=sh(["git","log","--since",f"{win} minutes ago","--pretty=format:%h %s (%an)"]) or "— No commits in this window."
          except Exception as e: log=f"— Could not read git log: {e}"
          plan=os.getenv('PLAN_FILE'); alt=os.getenv('ALT_PLAN_FILE'); text=""
          for p in [plan,alt]:
            if not p: continue
            fp=pathlib.Path(p)
            if not fp.exists(): continue
            lines=[l.rstrip() for l in fp.read_text(errors='ignore').splitlines()]
            idx=[i for i,l in enumerate(lines) if any(k in l.lower() for k in ['today','next','tasks'])]
            cap=[]
            for i in (idx[:1] or [0]):
              for l in lines[i+1:i+40]:
                s=l.strip()
                if s.startswith(('#','**')): break
                if s.startswith(('-','*','•','1.','2.','3.')): cap.append(s)
                if len(cap)>=8: break
            if cap: text='\\n'.join(cap); break
          next_steps=text or "— Check START_HERE_EXACT_PLAN.md for next tasks."
          blockers="— None seen."
          try:
            blob=pathlib.Path(plan).read_text(errors='ignore') if plan and pathlib.Path(plan).exists() else ''
            lines=[l for l in blob.splitlines() if any(k in l.upper() for k in ['BLOCKER','TODO:','RISK'])]
            if lines: blockers='\\n'.join(lines[:5])
          except Exception: pass
          msg=f"""*Status ({datetime.datetime.utcnow().isoformat(timespec='minutes')}Z)*
*What changed (last {win}m):*
{log}

*What's next:*
{next_steps}

*Blockers / decisions:*
{blockers}"""
          open('status.msg','w').write(msg)
          PY
      - name: Slack (optional)
        if: env.SLACK_WEBHOOK_URL != ''
        env: { SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }} }
        run: |
          curl -sS -X POST "$SLACK_WEBHOOK_URL" -H 'Content-type: application/json' \
            --data-binary @- <<'JSON'
          {"text": "$(sed 's/\"/\\\"/g' status.msg)"}
          JSON
      - name: Email hourly (optional)
        if: env.SENDGRID_API_KEY != '' && env.STATUS_EMAIL_TO != '' && env.STATUS_EMAIL_FROM != ''
        env:
          SENDGRID_API_KEY: ${{ secrets.SENDGRID_API_KEY }}
          STATUS_EMAIL_TO:  ${{ secrets.STATUS_EMAIL_TO }}
          STATUS_EMAIL_FROM: ${{ secrets.STATUS_EMAIL_FROM }}
          EMAIL_EVERY_MIN: ${{ vars.STATUS_EMAIL_EVERY_MIN || '60' }}
        run: |
          M=$(date -u +%s); MOD=$(( (M/60) % ${EMAIL_EVERY_MIN} ))
          [ "$MOD" = "0" ] || { echo "Skip email (throttle)"; exit 0; }
          curl -sS --fail -X POST https://api.sendgrid.com/v3/mail/send \
            -H "Authorization: Bearer $SENDGRID_API_KEY" -H 'Content-Type: application/json' \
            -d @- <<JSON
          {
            "personalizations": [{"to": [{"email": "${STATUS_EMAIL_TO}"}]}],
            "from": {"email": "${STATUS_EMAIL_FROM}", "name": "VS Handshake"},
            "subject": "VS Handshake Status",
            "content": [{"type": "text/plain", "value": $(python -c 'import json;print(json.dumps(open("status.msg").read()))') }]
          }
          JSON
YAML

if git rev-parse --git-dir >/dev/null 2>&1; then
  git add .github/workflows/handshake-status.yml docs/15_MINUTE_WORKFLOW.md || true
  git commit -m "bootstrap: 15m handshake status" || echo "No changes to commit"
  echo "✅ Push to enable: git push"
else
  echo "✅ Files written (not a git repo)."
fi

cat <<'NEXT'
Add secrets/vars (optional):
- Secrets: SLACK_WEBHOOK_URL; SENDGRID_API_KEY, STATUS_EMAIL_FROM, STATUS_EMAIL_TO
- Vars: STATUS_WINDOW_MINUTES (default 15), STATUS_EMAIL_EVERY_MIN (default 60), STATUS_PLAN_FILE
NEXT
