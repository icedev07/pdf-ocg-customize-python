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

# Content margins (from analyze_layout.py analysis)
CONTENT_LEFT_MARGIN_MM = 14.6
CONTENT_TOP_MARGIN_MM = 14.5

# Card grid: 4 columns x 2 rows (portrait cards)
CARDS_X = 4
CARDS_Y = 2
GAP_X_MM = 5
GAP_Y_MM = 5

print(f"Processing PDF: {PDF_FILE}")
print(f"Content margins: Left={CONTENT_LEFT_MARGIN_MM}mm, Top={CONTENT_TOP_MARGIN_MM}mm")

unique_back_hashes = set()
unique_back_count = 0

with fitz.open(PDF_FILE) as doc:
    
    for page_idx, page in enumerate(doc):
        # Get actual page dimensions
        mediabox = page.rect
        page_width_mm = pt2mm(mediabox.width)
        page_height_mm = pt2mm(mediabox.height)
        
        # Calculate content area based on fixed margins
        content_x0_mm = CONTENT_LEFT_MARGIN_MM
        content_y0_mm = CONTENT_TOP_MARGIN_MM
        content_x1_mm = page_width_mm - CONTENT_LEFT_MARGIN_MM  # Symmetric right margin
        content_y1_mm = page_height_mm - CONTENT_TOP_MARGIN_MM  # Symmetric bottom margin
        
        # Calculate available content area for cards
        content_width_mm = content_x1_mm - content_x0_mm
        content_height_mm = content_y1_mm - content_y0_mm
        
        # Calculate card dimensions based on available content area
        card_width_mm = (content_width_mm - (CARDS_X-1)*GAP_X_MM) / CARDS_X
        card_height_mm = (content_height_mm - (CARDS_Y-1)*GAP_Y_MM) / CARDS_Y
        
        print(f"Page {page_idx + 1}: {page_width_mm:.1f} x {page_height_mm:.1f} mm")
        print(f"  Content area: {content_width_mm:.1f} x {content_height_mm:.1f} mm")
        print(f"  Card size: {card_width_mm:.2f} x {card_height_mm:.2f} mm (plus 2mm margin each side)")
        
        is_front = (page_idx % 2 == 0)  # 0,2=front; 1,3=back
        if is_front:
            for row in range(CARDS_Y):
                for col in range(CARDS_X):
                    # Calculate card position relative to content area
                    x0_mm = content_x0_mm + col * (card_width_mm + GAP_X_MM)
                    y0_mm = content_y0_mm + row * (card_height_mm + GAP_Y_MM)
                    x1_mm = x0_mm + card_width_mm
                    y1_mm = y0_mm + card_height_mm
                    
                    # Add margin and clamp to page bounds
                    x0_mm_margin = max(0, x0_mm - MARGIN_MM)
                    y0_mm_margin = max(0, y0_mm - MARGIN_MM)
                    x1_mm_margin = min(page_width_mm, x1_mm + MARGIN_MM)
                    y1_mm_margin = min(page_height_mm, y1_mm + MARGIN_MM)
                    
                    if x1_mm_margin <= x0_mm_margin or y1_mm_margin <= y0_mm_margin:
                        continue
                        
                    rect = fitz.Rect(
                        mm2pt(x0_mm_margin), mm2pt(y0_mm_margin),
                        mm2pt(x1_mm_margin), mm2pt(y1_mm_margin)
                    )
                    idx = row * CARDS_X + col + 1
                    out_path = os.path.join(OUTPUT_DIR, f"front_card_{page_idx//2+1}_{idx}.pdf")
               
                    # Create new document and copy content with layer settings already applied
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
            x0_mm = content_x0_mm - MARGIN_MM
            y0_mm = content_y0_mm - MARGIN_MM
            # x1_mm = content_x0_mm + CARDS_X * card_width_mm + (CARDS_X-1) * GAP_X_MM + MARGIN_MM
            # y1_mm = content_y0_mm + CARDS_Y * card_height_mm + (CARDS_Y-1) * GAP_Y_MM + MARGIN_MM

            x1_mm = content_x0_mm + card_width_mm 
            y1_mm = content_y0_mm + card_height_mm
            
            # Clamp to page bounds
            x0_mm = max(0, x0_mm)
            y0_mm = max(0, y0_mm)
            x1_mm = min(page_width_mm, x1_mm)
            y1_mm = min(page_height_mm, y1_mm)
            
            rect = fitz.Rect(
                mm2pt(x0_mm), mm2pt(y0_mm),
                mm2pt(x1_mm), mm2pt(y1_mm)
            )
            out_path = os.path.join(OUTPUT_DIR, f"back_grid_{page_idx//2+1}.pdf")
            
            # Create new document and copy content with layer settings already applied
            new_doc = fitz.open()
            new_page = new_doc.new_page(width=rect.width, height=rect.height)
            
            new_page.show_pdf_page(
                fitz.Rect(0, 0, rect.width, rect.height),
                doc, page_idx, clip=rect
            )
            new_doc.save(out_path, garbage=4, deflate=True)
            new_doc.close()
            print(f"  Saved {out_path}") 