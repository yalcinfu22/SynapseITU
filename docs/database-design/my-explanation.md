# My explanation of the database design work

I prepared the database design proposal for WBS-14.7. I used our Requirements Specification, Project Plan, Dummy University API and embedding decision as the starting point.

I organized the model around accounts and student profiles, opportunities and applications, community discussions, credits and AI usage, notifications, and university imports. I documented the relationships, keys, constraints, indexes and migration approach.

I kept common identity fields in users and linked each student to one academic profile through the same user ID. This avoids repeating names, email addresses and authentication data. The profile provides a place for education, skills, projects, interests and preferences.

I specified unique constraints to prevent duplicate applications and imported records. I also described how credit movements should remain balanced and how reservations protect funds during boosts and paid AI runs. Application updates and notification events are committed together so that delivery can be retried reliably.

For search, I included full-text indexes and 1024-dimensional embeddings with model identity and content revision. For imports, I specified that failed or incomplete source fetches preserve the last good data. Records missing from a complete source snapshot can be archived.

The detailed data contract describes proposed field types, lifecycle states and which rules need database constraints or transactional service logic. The migration plan describes versioned changes, review, seed data and upgrade, downgrade and recovery checks.

The design package is ready for module-owner review. Final approval, migrations and database acceptance tests are still pending. We also need to agree on eligibility field types, imported-position integration, vote reward behavior, quota timezone and settlement during account deletion.

## Questions I may receive

| Question | My answer |
|---|---|
| Why separate users and profiles? | Identity is shared across account roles. Academic information belongs to a student profile with the same primary key. |
| What prevents duplicate applications? | A unique opportunity/student pair. |
| How do repeated imports work? | The source, record type and external ID identify the existing row. |
| How are credits protected? | A single posting transaction locks accounts, validates funds and writes balanced entries. |
| What happens if AI fails? | Its reservation is released through an idempotent state transition. |
| Have the migrations been tested? | This deliverable is the design proposal. Execution tests follow when WBS-14.3 implements the migrations. |
