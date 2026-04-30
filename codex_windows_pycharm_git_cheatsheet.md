# Codex + Git Cheat Sheet for Windows + PyCharm

This is a practical, safe workflow for using Codex from PyCharm on Windows.

## 1. Big picture

You do **not** need a PyCharm plugin to use Codex.

You can use Codex in any of these ways:

1. **Codex CLI inside PyCharm's Terminal** — recommended starting point.
2. **Codex JetBrains IDE integration** — optional, gives a Codex panel inside PyCharm.
3. **Codex Windows app** — optional, useful later for managing bigger tasks.

OpenAI docs:

- Codex CLI: https://developers.openai.com/codex/cli
- Codex IDE integration: https://developers.openai.com/codex/ide
- Codex on Windows: https://developers.openai.com/codex/windows

---

## 2. Install Codex CLI

Open PyCharm's terminal or PowerShell and run:

```bash
npm i -g @openai/codex
```

Then from inside your project folder:

```bash
codex
```

The first run should ask you to sign in.

To update Codex later:

```bash
npm i -g @openai/codex@latest
```

---

## 3. Before using Codex: protect your work

From your project folder:

```bash
git status
```

If you have unfinished changes, either commit them or stash them first.

### Option A: Commit your current work

```bash
git add .
git commit -m "Save work before Codex"
```

### Option B: Stash your current work

```bash
git stash push -m "before Codex"
```

To restore the stash later:

```bash
git stash pop
```

---

## 4. Create a safe branch for Codex

This is the main safety move.

```bash
git checkout -b codex-test
```

Or use a more specific branch name:

```bash
git checkout -b codex-trainingdata-refactor
```

Now Codex can edit without touching your main branch directly.

---

## 5. Start Codex from PyCharm

In PyCharm's terminal:

```bash
cd path\to\your\project
codex
```

A good first prompt:

```text
Read this repo and summarize the architecture. Do not edit anything.
```

Then:

```text
Find the file responsible for training data setup. Do not edit anything yet.
```

Then, only when you're ready:

```text
Make the smallest safe change. Preserve comments, formatting, docstrings, terse one-liners, and existing logic unless the change requires it.
```

---

## 6. Useful Codex prompts

### Read-only exploration

```text
Read this file and explain what it does. Do not edit anything.
```

```text
Trace where this method is called. Do not edit anything.
```

```text
Find the smallest place to make this change. Do not edit anything yet.
```

### Small edits

```text
Apply the smallest possible patch for this one issue only. Do not reformat unrelated code.
```

```text
Add this behavior while preserving all existing comments, spacing, docstrings, and logic unless required.
```

```text
Make this change in one class only. Do not modify public APIs unless there is no clean alternative.
```

### Testing

```text
Run the relevant tests and explain any failures. Do not fix them yet.
```

```text
Before changing code, tell me which tests should cover this behavior.
```

### Code review

```text
Review the current branch against main for bugs only. Do not edit anything.
```

```text
Review this diff for accidental logic changes, formatting churn, and risky assumptions.
```

---

## 7. After Codex edits: inspect everything

Always check what changed:

```bash
git status
git diff
```

If the diff is too large, stop and make Codex shrink it:

```text
This diff is too broad. Revert unrelated formatting and keep only the minimal logic change.
```

Run tests:

```bash
python -m pytest
```

Or if your project has a specific test command, use that instead.

---

## 8. Keep or discard Codex changes

### Keep the changes

```bash
git add .
git commit -m "Use Codex to update training data setup"
```

### Discard all Codex changes on the branch

Careful: this destroys uncommitted changes.

```bash
git reset --hard
```

### Go back to main

```bash
git checkout main
```

### Delete the Codex branch if you don't need it

```bash
git branch -D codex-test
```

---

## 9. If Codex made a bad commit

If the bad changes are already committed but not pushed:

```bash
git log --oneline
```

Then reset to the commit before the bad one:

```bash
git reset --hard <commit_hash>
```

If you want to undo the commit but preserve the changes as uncommitted files:

```bash
git reset --soft HEAD~1
```

---

## 10. Simple safety rules

Use Codex like a fast junior developer, not an authority.

Good rules:

- Start on a new branch.
- Ask it to inspect before editing.
- Keep prompts small.
- Avoid giant requests like "refactor the whole optimizer".
- Always inspect `git diff`.
- Make it explain failures before fixing them.
- Reject broad formatting churn.

A solid standing instruction for your style:

```text
Work surgically. Do not reformat unrelated code. Preserve comments, docstrings, spacing, terse one-liners, and existing logic unless I explicitly ask to change them. Before editing, explain the smallest viable change. Prefer simple code over clever code. If my request is risky or based on a mistaken assumption, say so directly before changing files.
```

---

## 11. Windows notes

Codex can run natively on Windows. OpenAI's Windows docs say Codex can also run through WSL2 if you need a Linux-native environment.

For your PyCharm workflow, start simple:

```bash
codex
```

inside PyCharm's terminal.

Only move to WSL2 if:

- your Python tooling already lives in WSL2,
- your project depends on Linux-only packages/scripts,
- native Windows sandboxing gives you trouble.

---

## 12. My recommended daily workflow

```bash
git status
git checkout -b codex-small-task
codex
```

Inside Codex:

```text
Inspect this issue and propose the smallest safe change. Do not edit yet.
```

After you approve the idea:

```text
Apply the smallest patch only. Preserve formatting and existing logic.
```

Back in terminal:

```bash
git diff
python -m pytest
git add .
git commit -m "Small Codex-assisted fix"
git checkout main
git merge codex-small-task
```

