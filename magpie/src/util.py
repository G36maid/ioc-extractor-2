from scipy.stats import entropy
from collections import Counter


def entropy_threshold(string, loc, tokens, base=22, threshold=0.8) -> bool:
    """
    # checkout entropy of charactors count
    length of hexnums (A-Fa-f0-9) is 22,
    length of hexnums lowercase (a-f0-9) is 17
    """
    char_counts = Counter(tokens[0])
    char_entropy = entropy(list(char_counts.values()), base=base)
    return char_entropy > threshold