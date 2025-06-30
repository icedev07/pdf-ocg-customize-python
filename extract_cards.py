import fitz  # PyMuPDF
import os

PDF_FILE = 'flattened.pdf'
OUTPUT_DIR = 'cards_output'
MM_PER_PT = 25.4 / 72
MARGIN_MM = 2
os.makedirs(OUTPUT_DIR, exist_ok=True)

def mm2pt(mm):
    return mm / MM_PER_PT

# Card configuration (from user measurements)
CARD_WIDTH_MM = 68.24
CARD_HEIGHT_MM = 92.70

CUT_MARK_MM = 3

PAGE_LEFT_MARGIN_MM = 12.07
PAGE_TOP_MARGIN_MM = 12.07

CARDS_X = 4
CARDS_Y = 2

GAP_X_MM = 0.4
GAP_Y_MM = 0.2

# Calculate page dimensions from the PDF to determine right and bottom margins
with fitz.open(PDF_FILE) as doc:
    page = doc[0]
    print(page.rect)
    page_width_mm = page.rect.width * MM_PER_PT
    page_height_mm = page.rect.height * MM_PER_PT

# Calculate total content width and height
total_content_width_mm = CARDS_X * CARD_WIDTH_MM + (CARDS_X - 1) * GAP_X_MM
total_content_height_mm = CARDS_Y * CARD_HEIGHT_MM + (CARDS_Y - 1) * GAP_Y_MM

# Calculate right and bottom margins to center the content
PAGE_RIGHT_MARGIN_MM = PAGE_LEFT_MARGIN_MM  # Same as left margin
PAGE_BOTTOM_MARGIN_MM = PAGE_TOP_MARGIN_MM  # Same as top margin

# Calculate card positions based on known dimensions
card_boxes_mm = []
for row in range(CARDS_Y):
    print(f"Row {row}")
    for col in range(CARDS_X):

        # x0_mm = PAGE_LEFT_MARGIN_MM + col * (CARD_WIDTH_MM + GAP_X_MM)
        # y0_mm = PAGE_TOP_MARGIN_MM + row * (CARD_HEIGHT_MM + GAP_Y_MM)
        if(row == 0):
            x0_mm = PAGE_LEFT_MARGIN_MM + col * (CARD_WIDTH_MM)
            y0_mm = PAGE_TOP_MARGIN_MM + row * (CARD_HEIGHT_MM)
            x1_mm = x0_mm + CARD_WIDTH_MM
            y1_mm = y0_mm + CARD_HEIGHT_MM
        else:
            x0_mm = PAGE_LEFT_MARGIN_MM + col * (CARD_WIDTH_MM)
            y0_mm = PAGE_TOP_MARGIN_MM + row * (CARD_HEIGHT_MM) + GAP_X_MM
            x1_mm = x0_mm + CARD_WIDTH_MM
            y1_mm = y0_mm + CARD_HEIGHT_MM + GAP_Y_MM

        card_boxes_mm.append((x0_mm + CUT_MARK_MM, y0_mm+CUT_MARK_MM, x1_mm-CUT_MARK_MM, y1_mm-CUT_MARK_MM))


# Now extract cards from flattened.pdf using calculated positions
with fitz.open(PDF_FILE) as doc:
    for page_idx, page in enumerate(doc):
        is_front = (page_idx % 2 == 0)
        if is_front:
            for idx, (x0_mm, y0_mm, x1_mm, y1_mm) in enumerate(card_boxes_mm, 1):
                rect = fitz.Rect(
                    mm2pt(x0_mm), mm2pt(y0_mm),
                    mm2pt(x1_mm), mm2pt(y1_mm)
                )
                out_path = os.path.join(OUTPUT_DIR, f"front_card_{page_idx//2+1}_{idx}.pdf")
                new_doc = fitz.open()
                new_page = new_doc.new_page(width=rect.width, height=rect.height)
                new_page.show_pdf_page(
                    fitz.Rect(0, 0, rect.width, rect.height),
                    doc, page_idx, clip=rect
                )
                new_doc.save(out_path, garbage=4, deflate=True)
                new_doc.close()
                print(f"  Saved {out_path}")
        else:
            x0_mm = PAGE_LEFT_MARGIN_MM + col * (CARD_WIDTH_MM)
            y0_mm = PAGE_TOP_MARGIN_MM + row * (CARD_HEIGHT_MM) + GAP_X_MM
            x1_mm = x0_mm + CARD_WIDTH_MM
            y1_mm = y0_mm + CARD_HEIGHT_MM + GAP_Y_MM
            rect = fitz.Rect(
                mm2pt(x0_mm), mm2pt(y0_mm),
                mm2pt(x1_mm), mm2pt(y1_mm)
            )
            out_path = os.path.join(OUTPUT_DIR, f"back_grid_{page_idx//2+1}.pdf")
            new_doc = fitz.open()
            new_page = new_doc.new_page(width=rect.width, height=rect.height)
            new_page.show_pdf_page(
                fitz.Rect(0, 0, rect.width, rect.height),
                doc, page_idx, clip=rect
            )
            new_doc.save(out_path, garbage=4, deflate=True)
            new_doc.close()
