# SynapseITU

Course project repository for SynapseITU.

Project documentation, team roles, and the project charter are being prepared through pull requests. The current code is a small calculator and test suite used to establish our development and CI workflow.

## Development workflow

Create an issue, branch from `dev`, implement and test your changes, then open a pull request back to `dev`. Request a teammate's review before merging. When a release is ready, open a separate PR from `dev` to `main`.

| Stage | When | How |
| --- | --- | --- |
| Inner loop | While writing code, after small changes | Run pytest locally with uv in the project's `.venv`. |
| Local Docker check | Before requesting review, and after further changes | Build a fresh test image and run the tests inside a container. |
| Outer loop / CI | When a PR targeting `dev` or `main` is opened, reopened, or updated | GitHub Actions builds the image and runs the tests automatically. |

Run the commands below from the repository root, where `pyproject.toml` and `Dockerfile` are located, unless a step says otherwise.

## First-time setup

### 1. Clone the repository and start a task branch

Install [Git](https://git-scm.com/downloads), then run:

```bash
git clone https://github.com/yalcinfu22/SynapseITU.git
cd SynapseITU
git switch dev
git pull --ff-only
```

Create a branch for your issue. Replace `42-short-description` with your issue number and a short task description:

```bash
git switch -c 42-short-description
```

If you already cloned the repository, use your existing checkout. Before switching branches, commit or stash any unfinished changes. For each new task, update `dev` and create a new task branch from it.

### 2. Install uv and prepare Python

We use **uv 0.13.0** and **Python 3.13.6** to match the versions in the Dockerfile. Follow the [official uv installation guide](https://docs.astral.sh/uv/getting-started/installation/), or use the installer for your operating system below.

**Windows: run this in PowerShell** (even if you normally use Git Bash):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/0.13.0/install.ps1 | iex"
```

**macOS or Linux:**

```bash
curl -LsSf https://astral.sh/uv/0.13.0/install.sh | sh
```

Open a new terminal after installation, return to the repository directory, and run:

```bash
uv --version
uv python install 3.13.6
uv sync --locked --group test --python 3.13.6
uv run --locked --group test python -m pytest
```

Check that `uv --version` reports `0.13.0`. The Python installation command lets uv install the required interpreter; a separate manual Python installation is unnecessary. The sync command creates `.venv` with Python 3.13.6 and installs the locked dependencies, including the `test` group. The current calculator suite should report **6 passed**.

### 3. Understand the local environment

- `.venv` is the project's isolated Python environment. uv creates and manages it; you do not need to run `python -m venv` separately.
- `uv run` uses that environment automatically. You do not need to activate or deactivate `.venv` in your terminal.
- If your editor asks for a Python interpreter, select `.venv/Scripts/python.exe` on Windows or `.venv/bin/python` on macOS/Linux.
- `.venv` stays on your machine and is ignored by Git. Each teammate creates their own environment from the same project files.

See the [uv project guide](https://docs.astral.sh/uv/guides/projects/) for more about environments and lockfiles.

## Inner loop: develop and test locally

Write or update a test for the behavior you are implementing, change the code, then run:

```bash
uv run --locked --group test python -m pytest
```

Repeat this after small changes. **Docker does not need to be running for local uv tests.** Fix failing tests before preparing the PR for review.

For faster feedback on one test file:

```bash
uv run --locked --group test python -m pytest tests/unit/test_calculator.py
```

Run the full suite before the Docker check. Tests live under `tests/`, including its subdirectories. Use `test_*.py` filenames and `test_` prefixes for test functions.

### Dependencies and the lockfile

`pyproject.toml` declares the dependencies and Python requirement; `uv.lock` records the resolved package versions. `--locked` checks that these files agree and fails if the lockfile would need to change.

After pulling someone else's dependency changes, the normal `uv run --locked --group test ...` command updates your local environment from the committed lockfile. No manual package installation is needed.

When your task intentionally adds a dependency, use `uv add PACKAGE` (or `uv add --group test PACKAGE` for a test dependency), replacing `PACKAGE` with the actual package name. If you edit dependencies in `pyproject.toml` manually, run `uv lock`. Review and commit both files when they change, then rerun the tests. Do not edit `uv.lock` by hand.

## Local Docker check: verify the shared test environment

Install [Docker Desktop](https://docs.docker.com/get-started/get-docker/), or Docker Engine on Linux. Start Docker before this step; on Windows, use Linux containers.

The Dockerfile supplies Python 3.13.6, uv 0.13.0, and the locked dependencies inside the image. Docker does not use your host machine's `.venv`; you can run this check without installing Python or uv on the host.

From the repository root, run these commands in order. Continue to the second command only if the build succeeds:

```bash
docker build -t synapseitu-tests .
docker run --rm synapseitu-tests
```

The first command builds the image. The second starts a container, runs `python -m pytest` using the container's own virtual environment, and removes the container when it exits. The current suite should report **6 passed**.

**Rebuild after changing code, tests, dependencies, or the Dockerfile.** The image contains a snapshot of the files at build time; running the existing image again does not pick up later edits.

The Dockerfile describes how to prepare the test environment. `.github/workflows/ci.yml` describes when GitHub should build that image and run the tests.

## Outer loop: pull requests and CI

Once local tests and the Docker check pass:

1. Review your changes with `git diff` and `git status`. Stage the intended files and commit them on your task branch.
2. Push the branch. On the first push, use `git push -u origin HEAD`; later pushes can use `git push`.
3. Open a PR with **base: `dev`** and **compare: your task branch**. Include the related issue, a short description, and how you tested the change. Add the appropriate assignee, labels, and a teammate as reviewer.
4. Check that **Docker tests** passes and address review feedback before merging. Release PRs from `dev` target `main` instead.

CI runs when a PR targeting `dev` or `main` is opened, reopened, or updated with new commits. Pushing a branch without an open PR does not trigger this workflow. No manual CI command is needed.

GitHub Actions checks out the PR code, builds the test image using the same Dockerfile as the local check, and runs pytest inside a container. A build or test failure causes the check to fail. This workflow tests the code; it does not deploy an application.

### View results and fix a failed check

- Open the PR's **Checks** tab and select **Docker tests**.
- Alternatively, open the repository's **Actions** tab, select **CI**, and open the relevant run.
- Expand **Build test image** or **Run tests** to inspect the failing step and its logs.

If CI fails, use the logs to identify the cause, reproduce the problem locally, fix it, and repeat the local tests and Docker check. Commit and push the fix to the **same PR branch**. GitHub reruns CI automatically; you do not need a new PR.

## Common setup problems

| Problem | What to check |
| --- | --- |
| `uv` is not found | Open a new terminal after installation and check `uv --version`. |
| `--locked` reports an outdated lockfile | Check whether dependency changes were intentional. Update the lockfile with `uv lock` for intentional changes; otherwise restore the unintended dependency edits. |
| Docker cannot connect to its daemon | Start Docker Desktop or Docker Engine and wait until it is ready. On Windows, check that Linux containers are enabled. |
| Container tests appear to use old code | Rebuild the image successfully before running the container again. |
| No CI run appears after a push | Check that the pushed branch has an open PR targeting `dev` or `main`. |
