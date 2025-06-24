import fitz  # PyMuPDF

input_pdf = 'input.pdf'
output_pdf = 'flattened.pdf'

# OCG xrefs
RUS_XREF = 564
ENG_XREF = 565

# Open the document
doc = fitz.open(input_pdf)

# Get all OCGs
target_ocgs = doc.get_ocgs()

# Prepare ON/OFF lists
on_list = []
off_list = []
for xref, info in target_ocgs.items():
    if xref == RUS_XREF:
        off_list.append(xref)
    elif xref == ENG_XREF:
        on_list.append(xref)
    elif info.get('on', False):
        on_list.append(xref)
    else:
        off_list.append(xref)

# Set OCG visibility
# -1 means default config
doc.set_layer(-1, on=on_list, off=off_list)

# Save the flattened PDF (removes OCGs)
doc.save(output_pdf, garbage=4, deflate=True)
doc.close()

print(f'Flattened PDF saved as {output_pdf}') 