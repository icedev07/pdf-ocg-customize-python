import zipfile
import os

OUTPUT_DIR = 'cards_output'
ZIP_NAME = 'cards_output.zip'

with zipfile.ZipFile(ZIP_NAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for fname in os.listdir(OUTPUT_DIR):
        if fname.lower().endswith('.pdf'):
            zipf.write(os.path.join(OUTPUT_DIR, fname), arcname=fname)
            print(f'Added {fname} to {ZIP_NAME}')
print(f'Created {ZIP_NAME}') 