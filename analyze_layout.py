import fitz  # PyMuPDF

PDF_FILE = 'flattened.pdf'
MM_PER_PT = 25.4 / 72  # 1 pt = 1/72 inch

# Open PDF and get first page
with fitz.open(PDF_FILE) as doc:
    page = doc[0]
    mediabox = page.rect
    width_mm = mediabox.width * MM_PER_PT
    height_mm = mediabox.height * MM_PER_PT
    print(f"Page size: {mediabox.width:.2f} x {mediabox.height:.2f} pt ({width_mm:.2f} x {height_mm:.2f} mm)")

    # Print all text blocks
    print("\nText blocks:")
    blocks = page.get_text("blocks")
    for i, block in enumerate(blocks):
        x0, y0, x1, y1, block_type, *rest = block
        print(f"Block {i}: type={block_type}, bbox=({x0:.2f}, {y0:.2f}, {x1:.2f}, {y1:.2f})")
        if block_type == 0:
            print(f"  Text: {rest[0][:60]!r}")

    # Print all path objects
    print("\nPath objects:")
    drawings = page.get_drawings()
    for i, d in enumerate(drawings):
        if d['type'] == 'path':
            print(f"Path {i}: bbox={d['rect']}, close_path={d.get('closePath', False)}, fill={d.get('fill', None)}, stroke={d.get('color', None)}")
            for op in d.get('items', []):
                print(f"  {op}")

    # Get all drawing objects (lines, rectangles, etc.)
    lines = [d for d in drawings if d['type'] == 'line']
    rects = [d for d in drawings if d['type'] == 'rect']

    # Find cut marks: lines near the page edges, short length
    cut_marks = []
    for line in lines:
        x0, y0, x1, y1 = line['rect']
        length = ((x1-x0)**2 + (y1-y0)**2) ** 0.5
        # Heuristic: short lines near the edge
        if length < 30 and (min(x0, x1) < 30 or max(x0, x1) > mediabox.width-30 or min(y0, y1) < 30 or max(y0, y1) > mediabox.height-30):
            cut_marks.append(((x0, y0), (x1, y1)))
    print(f"Detected {len(cut_marks)} cut marks (lines near edges, <30pt)")

    # Get bounding boxes of all rectangles (likely card borders)
    card_rects = [fitz.Rect(r['rect']) for r in rects if r['width'] > 0 and r['height'] > 0]
    print(f"Detected {len(card_rects)} rectangles (possible card borders)")

    # Try to cluster card rects by size and position
    if card_rects:
        # Find the most common card size
        from collections import Counter
        sizes = [(round(r.width,1), round(r.height,1)) for r in card_rects]
        most_common_size, count = Counter(sizes).most_common(1)[0]
        print(f"Most common card size: {most_common_size[0]:.2f} x {most_common_size[1]:.2f} pt ({most_common_size[0]*MM_PER_PT:.2f} x {most_common_size[1]*MM_PER_PT:.2f} mm), found {count} times")
        # Find bounding box of all cards
        min_x = min(r.x0 for r in card_rects)
        min_y = min(r.y0 for r in card_rects)
        max_x = max(r.x1 for r in card_rects)
        max_y = max(r.y1 for r in card_rects)
        print(f"Cards area: ({min_x:.2f}, {min_y:.2f}) - ({max_x:.2f}, {max_y:.2f}) pt")
        print(f"Cards area size: {(max_x-min_x)*MM_PER_PT:.2f} x {(max_y-min_y)*MM_PER_PT:.2f} mm")
    else:
        print("No card rectangles detected.")

    # Try to find background image size
    images = page.get_images(full=True)
    if images:
        for img in images:
            xref = img[0]
            bbox = None
            # Try to find the image bbox from drawings
            for d in drawings:
                if d['type'] == 'image' and d.get('xref') == xref:
                    bbox = d['rect']
                    break
            if bbox:
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                print(f"Background image xref {xref}: {w*MM_PER_PT:.2f} x {h*MM_PER_PT:.2f} mm at ({bbox[0]:.2f}, {bbox[1]:.2f})")
            else:
                print(f"Image xref {xref}: bbox not found in drawings.")
    else:
        print("No images found on page.") 