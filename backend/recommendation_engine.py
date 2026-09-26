"""
recommendation_engine.py - CONTENT-BASED RECOMMENDATION using TF-IDF + COSINE SIMILARITY

Written with only the Python standard library (no numpy / scikit-learn), so it
runs on AWS Lambda without any extra layer.

HOW IT WORKS (simple version)
-----------------------------
1. Every book becomes a "text profile": category + subject + keywords +
   description (+ title). Important fields (subject, keywords) count more.
2. TF-IDF turns each text into numbers:
     TF  = how often a word appears in that text (1 + log(count))
     IDF = how rare the word is across ALL books  log((1+N)/(1+df)) + 1
     weight = TF x IDF   (rare, meaningful words get bigger weights)
3. The STUDENT also gets a text profile:
     interests (weight 3) + subjects (weight 2)  -> "interest vector"
     previously selected books                   -> "history vector" (average)
4. COSINE SIMILARITY = how close two vectors point in the same direction
     cos = (A . B) / (|A| x |B|)  ->  0 (nothing in common) ... 1 (identical)
5. PERSONALIZED SCORE
     with history : 0.7 x cos(interests, book) + 0.3 x cos(history, book)
     no history   : cos(interests, book)             (new student)
     no interests : cos(history, book)               (only history exists)
6. Books already read are removed, the rest are sorted by score,
   and the TOP 5 (score > 0) are returned.
"""
import math
import re
from collections import Counter

INTEREST_WEIGHT = 3       # student's interests count 3x
SUBJECT_WEIGHT = 2        # student's subjects count 2x
INTEREST_SHARE = 0.7      # share of the final score from interests
HISTORY_SHARE = 0.3       # share of the final score from reading history

# Field weights when building a BOOK profile
BOOK_FIELD_WEIGHTS = (
    ("category", 1),
    ("subject", 2),
    ("keywords", 2),
    ("title", 1),
    ("description", 1),
)

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "in",
    "is", "it", "its", "of", "on", "or", "that", "the", "to", "was", "with",
    "this", "these", "those", "into", "also", "than", "then", "their", "them",
    "who", "will", "can", "how", "book", "books", "covers", "cover", "study",
}

# Short forms students type -> full words that appear in book descriptions.
SYNONYMS = {
    "ai": ["artificial", "intelligence"],
    "ml": ["machine", "learning"],
    "dl": ["deep", "learning"],
    "js": ["javascript"],
    "db": ["database"],
    "dbms": ["database"],
    "os": ["operating", "system"],
    "ds": ["data", "structure"],
    "cn": ["network"],
    "se": ["software", "engineering"],
    "iot": ["sensor", "embedded"],
    "cyber": ["security"],
}

TOKEN_RE = re.compile(r"[a-z0-9+#]+")


# ----------------------------------------------------------------------------
# Step 1: text cleaning
# ----------------------------------------------------------------------------
def _stem(word):
    """Very light stemming: 'networks' -> 'network'. Same rule for books and students."""
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def tokenize(text):
    """Lower-case, split into words, remove stop-words, expand short forms."""
    if not text:
        return []
    if isinstance(text, (list, tuple)):
        text = " ".join(str(t) for t in text)
    tokens = []
    for raw in TOKEN_RE.findall(str(text).lower()):
        if raw in STOP_WORDS:
            continue
        tokens.append(_stem(raw))
        for extra in SYNONYMS.get(raw, []):
            tokens.append(_stem(extra))
    return tokens


def term_counts(parts):
    """parts = [(text, weight), ...]  ->  Counter({word: weighted count})"""
    counts = Counter()
    for text, weight in parts:
        for tok in tokenize(text):
            counts[tok] += weight
    return counts


def book_term_counts(book):
    """Build the weighted word counts of ONE book."""
    return term_counts([(book.get(field, ""), w) for field, w in BOOK_FIELD_WEIGHTS])


# ----------------------------------------------------------------------------
# Step 2: TF-IDF
# ----------------------------------------------------------------------------
def compute_idf(list_of_counts):
    """IDF for every word in the library:  log((1+N)/(1+df)) + 1"""
    n_docs = len(list_of_counts)
    doc_freq = Counter()
    for counts in list_of_counts:
        doc_freq.update(counts.keys())
    return {t: math.log((1 + n_docs) / (1 + df)) + 1 for t, df in doc_freq.items()}


def tfidf_vector(counts, idf):
    """Turn word counts into a normalised TF-IDF vector (dict word -> weight)."""
    vec = {}
    for term, count in counts.items():
        if term in idf and count > 0:
            vec[term] = (1 + math.log(count)) * idf[term]
    return _normalize(vec)


def _normalize(vec):
    length = math.sqrt(sum(v * v for v in vec.values()))
    if length == 0:
        return {}
    return {t: v / length for t, v in vec.items()}


# ----------------------------------------------------------------------------
# Step 3: cosine similarity
# ----------------------------------------------------------------------------
def cosine_similarity(vec_a, vec_b):
    """Both vectors are already normalised, so cosine = dot product."""
    if not vec_a or not vec_b:
        return 0.0
    if len(vec_a) > len(vec_b):
        vec_a, vec_b = vec_b, vec_a
    return sum(w * vec_b.get(t, 0.0) for t, w in vec_a.items())


def _centroid(vectors):
    """Average of several vectors (used for the reading-history profile)."""
    total = Counter()
    for vec in vectors:
        for t, w in vec.items():
            total[t] += w
    return _normalize({t: w / len(vectors) for t, w in total.items()}) if vectors else {}


# ----------------------------------------------------------------------------
# Step 4: main function
# ----------------------------------------------------------------------------
def recommend(books, interests, subjects, history=None, top_n=5):
    """
    books     : list of book dicts (bookId, title, author, category, subject,
                keywords, description, imageUrl)
    interests : list of strings, e.g. ["Java", "AI"]
    subjects  : list of strings, e.g. ["Programming"]
    history   : list of {"bookId": "B001", "rating": 4 or None}
    Returns   : list of book dicts + score, matchPercent, matchedTerms (best first)
    """
    interests = interests or []
    subjects = subjects or []
    history = history or []
    if not books:
        return []

    # 1) Vectors for all books
    counts_list = [book_term_counts(b) for b in books]
    idf = compute_idf(counts_list)
    book_vectors = [tfidf_vector(c, idf) for c in counts_list]
    by_id = {b.get("bookId"): i for i, b in enumerate(books)}

    # 2) Student interest vector
    interest_counts = term_counts(
        [(" ".join(interests), INTEREST_WEIGHT), (" ".join(subjects), SUBJECT_WEIGHT)]
    )
    interest_vec = tfidf_vector(interest_counts, idf)

    # 3) Student history vector (books rated 1-2 are ignored: student did not like them)
    read_ids = set()
    history_vectors = []
    for item in history:
        book_id = item.get("bookId")
        if book_id not in by_id:
            continue
        read_ids.add(book_id)
        rating = item.get("rating")
        if rating is not None and rating <= 2:
            continue
        vec = book_vectors[by_id[book_id]]
        repeat = 2 if (rating is not None and rating >= 4) else 1   # liked books count double
        history_vectors.extend([vec] * repeat)
    history_vec = _centroid(history_vectors)

    # 4) Score every book
    scored = []
    for book, book_vec in zip(books, book_vectors):
        if book.get("bookId") in read_ids:
            continue  # do not recommend a book the student already selected
        if interest_vec and history_vec:
            score = INTEREST_SHARE * cosine_similarity(interest_vec, book_vec) \
                    + HISTORY_SHARE * cosine_similarity(history_vec, book_vec)
        elif interest_vec:
            score = cosine_similarity(interest_vec, book_vec)
        else:
            score = cosine_similarity(history_vec, book_vec)
        if score > 0:
            scored.append((score, book, book_vec))

    # 5) Sort (best first; title breaks ties so results are stable) and cut to top N
    scored.sort(key=lambda x: (-x[0], x[1].get("title", "")))
    results = []
    for score, book, book_vec in scored[:top_n]:
        item = dict(book)
        item["score"] = round(score, 4)
        item["matchPercent"] = int(round(score * 100))
        item["matchedTerms"] = _matched_terms(interest_vec or history_vec, book_vec)
        results.append(item)
    return results


def _matched_terms(profile_vec, book_vec, limit=4):
    """Words that contributed most to the match (shown as 'Why this book?')."""
    shared = [(profile_vec[t] * book_vec[t], t) for t in profile_vec if t in book_vec]
    shared.sort(reverse=True)
    return [t for _, t in shared[:limit]]


def build_model_snapshot(books):
    """Summary of the TF-IDF model (saved to S3 model/ folder for demo / viva)."""
    counts_list = [book_term_counts(b) for b in books]
    idf = compute_idf(counts_list)
    top = sorted(idf.items(), key=lambda kv: -kv[1])[:20]
    return {
        "algorithm": "TF-IDF + cosine similarity (content-based)",
        "numBooks": len(books),
        "vocabularySize": len(idf),
        "interestWeight": INTEREST_WEIGHT,
        "subjectWeight": SUBJECT_WEIGHT,
        "interestShare": INTEREST_SHARE,
        "historyShare": HISTORY_SHARE,
        "idf": {t: round(v, 4) for t, v in sorted(idf.items())},
        "rarestTerms": [t for t, _ in top],
    }
