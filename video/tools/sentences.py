"""Split a scene's narration into sentences, the same way for every language (used to line up translations)."""
import re

SPLIT = re.compile(r"(?<=[.?!…»”\"])\s+(?=[«“\"A-ZА-ЯІЇЄҐ0-9])")


def sentences(text):
    return [x for x in SPLIT.split(text.replace("\n\n", " ").strip()) if x]
