"""User profile and life periods.

Life periods are product categories for browsing memories, not medical or scientific facts.
"""
from dataclasses import dataclass, field

LIFE_PERIODS = {
    "Childhood": (10, 15),
    "College": (16, 22),
    "Early adulthood": (23, 30),
    "Family/Career": (31, 45),
}
# Used when the user does not pick a period: the teenage and early-adult years.
DEFAULT_AGE_RANGE = (10, 30)


def period_for_age(age: int) -> str:
    for name, (first, last) in LIFE_PERIODS.items():
        if first <= age <= last:
            return name
    return "Other"


@dataclass
class UserProfile:
    birth_year: int
    language: str
    genres: list[str] = field(default_factory=list)
    artists: list[str] = field(default_factory=list)
    name: str = ""

    def age_range(self, period: str | None) -> tuple[int, int]:
        if period is None:
            return DEFAULT_AGE_RANGE
        if period not in LIFE_PERIODS:
            raise ValueError(f"Unknown life period '{period}'. Choose from: {', '.join(LIFE_PERIODS)}")
        return LIFE_PERIODS[period]

    def year_range(self, period: str | None) -> tuple[int, int]:
        first_age, last_age = self.age_range(period)
        return self.birth_year + first_age, self.birth_year + last_age
