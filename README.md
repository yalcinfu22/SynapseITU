# SynapseITU

Course project repository for SynapseITU.

Project documentation, team roles, and the project charter are being prepared through pull requests.

## Development and testing

### Prerequisites

- Docker must be installed and running with Linux container support.
  On Windows, start Docker Desktop before running the commands below.
- The test image uses Python 3.13.6 and uv 0.13.0.
- Test dependencies are declared in `pyproject.toml`, with resolved
  versions recorded in `uv.lock`.

### Run tests with Docker

Run these commands from the repository root:

```bash
docker build -t synapseitu-tests .
docker run --rm synapseitu-tests
```

The first command builds the test image. The second runs
`python -m pytest` using the container's virtual environment.

Rebuild the image after changing the code, tests, dependencies,
or Dockerfile so that the container includes your latest changes.

### Fast local testing

For quick feedback during development, install Python 3.13.6
and uv 0.13.0, then run:

```bash
uv run --locked --group test python -m pytest
```

uv creates the local `.venv` environment if needed and installs the
required dependencies from the lockfile.

Tests are located under `tests/`, including its subdirectories.
Use `test_*.py` filenames and `test_` prefixes for test functions.

## Continuous integration

The workflow is defined in `.github/workflows/ci.yml`.

It runs when a pull request targeting `dev` or `main` is opened,
reopened, or updated with new commits.

The workflow checks out the code, builds a test image using the
same Dockerfile used locally, and runs pytest inside a container.
A build or test failure causes the CI check to fail.

### View CI results

- Open the pull request's **Checks** tab and select **Docker tests**.
- Alternatively, open the repository's **Actions** tab, select
  **CI**, and open the relevant workflow run.
- Expand **Build test image** or **Run tests** to inspect the logs.