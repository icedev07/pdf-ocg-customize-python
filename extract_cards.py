import fitz  # PyMuPDF
import os
import math

PDF_FILE = 'flattened.pdf'
OUTPUT_DIR = 'cards_output'
MM_PER_PT = 25.4 / 72
MARGIN_MM = 2
MARGIN_PT = MARGIN_MM / MM_PER_PT

os.makedirs(OUTPUT_DIR, exist_ok=True)

def rect_distance(r1, r2):
    # Distance between two rectangles (0 if they overlap)
    if r1.intersects(r2):
        return 0
    dx = max(r1.x0 - r2.x1, r2.x0 - r1.x1, 0)
    dy = max(r1.y0 - r2.y1, r2.y0 - r1.y1, 0)
    return math.hypot(dx, dy)

def cluster_blocks(blocks, threshold=30):
    # Simple agglomerative clustering by bbox distance (in pt)
    clusters = []
    for rect in blocks:
        added = False
        for cluster in clusters:
            if any(rect_distance(rect, r) < threshold for r in cluster):
                cluster.append(rect)
                added = True
                break
        if not added:
            clusters.append([rect])
    return clusters

with fitz.open(PDF_FILE) as doc:
    page = doc[0]
    blocks = page.get_text("blocks")
    print("All block types and content:")
    for i, b in enumerate(blocks):
        print(f"Block {i}: type={b[4]!r}, bbox=({b[0]:.2f}, {b[1]:.2f}, {b[2]:.2f}, {b[3]:.2f})")
        if len(b) > 5:
            print(f"  Content: {str(b[5])[:60]!r}")
    # Use all blocks for clustering
    text_rects = [fitz.Rect(b[0], b[1], b[2], b[3]) for b in blocks]
    clusters = cluster_blocks(text_rects, threshold=40)  # 40pt ~ 14mm
    print(f"Detected {len(clusters)} card clusters.")

    for idx, cluster in enumerate(clusters, 1):
        # Bounding box for the card
        min_x = min(r.x0 for r in cluster)
        min_y = min(r.y0 for r in cluster)
        max_x = max(r.x1 for r in cluster)
        max_y = max(r.y1 for r in cluster)
        card_rect = fitz.Rect(min_x, min_y, max_x, max_y)
        # Add margin
        card_rect.x0 = max(0, card_rect.x0 - MARGIN_PT)
        card_rect.y0 = max(0, card_rect.y0 - MARGIN_PT)
        card_rect.x1 = min(page.rect.width, card_rect.x1 + MARGIN_PT)
        card_rect.y1 = min(page.rect.height, card_rect.y1 + MARGIN_PT)

        # Create new PDF with cropped page
        new_doc = fitz.open()
        new_page = new_doc.new_page(width=card_rect.width, height=card_rect.height)
        # Show the cropped area from the original page
        new_page.show_pdf_page(
            fitz.Rect(0, 0, card_rect.width, card_rect.height),
            doc,
            0,
            clip=card_rect
        )
        out_path = os.path.join(OUTPUT_DIR, f"card_{idx}.pdf")
        new_doc.save(out_path, garbage=4, deflate=True)
        new_doc.close()
        print(f"Saved {out_path}") 