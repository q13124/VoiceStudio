# VoiceStudio Branch Merge Policy

> **Version**: 1.0  
> **Owner**: Overseer (Role 0)  
> **Created**: 2026-02-02  
> **Status**: Active

---

## Purpose

This policy establishes guardrails to prevent branch divergence that can lead to merge conflicts, lost work, and synchronization issues. It codifies lessons learned from TASK-0022 (Git History Reconstruction).

---

## Policy Rules

### 1. Maximum Divergence Limits

| Threshold | Action Required |
|-----------|-----------------|
| **10 commits** OR **2 weeks** | Merge to main required |
| **20 commits** | Mandatory review before further work |
| **50 commits** | Process violation - escalate to Overseer |

### 2. Branch Lifecycle

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Create    │────▶│    Work     │────▶│   Merge     │
│   Branch    │     │  (≤10 commits) │     │   to Main   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼ (if >10 commits)
                    ┌─────────────┐
                    │   Sync or   │
                    │   Merge PR  │
                    └─────────────┘
```

### 3. Branch Naming Convention

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/<scope>-<description>` | `feature/ui-panel-navigation` |
| Bugfix | `fix/<issue-id>-<description>` | `fix/VS-0042-null-reference` |
| Release | `release/<version>` | `release/1.0.1` |
| Hotfix | `hotfix/<version>-<description>` | `hotfix/1.0.1-crash-fix` |

### 4. Protected Branches

| Branch | Protection Level | Rules |
|--------|-----------------|-------|
| `main` | High | No direct push; PR required; CI must pass |
| `release/*` | High | No force push; requires approval |
| `baseline-*` | Read-only | Historical snapshots; never modify |

---

## Enforcement

### Weekly Audit

Run the following command weekly to check branch divergence:

```bash
# Check all branches' divergence from main
git fetch origin
for branch in $(git branch -r | grep -v main); do
  commits=$(git rev-list --count origin/main..$branch 2>/dev/null)
  if [ "$commits" -gt 10 ]; then
    echo "WARNING: $branch is $commits commits ahead of main"
  fi
done
```

### Pre-commit Check (Optional)

Add to `.pre-commit-config.yaml` if automated enforcement is desired:

```yaml
- repo: local
  hooks:
    - id: branch-divergence-check
      name: Check branch divergence
      entry: python scripts/check_branch_divergence.py
      language: python
      pass_filenames: false
      always_run: true
```

---

## Exceptions

### Valid Reasons for Exceeding Limits

1. **Long-running feature branches** - Must have Overseer approval and weekly sync schedule
2. **Release stabilization** - Release branches may diverge during stabilization window
3. **External dependency updates** - Large dependency updates may require extended branches

### Exception Process

1. Document reason in task brief or STATE.md
2. Get Overseer acknowledgment
3. Set explicit merge deadline
4. Schedule interim syncs if >2 weeks

---

## Merge Strategies

### Default: Squash Merge

Use squash merge for feature branches to keep main history clean:

```bash
git checkout main
git merge --squash feature/my-feature
git commit -m "feat: description of feature"
```

### When to Use Regular Merge

- Release branch merges (preserve commit history)
- Hotfixes that need to go to multiple branches
- When individual commits have value for bisecting

### Rebase Policy

- **Allowed**: On personal/unshared branches before PR
- **Prohibited**: On shared branches or after PR review started
- **Never**: On protected branches

---

## Recovery Procedures

### If Branch Diverged Too Far

1. Create backup: `git branch backup-<branch>-<date>`
2. Identify merge base: `git merge-base main <branch>`
3. Consider interactive rebase to clean history
4. Create PR with detailed description of changes
5. Request code review focusing on conflict resolution

### If Merge Conflict Occurs

1. Do NOT force push to resolve
2. Pull latest from both branches
3. Resolve conflicts locally
4. Test thoroughly before pushing
5. Document resolution in commit message

---

## References

- [TASK-0022 Recovery Report](../reports/post_mortem/TASK-0022_COMPLETE_RECOVERY_REPORT_2026-01-30.md)
- [Git Conventions Rule](.cursor/rules/workflows/git-conventions.mdc)
- [Closure Protocol](.cursor/rules/workflows/closure-protocol.mdc)

---

## Changelog

| Date | Change |
|------|--------|
| 2026-02-02 | Initial policy created (TD-010) |
