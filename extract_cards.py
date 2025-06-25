import fitz  # PyMuPDF
import os
import hashlib

PDF_FILE = 'flattened.pdf'  # Use the original layered PDF
OUTPUT_DIR = 'cards_output'
MM_PER_PT = 25.4 / 72
MARGIN_MM = 2
os.makedirs(OUTPUT_DIR, exist_ok=True)

def mm2pt(mm):
    return mm / MM_PER_PT

def pt2mm(pt):
    return pt * MM_PER_PT

def pdf_bytes_hash(pdf_bytes):
    return hashlib.md5(pdf_bytes).hexdigest()

# Landscape A4 size in mm
A4_WIDTH_MM = 297
A4_HEIGHT_MM = 210
# Card grid: 4 columns x 2 rows (portrait cards)
CARDS_X = 4
CARDS_Y = 2
PADDING_X_MM = 10
PADDING_Y_MM = 10
GAP_X_MM = 5
GAP_Y_MM = 5
CARD_WIDTH_MM = (A4_WIDTH_MM - 2*PADDING_X_MM - (CARDS_X-1)*GAP_X_MM) / CARDS_X
CARD_HEIGHT_MM = (A4_HEIGHT_MM - 2*PADDING_Y_MM - (CARDS_Y-1)*GAP_Y_MM) / CARDS_Y

print(f"Landscape A4: {A4_WIDTH_MM} x {A4_HEIGHT_MM} mm")
print(f"Card size: {CARD_WIDTH_MM:.2f} x {CARD_HEIGHT_MM:.2f} mm (plus 2mm margin each side)")

unique_back_hashes = set()
unique_back_count = 0

with fitz.open(PDF_FILE) as doc:
    # Identify RU layer xref
    ocgs = doc.get_ocgs()
    ru_xref = None
    eng_xref = None
    if ocgs:
        for xref, info in ocgs.items():
            name = info.get('name', '').strip().upper()
            if name in ('RU', 'RUS', 'RUSSIAN'):
                ru_xref = xref
                break
            elif name in ('EN', 'ENG', 'ENGLISH'):
                eng_xref = xref
                break
    if ru_xref is None:
        print("Warning: RU layer not found. All layers will be ON.")

    print(ru_xref)
    # Prepare ON/OFF lists for OCGs
    on_list = []
    off_list = []
    if ocgs:
        for xref, info in ocgs.items():
            if xref == ru_xref:
                off_list.append(xref)
            elif xref == eng_xref:
                on_list.append(xref)
            elif info.get('on', False):
                on_list.append(xref)
            else:
                off_list.append(xref)

    doc.set_layer(-1, on=on_list, off=off_list)

    for page_idx, page in enumerate(doc):
        is_front = (page_idx % 2 == 0)  # 0,2=front; 1,3=back
        if is_front:
            for row in range(CARDS_Y):
                for col in range(CARDS_X):
                    x0_mm = PADDING_X_MM + col * (CARD_WIDTH_MM + GAP_X_MM)
                    y0_mm = PADDING_Y_MM + row * (CARD_HEIGHT_MM + GAP_Y_MM)
                    x1_mm = x0_mm + CARD_WIDTH_MM
                    y1_mm = y0_mm + CARD_HEIGHT_MM
                    # Add margin and clamp to page bounds
                    x0_mm_margin = max(0, x0_mm - MARGIN_MM)
                    y0_mm_margin = max(0, y0_mm - MARGIN_MM)
                    x1_mm_margin = min(A4_WIDTH_MM, x1_mm + MARGIN_MM)
                    y1_mm_margin = min(A4_HEIGHT_MM, y1_mm + MARGIN_MM)
                    if x1_mm_margin <= x0_mm_margin or y1_mm_margin <= y0_mm_margin:
                        continue
                    rect = fitz.Rect(
                        mm2pt(x0_mm_margin), mm2pt(y0_mm_margin),
                        mm2pt(x1_mm_margin), mm2pt(y1_mm_margin)
                    )
                    idx = row * CARDS_X + col + 1
                    out_path = os.path.join(OUTPUT_DIR, f"front_card_{page_idx//2+1}_{idx}.pdf")
               
                    new_doc = fitz.open()
                    new_page = new_doc.new_page(width=rect.width, height=rect.height)
                    new_page.show_pdf_page(
                        fitz.Rect(0, 0, rect.width, rect.height),
                        doc, page_idx, clip=rect
                    )
                    new_doc.save(out_path, garbage=4, deflate=True)
                    new_doc.close()
                    print(f"Saved {out_path}")
        else:
            # For back, extract one rectangle covering the entire card grid (with margin)
            x0_mm = PADDING_X_MM - MARGIN_MM
            y0_mm = PADDING_Y_MM - MARGIN_MM
            x1_mm = PADDING_X_MM + CARDS_X * CARD_WIDTH_MM + (CARDS_X-1) * GAP_X_MM + MARGIN_MM
            y1_mm = PADDING_Y_MM + CARDS_Y * CARD_HEIGHT_MM + (CARDS_Y-1) * GAP_Y_MM + MARGIN_MM
            x0_mm = max(0, x0_mm)
            y0_mm = max(0, y0_mm)
            x1_mm = min(A4_WIDTH_MM, x1_mm)
            y1_mm = min(A4_HEIGHT_MM, y1_mm)
            rect = fitz.Rect(
                mm2pt(x0_mm), mm2pt(y0_mm),
                mm2pt(x1_mm), mm2pt(y1_mm)
            )
            out_path = os.path.join(OUTPUT_DIR, f"back_grid_{page_idx//2+1}.pdf")
            # Set OCG visibility for this crop
            if ocgs and ru_xref is not None:
                doc.set_layer(-1, on=on_list, off=off_list)
            new_doc = fitz.open()
            new_page = new_doc.new_page(width=rect.width, height=rect.height)
            new_page.show_pdf_page(
                fitz.Rect(0, 0, rect.width, rect.height),
                doc, page_idx, clip=rect
            )
            new_doc.save(out_path, garbage=4, deflate=True)
            new_doc.close()
            print(f"Saved {out_path}") 