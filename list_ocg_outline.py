import fitz  # PyMuPDF
from PyPDF2 import PdfReader

pdf_path = 'input.pdf'

# List OCGs (layers) using PyMuPDF
doc = fitz.open(pdf_path)
ocgs = doc.get_ocgs()
print('OCGs (Layers) in PDF:')
if ocgs:
    for xref, info in ocgs.items():
        name = info.get('name', f'OCG_{xref}')
        on = info.get('on', None)
        print(f"- Name: {name}, XREF: {xref}, Default Visible: {on}")
else:
    print('No OCGs found.')

doc.close()

# List outlines (bookmarks) using PyPDF2
reader = PdfReader(pdf_path)
def print_outlines(outlines, level=0):
    for item in outlines:
        if isinstance(item, list):
            print_outlines(item, level+1)
        else:
            title = getattr(item, 'title', str(item))
            print('  ' * level + f'- {title}')

print('\nOutlines (Bookmarks) in PDF:')
try:
    outlines = reader.outlines
    print_outlines(outlines)
except Exception as e:
    print('No outlines found or error:', e) 