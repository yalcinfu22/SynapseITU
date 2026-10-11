# SynapseITU

Course project for **BLG 411E, 2026–2027 Fall**, developed by **The GOATS**.

- [Project board](https://github.com/users/yalcinfu22/projects/7)
- Customer TA: **Muhammet Alpaslan Tavukçu** ([@alpaslantavukcu](https://github.com/alpaslantavukcu))

## Team

The accounts below are the existing project-board collaborators. Development and management roles still need to be confirmed by the team.

| Member | GitHub | Development role | Management role |
| --- | --- | --- | --- |
| Furkan Yalçın | [@yalcinfu22](https://github.com/yalcinfu22) | To be confirmed | To be confirmed |
| Ahmed Said Gülşen | [@Ahmedsaid3](https://github.com/Ahmedsaid3) | To be confirmed | To be confirmed |
| Yavuz Selim Yağlıca | [@Aksaka56](https://github.com/Aksaka56) | To be confirmed | To be confirmed |
| Amr Nael Zuhdi Taweel | [@amrtaweel12](https://github.com/amrtaweel12) | To be confirmed | To be confirmed |
| Najib Attar | [@najib-attar](https://github.com/najib-attar) | To be confirmed | To be confirmed |
| Name to be confirmed | [@yusufkrkz](https://github.com/yusufkrkz) | To be confirmed | To be confirmed |

Each member must check that the email used for Git commits is linked to their own GitHub account. Run `git config user.email` in the local clone and compare it with GitHub **Settings → Emails**. Submit work and reviews using your own account.

## Repository layout

- `docs/`: project documents.
- `tests/`: tests; add subfolders for unit, performance, security, or other test types as needed.

## Document delivery workflow

Follow the course's [Project Submission and Tracking Guide](https://ninova.itu.edu.tr/Sinif/139.122080/SinifDosyalari?g8732594).

1. Write each document on its own branch and open a pull request to `main`.
2. Obtain at least one teammate's approval before requesting the TA's review.
3. Publish the named release by the announced deadline, targeting the document's PR branch. Verify that the release contains the document.
4. Request the TA's review. Apply requested revisions in the same PR and merge by the next deliverable's deadline.

| Deliverable | Branch | File | Release |
| --- | --- | --- | --- |
| Project Charter | `docs/charter` | `docs/Charter.md` | `charter-v1.0` |
| Project Plan | `docs/project-plan` | `docs/ProjectPlan.md` | `project-plan-v1.0` |
| Requirements Spec | `docs/requirements-spec` | `docs/RequirementsSpec.md` | `requirements-spec-v1.0` |
| Requirements Analysis | `docs/requirements-analysis` | `docs/RequirementsAnalysis.md` | `requirements-analysis-v1.0` |
| Design Spec | `docs/design-spec` | `docs/DesignSpec.md` | `design-spec-v1.0` |
| Test Spec | `docs/test-spec` | `docs/TestSpec.md` | `test-spec-v1.0` |

Exact deadlines are announced separately on Ninova. A release is the graded submission; opening a PR alone does not submit a document.

## Customer requests and tracking

- Within 48 hours of each customer meeting, open one issue per request and apply the existing `customer-requests` label.
- Include the request description, acceptance criteria, and the meeting it came from.
- Give each issue an assignee and a status on the project board.
- Include `Closes #<issue number>` in the PR that implements a request.
- If a request is deferred or declined, explain the scope or time constraint in its issue and close it as **not planned**.
