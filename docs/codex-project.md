# Codex Project And Worktree Boot

The local Codex project `PROD 0.1 YKS METAXIS` points directly to this
repository checkout:

    /Users/adminprime/Documents/PROD 0.1 YKS METAXIS

The checked-in local environment at `.codex/environments/environment.toml`
runs whenever Codex creates a managed worktree. It creates an isolated Python
environment, installs METAXIS in editable mode, and runs the contract suite.

## Task posture

1. Start implementation tasks with **Worktree** selected.
2. Start from `main` unless an existing authority-linked branch is required.
3. Let Codex create its managed detached worktree.
4. Create a branch in that worktree only when the change is ready to persist.
5. Push the branch and open a draft pull request.

For a long-lived environment, create a permanent worktree from the project's
three-dot menu. Permanent worktrees appear as their own Codex projects and are
not automatically deleted.

The repository can carry setup and boot instructions, but task placement is a
Codex app choice: select Worktree in the composer or use a permanent worktree.

## Authority

- Work and product decisions remain in YKS Ops issues.
- Implementation issue 1 is a read-only one-way mirror of YKS Ops root 422.
- Implementation work must link to its YKS Ops issue or formal requirement.
- Do not store tokens, model credentials, or secrets in the repository or a
  worktree.

