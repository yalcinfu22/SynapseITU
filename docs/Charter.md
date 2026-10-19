# Project Charter: SynapseITU

## 1. Project Purpose and Objectives

SynapseITU is a web platform that connects students, academics, researchers, clinicians and industry professionals around education and research opportunities through intelligent matching. Students describe their interests, skills and goals, talk to a university-aware chatbot to discover suitable opportunities and graduate programs, receive explainable recommendations, adapt their CV to a specific opportunity, and send interest requests to academics, and vice versa. Opportunity owners publish positions with structured requirements and receive a ranked, explained list of suitable candidates. Both parties make comments and recommendations on each other.

### 1.1 How SynapseITU Differs from LinkedIn and Similar Platforms

General platforms such as LinkedIn already use embedding-based retrieval and LLM-based ranking for job search. SynapseITU does not compete on general job matching; its difference lies in being designed for **academic and research opportunities** and their specific needs:

| LinkedIn and similar platforms | SynapseITU |
|---|---|
| General jobs and companies | Specialized for academic opportunities: lab positions, research assistantships, MSc/PhD programs, clinical and industry research collaborations |
| No knowledge of university programs, admission rules or lab structure | A university-aware chatbot answers from institutional data: programs, labs, advisors, requirements and deadlines |
| Relevance score without reasons | Logical matching: every eligibility rule (degree, GPA, language, deadline) is checked explicitly and every recommendation is explained requirement by requirement |
| Profile is static | CV Adaptor suggests changes to the student's CV for a specific opportunity or program |
| Reviews only for companies (on other sites), not for labs or advisors | Verified comments from students and academics on each opportunity, moderated by AI |
| Same recommendations for all users | Credit system: users who contribute to the community earn credits that unlock deeper AI recommendations |

## 2. Stakeholders & Roles

* **Project Manager:** Yavuz Selim Yağlıca
* **Software Engineering Team:** All members work full-stack, but each member owns one module end to end (frontend, backend and tests), one broader technical role and holds one management role. The detailed work breakdown will be given in the Project Plan.

| Member | Development Role (Owned Module) | Broad Technical Role | Management Role |
|---|---|---|
| Yavuz Selim Yağlıca | Full-Stack Developer: Opportunities, Applications, Notifications & Comment System | Backend & API Manager | Project Manager |
| Furkan Yalçın | Full-Stack Developer: Matching & Recommendation Engine + Credit System | Designer-Architect | GitHub Workflow Manager |
| Ahmed Said Gülşen | Full-Stack Developer: Chatbot & MCP Integration | AI Manager | DevOps Manager |
| Ahmet Yusuf Kurukız | Full-Stack Developer: User Profiles & CV Adaptor | UI Manager | Scrum Master |
| Najeeb Attar | Full-Stack Developer: Authentication & RBAC (Role-Based Access Control), AI Moderation & Admin Panel | QA Tester | Requirement Document Manager |
| Amr Naweel Zuhdi Taweel | Full-Stack Developer: Data Agent & Dummy University Integration | Database Manager | Test Manager |
| AI Coding Assistants | Software Developer (supervised): code generation, refactoring, test writing | – |

* **Rules for AI team members:** AI coding assistants may open pull requests, but every PR is reviewed and approved by at least one human team member; nothing is merged directly. Token usage of AI tools is tracked from the start of implementation.
* **GH Repo/Project URL:** https://github.com/yalcinfu22/SynapseITU

## 3. Project Scope

### Project domain

Higher education, academic research, and university–industry–hospital collaboration. Possible customers are universities, research hospitals, research institutes, laboratories and the R&D departments of companies. Key users are:

* **Students and early-career researchers** looking for lab positions, research assistantships, internships, and MSc/PhD programs
* **Opportunity owners** (academics, lab leaders, clinicians, industry R&D teams) publishing positions and collaboration calls
* **Administrators** managing users, institutions and moderation

### In-Scope

* **User Accounts, Authentication & Authorization:** Registration, login, institutional e-mail verification (e.g. `@itu.edu.tr`), and role-based access control for Student, Academic/Opportunity Owner and Admin roles.

* **User Profile Management:** Profiles with education, skills, research interests, publications, projects and preferences (field, degree, country, start date). Profiles can be filled automatically from an uploaded CV.

* **Opportunity & Application Management:** Creating and editing opportunities with structured requirements (must-have and nice-to-have, each with a weight) and a free-text description; publishing, opening and closing applications, archiving; applying to an opportunity and tracking application status; announcements to applicants.

* **Feature 1 – University Chatbot (unique):** A chat interface where students describe what they are looking for in natural language (Turkish or English) and find suitable opportunities and graduate programs at the university.
    * The chatbot answers **only from the platform database** (opportunities, programs, labs, advisors, requirements, deadlines) and links every answer to its source.
    * It asks clarifying questions when the request is vague (e.g. degree level, field, funding).
    * It accesses the database through tools exposed by an MCP server (see Section 4.3), so it can search, filter and compare opportunities instead of guessing.
    * A separate **data agent** collects information from external sources (the dummy university's API, public program pages, OpenAlex) and stores it in the database. The agent gathers data from many sources; the chatbot only serves what is stored.

* **Feature 2 – CV Adaptor (unique):** The student selects an opportunity or program, and the AI compares their CV with its requirements.
    * Shows which requirements are met, partially met or missing.
    * Suggests concrete changes: sections to reorder, relevant projects or skills to highlight, missing keywords, wording improvements.
    * The AI never invents experience; it only reorganises and rephrases what is in the CV and points out real gaps.
    * The student accepts or rejects each suggestion and can download the adapted version.

* **Feature 3 – Recommendation System:** Personalised recommendation of opportunities to students (and of candidates to opportunity owners), similar to LinkedIn's "Jobs recommended for you", using the matching engine described in Section 4.2.
    * A "Recommended for you" feed on the dashboard
    * An explanation for each recommendation ("You match 4 of 5 requirements; missing: German B2")
    * Recommendations improve with user feedback (saved, applied, dismissed)

* **Feature 4 – Comment System with AI Moderation (unique):** Comments on each opportunity that stay inside the application.
    * Students (e.g. current or former lab members) and academics can comment; each comment shows the commenter's verified role.
    * Opportunity owners can reply; their answers are highlighted.
    * An AI moderation step checks every comment before it is published and blocks insulting, abusive or spam comments; borderline cases go to an admin.
    * Users can report comments.

* **Feature 5 – Credit System (unique):** Users earn credits by contributing to the platform and spend them on advanced AI features.
    * Earning: completing the profile, writing helpful comments (upvoted by others), verified reviews.
    * Spending: deeper AI recommendations (full LLM-based analysis instead of the basic list), additional CV Adaptor runs, higher visibility of questions in comments.
    * Credits also limit the use of expensive LLM calls, keeping AI costs under control.

* **Feature 6 – Notifications:** In-website notifications (and optional e-mail) for new recommended opportunities, application status changes, replies to comments, interest requests and approaching deadlines.

* **Dummy University Integration:** A dummy university service with its own API (programs, labs, positions). A connector imports this data into SynapseITU to demonstrate how real institutional systems could be integrated.

### Optional In-Scope Features

These may be implemented if time permits after the core functionality is completed.

* **Learning from feedback:** Learning recommendation weights from user actions.
* **Direct messaging:** Messaging between a student and an academic after an interest request is accepted.

### Out-of-Scope

* **Native Mobile Applications:** Development of native Android and iOS applications. The platform will be accessible through a responsive web interface.
* **Payments & Subscriptions:** Payment processing, billing and subscription management. Credits cannot be bought with money.
* **Integration with Real Institutions' Internal Systems:** Connecting to real university, hospital or company systems. This is demonstrated only with the dummy university.
* **Training our own LLM:** Pre-trained models are used through APIs.
* **Autonomous AI decisions:** The AI never accepts or rejects applicants and never applies on behalf of a student; it only recommends.
* **Languages other than Turkish and English.**

## 4. Technology Stack

### Backend Stack

* Python and FastAPI (service-oriented REST APIs)
* PostgreSQL for structured application data, with the pgvector extension for storing embeddings
* Redis for caching and background jobs (embedding generation, notifications, moderation)
* JWT-based authentication and role-based access control
* Docker and Docker Compose for containerization and local development
* Cloud deployment on a provider such as Amazon Web Services (AWS); final provider to be selected based on cost, availability and deployment requirements
* GitHub Actions for CI/CD

### Frontend Stack

* Next.js (React and TypeScript)
* Tailwind CSS
* Streaming chat interface for the chatbot

### AI Stack

* **Large Language Model (LLM):** [Provider and model to be decided, e.g. Claude, GPT or Gemini] accessed via API. Used for the chatbot, logical matching reasoning, recommendation explanations, CV Adaptor and comment moderation. A smaller, cheaper model from the same provider is used for simple tasks such as extracting fields from CVs.
* **Text embedding model:** A multilingual embedding model (e.g. BAAI bge-m3, which supports Turkish and English) that converts profiles, opportunities and programs into vectors.
* **Vector search:** pgvector inside PostgreSQL for semantic similarity search, combined with PostgreSQL full-text search for keyword matching.
* **Model Context Protocol (MCP):** An MCP server exposes platform functions (search opportunities, get program details, check eligibility, read profile, read comments) as tools that the LLM can call.
* **Agent framework:** LangGraph for multi-step chatbot and data-agent workflows.
* **Observability:** Langfuse for tracing LLM calls and tracking token usage and cost.

#### 4.1 How the AI components work (text-based pipeline)

All AI features work on text. The same pipeline is used everywhere:

1. **Text preparation:** Profiles, CVs, opportunities and programs are converted into clean text (CVs are parsed from PDF).
2. **Embedding:** The embedding model turns each text into a vector. Texts with similar meaning have nearby vectors, so "computer vision" and "görüntü işleme" are close even though the words differ.
3. **Storage:** Vectors are stored in PostgreSQL (pgvector) next to the structured data.
4. **Retrieval:** For a query, the system finds the most similar items by vector distance and by keywords.
5. **Giving the results to the LLM:** Only the retrieved items, the user's profile and the relevant requirements are given to the LLM, together with instructions. The LLM never answers from its own general knowledge about our data.
6. **Generation:** The LLM produces the answer, recommendation explanation, CV suggestions or moderation decision in a fixed, validated format.

#### 4.2 How matching works (logical matching with an LLM and MCP)

Matching is the core of the system and runs in four steps:

1. **Logical eligibility check (rules):** Hard requirements are checked as explicit rules: degree level, GPA threshold, language certificate, citizenship constraints, deadline, application status. Ineligible opportunities are removed or marked, with the reason shown.
2. **Semantic retrieval (embeddings):** Among eligible opportunities, the most relevant ones are found with vector similarity and keyword search together.
3. **LLM reasoning via MCP:** The LLM receives the short list and evaluates each opportunity against the user's profile requirement by requirement. When it needs more information, it calls MCP tools (e.g. get program details, check eligibility) instead of guessing.
4. **Scoring and explanation:** Each match gets a score and a report: met, partially met and missing requirements, with the evidence from the profile.

Cheap steps (rules and vector search) run on all data; the expensive LLM step runs only on a short list. This keeps matching accurate, explainable and affordable. We will compare this approach with plain keyword search and plain embedding search on a labelled test set, and keep only the steps that improve the results.

#### 4.3 Chatbot vs. data agent

| | Data Agent | Chatbot |
|---|---|---|
| Purpose | Collects and updates data | Answers users |
| Sources | Dummy university API, public program pages, OpenAlex | Only the SynapseITU database (through MCP tools) |
| Runs | In the background, on a schedule | On demand, in the chat interface |
| Output | Structured records stored in the database | Answers with links to opportunities and programs |

## 5. Project Milestones

| Deliverable | Submission Schedule | Revision Deadline |
|---|---|---|
| Project Charter | Week of 5 October 2026 | Week of 19 October 2026 |
| Project Plan | Week of 19 October 2026 | Week of 2 November 2026 |
| Requirements Specification | Week of 2 November 2026 | Week of 23 November 2026 |
| Requirements Analysis | Week of 23 November 2026 | Week of 7 December 2026 |
| Design Specification | Week of 7 December 2026 | Week of 21 December 2026 |
| Test Specification | Week of 21 December 2026 | 25 December 2026 |
| Code Freeze / Final Release | 25 December 2026 | — |
| Final Demo | 26 December 2026 | — |
| Final Presentation | Week of 28 December 2026 | — |
