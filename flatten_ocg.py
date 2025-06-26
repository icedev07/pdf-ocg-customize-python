import os
from apryse_sdk import *

# === 1. Initialize PDFNet ===
PDFNet.Initialize("demo:1750962399989:61d2e25d030000000084e44e30437ec5289b7b231800b98e3b279f3f0d")  # Replace with your actual key

# === 2. Open the input PDF ===
input_pdf = "input.pdf"

# Get the directory path of the input file
input_dir = os.path.dirname(os.path.abspath(input_pdf))
output_pdf = os.path.join(input_dir, "flattened.pdf")

doc = PDFDoc(input_pdf)
doc.InitSecurityHandler()

default_config = doc.GetOCGConfig()
ctx = Context(default_config)

# === 3. Find all OCGs ===
ocgs_obj = doc.GetOCGs()
ocgs = []
if ocgs_obj and ocgs_obj.IsArray():
    for i in range(ocgs_obj.Size()):
        ocgs.append(Group(ocgs_obj.GetAt(i)))

if not ocgs:
    print("No layers found in this PDF.")
    exit()

# === 4. Create new OCG configuration (layer settings) ===
config = Config.Create(doc, True)

on_array = doc.GetSDFDoc().CreateIndirectArray()
off_array = doc.GetSDFDoc().CreateIndirectArray()

# === 5. Enable/Disable layers ===
for ocg in ocgs:
    name = ocg.GetName().strip().lower()
    print(f"Processing layer: {name}")
    if name in ("rus", "russian", "ru"):
        print(f"Disabling layer: {name}")
        off_array.PushBack(ocg.GetSDFObj())
    elif name in ("en", "eng", "english"):
        print(f"Enabling layer: {name}")
        on_array.PushBack(ocg.GetSDFObj())
    else:
        # Preserve current state for other layers
        if ctx.GetState(ocg):
            on_array.PushBack(ocg.GetSDFObj())
        else:
            off_array.PushBack(ocg.GetSDFObj())

config.SetName("Hide RUS Layer")
config.SetInitOnStates(on_array)
config.SetInitOffStates(off_array)

# === 6. Set this config as the default ===
root = doc.GetRoot()
ocprops = root.FindObj("OCProperties")

if not ocprops:
    ocprops = doc.GetSDFDoc().CreateIndirectDict()
    root.Put("OCProperties", ocprops)

ocprops.Put("D", config.GetSDFObj())  # Set as default config

# === 7. Print PDF with OCG configuration ===
print("Creating flattened PDF with invisible OCGs excluded...")

# Set PrinterMode options
printerMode = PrinterMode()
printerMode.SetOrientation(PrinterMode.e_Orientation_Landscape)
printerMode.SetPaperSize(Rect(0, 0, 842, 595))  # A4 landscape in points (297mm x 210mm)

# Print to file instead of printer
# The third parameter is the output file path
Print.StartPrintJob(doc, "", "flattened.pdf", output_pdf, None, printerMode, None)

doc.Close()
print(f"Flattened PDF created successfully: {output_pdf}")

# === 8. Cleanup ===
PDFNet.Terminate()
