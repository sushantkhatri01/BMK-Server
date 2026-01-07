# Basic content filter for offensive words
# You can expand this list or use a library for more advanced filtering
BAD_WORDS = [
    "badword1", "badword2", "offensive1", "offensive2", "spamword"
]

def contains_bad_words(text: str) -> bool:
    text_lower = text.lower()
    for word in BAD_WORDS:
        if word in text_lower:
            return True
    return False

# Optionally, you can return the list of found words

def find_bad_words(text: str):
    text_lower = text.lower()
    return [word for word in BAD_WORDS if word in text_lower]
