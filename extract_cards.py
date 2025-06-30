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

# CARD_WIDTH_MM = 64.04
# CARD_HEIGHT_MM = 88.4
PAGE_LEFT_MARGIN_MM = 12.07
PAGE_TOP_MARGIN_MM = 12.07
# 2.2 * 1.9

# PAGE_LEFT_MARGIN_MM = 14.22
# PAGE_TOP_MARGIN_MM = 14.24

CARDS_X = 4
CARDS_Y = 2
GAP_X_MM = 5  # Gap between cards (estimated)
GAP_Y_MM = 5  # Gap between cards (estimated)

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

# Verify the layout fits within page bounds
total_width_needed = PAGE_LEFT_MARGIN_MM + total_content_width_mm + PAGE_RIGHT_MARGIN_MM
total_height_needed = PAGE_TOP_MARGIN_MM + total_content_height_mm + PAGE_BOTTOM_MARGIN_MM

print(f"Processing PDF: {PDF_FILE}")
print(f"Page size: {page_width_mm:.1f} x {page_height_mm:.1f} mm")
print(f"Card size: {CARD_WIDTH_MM} x {CARD_HEIGHT_MM} mm")
print(f"Page margins: Left={PAGE_LEFT_MARGIN_MM}mm, Top={PAGE_TOP_MARGIN_MM}mm, Right={PAGE_RIGHT_MARGIN_MM}mm, Bottom={PAGE_BOTTOM_MARGIN_MM}mm")
print(f"Total content area: {total_content_width_mm:.1f} x {total_content_height_mm:.1f} mm")
print(f"Total layout size: {total_width_needed:.1f} x {total_height_needed:.1f} mm")

if total_width_needed > page_width_mm or total_height_needed > page_height_mm:
    print("WARNING: Layout exceeds page bounds!")
    print(f"Page width: {page_width_mm:.1f}mm, needed: {total_width_needed:.1f}mm")
    print(f"Page height: {page_height_mm:.1f}mm, needed: {total_height_needed:.1f}mm")

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
            y0_mm = PAGE_TOP_MARGIN_MM + row * (CARD_HEIGHT_MM) + 0.4
            x1_mm = x0_mm + CARD_WIDTH_MM
            y1_mm = y0_mm + CARD_HEIGHT_MM + 0.2
        card_boxes_mm.append((x0_mm, y0_mm, x1_mm, y1_mm))
        print(f"Card {row*CARDS_X + col + 1}: ({x0_mm:.1f}, {y0_mm:.1f}) to ({x1_mm:.1f}, {y1_mm:.1f}) mm")

# Now extract cards from flattened.pdf using calculated positions
with fitz.open(PDF_FILE) as doc:
    for page_idx, page in enumerate(doc):
        is_front = (page_idx % 2 == 0)
        if is_front:
            for idx, (x0_mm, y0_mm, x1_mm, y1_mm) in enumerate(card_boxes_mm, 1):
                # Add margin and clamp to page bounds
                # x0_mm_margin = max(0, x0_mm - MARGIN_MM)
                # y0_mm_margin = max(0, y0_mm - MARGIN_MM)
                # x1_mm_margin = x1_mm + MARGIN_MM
                # y1_mm_margin = y1_mm + MARGIN_MM
                # rect = fitz.Rect(
                #     mm2pt(x0_mm_margin), mm2pt(y0_mm_margin),
                #     mm2pt(x1_mm_margin), mm2pt(y1_mm_margin)
                # )
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
            # For back, extract one rectangle covering the entire card grid (with margin)
            x0_mm = min(x[0] for x in card_boxes_mm) - MARGIN_MM
            y0_mm = min(x[1] for x in card_boxes_mm) - MARGIN_MM
            x1_mm = max(x[2] for x in card_boxes_mm) + MARGIN_MM
            y1_mm = max(x[3] for x in card_boxes_mm) + MARGIN_MM
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
            print(f"  Saved {out_path}")
