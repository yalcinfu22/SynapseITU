"""Turkish/English normalization for the keyword baseline.

* Case folding that is safe for both languages (``I`` and ``İ`` -> ``i``) and folds the
  Turkish letters to ASCII, so "goruntu isleme" matches "görüntü işleme".
* First-5-characters stemming (F5). For Turkish, an agglutinative language, F5 truncation
  performs close to a morphological stemmer in retrieval (Can et al., "Information
  retrieval on Turkish texts", JASIST 59(3), 2008); it is also acceptable for English.
"""

import re
import unicodedata

_TR_FOLD = str.maketrans(
    {"İ": "i", "I": "i", "ı": "i", "ğ": "g", "Ğ": "g", "ü": "u", "Ü": "u", "ş": "s", "Ş": "s"}
    | {"ö": "o", "Ö": "o", "ç": "c", "Ç": "c", "â": "a", "î": "i", "û": "u"}
)
_TOKEN = re.compile(r"[a-z0-9+#]+")

_EN_STOPWORDS = (
    "a an and are as at be by for from has have in is it its of on or that the this to "
    "was were will with we you your our i me my"
)
_TR_STOPWORDS = (  # already ASCII-folded
    "ve veya ile de da bir bu su o icin gibi olan olarak ama fakat ancak cok daha en "
    "mi mu ne ki ya hem her ise kadar sonra once ben biz sen siz"
)
STOPWORDS = frozenset(_EN_STOPWORDS.split(" ") + _TR_STOPWORDS.split(" "))
STEM_LENGTH = 5


def fold(text: str) -> str:
    text = text.translate(_TR_FOLD).lower()
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def tokenize(text: str) -> list[str]:
    return [t[:STEM_LENGTH] for t in _TOKEN.findall(fold(text)) if t not in STOPWORDS]
