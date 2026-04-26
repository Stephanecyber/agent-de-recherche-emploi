from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Job:
    id: str
    title: str
    company: str
    url: str
    source: str
    location: str
    region: str
    salary: str
    remote: str
    contract_type: str
    published_at: datetime
    age_hours: float
    description: str
    skills_detected: list
    experience_level: str
    relevance_score: int
    detected_at: datetime = field(default_factory=datetime.now)
    status: str = "Nouveau"
    notes: str = ""
    domain: str = "Reseaux & Securite"
    phone: str = ""
    email_contact: str = ""

    def unique_key(self) -> str:
        return f"{self.source}::{self.id}"
