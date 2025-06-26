from apryse_sdk import *

# === 1. Initialize PDFNet ===
PDFNet.Initialize("demo:1750962399989:61d2e25d030000000084e44e30437ec5289b7b231800b98e3b279f3f0d")  # Replace with your actual key

# === 2. Open the input PDF ===
input_pdf = "input.pdf"
output_pdf = "disabled_layer.pdf"

doc = PDFDoc(input_pdf)
doc.InitSecurityHandler()

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
default_config = doc.GetOCGConfig()
config = Config.Create(doc, True)
on_array = doc.GetSDFDoc().CreateIndirectArray()
off_array = doc.GetSDFDoc().CreateIndirectArray()

# === 5. Enable/Disable layers ===
for ocg in ocgs:
    name = ocg.GetName().strip().lower()
    print(name)
    if name in ("rus", "russian", "ru"):
        print(f"Disabling layer: {name}")
        off_array.PushBack(ocg.GetSDFObj())
    elif name in ("en", "eng", "english"):
        print(f"Enabling layer: {name}")
        on_array.PushBack(ocg.GetSDFObj())
    else:
        # For other layers, keep them ON by default (or you can modify this logic)
        print(f"Keeping layer: {name} (default state)")
        on_array.PushBack(ocg.GetSDFObj())

config.SetName("Hide RUS Layer")
config.SetInitOnStates(on_array)
config.SetInitOffStates(off_array)

# Optional: preserve the original order
ocgs_array = doc.GetSDFDoc().CreateIndirectArray()
for ocg in ocgs:
    ocgs_array.PushBack(ocg.GetSDFObj())
config.SetOrder(ocgs_array)

# === 6. Set this config as the default ===
root = doc.GetRoot()
ocprops = root.FindObj("OCProperties")

if not ocprops:
    ocprops = doc.GetSDFDoc().CreateIndirectDict()
    root.Put("OCProperties", ocprops)

ocprops.Put("D", config.GetSDFObj())  # Set as default config

# === 7. Save output ===
doc.Save(output_pdf, 0)
doc.Close()
print(f"Saved PDF with RUS layer disabled: {output_pdf}")
