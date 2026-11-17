# Data contract and enforcement

Version 2 · Proposed implementation decisions · WBS-14.7

## Shared conventions

| Concept | Proposed PostgreSQL representation |
|---|---|
| Primary and foreign keys | uuid; application-generated IDs; matching types on both sides |
| Names, URLs, storage keys, digests and external identifiers | text; required human-readable names must contain non-whitespace characters |
| Timestamps | timestamptz; creation timestamps default to current_timestamp; application maintains updated_at |
| States and roles | text with named CHECK constraints, with explicit values below and in the schema |
| Credits and ledger entries | bigint; positive quantities for requests, signed quantities for entries |
| Counters and ordinal values | integer; nonnegative counters and positive suggestion ordinals |
| Profile sections and validated AI payloads | jsonb; require correct JSON container type in DB and validate field schemas in service |
| Flags and weights | boolean and numeric; finite nonnegative requirement weights |
| Source deadline | date; retain the source value and agree a closing timezone before converting to an instant |
| Platform opportunity deadline | timestamptz; form supplies a timezone-aware instant |
| Quota month | date representing the first day of the accounting month |
| Vector model identity | text containing provider/model/revision; vector(1024) and content hash alongside it |

## Profile sections and eligibility

Propose arrays for education, skills, projects and interests, and an object for preferences. Education entries contain institution, degree level, field, start date and optional end date and grade with its grading scale. Skills and interests use normalized terms. Projects contain title and description. Preferences may contain locations and opportunity types.

Completion is the number of valid, populated sections divided by five. The reward requires at least four sections including education and skills. An empty object or array never counts as complete. The completion reward uses a stable user-scoped event key.

| Proposed requirement type | Threshold shape | Evaluation |
|---|---|---|
| degree_level | minimum level using an agreed ordered vocabulary | Compare the student's qualifying education |
| field_of_study | allowed normalized fields | Match qualifying education |
| skill | required normalized term | Match the skills array |
| language | language and minimum level | Requires a reviewed structured language field |
| grade | minimum and grading scale | Compare only on a matching scale; otherwise report cannot be checked |

These are proposed rule types for review with the Eligibility owner. Language support requires extending the profile contract before implementation. Preserve the distinction between missing data and a confirmed failure. Reject unrecognized rule types on opportunity publication.

## Lifecycle values

| Field | Proposed allowed values |
|---|---|
| posts.visibility | visible, hidden, removed |
| posts.question_state | open, closed for questions; NULL for discussions and replies |
| reports.status | open, resolved, dismissed |
| import_runs.outcome | running, succeeded, partial, failed |
| import_source_runs.status | running, succeeded, partial, failed |
| ai_runs.state | reserved, running, succeeded, failed |
| ai_runs.feature | cv_adaptor, ai_search, discovery, chatbot, candidate_ranking, cv_summary |
| import_sources.source_type | dummy_api, public_page |

Every completed import source result includes a finish time. A run can succeed with zero records only when a complete source snapshot was obtained. AI charging is feature-specific. Student-initiated quota-bearing requests reserve allowance. Background summaries and owner ranking require an explicit unmetered funding value, with NULL quota month and no student counter update.

## Database and service responsibilities

| Invariant | Enforcement |
|---|---|
| Unique identity | Unique normalized users.email; registration service normalizes consistently |
| One student profile | student_profiles.user_id is both PK and FK |
| A reply belongs to its parent's board | UNIQUE posts(id, board_id), composite FK (parent_id, board_id) references posts(id, board_id) |
| An accepted answer belongs to its question | UNIQUE posts(id, parent_id), FK (answer_id, question_id) references posts(id, parent_id) |
| Answer acceptance is valid | Lock question; require question kind, eligible reply, asker authorization and distinct answer author |
| Required lab for imported position | Import transaction validates exactly one position_lab link before commit; reject incomplete positions |
| Credit conservation | Restricted posting function inserts at least two net entries and validates zero sum; revoke direct runtime writes to entries and cached balances |
| Credit balance consistency | Same posting transaction updates cached balances and ledger; reconcile balance against ledger sum in acceptance tests |
| Exactly-once profile reward | Unique stable transaction key for user and completion event |
| Retry-safe AI settlement | Lock AI run; state guard plus unique settlement transaction reference |
| Atomic application event | Application update, history row and outbox insert share one transaction |
| Search index freshness | Persist content revision; background result updates only the matching revision |

Add created_at to credit_entries for account/time history and a UNIQUE stable_key to credit_accounts for treasury and escrow accounts. A boost receives its own escrow account through question_boosts.escrow_account_id, a unique required FK. This makes reserved boost funds identifiable and settlement auditable.

## Proposed accounting defaults

| Setting | Initial value from Requirements Specification |
|---|---|
| Answer upvote reward | 2 credits |
| Accepted answer reward | 5 credits |
| First qualifying profile completion | 10 credits |
| Verified-user post reward | 1 credit |
| Minimum question boost | 5 credits |
| Monthly student AI allowance | 10 runs |
| Extra CV Adaptor run | 10 credits |

Treasury supplies rewards and receives settled paid-run charges. A boost transfers spendable funds into its escrow and later to the answerer or back to the asker. The treasury can carry a negative accounting balance. User and escrow accounts must remain nonnegative.

For quota reservation, lock the user/month row and check used plus reserved against the current configured limit. Count reservations as occupied capacity. Failed runs release the reservation. A recovery worker reconciles interrupted runs using a durable execution identifier before settling or releasing. Persist the cost and settings revision on each run so settings changes cannot alter an existing reservation.

## Deletion and historical references

| Data | Proposed action |
|---|---|
| Tokens, profile, CV metadata and adaptations | Revoke tokens, enqueue file cleanup, then cascade dependent personal data |
| Applications and interest requests | Delete the departing user's private workflow records and associated history; scrub related notification payloads |
| Posts and moderation history | Retain anonymized public content where required; null author/admin/reporter references and scrub identifying payloads |
| Ledger | Retain balanced entries under an anonymous account; remove personal account mapping after reservation settlement |
| AI runs and outbox | Remove personal payloads; retain minimum operational state needed to finish pending work |
| Embeddings | Cascade with deleted parent records; regenerate after anonymized content changes |

Each ON DELETE action must be written explicitly in the migration. Settlement of an account's outstanding reservations and treatment of a deleted report target require owner agreement, to be recorded during the subsequent schema review.
