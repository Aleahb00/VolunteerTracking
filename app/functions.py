from rapidfuzz import fuzz

def is_similar(a, b, threshold=75):
    return fuzz.ratio(a.lower(), b.lower()) >= threshold