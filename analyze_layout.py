import fitz  # PyMuPDF

PDF_FILE = 'input.pdf'
MM_PER_PT = 25.4 / 72  # 1 pt = 1/72 inch

with fitz.open(PDF_FILE) as doc:
    page = doc[0]
    mediabox = page.rect
    width_mm = mediabox.width * MM_PER_PT
    height_mm = mediabox.height * MM_PER_PT
    print(f"Page size: {mediabox.width:.2f} x {mediabox.height:.2f} pt ({width_mm:.2f} x {height_mm:.2f} mm)")

    # --- OCG/Layers ---
    ocgs = doc.get_ocgs()
    print(ocgs)
    if ocgs:
        print("\nAvailable OCGs (layers):")
        for i, ocg in enumerate(ocgs):
            if isinstance(ocg, dict):
                print(f"{i}: {ocg.get('name', '(no name)')} (id={ocg.get('ocg', ocg)})")
            else:
                print(f"{i}: (id={ocg})")
    else:
        print("\nNo OCGs (layers) found in this PDF.")

    # --- Enable only the cut mark layer if you know its name ---
    # Replace this with the actual layer name for cut marks, or leave as None to use all layers
    cut_mark_layer_name = None  # e.g. 'Crop Marks'
    cut_mark_ocg_id = None
    if cut_mark_layer_name and ocgs:
        for ocg in ocgs:
            if ocg['name'] == cut_mark_layer_name:
                cut_mark_ocg_id = ocg['ocg']
                break
        if cut_mark_ocg_id is not None:
            ocg_config = {ocg['ocg']: (ocg['ocg'] == cut_mark_ocg_id) for ocg in ocgs}
            doc.set_ocg_state(ocg_config)
            print(f"\nEnabled only layer: {cut_mark_layer_name}")
        else:
            print(f"\nLayer '{cut_mark_layer_name}' not found! Using all layers.")

    # --- Path and line detection as before ---
    print("\nText blocks:")
    blocks = page.get_text("blocks")
    for i, block in enumerate(blocks):
        x0, y0, x1, y1, block_type, *rest = block
        print(f"Block {i}: type={block_type}, bbox=({x0:.2f}, {y0:.2f}, {x1:.2f}, {y1:.2f})")
        if block_type == 0:
            print(f"  Text: {rest[0][:60]!r}")

    print("\nPath objects:")
    drawings = page.get_drawings()
    for i, d in enumerate(drawings):
        if d['type'] == 'path':
            print(f"Path {i}: bbox={d['rect']}, close_path={d.get('closePath', False)}, fill={d.get('fill', None)}, stroke={d.get('color', None)}")
            for op in d.get('items', []):
                print(f"  {op}")

    lines = [d for d in drawings if d['type'] == 'line']
    rects = [d for d in drawings if d['type'] == 'rect']

    # Find cut marks: short lines (not just near the edge)
    cut_marks = []
    for line in lines:
        x0, y0, x1, y1 = line['rect']
        length = ((x1-x0)**2 + (y1-y0)**2) ** 0.5
        if length < 30:  # Short lines anywhere
            cut_marks.append(((x0, y0), (x1, y1)))
    print(f"Detected {len(cut_marks)} cut marks (short lines <30pt)")

    for i, ((x0, y0), (x1, y1)) in enumerate(cut_marks):
        print(f"Cut mark {i}: ({x0:.2f}, {y0:.2f}) to ({x1:.2f}, {y1:.2f})")

    # Build OCG dict if needed
    if isinstance(ocgs, dict):
        ocg_dict = ocgs
    else:
        ocg_dict = {ocg['ocg']: ocg for ocg in ocgs if isinstance(ocg, dict)}

    # Find all OCG ids with 'card' in the name
    card_ocg_ids = [ocg_id for ocg_id, info in ocg_dict.items() if 'card' in info['name'].lower()]
    print("OCG IDs with 'card' in the name:", card_ocg_ids)

    # Enable only those layers
    if card_ocg_ids:
        ocg_config = {ocg_id: (ocg_id in card_ocg_ids) for ocg_id in ocg_dict}
        doc.set_ocg_state(ocg_config)
        print("Enabled only 'card' layers.")

    # Now detect rectangles (card borders)
    drawings = page.get_drawings()
    rects = [d for d in drawings if d['type'] == 'rect']
    card_rects = [fitz.Rect(r['rect']) for r in rects if r['width'] > 0 and r['height'] > 0]
    print(f"Detected {len(card_rects)} rectangles (possible card borders)")

    if card_rects:
        from collections import Counter
        sizes = [(round(r.width,1), round(r.height,1)) for r in card_rects]
        most_common_size, count = Counter(sizes).most_common(1)[0]
        print(f"Most common card size: {most_common_size[0]:.2f} x {most_common_size[1]:.2f} pt ({most_common_size[0]*MM_PER_PT:.2f} x {most_common_size[1]*MM_PER_PT:.2f} mm), found {count} times")
        min_x = min(r.x0 for r in card_rects)
        min_y = min(r.y0 for r in card_rects)
        max_x = max(r.x1 for r in card_rects)
        max_y = max(r.y1 for r in card_rects)
        print(f"Cards area: ({min_x:.2f}, {min_y:.2f}) - ({max_x:.2f}, {max_y:.2f}) pt")
        print(f"Cards area size: {(max_x-min_x)*MM_PER_PT:.2f} x {(max_y-min_y)*MM_PER_PT:.2f} mm")
        print(f"Page margin left: {min_x*MM_PER_PT:.2f} mm, top: {min_y*MM_PER_PT:.2f} mm")
    else:
        print("No card rectangles detected.")

    # Try to find background image size
    images = page.get_images(full=True)
    if images:
        for img in images:
            xref = img[0]
            bbox = None
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

    # Optionally, reset OCG state after
    if cut_mark_layer_name and ocgs:
        doc.set_ocg_state()  # Reset to default

    # Suppose ocgs is your OCG dictionary as above
    card_ocg_ids = [ocg_id for ocg_id, info in ocgs.items() if 'card' in info['name'].lower()]
    print("OCG IDs with 'card' in the name:", card_ocg_ids) 