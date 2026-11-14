# SynapseITU

Course project repository for SynapseITU.

Project documentation, team roles, and the project charter are prepared through pull requests.

## Team

The Goats, BLG411E Software Engineering, Fall 2026. Roles from the Project Plan (Section 4.1).

| Member | Development role (owned module) | Technical role | Management role |
| --- | --- | --- | --- |
| Yavuz Selim Yağlıca | Opportunities, Applications, Questions & Discussions, Knowledge Search | Backend & API Manager | Project Manager |
| Furkan Yalçın | Eligibility & AI Search | Designer-Architect | GitHub Workflow Manager |
| Ahmed Said Gülşen | Chatbot & Candidate Ranking | AI Manager | DevOps Manager |
| Ahmet Yusuf Kurukız | Profiles, CV Adaptor & Discovery | UI Manager | Scrum Master |
| Najib Attar | Authentication, Administration & Notifications | QA Tester | Requirement Document Manager |
| Amr Naweel Zuhdi Taweel | University Data Agent & Credits | Database Manager | Test Manager |

## Repository layout

| Path | Contents |
| --- | --- |
| `backend/` | FastAPI service (Python 3.13.6, uv 0.13.0). Feature modules add their routers under `backend/app/`. |
| `backend/evaluation/` | Matching evaluation harness (WBS-15.4). See `docs/evaluation-harness.md`. |
| `frontend/` | Next.js app (TypeScript, Tailwind CSS, Vitest; Node 22). |
| `tests/` | All tests (course rule): `tests/backend/` (pytest) and `tests/frontend/` (Vitest). |
| `docs/` | All documents (course rule). `docs/adr/` has the architecture decision records. |
| `.github/workflows/` | `ci.yml` (lint and tests on every PR) and `deploy.yml` (staging and production). |

## Development workflow

Create an issue, branch from `dev`, implement and test your changes, then open a pull request back to `dev`. Request a teammate's review before merging. When a release is ready, open a separate PR from `dev` to `main`. `dev` and `main` are protected: they accept changes only through pull requests with a green CI.

| Stage | When | How |
| --- | --- | --- |
| Inner loop | While writing code, after small changes | Run the linters and tests locally (uv for the backend, npm for the frontend). |
| Local Docker check | Before requesting review, and after further changes | Build the `test` stage of each Dockerfile. |
| Outer loop / CI | When a PR targeting `dev` or `main` is opened, reopened, or updated | GitHub Actions runs the same checks automatically. |

Backend commands run from `backend/` and frontend commands from `frontend/`, unless a step says otherwise.

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

Open a new terminal after installation, go to the repository's `backend/` directory, and run:

```bash
uv --version
uv python install 3.13.6
uv sync --locked --all-groups --python 3.13.6
uv run --locked python -m pytest
```

Check that `uv --version` reports `0.13.0`. The Python installation command lets uv install the required interpreter; a separate manual Python installation is unnecessary. The sync command creates `backend/.venv` with Python 3.13.6 and installs the locked dependencies, including the `test` and `lint` groups. All tests should pass.

### 3. Install Node.js for the frontend

Install [Node.js 22](https://nodejs.org/) (npm comes with it), then run from `frontend/`:

```bash
npm ci
npm test
```

`npm ci` installs the exact versions in `package-lock.json` into `frontend/node_modules`.

### 4. Understand the local environment

- `backend/.venv` is the backend's isolated Python environment. uv creates and manages it; you do not need to run `python -m venv` separately.
- `uv run` uses that environment automatically. You do not need to activate or deactivate `.venv` in your terminal.
- If your editor asks for a Python interpreter, select `backend/.venv/Scripts/python.exe` on Windows or `backend/.venv/bin/python` on macOS/Linux.
- `.venv` and `node_modules` stay on your machine and are ignored by Git. Each teammate creates their own environment from the same project files.

See the [uv project guide](https://docs.astral.sh/uv/guides/projects/) for more about environments and lockfiles.

## Inner loop: develop and test locally

Write or update a test for the behavior you are implementing, change the code, then run the same checks that CI runs:

```bash
# in backend/
uv run --locked ruff check . ../tests/backend
uv run --locked ruff format --check . ../tests/backend   # without --check, it fixes formatting
uv run --locked python -m pytest

# in frontend/
npm run lint
npm run typecheck
npm test
```

Repeat this after small changes. **Docker does not need to be running for local tests.** Fix failing checks before preparing the PR for review.

For faster feedback on one test file:

```bash
uv run --locked python -m pytest ../tests/backend/unit/test_health.py
```

Run the full suite before the Docker check. All tests are in the root `tests/` folder (course rule): backend tests in `tests/backend/`, frontend tests in `tests/frontend/`. Use `test_*.py` and `test_` function names for Python, and `*.test.ts(x)` for TypeScript.

### Dependencies and the lockfile

`pyproject.toml` declares the dependencies and Python requirement; `uv.lock` records the resolved package versions. `--locked` checks that these files agree and fails if the lockfile would need to change.

After pulling someone else's dependency changes, the normal `uv run --locked ...` command updates your local environment from the committed lockfile. No manual package installation is needed.

When your task intentionally adds a dependency, use `uv add PACKAGE` (or `uv add --group test PACKAGE` for a test dependency), replacing `PACKAGE` with the actual package name. If you edit dependencies in `pyproject.toml` manually, run `uv lock`. Review and commit both files when they change, then rerun the tests. Do not edit `uv.lock` by hand.

## Local Docker check: verify the shared test environment

Install [Docker Desktop](https://docs.docker.com/get-started/get-docker/), or Docker Engine on Linux. Start Docker before this step; on Windows, use Linux containers.

The backend Dockerfile supplies Python 3.13.6, uv 0.13.0 and the locked dependencies; the frontend Dockerfile supplies Node 22 and the locked npm packages. Docker does not use your host's `.venv` or `node_modules`, so you can run this check without installing Python, uv or Node on the host.

From the repository root, run:

```bash
docker build -f backend/Dockerfile --target test -t synapseitu-backend:test .
docker build -f frontend/Dockerfile --target test -t synapseitu-frontend:test .
```

Each command builds the `test` stage of that Dockerfile, which runs the linters and tests while the image is built. A failing check fails the build. Without `--target test`, the same Dockerfiles build the production images that `deploy.yml` deploys.

**Rebuild after changing code, tests, dependencies, or a Dockerfile.** An image contains a snapshot of the files at build time.

The Dockerfiles describe how to prepare the test and production images. `.github/workflows/ci.yml` describes when GitHub runs the checks.

## Outer loop: pull requests and CI

Once local tests and the Docker check pass:

1. Review your changes with `git diff` and `git status`. Stage the intended files and commit them on your task branch.
2. Push the branch. On the first push, use `git push -u origin HEAD`; later pushes can use `git push`.
3. Open a PR with **base: `dev`** and **compare: your task branch**. Include the related issue, a short description, and how you tested the change. Add the appropriate assignee, labels, and a teammate as reviewer.
4. Fill in the PR template, including the **AI usage** section. Check that all CI jobs pass and address review feedback before merging. Release PRs from `dev` target `main` instead.

CI runs when a PR targeting `dev` or `main` is opened, reopened, or updated with new commits. Pushing a branch without an open PR does not trigger this workflow. No manual CI command is needed.

GitHub Actions checks out the PR code and runs three jobs: **Backend lint and tests** and **Frontend lint, typecheck and tests** build the `test` stages (the same commands as the local check), then **Production images build** builds both production images. Any failure fails the check.

### Deployment

`deploy.yml` deploys a merge to `dev` to the **staging** environment and a release merge to `main` to **production**. Until the servers are connected (WBS-14.6 sets the `DEPLOY_HOST`, `DEPLOY_USER` and `DEPLOY_SSH_KEY` secrets of each GitHub environment), every run is a dry run: it builds the images and reports what it would deploy.

### View results and fix a failed check

- Open the PR's **Checks** tab and select the failing job.
- Alternatively, open the repository's **Actions** tab, select **CI**, and open the relevant run.
- Expand the failing step to inspect its logs.

If CI fails, use the logs to identify the cause, reproduce the problem locally, fix it, and repeat the local tests and Docker check. Commit and push the fix to the **same PR branch**. GitHub reruns CI automatically; you do not need a new PR.

## Common setup problems

| Problem | What to check |
| --- | --- |
| `uv` is not found | Open a new terminal after installation and check `uv --version`. |
| `--locked` reports an outdated lockfile | Check whether dependency changes were intentional. Update the lockfile with `uv lock` for intentional changes; otherwise restore the unintended dependency edits. |
| Docker cannot connect to its daemon | Start Docker Desktop or Docker Engine and wait until it is ready. On Windows, check that Linux containers are enabled. |
| Container tests appear to use old code | Rebuild the image successfully before running the container again. |
| No CI run appears after a push | Check that the pushed branch has an open PR targeting `dev` or `main`. |
| Ruff reports formatting differences | Run `uv run --locked ruff format . ../tests/backend` in `backend/` and commit the result. |
| `npm ci` fails with a lockfile mismatch | Run `npm install` in `frontend/` only for an intentional dependency change, then commit `package.json` and `package-lock.json` together. |
