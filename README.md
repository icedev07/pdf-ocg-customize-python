# PDF Card Extraction Tool

This tool processes PDF files with Optional Content Groups (OCGs/layers) to extract individual cards with proper margins. It's designed for card games, trading cards, or any multi-card layouts on A4 pages.

## Features

- **OCG Management**: List, enable/disable PDF layers (Optional Content Groups)
- **PDF Flattening**: Convert layered PDFs to flat versions with selected layers
- **Smart Card Detection**: Automatically detect card boundaries using text block clustering
- **Precise Cropping**: Extract individual cards with configurable margins
- **PDF Preservation**: Maintain all PDF features (text, fonts, images, etc.) - not just raster images
- **Batch Processing**: Process multiple cards and compress results

## Requirements

```bash
pip install pymupdf pikepdf PyPDF2
```

## Files Overview

### Core Scripts
- `list_ocg_outline.py` - List OCGs and outlines in PDF
- `flatten_ocg.py` - Flatten PDF with specific OCG settings
- `analyze_layout.py` - Analyze PDF layout and detect elements
- `extract_cards.py` - Extract individual cards from PDF
- `zip_cards.py` - Compress extracted cards into ZIP file

### Input/Output
- `input.pdf` - Original PDF file (A4 with multiple cards)
- `flattened.pdf` - Intermediate flattened PDF
- `cards_output/` - Directory containing individual card PDFs
- `cards_output.zip` - Compressed archive of all cards

## Usage

### 1. List OCGs and Outlines

First, examine the PDF structure:

```bash
python list_ocg_outline.py
```

This will show:
- All OCGs (layers) with their default visibility states
- Outline/bookmark structure (if any)

Example output:
```
OCGs (Layers) in PDF:
- Name: RUS, XREF: 564, Default Visible: True
- Name: ENG, XREF: 565, Default Visible: False
- Name: Cards, XREF: 562, Default Visible: True
...
```

### 2. Flatten PDF with OCG Settings

Modify `flatten_ocg.py` to set your desired OCG states, then run:

```bash
python flatten_ocg.py
```

Default behavior:
- Disables "RUS" layer
- Enables "ENG" layer
- Keeps other layers at their default states
- Saves as `flattened.pdf`

### 3. Analyze Layout (Optional)

For debugging or understanding the PDF structure:

```bash
python analyze_layout.py
```

Shows:
- Page dimensions
- Text block positions and content
- Path objects
- Image information

### 4. Extract Individual Cards

```bash
python extract_cards.py
```

This script:
- Clusters text blocks by proximity to identify card boundaries
- Adds 2mm margin around each card
- Saves each card as `card_1.pdf`, `card_2.pdf`, etc.
- Preserves all PDF features (text, fonts, images, etc.)

### 5. Compress Results

```bash
python zip_cards.py
```

Creates `cards_output.zip` containing all extracted cards.

## Configuration

### Card Extraction Settings

In `extract_cards.py`:
```python
MARGIN_MM = 2  # Margin around each card in millimeters
threshold = 40  # Clustering threshold in points (~14mm)
```

### OCG Configuration

In `flatten_ocg.py`:
```python
RUS_XREF = 564  # XREF of Russian language layer
ENG_XREF = 565  # XREF of English language layer
```

## Output Format

### Individual Cards
- **Format**: PDF (not raster images)
- **Features Preserved**: Text, fonts, images, vector graphics, annotations
- **Naming**: `card_1.pdf`, `card_2.pdf`, etc.
- **Margin**: 2mm around detected card boundaries

### Archive
- **Format**: ZIP file
- **Contents**: All extracted card PDFs
- **Name**: `cards_output.zip`

## Technical Details

### OCG (Optional Content Groups)
- PDF layers that can be shown/hidden
- Used for multi-language documents, different card versions, etc.
- This tool can list, modify, and flatten OCGs

### Card Detection Algorithm
1. Extract all text blocks from PDF
2. Cluster blocks by spatial proximity (40pt threshold)
3. Calculate bounding box for each cluster
4. Add margin and crop

### PDF Preservation
- Uses PyMuPDF's `show_pdf_page()` with clipping
- Maintains all original PDF features
- Output is a proper PDF, not just an image

## Troubleshooting

### No Cards Detected
- Check if text blocks are being found in `analyze_layout.py`
- Adjust clustering threshold in `extract_cards.py`
- Verify PDF structure with `list_ocg_outline.py`

### Wrong Card Boundaries
- Review text block clustering in `analyze_layout.py`
- Adjust `threshold` parameter in `extract_cards.py`
- Consider manual boundary definition if needed

### OCG Issues
- Verify OCG XREF numbers in `list_ocg_outline.py`
- Check OCG names and states
- Ensure PDF supports OCGs

## Example Workflow

```bash
# 1. Examine PDF structure
python list_ocg_outline.py

# 2. Flatten with desired layers
python flatten_ocg.py

# 3. Extract cards
python extract_cards.py

# 4. Compress results
python zip_cards.py

# 5. Extract from ZIP (if needed)
python -c "import zipfile; zipfile.ZipFile('cards_output.zip').extractall('extracted_cards')"
```

## File Structure

```
pdf-ocg-customize-python/
├── input.pdf                 # Original PDF
├── flattened.pdf            # Intermediate flattened PDF
├── cards_output/            # Extracted cards
│   ├── card_1.pdf
│   ├── card_2.pdf
│   └── ...
├── cards_output.zip         # Compressed archive
├── list_ocg_outline.py      # OCG/outline listing
├── flatten_ocg.py          # PDF flattening
├── analyze_layout.py       # Layout analysis
├── extract_cards.py        # Card extraction
├── zip_cards.py           # Compression
└── README.md              # This file
```

## Dependencies

- **PyMuPDF (fitz)**: PDF manipulation, OCG handling, text extraction
- **pikepdf**: Advanced PDF features, OCG management
- **PyPDF2**: Outline/bookmark extraction
- **zipfile**: Archive compression (built-in)

## License

This tool is provided as-is for educational and practical use. Modify as needed for your specific requirements. 