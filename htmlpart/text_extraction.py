import pdfplumber
import spacy

nlp = spacy.load("el_core_news_sm")


# ----------   Εξαγωγη σελίδων   ----------------

def open_pdf_pages(pdf_path):
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            yield page_num, page


# ----------   Εξαγωγή λέξεων από το PDF   ----------------

def extract_words_from_page(page):
    
    return page.extract_words(
        extra_attrs=["fontname", "size"],
        keep_blank_chars=False,
        use_text_flow=True
    )



# ----------   Δημιουργία ακατέργαστου κειμένου και μετατοπίσεων από τις εξαγόμενες λέξεις   ----------------

def build_raw_text_and_offsets(words):
    """Build raw text and offsets from extracted words."""
    texts = [w['text'] for w in words]
    offsets = []
    cur_offset = 0
    for t in texts:
        offsets.append(cur_offset)
        cur_offset += len(t) + 1  # account for space
    raw_text = ' '.join(texts)
    return raw_text, offsets


# ----------   lemmatizetion of raw text  ----------------

def lemmatize_text(raw_text):
    doc = nlp(raw_text)
    lemmas = []

    for token in doc:
        # αγνόησε σημεία στίξης και κενά
        if token.is_punct or not token.text.strip():
            continue

        lemmas.append({
            'lemma': token.lemma_,
            'start': token.idx,
            'end': token.idx + len(token.text)
        })

    return lemmas

# ----------   Αντιστοίχηση λέξεων με συντεταγμένες τοποθεσίας   ----------------

def match_words_to_lemmas(words, offsets, lemma_map, page, page_num, word_index_start=0):
    
    full_text = []
    positions = []
    word_index = word_index_start

    for i, word in enumerate(words):
        word_text = word['text']
        matched_lemma = word_text.lower()

        word_offset = offsets[i]
        for lm in lemma_map:
            if lm['start'] <= word_offset < lm['end']:
                matched_lemma = lm['lemma']
                break

        full_text.append(matched_lemma)
        position_data = {
            'page': page_num + 1,
            'x0': word['x0'],
            'y0': page.height - word['bottom'],
            'x1': word['x1'],
            'y1': page.height - word['top'],
            'word_index': word_index,
            'text': matched_lemma
        }
        positions.append(position_data)

        print(f"[{word_index}] Word: \"{matched_lemma}\"")
        print(f"    -> Page: {position_data['page']}, X0: {position_data['x0']:.2f}, Y0: {position_data['y0']:.2f}, X1: {position_data['x1']:.2f}, Y1: {position_data['y1']:.2f}")

        word_index += 1

    return full_text, positions, word_index


# ----------   workflow για την εξαγωγη και επεξεργασία κειμένου   ----------------

def extract_text_with_positions(pdf_path):

    full_text = []
    positions = []
    word_index = 0

    for page_num, page in open_pdf_pages(pdf_path):
        words = extract_words_from_page(page)
        if not words:
            continue

        raw_text, offsets = build_raw_text_and_offsets(words)
        lemma_map = lemmatize_text(raw_text)
        page_text, page_positions, word_index = match_words_to_lemmas(words, offsets, lemma_map, page, page_num, word_index)

        full_text.extend(page_text)
        positions.extend(page_positions)

    return ' '.join(full_text), positions