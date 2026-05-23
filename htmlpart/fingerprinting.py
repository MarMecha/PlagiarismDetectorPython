import hashlib
import spacy

nlp = spacy.load("el_core_news_sm")


# ----------   Έλεγχος ποιότητας Shingles  ----------------

def shingle_quality(shingle, nlp_model):
    
    doc = nlp_model(shingle)
    stop_words_count = sum(1 for token in doc if token.is_stop)
    quality = 1 - (stop_words_count / len(doc)) if len(doc) > 0 else 0
    return quality


# ----------   Δημιουργία k-word Shingles  ----------------

def create_shingles(words, k):
    return [' '.join(words[i:i+k]) for i in range(len(words) - k + 1)]


# ----------   Hash με MD5  ----------------

def hash_shingle(shingle):
    return hashlib.md5(shingle.encode()).hexdigest()


# ----------   Εφαρμογή winnowing για μείωση τον fingerprints  ----------------

def winnow_fingerprints(fingerprints, w):

    filtered = []
    for i in range(len(fingerprints) - w + 1):
        window = fingerprints[i:i+w]
        min_fp = min(window, key=lambda x: x.split("|")[0])
        if not filtered or min_fp != filtered[-1]:
            filtered.append(min_fp)
    return filtered


# ----------   Workflow για την δημιουργία τον fingerprint   ----------------

def generate_fingerprints(text, k=7, w=30, quality_threshold=0.4):
    
    if not text:
        print("\nNo text provided.\n")
        return []

    words = text.split()
    if len(words) < k:
        print("\nNot enough words for shingling.\n")
        return []

    total_shingles = 0
    accepted_shingles = 0
    fingerprints = []

    shingles = create_shingles(words, k)

    for idx, shingle in enumerate(shingles):
        total_shingles += 1
        quality = shingle_quality(shingle, nlp)

        if quality >= quality_threshold:
            fp_hash = hash_shingle(shingle)
            fingerprint = f"{fp_hash}|{idx}"
            fingerprints.append(fingerprint)
            accepted_shingles += 1
            print(f"[{idx}] ✅ Shingle: \"{shingle}\" (quality: {quality:.2f})")
        else:
            print(f"[{idx}] ❌ Skipped: \"{shingle}\" (quality: {quality:.2f})")

    filtered_fps = winnow_fingerprints(fingerprints, w)

    # Efficiency report
    if total_shingles > 0:
        efficiency = (accepted_shingles / total_shingles) * 100
        print(f"\nFingerprint generation efficiency: {accepted_shingles}/{total_shingles} ({efficiency:.2f}%) accepted.\n")
    else:
        print("\nNo shingles generated.\n")

    return filtered_fps
    



    