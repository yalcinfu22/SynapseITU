"""Fictional and deterministic seed records; no external university data is used."""

PROGRAMS = (
    {
        "id": "prog-cs-msc",
        "university_id": "demo-uni",
        "name": "MSc in Computer Science",
        "description": "Graduate study in computing, networks, and intelligent systems.",
        "updated_at": "2026-11-01T12:00:00Z",
        "department": "Computer Science",
        "degree_level": "MSc",
    },
    {
        "id": "prog-ee-phd",
        "university_id": "demo-uni",
        "name": "PhD in Electrical Engineering",
        "description": "Doctoral research in communication and signal processing.",
        "updated_at": "2026-11-02T12:00:00Z",
        "department": "Electrical Engineering",
        "degree_level": "PhD",
    },
)

LABS = (
    {
        "id": "lab-wireless",
        "university_id": "demo-uni",
        "name": "Wireless Systems Laboratory",
        "description": "Research in wireless networks and semantic communication.",
        "updated_at": "2026-11-03T12:00:00Z",
        "research_areas": ["Wireless Networks", "Semantic Communication"],
    },
    {
        "id": "lab-vision",
        "university_id": "demo-uni",
        "name": "Computer Vision Laboratory",
        "description": "Research in visual perception and machine learning.",
        "updated_at": "2026-11-03T12:00:00Z",
        "research_areas": ["Computer Vision", "Machine Learning"],
    },
)

POSITIONS = (
    {
        "id": "pos-wireless-ra",
        "university_id": "demo-uni",
        "name": "Graduate Research Assistant — Wireless Systems",
        "description": "Help develop and evaluate reliable wireless communication methods.",
        "updated_at": "2026-11-04T12:00:00Z",
        "lab_id": "lab-wireless",
        "program_id": "prog-cs-msc",
        "position_type": "Research Assistant",
        "status": "open",
        "application_deadline": "2027-03-01",
    },
    {
        "id": "pos-vision-intern",
        "university_id": "demo-uni",
        "name": "Research Internship — Computer Vision",
        "description": "Explore visual recognition models and evaluation workflows.",
        "updated_at": "2026-11-05T12:00:00Z",
        "lab_id": "lab-vision",
        "program_id": None,
        "position_type": "Internship",
        "status": "open",
        "application_deadline": "2027-04-15",
    },
)
