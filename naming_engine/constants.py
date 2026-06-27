"""Naming suggestion constants."""

from __future__ import annotations

# Simplified syllable seeds by nakshatra pada (demo knowledge base)
NAKSHATRA_PADA_SYLLABLES: dict[tuple[str, int], tuple[str, ...]] = {
    ("Ashwini", 1): ("Chu", "Che", "Cho", "La"),
    ("Ashwini", 2): ("Li", "Lu", "Le", "Lo"),
    ("Bharani", 1): ("Li", "Lu", "Le", "Lo"),
    ("Rohini", 1): ("O", "Va", "Vi", "Vu"),
    ("Mrigashira", 1): ("Ve", "Vo", "Ka", "Ki"),
    ("Ardra", 1): ("Ku", "Gha", "Na", "Cha"),
    ("Punarvasu", 1): ("Ke", "Ko", "Ha", "Hi"),
    ("Pushya", 1): ("Hu", "He", "Ho", "Da"),
    ("Ashlesha", 1): ("Di", "Du", "De", "Do"),
    ("Magha", 1): ("Ma", "Mi", "Mu", "Me"),
}

RASHI_NAME_PREFIXES: dict[int, tuple[str, ...]] = {
    0: ("Ari", "Arjun", "Arya"),
    1: ("Vri", "Ved", "Varun"),
    2: ("Mit", "Mihir", "Manas"),
    3: ("Kar", "Kiran", "Kavya"),
    4: ("Sim", "Surya", "Saar"),
    5: ("Kan", "Kunal", "Kirti"),
    6: ("Tul", "Tara", "Tanvi"),
    7: ("Vrish", "Veer", "Vani"),
    8: ("Dhan", "Dhruv", "Diya"),
    9: ("Mak", "Maya", "Mohan"),
    10: ("Kumb", "Kiaan", "Kiran"),
    11: ("Meen", "Meera", "Milan"),
}

GENDER_SUFFIXES = {
    "male": ("esh", "an", "av", "in"),
    "female": ("a", "i", "ika", "ini"),
    "neutral": ("am", "an", "i", "ya"),
}
