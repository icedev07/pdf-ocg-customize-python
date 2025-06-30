# PDF Card Extraction Tool

This tool processes PDF files with Optional Content Groups (OCGs/layers) to extract individual cards with proper margins. 

## What is PDF OCG (Optional Content Groups)?

**Optional Content Groups (OCGs)** are PDF layers that can be shown or hidden independently. They are commonly used for:

- **Multi-language documents**: Different language versions on the same page
- **Card game variations**: Different card designs or versions
- **Interactive content**: Show/hide elements based on user preferences
- **Print variations**: Different content for different print runs

### OCG Structure
- Each OCG has a **name** (e.g., "RUS", "ENG", "Cards")
- Each OCG has a **visibility state** (visible/hidden by default)
- OCGs can be **nested** (groups within groups)
- OCGs are stored in the PDF's **OCProperties** dictionary

## Requirements

```bash
pip install pymupdf PyPDF2 apryse-sdk
```

**Note**: `apryse-sdk` requires a license key. For testing, you can use the demo key provided in the code, but for production use, you'll need to obtain a proper license from Apryse.

## Essential Workflow

This tool follows a specific 7-step workflow to extract individual cards from A4 PDFs with multiple cards:

### Step 1: Convert PDF to Images
First, convert the PDF to images to visually understand the page layout and card arrangement.

**Purpose**: Understand the visual structure before technical analysis.

### Step 2: Research PDF OCG and Extraction Methods
Search and understand how to work with PDF Optional Content Groups (OCGs) in Python and how to extract parts of PDFs while preserving all features.

**Key Concepts**:
- **PyMuPDF (fitz)**: For PDF manipulation and OCG handling
- **apryse-sdk**: For advanced OCG flattening
- **PDF structure**: Understanding how OCGs are stored and accessed

### Step 3: Check and List OCGs
Check and list all OCGs in the PDF, showing which are default visible and which are hidden.

**What to look for**:
- OCG names (e.g., "RUS", "ENG", "Cards")
- Default visibility states
- OCG hierarchy (if nested)

### Step 4: Disable RUS and Enable ENG OCG. Flatten PDF
Disable RUS (Russian) layer and enable ENG (English) layer, then flatten the PDF with these settings.

**This is the core functionality** - handled by `flatten_ocg.py`

### Step 5: Measure Card Dimensions
Measure distances between cut marks for individual cards to determine:
- Default card size (with and without borders)
- Background image size
- Page padding (cards don't take full page)

**Critical measurements**:
- Card dimensions: 68.24mm × 92.70mm
- Page margins: 12.07mm (left/top)
- Cut marks: 3mm allowance

### Step 6: Extract Individual Cards
Write Python script to cut out individual cards in appropriate size (poker or bridge) with +2mm margin as individual PDFs. **IMPORTANT**: Output must be proper PDFs with all text fields, fonts, etc., not just cut-out images.

**This is the core functionality** - handled by `extract_cards.py`

### Step 7: Compress Results
Compress all extracted PDFs into a ZIP file and provide code to compress and extract.

## Core Scripts (Essential)

### `flatten_ocg.py` - PDF Flattening with OCG Settings
This script is **essential** for Step 4. It:

1. **Opens the input PDF** with OCG support
2. **Lists all available OCGs** and their current states
3. **Configures OCG visibility**:
   - Disables "RUS" (Russian) layer
   - Enables "ENG" (English) layer
   - Preserves other layers' default states
4. **Flattens the PDF** with these settings
5. **Saves as `flattened.pdf`**

**Usage**:
```bash
python flatten_ocg.py
```

**Key Features**:
- Uses `apryse-sdk` for advanced OCG manipulation
- Creates a new OCG configuration
- Sets the configuration as default
- Flattens with proper page settings (A4 landscape)

### `extract_cards.py` - Individual Card Extraction
This script is **essential** for Step 6. It:

1. **Uses measured dimensions** from Step 5
2. **Calculates card positions** based on grid layout
3. **Accounts for cut marks** and margins
4. **Extracts individual cards** as proper PDFs
5. **Preserves all PDF features** (text, fonts, images, etc.)

**Usage**:
```bash
python extract_cards.py
```

**Key Features**:
- Uses `PyMuPDF` for precise PDF extraction
- Maintains all original PDF features
- Adds 2mm margin around each card
- Handles both front and back sides
- Accounts for cut marks (3mm allowance)

## Configuration

### Card Extraction Settings (extract_cards.py)

```python
# Card dimensions (measured from cut marks)
CARD_WIDTH_MM = 68.24
CARD_HEIGHT_MM = 92.70

# Cut mark allowance
CUT_MARK_MM = 3

# Page margins (measured)
PAGE_LEFT_MARGIN_MM = 12.07
PAGE_TOP_MARGIN_MM = 12.07

# Card grid (A4 with 8 cards)
CARDS_X = 4
CARDS_Y = 2

# Gaps between cards
GAP_X_MM = 0.4
GAP_Y_MM = 0.2
```

### OCG Configuration (flatten_ocg.py)

```python
# OCG layer names to process
RUS_LAYERS = ["rus", "russian", "ru"]
ENG_LAYERS = ["en", "eng", "english"]

# Apryse SDK license key (demo key for testing)
LICENSE_KEY = "demo:1750962399989:61d2e25d030000000084e44e30437ec5289b7b231800b98e3b279f3f0d"
```

## Output Format

### Individual Cards
- **Format**: PDF (not raster images)
- **Features Preserved**: Text, fonts, images, vector graphics, annotations
- **Naming**: `front_card_{page}_{index}.pdf`, `back_grid_{page}.pdf`
- **Margin**: 2mm around detected card boundaries
- **Cut Marks**: Properly accounted for in extraction

### Archive
- **Format**: ZIP file
- **Contents**: All extracted card PDFs
- **Name**: `cards_output.zip`

## Technical Details

### OCG (Optional Content Groups) Deep Dive

**Structure in PDF**:
```
OCProperties
├── D (Default configuration)
│   ├── ON (Visible OCGs)
│   └── OFF (Hidden OCGs)
├── OCGs (OCG definitions)
│   ├── OCG1 (Name: "RUS", State: Visible)
│   ├── OCG2 (Name: "ENG", State: Hidden)
│   └── OCG3 (Name: "Cards", State: Visible)
└── Configs (Configuration sets)
```

**How OCGs Work**:
1. **Definition**: Each OCG is defined with a name and default state
2. **Configuration**: Sets of OCG states can be saved as configurations
3. **Application**: Configurations determine what's visible in the PDF
4. **Flattening**: Converting OCG states to permanent content

### Card Detection and Extraction Process

1. **Manual Measurement**: Measure cut marks and card dimensions
2. **Position Calculation**: Calculate card positions based on grid layout
3. **Cut Mark Handling**: Account for cut marks in extraction boundaries
4. **PDF Extraction**: Use PyMuPDF's `show_pdf_page()` with clipping
5. **Feature Preservation**: Maintain all original PDF features

### PDF Preservation Techniques

**Why Proper PDFs (Not Images)**:
- **Text remains searchable** and selectable
- **Fonts are preserved** exactly as designed
- **Vector graphics** maintain quality at any scale
- **Annotations** and interactive elements are preserved
- **File sizes** are typically smaller than raster images

**Technical Implementation**:
```python
# Extract with clipping (preserves all features)
new_page.show_pdf_page(
    fitz.Rect(0, 0, rect.width, rect.height),
    doc, page_idx, clip=rect
)
```

## Complete Workflow Example

```bash
# Step 1: Convert PDF to images (manual - use any PDF viewer)

# Step 2: Research PDF OCG methods (manual - study documentation)

# Step 3: Check OCGs (optional - for understanding)
python list_ocg_outline.py

# Step 4: Flatten with OCG settings (ESSENTIAL)
python flatten_ocg.py

# Step 5: Measure dimensions (manual - use ruler/caliper)

# Step 6: Extract cards (ESSENTIAL)
python extract_cards.py

# Step 7: Compress results (optional)
python zip_cards.py
```

## Troubleshooting

### OCG Flattening Issues
- **License key**: Ensure apryse-sdk license is valid
- **OCG names**: Check exact layer names in the PDF
- **PDF structure**: Verify PDF supports OCGs

### Card Extraction Issues
- **Measurements**: Double-check all dimensions
- **Cut marks**: Ensure cut mark allowance is correct
- **Page margins**: Verify margin calculations

### Common Problems
- **Wrong card boundaries**: Review measurements in extract_cards.py
- **Missing text**: Ensure PDF features are preserved during extraction
- **File size issues**: Check compression settings

## File Structure

```
pdf-ocg-customize-python/
├── input.pdf                 # Original PDF with OCGs
├── flattened.pdf            # Flattened PDF (Step 4 output)
├── cards_output/            # Extracted cards (Step 6 output)
│   ├── front_card_1_1.pdf
│   ├── front_card_1_2.pdf
│   ├── back_grid_1.pdf
│   └── ...
├── cards_output.zip         # Compressed archive (Step 7 output)
├── flatten_ocg.py          # ESSENTIAL: PDF flattening (Step 4)
├── extract_cards.py        # ESSENTIAL: Card extraction (Step 6)
├── list_ocg_outline.py     # Optional: OCG analysis (Step 3)
├── analyze_layout.py       # Optional: Layout analysis (Step 5)
├── zip_cards.py           # Optional: Compression (Step 7)
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Dependencies

- **PyMuPDF (fitz)**: PDF manipulation, OCG handling, text extraction, page analysis
- **apryse-sdk**: Advanced PDF features, OCG management, PDF flattening (requires license)
- **PyPDF2**: Outline/bookmark extraction
- **collections** (built-in): Counter for data analysis
- **zipfile** (built-in): Archive compression
- **os** (built-in): File and directory operations

## License

This tool is provided as-is for educational and practical use. Modify as needed for your specific requirements.

**Note**: The apryse-sdk demo license is for testing only. For production use, obtain a proper license from Apryse. 