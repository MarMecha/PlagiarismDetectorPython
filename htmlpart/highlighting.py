# ----------   Μείωση τονικότητας στα highlights   ----------------

def lighten_color(rgb_tuple, factor=0.6):
    
    return tuple(min(1, c + (1 - c) * factor) for c in rgb_tuple)


# ----------   Ομαδοποίηση κοινών ανα σελίδα   ----------------

def group_matches_by_page(matches):
    from collections import defaultdict

    page_map = defaultdict(list)
    for match in matches:
        page_map[match['page']].append({
            'coords': (match['x0'], match['y0'], match['x1'], match['y1']),
            'color': tuple(int(match['color'][i:i+2], 16)/255 for i in (1, 3, 5)),
            'rank': match.get('rank', ''),
            'source_file': match.get('source_file', None)
        })
    return page_map


# ----------   Δημιουργία Highlight   ----------------

def draw_highlight(page, rect, color):
    light_color = lighten_color(color, factor=0.6)
    page.draw_rect(rect, fill=light_color, overlay=False, width=0)


# ----------   Δημιουργία Rank   ----------------

def draw_rank(page, rect, rank, color):
    page.draw_rect(rect, fill=color, overlay=True, width=0)
    page.insert_textbox(
        rect,
        str(rank),
        fontsize=7,
        fontname="helv",
        color=(1, 1, 1),
        align=1
    )


# ----------   Workflow και positioning highlight και rank   ----------------

def create_highlights_pdf(original_path, matches, output_path):
    """
    Create PDF with solid-color highlights and numeric ranks above the last highlight per source per page.
    """
    import fitz
    import time

    start = time.time()
    out_doc = fitz.open()
    page_map = group_matches_by_page(matches)

    src_doc = fitz.open(original_path)
    for page_idx in range(src_doc.page_count):
        out_doc.insert_pdf(src_doc, from_page=page_idx, to_page=page_idx)
        page = out_doc[-1]
        pnum = page_idx + 1

        page_height = src_doc[page_idx].rect.height
        matches_on_page = page_map.get(pnum, [])
        matches_on_page.sort(key=lambda m: (m['coords'][1], m['coords'][0]))  # top-to-bottom

        ranked_sources_on_page = set()

        for item in reversed(matches_on_page):
            x0, y0, x1, y1 = item['coords']
            highlight_rect = fitz.Rect(
                x0,
                page_height - y1,
                x1,
                page_height - y0
            )

            draw_highlight(page, highlight_rect, item['color'])

            if item['source_file'] not in ranked_sources_on_page:
                rank_rect = fitz.Rect(
                    highlight_rect.x0,
                    max(0, highlight_rect.y0 - 12),
                    highlight_rect.x0 + 12,
                    highlight_rect.y0
                )
                draw_rank(page, rank_rect, item['rank'], item['color'])
                ranked_sources_on_page.add(item['source_file'])

    out_doc.save(output_path, garbage=4, deflate=True)
    elapsed = time.time() - start

    src_doc.close()
    out_doc.close()


# ----------   Ένωση highlight για πιο όμορφο UI   ----------------

def merge_highlights(highlight_data):

    merged = []
    sorted_highlights = sorted(highlight_data, key=lambda x: (x['page'], x['y0'], x['x0']))
    current = None
    for h in sorted_highlights:
        if not current:
            current = h.copy()
            continue
        same_source = current['source_file'] == h['source_file']
        same_page = current['page'] == h['page']

        vertical_threshold = (current['y1'] - current['y0']) * 0.7
        horizontal_threshold = (current['x1'] - current['x0']) * 1.5

        vertical_overlap = abs(current['y0'] - h['y0']) < vertical_threshold
        effective_gap = h['x0'] - current['x1']

        if same_source and same_page and vertical_overlap and effective_gap <= horizontal_threshold:
            current['x1'] = max(current['x1'], h['x1'])
            current['y0'] = min(current['y0'], h['y0'])
            current['y1'] = max(current['y1'], h['y1'])
        else:
            merged.append(current)
            current = h.copy()

    if current:
        merged.append(current)

    return merged
