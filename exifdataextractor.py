import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
from PIL import Image, ExifTags
import piexif
import os

SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".tiff", ".tif")

def extract_exif(path):
    try:
        image = Image.open(path)
        data = image._getexif() or {}
        exif = {}

        for tag_id, value in data.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            exif[tag] = value

        return exif
    except Exception:
        return {}

def clean_image(src: Path):
    try:
        if src.stem.endswith("_cleaned"):
            log_message("Image already appears to be cleaned.")
            messagebox.showwarning(
                "Already Cleaned",
                "This image already appears to be cleaned."
            )
            return None

        image = Image.open(src)
        cleaned_path = src.with_name(src.stem + "_cleaned" + src.suffix)

        if src.suffix.lower() in (".jpg", ".jpeg", ".tiff", ".tif"):
            try:
                piexif.remove(str(src))
            except Exception:
                pass
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(cleaned_path)

        return cleaned_path

    except Exception as e:
        messagebox.showerror("Error", f"Cleaning failed:\n{e}")
        return None
def log_message(text):
    log_box.insert(tk.END, text + "\n")
    log_box.see(tk.END)

def browse_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.tiff *.tif")]
    )
    if file_path:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, file_path)
        process_btn.config(state=tk.NORMAL)

        log_box.delete(1.0, tk.END)
        log_message("New image selected.Ready to process.")

def process_image():
    filepath = path_entry.get().strip().strip('"').strip("'")

    if not filepath:
        messagebox.showwarning("Warning", "Please select an image.")
        return

    path = Path(filepath)

    if not path.exists():
        messagebox.showerror("Error", "File not found.")
        return

    if path.suffix.lower() not in SUPPORTED_FORMATS:
        messagebox.showerror("Error", "Unsupported file format.")
        return

    log_box.delete(1.0, tk.END)
    log_message("===== EXIF DATA BEFORE CLEANING =====")
    log_message(f"File: {path}")
    log_message(f"Size: {path.stat().st_size} bytes")

    exif = extract_exif(path)

    log_message(f"Make: {exif.get('Make')}")
    log_message(f"Model: {exif.get('Model')}")
    log_message(
        f"DateTime: {exif.get('DateTime') or exif.get('DateTimeOriginal')}"
    )
    log_message(f"Total EXIF tags: {len(exif)}")

    if len(exif) == 0:
        log_message("\n No EXIF metadata found in this image.")
        log_message("Skipping cleaning process.")

        messagebox.showinfo(
            "No Metadata",
            "This image does not contain any EXIF metadata."
        )
        return

    cleaned_path = clean_image(path)

    if cleaned_path:
        log_message("\n CLEANED IMAGE SAVED TO:")
        log_message(str(cleaned_path))

        log_message("\n===== EXIF DATA AFTER CLEANING =====")
        exif_after = extract_exif(cleaned_path)
        log_message(f"Total EXIF tags: {len(exif_after)}")

        process_btn.config(state=tk.DISABLED)

        messagebox.showinfo("Success", "Metadata removed successfully!")
        
root = tk.Tk()
root.title("EXIF Metadata Cleaner Tool")
root.geometry("650x500")
root.resizable(False, False)

title_label = tk.Label(
    root,
    text="EXIF Metadata Extractor & Cleaning Tool",
    font=("Arial", 14, "bold"),
)
title_label.pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=5)

path_entry = tk.Entry(frame, width=55)
path_entry.pack(side=tk.LEFT, padx=5)

browse_btn = tk.Button(frame, text="Browse", command=browse_file)
browse_btn.pack(side=tk.LEFT)

process_btn = tk.Button(
    root,
    text="Extract & Clean Metadata",
    command=process_image,
    bg="#4CAF50",
    fg="white",
    font=("Arial", 10, "bold"),
)
process_btn.pack(pady=10)

log_box = scrolledtext.ScrolledText(root, width=75, height=20)
log_box.pack(padx=10, pady=10)

root.mainloop()
