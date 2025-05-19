import os
import json
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import exifread
import hashlib
# Configure matplotlib to use Agg backend for headless environments
import matplotlib

matplotlib.use('Agg')  # Must be before importing pyplot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import io
import struct
import re
import PyPDF2
import random
import string
import datetime
import base64
import shutil

# Constants
APP_NAME = "Digital Forensics Toolkit"
APP_VERSION = "3.0.0"

# Define theme colors
LIGHT_THEME = {
    "bg_color": "#F0F0F0",
    "fg_color": "#000000",
    "secondary_bg": "#E0E0E0",
    "button_bg": "#DDDDDD",
    "button_fg": "#000000",
    "text_area_bg": "#FFFFFF",
    "text_area_fg": "#000000",
    "accent_color": "#4CAF50"
}

DARK_THEME = {
    "bg_color": "#2D2D2D",
    "fg_color": "#FFFFFF",
    "secondary_bg": "#3D3D3D",
    "button_bg": "#444444",
    "button_fg": "#FFFFFF",
    "text_area_bg": "#222222",
    "text_area_fg": "#FFFFFF",
    "accent_color": "#4CAF50"
}


class DigitalForensicsToolkit:
    """Main application class for the Digital Forensics Toolkit"""

    def __init__(self, root):
        # Initialize root window
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")

        # Initialize state variables
        self.current_file = None
        self.file_metadata = {}
        self.theme = "light"
        self.colors = LIGHT_THEME  # Default to light theme

        # Configure window
        self.root.geometry("1000x800")
        self.root.minsize(800, 600)
        self.root.configure(bg=self.colors["bg_color"])

        # Create UI
        self.create_ui()

        # Create menu
        self.create_menu()

    def create_ui(self):
        """Create the application UI"""
        # Title and theme toggle
        header_frame = tk.Frame(self.root, bg=self.colors["bg_color"])
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        title_label = tk.Label(
            header_frame,
            text=APP_NAME,
            font=("Arial", 24, "bold"),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"]
        )
        title_label.pack(side=tk.LEFT)

        theme_button = tk.Button(
            header_frame,
            text="Toggle Theme",
            command=self.toggle_theme,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            font=("Arial", 10)
        )
        theme_button.pack(side=tk.RIGHT)

        # File upload section
        upload_frame = tk.Frame(self.root, bg=self.colors["bg_color"])
        upload_frame.pack(fill=tk.X, padx=10, pady=5)

        upload_button = tk.Button(
            upload_frame,
            text="Upload File",
            command=self.upload_file,
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=10,
            pady=5
        )
        upload_button.pack(side=tk.LEFT, padx=5)

        self.file_path_var = tk.StringVar(value="No file selected")
        file_path_label = tk.Label(
            upload_frame,
            textvariable=self.file_path_var,
            bg=self.colors["secondary_bg"],
            fg=self.colors["fg_color"],
            font=("Arial", 10),
            anchor="w",
            padx=10,
            pady=5,
            relief=tk.GROOVE
        )
        file_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Content area
        content_frame = tk.Frame(self.root, bg=self.colors["bg_color"])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left panel for preview
        left_panel = tk.Frame(content_frame, bg=self.colors["bg_color"], width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_panel.pack_propagate(False)  # Prevent frame from shrinking

        # Preview title
        preview_title = tk.Label(
            left_panel,
            text="File Preview",
            font=("Arial", 14, "bold"),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"]
        )
        preview_title.pack(anchor="w", pady=(0, 5))

        # Preview frame
        self.preview_frame = tk.Frame(
            left_panel,
            bg=self.colors["secondary_bg"],
            width=280,
            height=280,
            relief=tk.GROOVE,
            bd=1
        )
        self.preview_frame.pack(pady=5)
        self.preview_frame.pack_propagate(False)  # Prevent frame from shrinking

        # Preview label
        self.preview_label = tk.Label(
            self.preview_frame,
            text="No preview available",
            bg=self.colors["secondary_bg"],
            fg=self.colors["fg_color"],
            font=("Arial", 10)
        )
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        # Keep reference to prevent garbage collection
        self.image_reference = None

        # Right panel for metadata display
        right_panel = tk.Frame(content_frame, bg=self.colors["bg_color"])
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Metadata title
        metadata_title = tk.Label(
            right_panel,
            text="Metadata Results",
            font=("Arial", 14, "bold"),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"]
        )
        metadata_title.pack(anchor="w", pady=(0, 5))

        # Metadata display
        self.metadata_display = scrolledtext.ScrolledText(
            right_panel,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg=self.colors["text_area_bg"],
            fg=self.colors["text_area_fg"],
            insertbackground=self.colors["fg_color"]
        )
        self.metadata_display.pack(fill=tk.BOTH, expand=True, pady=5)
        self.metadata_display.config(state="disabled")

        # Action buttons
        buttons_frame = tk.Frame(self.root, bg=self.colors["bg_color"])
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)

        check_button = tk.Button(
            buttons_frame,
            text="Check Metadata",
            command=self.check_metadata,
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=10,
            pady=5
        )
        check_button.pack(side=tk.LEFT, padx=5)

        remove_button = tk.Button(
            buttons_frame,
            text="Remove Metadata",
            command=self.remove_metadata,
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=10,
            pady=5
        )
        remove_button.pack(side=tk.LEFT, padx=5)

        save_button = tk.Button(
            buttons_frame,
            text="Save Metadata",
            command=self.save_metadata,
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=10,
            pady=5
        )
        save_button.pack(side=tk.LEFT, padx=5)

        compare_button = tk.Button(
            buttons_frame,
            text="Compare Files",
            command=self.compare_files,
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=10,
            pady=5
        )
        compare_button.pack(side=tk.LEFT, padx=5)

        visualize_button = tk.Button(
            buttons_frame,
            text="Visualize Data",
            command=self.visualize_metadata,
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=10,
            pady=5
        )
        visualize_button.pack(side=tk.LEFT, padx=5)

        # Status bar
        status_frame = tk.Frame(self.root, bg=self.colors["secondary_bg"])
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            bg=self.colors["secondary_bg"],
            fg=self.colors["fg_color"],
            font=("Arial", 10),
            anchor="w",
            padx=10,
            pady=5
        )
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Progress bar
        self.progress = ttk.Progressbar(status_frame, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(side=tk.RIGHT, padx=10, pady=5)

    def create_menu(self):
        """Create the application menu"""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open File", command=self.upload_file)
        file_menu.add_separator()
        file_menu.add_command(label="Save Metadata", command=self.save_metadata)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # View menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=view_menu)

        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        theme_menu.add_command(label="Light", command=lambda: self.set_theme("light"))
        theme_menu.add_command(label="Dark", command=lambda: self.set_theme("dark"))

        # Tools menu
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Forensic Tools", menu=tools_menu)
        tools_menu.add_command(label="PDF Analyzer", command=self.analyze_pdf)
        tools_menu.add_command(label="PDF Script Injector", command=self.inject_pdf_script)
        tools_menu.add_command(label="Metadata Faker", command=self.open_metadata_faker)
        tools_menu.add_command(label="File Type Spoofer", command=self.open_file_spoofer)
        tools_menu.add_command(label="Advanced File Analysis", command=self.advanced_analysis)

        # Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        new_theme = "dark" if self.theme == "light" else "light"
        self.set_theme(new_theme)

    def set_theme(self, theme):
        """Set a specific theme"""
        if theme in ["light", "dark"] and theme != self.theme:
            self.theme = theme
            self.colors = LIGHT_THEME if theme == "light" else DARK_THEME
            self.update_ui_theme()

    def update_ui_theme(self):
        """Update the theme of all UI components"""
        # Update root window
        self.root.configure(bg=self.colors["bg_color"])

        # Update all frames and widgets
        for widget in self.root.winfo_children():
            widget_class = widget.winfo_class()

            if widget_class in ["Frame", "Labelframe"]:
                widget.configure(bg=self.colors["bg_color"])
                # Update child widgets
                for child in widget.winfo_children():
                    child_class = child.winfo_class()
                    if child_class == "Label":
                        child.configure(bg=self.colors["bg_color"], fg=self.colors["fg_color"])
                    elif child_class == "Button":
                        child.configure(bg=self.colors["button_bg"], fg=self.colors["button_fg"])
                    elif child_class == "Text" or child_class == "Scrollbar":
                        child.configure(bg=self.colors["text_area_bg"], fg=self.colors["text_area_fg"])

            # Update other widgets
            elif widget_class == "Label":
                widget.configure(bg=self.colors["bg_color"], fg=self.colors["fg_color"])
            elif widget_class == "Button":
                widget.configure(bg=self.colors["button_bg"], fg=self.colors["button_fg"])

        # Update specific widgets
        self.preview_frame.configure(bg=self.colors["secondary_bg"])
        self.preview_label.configure(bg=self.colors["secondary_bg"], fg=self.colors["fg_color"])

        self.metadata_display.configure(
            bg=self.colors["text_area_bg"],
            fg=self.colors["text_area_fg"],
            insertbackground=self.colors["fg_color"]
        )

        # Update status bar specific widgets
        for widget in self.root.winfo_children():
            if widget.winfo_class() == "Frame" and widget.cget("bg") == self.colors["secondary_bg"]:
                for child in widget.winfo_children():
                    if child.winfo_class() == "Label":
                        child.configure(bg=self.colors["secondary_bg"], fg=self.colors["fg_color"])

    def upload_file(self):
        """Handle file upload"""
        file_path = filedialog.askopenfilename(
            title="Select a File",
            filetypes=[
                ("All Files", "*.*"),
                ("Image Files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"),
                ("Document Files", "*.pdf *.doc *.docx *.txt"),
                ("Audio Files", "*.mp3 *.wav *.flac *.aac *.ogg"),
                ("Video Files", "*.mp4 *.avi *.mov *.mkv")
            ]
        )

        if file_path:
            self.current_file = file_path
            self.file_path_var.set(file_path)
            self.set_image(file_path)
            self.status_var.set(f"Loaded file: {os.path.basename(file_path)}")
        else:
            self.status_var.set("No file selected")

    def set_image(self, file_path):
        """Set an image for preview"""
        # Clear existing preview
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        if file_path and os.path.exists(file_path):
            try:
                # Check if it's an image file
                file_ext = os.path.splitext(file_path)[1].lower()
                image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]

                if file_ext in image_extensions:
                    # Open and resize image for preview
                    img = Image.open(file_path)
                    img = img.resize((280, 280), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)

                    # Display image
                    self.preview_label = tk.Label(
                        self.preview_frame,
                        image=img_tk,
                        bg=self.preview_frame["bg"]
                    )
                    self.preview_label.pack(fill=tk.BOTH, expand=True)
                    self.image_reference = img_tk  # Keep reference at instance level
                else:
                    # Show file type icon instead
                    file_type = self.get_file_type_category(file_path)
                    self.preview_label = tk.Label(
                        self.preview_frame,
                        text=f"{file_type} File\n\n{os.path.basename(file_path)}",
                        bg=self.preview_frame["bg"],
                        fg=self.colors["fg_color"],
                        font=("Arial", 12)
                    )
                    self.preview_label.pack(fill=tk.BOTH, expand=True)
            except Exception as e:
                # Display error
                self.preview_label = tk.Label(
                    self.preview_frame,
                    text=f"Preview error:\n{str(e)}",
                    bg=self.preview_frame["bg"],
                    fg=self.colors["fg_color"],
                    font=("Arial", 10)
                )
                self.preview_label.pack(fill=tk.BOTH, expand=True)
        else:
            # No image provided or file doesn't exist
            self.preview_label = tk.Label(
                self.preview_frame,
                text="No preview available",
                bg=self.preview_frame["bg"],
                fg=self.colors["fg_color"],
                font=("Arial", 10)
            )
            self.preview_label.pack(fill=tk.BOTH, expand=True)

    def get_file_type_category(self, file_path):
        """Determine the category of a file based on its extension"""
        ext = os.path.splitext(file_path)[1].lower()

        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        audio_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
        document_extensions = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx']

        if ext in image_extensions:
            return "Image"
        elif ext in audio_extensions:
            return "Audio"
        elif ext in video_extensions:
            return "Video"
        elif ext in document_extensions:
            return "Document"
        else:
            return "Other"

    def check_metadata(self):
        """Check metadata for the current file"""
        if not self.current_file:
            messagebox.showwarning("No File Selected", "Please upload a file first")
            return

        # Update status
        self.status_var.set(f"Extracting metadata from {os.path.basename(self.current_file)}...")
        self.progress.start()

        # Extract metadata in a background thread
        threading.Thread(target=self._extract_metadata_thread).start()

    def _extract_metadata_thread(self):
        """Extract metadata in a background thread"""
        try:
            # Extract metadata
            self.file_metadata = self.extract_metadata(self.current_file)

            # Update UI in the main thread
            self.root.after(0, self._update_metadata_display)
        except Exception as e:
            # Show error in the main thread
            self.root.after(0, lambda: self._show_error(f"Error extracting metadata: {str(e)}"))

    def _update_metadata_display(self):
        """Update the metadata display (called in main thread)"""
        self.metadata_display.config(state="normal")
        self.metadata_display.delete(1.0, tk.END)

        for key, value in self.file_metadata.items():
            if key == 'GPS Coordinates' and value and isinstance(value, tuple):
                lat, lon = value
                self.metadata_display.insert(tk.END, f"{key}: https://www.google.com/maps?q={lat},{lon}\n")
            else:
                self.metadata_display.insert(tk.END, f"{key}: {value}\n")

        self.metadata_display.config(state="disabled")
        self.progress.stop()
        self.status_var.set(f"Metadata extracted successfully for {os.path.basename(self.current_file)}")

    def _show_error(self, message):
        """Show an error message (called in main thread)"""
        messagebox.showerror("Error", message)
        self.progress.stop()
        self.status_var.set("Error occurred")

    def extract_metadata(self, file_path):
        """Extract metadata based on file type"""
        metadata = {}
        file_type = self.get_file_type_category(file_path)

        # Common file metadata
        metadata['File Name'] = os.path.basename(file_path)
        metadata['File Path'] = file_path
        metadata['File Size'] = self.format_file_size(os.path.getsize(file_path))
        metadata['File Type Category'] = file_type
        metadata['File Extension'] = os.path.splitext(file_path)[1].lower()
        metadata['Last Modified'] = time.ctime(os.path.getmtime(file_path))
        metadata['Created'] = time.ctime(os.path.getctime(file_path))
        metadata['MD5 Checksum'] = self.calculate_checksum(file_path)

        # Type-specific metadata
        if file_type == "Image":
            image_metadata = self.extract_image_metadata(file_path)
            metadata.update(image_metadata)
        elif file_type == "Audio":
            audio_metadata = {"Format": "Audio file"}
            # TODO: Implement audio metadata extraction
            metadata.update(audio_metadata)
        elif file_type == "Video":
            video_metadata = {"Format": "Video file"}
            # TODO: Implement video metadata extraction
            metadata.update(video_metadata)
        elif file_type == "Document":
            document_metadata = {"Format": "Document file"}
            # TODO: Implement document metadata extraction
            metadata.update(document_metadata)

        return metadata

    def extract_image_metadata(self, file_path):
        """Extract metadata from image files"""
        metadata = {}

        # Get basic image info using PIL
        try:
            with Image.open(file_path) as img:
                metadata['Image Format'] = img.format
                metadata['Image Mode'] = img.mode
                metadata['Image Size'] = f"{img.width} x {img.height} pixels"
                metadata['Image Resolution'] = f"{img.info.get('dpi', 'Unknown')}"
        except Exception as e:
            metadata['Image Processing Error'] = str(e)

        # Get EXIF data
        try:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f)

                if tags:
                    metadata['Camera Model'] = str(tags.get('Image Model', 'Not available'))
                    metadata['Camera Make'] = str(tags.get('Image Make', 'Not available'))
                    metadata['Date Taken'] = str(tags.get('EXIF DateTimeOriginal', 'Not available'))
                    metadata['Exposure Time'] = str(tags.get('EXIF ExposureTime', 'Not available'))
                    metadata['F Number'] = str(tags.get('EXIF FNumber', 'Not available'))
                    metadata['ISO'] = str(tags.get('EXIF ISOSpeedRatings', 'Not available'))
                    metadata['Focal Length'] = str(tags.get('EXIF FocalLength', 'Not available'))

                    # GPS information
                    if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                        lat = self.convert_to_degrees(tags['GPS GPSLatitude'].values)
                        lon = self.convert_to_degrees(tags['GPS GPSLongitude'].values)

                        if 'GPS GPSLatitudeRef' in tags:
                            if str(tags['GPS GPSLatitudeRef'].values) != 'N':
                                lat = -lat

                        if 'GPS GPSLongitudeRef' in tags:
                            if str(tags['GPS GPSLongitudeRef'].values) != 'E':
                                lon = -lon

                        metadata['GPS Coordinates'] = (lat, lon)
                else:
                    metadata['EXIF Data'] = 'No EXIF data found'
        except Exception as e:
            metadata['EXIF Processing Error'] = str(e)

        return metadata

    def convert_to_degrees(self, value):
        """Convert GPS coordinates to degrees"""
        d = float(value[0].num) / float(value[0].den)
        m = float(value[1].num) / float(value[1].den)
        s = float(value[2].num) / float(value[2].den)
        return d + (m / 60.0) + (s / 3600.0)

    def format_file_size(self, size_bytes):
        """Format file size in bytes to human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

    def calculate_checksum(self, file_path):
        """Calculate MD5 checksum for a file"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read(65536)  # Read in 64k chunks
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()

    def remove_metadata(self):
        """Remove metadata from the current file"""
        if not self.current_file:
            messagebox.showwarning("No File Selected", "Please upload a file first")
            return

        # Confirm with user
        if not messagebox.askyesno(
                "Remove Metadata",
                "This will create a new copy of the file with metadata removed. Continue?"
        ):
            return

        # Update status
        self.status_var.set(f"Removing metadata from {os.path.basename(self.current_file)}...")
        self.progress.start()

        # Remove metadata in a background thread
        threading.Thread(target=self._remove_metadata_thread).start()

    def _remove_metadata_thread(self):
        """Remove metadata in a background thread"""
        try:
            file_type = self.get_file_type_category(self.current_file)

            if file_type == "Image":
                # Remove metadata from image file
                with Image.open(self.current_file) as img:
                    data = list(img.getdata())
                    new_img = Image.new(img.mode, img.size)
                    new_img.putdata(data)

                    # Generate new file path
                    base_path, ext = os.path.splitext(self.current_file)
                    new_file_path = f"{base_path}_no_metadata{ext}"

                    # Save new image without metadata
                    new_img.save(new_file_path)

                    # Update UI in the main thread
                    self.root.after(0, lambda: self._metadata_removal_complete(new_file_path))
            else:
                # Not supported for other file types yet
                raise Exception(f"Metadata removal not supported for {file_type} files yet")

        except Exception as e:
            # Show error in the main thread
            self.root.after(0, lambda: self._show_error(f"Error removing metadata: {str(e)}"))

    def _metadata_removal_complete(self, new_file_path):
        """Handle metadata removal completion (called in main thread)"""
        self.progress.stop()

        if os.path.exists(new_file_path):
            # Success - open the new file
            messagebox.showinfo(
                "Metadata Removed",
                f"Metadata has been removed. New file saved as:\n{new_file_path}"
            )

            # Load the new file
            self.current_file = new_file_path
            self.file_path_var.set(new_file_path)
            self.set_image(new_file_path)
            self.status_var.set(f"Loaded file: {os.path.basename(new_file_path)}")

            # Check metadata of new file
            self.check_metadata()
        else:
            # Failed
            messagebox.showerror("Error", "Failed to remove metadata")
            self.status_var.set("Metadata removal failed")

    def save_metadata(self):
        """Save metadata to a file"""
        if not self.file_metadata:
            messagebox.showwarning("No Metadata", "No metadata available to save")
            return

        file_types = [("Text File", "*.txt"), ("JSON File", "*.json")]
        file_path = filedialog.asksaveasfilename(
            title="Save Metadata",
            filetypes=file_types,
            defaultextension=".txt"
        )

        if file_path:
            try:
                self.status_var.set(f"Saving metadata to {os.path.basename(file_path)}...")
                self.progress.start()

                # Save in a background thread
                threading.Thread(
                    target=self._save_metadata_thread,
                    args=(file_path,)
                ).start()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save metadata: {str(e)}")
                self.progress.stop()
                self.status_var.set("Metadata save failed")

    def _save_metadata_thread(self, file_path):
        """Save metadata in a background thread"""
        try:
            if file_path.endswith(".json"):
                with open(file_path, 'w') as file:
                    # Convert any non-serializable values to strings
                    serializable_metadata = {}
                    for key, value in self.file_metadata.items():
                        if isinstance(value, tuple):
                            serializable_metadata[key] = str(value)
                        else:
                            serializable_metadata[key] = value

                    json.dump(serializable_metadata, file, indent=4)
            else:
                with open(file_path, 'w') as file:
                    for key, value in self.file_metadata.items():
                        file.write(f"{key}: {value}\n")

            # Update UI in the main thread
            self.root.after(0, lambda: self._save_complete(file_path))
        except Exception as e:
            # Show error in the main thread
            self.root.after(0, lambda: self._show_error(f"Error saving metadata: {str(e)}"))

    def _save_complete(self, file_path):
        """Handle save completion (called in main thread)"""
        self.progress.stop()
        messagebox.showinfo("Success", f"Metadata saved as {file_path}")
        self.status_var.set(f"Metadata saved to {os.path.basename(file_path)}")

    def compare_files(self):
        """Compare metadata between two files"""
        if not self.file_metadata:
            messagebox.showwarning("No Metadata", "Please check metadata of a file first")
            return

        # Create comparison dialog
        compare_dialog = tk.Toplevel(self.root)
        compare_dialog.title("Compare Files")
        compare_dialog.geometry("500x400")
        compare_dialog.configure(bg=self.colors["bg_color"])
        compare_dialog.transient(self.root)
        compare_dialog.grab_set()

        # First file info
        file1_frame = tk.Frame(compare_dialog, bg=self.colors["bg_color"])
        file1_frame.pack(fill=tk.X, padx=10, pady=10)

        file1_label = tk.Label(
            file1_frame,
            text="First File:",
            font=("Arial", 12),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"]
        )
        file1_label.pack(side=tk.LEFT)

        file1_path_var = tk.StringVar(value=self.current_file)
        file1_path = tk.Entry(
            file1_frame,
            textvariable=file1_path_var,
            bg=self.colors["text_area_bg"],
            fg=self.colors["text_area_fg"],
            width=30
        )
        file1_path.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        file1_button = tk.Button(
            file1_frame,
            text="Browse",
            command=lambda: self._select_file(file1_path_var),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"]
        )
        file1_button.pack(side=tk.RIGHT)

        # Second file info
        file2_frame = tk.Frame(compare_dialog, bg=self.colors["bg_color"])
        file2_frame.pack(fill=tk.X, padx=10, pady=10)

        file2_label = tk.Label(
            file2_frame,
            text="Second File:",
            font=("Arial", 12),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"]
        )
        file2_label.pack(side=tk.LEFT)

        file2_path_var = tk.StringVar()
        file2_path = tk.Entry(
            file2_frame,
            textvariable=file2_path_var,
            bg=self.colors["text_area_bg"],
            fg=self.colors["text_area_fg"],
            width=30
        )
        file2_path.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        file2_button = tk.Button(
            file2_frame,
            text="Browse",
            command=lambda: self._select_file(file2_path_var),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"]
        )
        file2_button.pack(side=tk.RIGHT)

        # Compare button
        compare_button_frame = tk.Frame(compare_dialog, bg=self.colors["bg_color"])
        compare_button_frame.pack(fill=tk.X, padx=10, pady=10)

        compare_button = tk.Button(
            compare_button_frame,
            text="Compare Files",
            command=lambda: self._compare_files(file1_path_var.get(), file2_path_var.get(), compare_dialog),
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=10,
            pady=5
        )
        compare_button.pack()

    def _select_file(self, path_var):
        """Select a file and update the path variable"""
        file_path = filedialog.askopenfilename(
            title="Select a File",
            filetypes=[
                ("All Files", "*.*"),
                ("Image Files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"),
                ("Document Files", "*.pdf *.doc *.docx *.txt"),
                ("Audio Files", "*.mp3 *.wav *.flac *.aac *.ogg"),
                ("Video Files", "*.mp4 *.avi *.mov *.mkv")
            ]
        )
        if file_path:
            path_var.set(file_path)

    def _compare_files(self, file1_path, file2_path, dialog):
        """Compare metadata of two files"""
        if not file1_path or not file2_path:
            messagebox.showwarning("Missing Files", "Please select two files to compare", parent=dialog)
            return

        if file1_path == file2_path:
            messagebox.showwarning("Same File", "Please select two different files", parent=dialog)
            return

        # Extract metadata
        self.status_var.set("Comparing files...")
        self.progress.start()

        try:
            file1_metadata = self.extract_metadata(file1_path)
            file2_metadata = self.extract_metadata(file2_path)

            # Create comparison results dialog
            results_dialog = tk.Toplevel(self.root)
            results_dialog.title("Comparison Results")
            results_dialog.geometry("800x600")
            results_dialog.configure(bg=self.colors["bg_color"])
            results_dialog.transient(self.root)
            results_dialog.grab_set()

            # Header with file names
            header_frame = tk.Frame(results_dialog, bg=self.colors["bg_color"])
            header_frame.pack(fill=tk.X, padx=10, pady=10)

            file1_name = os.path.basename(file1_path)
            file2_name = os.path.basename(file2_path)

            header_label = tk.Label(
                header_frame,
                text=f"Comparing: {file1_name} vs {file2_name}",
                font=("Arial", 14, "bold"),
                bg=self.colors["bg_color"],
                fg=self.colors["fg_color"]
            )
            header_label.pack()

            # Create notebook for different views
            notebook = ttk.Notebook(results_dialog)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Summary tab
            summary_frame = tk.Frame(notebook, bg=self.colors["bg_color"])
            notebook.add(summary_frame, text="Summary")

            summary_text = scrolledtext.ScrolledText(
                summary_frame,
                wrap=tk.WORD,
                font=("Arial", 10),
                bg=self.colors["text_area_bg"],
                fg=self.colors["text_area_fg"]
            )
            summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Calculate similarities and differences
            common_keys = set(file1_metadata.keys()) & set(file2_metadata.keys())
            only_file1_keys = set(file1_metadata.keys()) - set(file2_metadata.keys())
            only_file2_keys = set(file2_metadata.keys()) - set(file1_metadata.keys())

            # Find differences in common keys
            differences = {}
            similarities = {}

            for key in common_keys:
                if file1_metadata[key] != file2_metadata[key]:
                    differences[key] = (file1_metadata[key], file2_metadata[key])
                else:
                    similarities[key] = file1_metadata[key]

            # Summary content
            summary_text.insert(tk.END, f"COMPARISON SUMMARY\n{'=' * 50}\n\n")
            summary_text.insert(tk.END, f"Total fields in File 1: {len(file1_metadata)}\n")
            summary_text.insert(tk.END, f"Total fields in File 2: {len(file2_metadata)}\n")
            summary_text.insert(tk.END, f"Common fields: {len(common_keys)}\n")
            summary_text.insert(tk.END, f"Similar values: {len(similarities)}\n")
            summary_text.insert(tk.END, f"Different values: {len(differences)}\n")
            summary_text.insert(tk.END, f"Only in File 1: {len(only_file1_keys)}\n")
            summary_text.insert(tk.END, f"Only in File 2: {len(only_file2_keys)}\n\n")

            # Differences tab
            if differences:
                diff_frame = tk.Frame(notebook, bg=self.colors["bg_color"])
                notebook.add(diff_frame, text="Differences")

                diff_text = scrolledtext.ScrolledText(
                    diff_frame,
                    wrap=tk.WORD,
                    font=("Arial", 10),
                    bg=self.colors["text_area_bg"],
                    fg=self.colors["text_area_fg"]
                )
                diff_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                diff_text.insert(tk.END, f"DIFFERENCES BETWEEN FILES\n{'=' * 50}\n\n")
                for key in sorted(differences.keys()):
                    diff_text.insert(tk.END, f"{key}:\n")
                    diff_text.insert(tk.END, f"  File 1: {differences[key][0]}\n")
                    diff_text.insert(tk.END, f"  File 2: {differences[key][1]}\n\n")

            # Close dialog button
            button_frame = tk.Frame(results_dialog, bg=self.colors["bg_color"])
            button_frame.pack(fill=tk.X, padx=10, pady=10)

            close_button = tk.Button(
                button_frame,
                text="Close",
                command=results_dialog.destroy,
                font=("Arial", 12),
                bg=self.colors["button_bg"],
                fg=self.colors["button_fg"],
                padx=10,
                pady=5
            )
            close_button.pack()

            self.progress.stop()
            self.status_var.set("Comparison complete")

            # Close the file selection dialog
            dialog.destroy()

        except Exception as e:
            self.progress.stop()
            self.status_var.set("Error during comparison")
            messagebox.showerror("Error", f"Error comparing files: {str(e)}", parent=dialog)

    def visualize_metadata(self):
        """Visualize metadata"""
        if not self.file_metadata:
            messagebox.showwarning("No Metadata", "Please check metadata of a file first")
            return

        # Create visualization dialog
        viz_dialog = tk.Toplevel(self.root)
        viz_dialog.title("Visualize Metadata")
        viz_dialog.geometry("400x250")
        viz_dialog.configure(bg=self.colors["bg_color"])
        viz_dialog.transient(self.root)
        viz_dialog.grab_set()

        # Header
        header_label = tk.Label(
            viz_dialog,
            text="Choose Visualization Type",
            font=("Arial", 14, "bold"),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"]
        )
        header_label.pack(pady=10)

        # Visualization options
        options_frame = tk.Frame(viz_dialog, bg=self.colors["bg_color"])
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Helper function to create option buttons
        def create_option(text, command):
            button = tk.Button(
                options_frame,
                text=text,
                command=command,
                font=("Arial", 12),
                bg=self.colors["button_bg"],
                fg=self.colors["button_fg"],
                padx=10,
                pady=5,
                width=30
            )
            button.pack(pady=5)
            return button

        # Add visualization options
        create_option("Image Metadata Pie Chart",
                      lambda: self._show_pie_chart(viz_dialog))

        create_option("File Size Bar Chart",
                      lambda: self._show_bar_chart(viz_dialog))

        # Cancel button
        cancel_button = tk.Button(
            viz_dialog,
            text="Cancel",
            command=viz_dialog.destroy,
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=10,
            pady=5
        )
        cancel_button.pack(pady=10)

    def _show_pie_chart(self, parent_dialog):
        """Show a pie chart of metadata categories"""
        # Create categories and count metadata fields in each
        categories = {}
        for key in self.file_metadata.keys():
            category = key.split(' ')[0] if ' ' in key else "Other"
            categories[category] = categories.get(category, 0) + 1

        # Create a new dialog for the chart
        chart_dialog = tk.Toplevel(self.root)
        chart_dialog.title("Metadata Categories")
        chart_dialog.geometry("800x600")
        chart_dialog.configure(bg=self.colors["bg_color"])
        chart_dialog.transient(self.root)
        chart_dialog.grab_set()

        # Header
        header_label = tk.Label(
            chart_dialog,
            text=f"Metadata Categories for {os.path.basename(self.current_file)}",
            font=("Arial", 14, "bold"),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"]
        )
        header_label.pack(pady=10)

        # Create figure and canvas for the chart
        fig, ax = plt.subplots(figsize=(8, 6), facecolor=self.colors["bg_color"])
        canvas = FigureCanvasTkAgg(fig, master=chart_dialog)

        # Create pie chart
        labels = list(categories.keys())
        values = list(categories.values())

        # Use custom colors
        theme_colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6', '#c4e17f']

        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=theme_colors)
        ax.set_title('Metadata Field Categories', color=self.colors["fg_color"])
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle

        # Adjust text color based on theme
        for text in ax.texts:
            text.set_color(self.colors["fg_color"])
        for text in ax.get_xticklabels() + ax.get_yticklabels():
            text.set_color(self.colors["fg_color"])
        for item in ax.get_children():
            if isinstance(item, plt.Text):
                item.set_color(self.colors["fg_color"])

        # Display the chart
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Close button
        close_button = tk.Button(
            chart_dialog,
            text="Close",
            command=chart_dialog.destroy,
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=10,
            pady=5
        )
        close_button.pack(pady=10)

        # Close the parent dialog
        parent_dialog.destroy()

    def _show_bar_chart(self, parent_dialog):
        """Show a bar chart of file size comparison with average sizes"""
        # Get file size in bytes
        file_path = self.current_file
        file_size = os.path.getsize(file_path)
        file_type = self.get_file_type_category(file_path)

        # Average sizes for comparison (in bytes)
        avg_sizes = {
            "Image": 2 * 1024 * 1024,  # 2MB
            "Audio": 5 * 1024 * 1024,  # 5MB
            "Video": 20 * 1024 * 1024,  # 20MB
            "Document": 1 * 1024 * 1024,  # 1MB
            "Other": 3 * 1024 * 1024,  # 3MB
        }

        # Create a new dialog for the chart
        chart_dialog = tk.Toplevel(self.root)
        chart_dialog.title("File Size Comparison")
        chart_dialog.geometry("800x600")
        chart_dialog.configure(bg=self.colors["bg_color"])
        chart_dialog.transient(self.root)
        chart_dialog.grab_set()

        # Header
        header_label = tk.Label(
            chart_dialog,
            text=f"File Size Comparison for {os.path.basename(file_path)}",
            font=("Arial", 14, "bold"),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"]
        )
        header_label.pack(pady=10)

        # Create figure and canvas for the chart
        fig, ax = plt.subplots(figsize=(8, 6), facecolor=self.colors["bg_color"])
        canvas = FigureCanvasTkAgg(fig, master=chart_dialog)

        # Create bar chart
        labels = ["This File", f"Average {file_type}"]
        sizes = [file_size / (1024 * 1024), avg_sizes.get(file_type, 0) / (1024 * 1024)]  # Convert to MB

        bar_colors = ['#ff9999', '#66b3ff']

        bars = ax.bar(labels, sizes, color=bar_colors)
        ax.set_ylabel('Size (MB)', color=self.colors["fg_color"])
        ax.set_title('File Size Comparison', color=self.colors["fg_color"])

        # Add labels above bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f} MB',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom',
                        color=self.colors["fg_color"])

        # Adjust colors for theme
        ax.spines['bottom'].set_color(self.colors["fg_color"])
        ax.spines['top'].set_color(self.colors["fg_color"])
        ax.spines['left'].set_color(self.colors["fg_color"])
        ax.spines['right'].set_color(self.colors["fg_color"])
        ax.tick_params(axis='x', colors=self.colors["fg_color"])
        ax.tick_params(axis='y', colors=self.colors["fg_color"])

        # Display the chart
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Close button
        close_button = tk.Button(
            chart_dialog,
            text="Close",
            command=chart_dialog.destroy,
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=10,
            pady=5
        )
        close_button.pack(pady=10)

        # Close the parent dialog
        parent_dialog.destroy()

    def advanced_analysis(self):
        """Advanced file analysis for detecting anomalies and hidden content"""
        if not self.current_file:
            messagebox.showwarning("No File Selected", "Please upload a file first")
            return

        # Create analysis dialog
        analysis_dialog = tk.Toplevel(self.root)
        analysis_dialog.title("Advanced File Analysis")
        analysis_dialog.geometry("800x600")
        analysis_dialog.configure(bg=self.colors["bg_color"])
        analysis_dialog.transient(self.root)
        analysis_dialog.grab_set()

        # Header
        header_frame = tk.Frame(analysis_dialog, bg=self.colors["bg_color"])
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        header_label = tk.Label(
            header_frame,
            text=f"Advanced Analysis: {os.path.basename(self.current_file)}",
            font=("Arial", 14, "bold"),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"]
        )
        header_label.pack()

        # Create notebook for tabs
        notebook = ttk.Notebook(analysis_dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        binary_frame = tk.Frame(notebook, bg=self.colors["bg_color"])
        entropy_frame = tk.Frame(notebook, bg=self.colors["bg_color"])
        strings_frame = tk.Frame(notebook, bg=self.colors["bg_color"])

        notebook.add(binary_frame, text="Binary Preview")
        notebook.add(entropy_frame, text="Entropy Analysis")
        notebook.add(strings_frame, text="String Extraction")

        # Binary preview tab
        binary_text = scrolledtext.ScrolledText(
            binary_frame,
            wrap=tk.WORD,
            bg=self.colors["text_area_bg"],
            fg=self.colors["text_area_fg"],
            font=("Courier New", 10)
        )
        binary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Entropy visualization tab
        entropy_frame_inner = tk.Frame(entropy_frame, bg=self.colors["bg_color"])
        entropy_frame_inner.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Strings tab
        strings_text = scrolledtext.ScrolledText(
            strings_frame,
            wrap=tk.WORD,
            bg=self.colors["text_area_bg"],
            fg=self.colors["text_area_fg"],
            font=("Courier New", 10)
        )
        strings_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Load and analyze the file
        try:
            with open(self.current_file, 'rb') as f:
                file_bytes = f.read()

            # Update binary preview
            binary_text.delete(1.0, tk.END)
            bytes_per_row = 16
            for i in range(0, min(len(file_bytes), 4096), bytes_per_row):
                # Offset
                binary_text.insert(tk.END, f"{i:08X}: ")

                # Hex representation
                hex_line = ""
                for j in range(bytes_per_row):
                    if i + j < len(file_bytes):
                        hex_line += f"{file_bytes[i + j]:02X} "
                    else:
                        hex_line += "   "
                binary_text.insert(tk.END, f"{hex_line}  ")

                # ASCII representation
                ascii_line = ""
                for j in range(bytes_per_row):
                    if i + j < len(file_bytes):
                        byte = file_bytes[i + j]
                        if 32 <= byte <= 126:  # Printable ASCII
                            ascii_line += chr(byte)
                        else:
                            ascii_line += "."
                    else:
                        ascii_line += " "
                binary_text.insert(tk.END, f"{ascii_line}\n")

            if len(file_bytes) > 4096:
                binary_text.insert(tk.END, "\n[Preview limited to first 4KB. File is larger.]\n")

            # Calculate and display entropy
            def calculate_entropy(data):
                if not data:
                    return 0

                # Count byte occurrences
                byte_counts = {}
                for byte in data:
                    if byte not in byte_counts:
                        byte_counts[byte] = 0
                    byte_counts[byte] += 1

                # Calculate entropy
                entropy = 0
                for count in byte_counts.values():
                    probability = count / len(data)
                    entropy -= probability * np.log2(probability)

                return entropy

            # Calculate entropy for file chunks
            chunk_size = 1024  # 1KB chunks
            chunks = [file_bytes[i:i + chunk_size] for i in range(0, len(file_bytes), chunk_size)]
            chunk_entropies = [calculate_entropy(chunk) for chunk in chunks]

            # Create entropy visualization
            fig, ax = plt.subplots(figsize=(8, 4), facecolor=self.colors["bg_color"])
            canvas = FigureCanvasTkAgg(fig, master=entropy_frame_inner)

            x_values = list(range(len(chunk_entropies)))
            ax.plot(x_values, chunk_entropies, '-o', color='#4CAF50', markersize=3)
            ax.set_xlabel('Chunk (1KB blocks)', color=self.colors["fg_color"])
            ax.set_ylabel('Entropy (bits)', color=self.colors["fg_color"])
            ax.set_title('File Entropy Analysis', color=self.colors["fg_color"])
            ax.grid(True, linestyle='--', alpha=0.7)

            # Mark suspicious regions (high entropy)
            high_entropy_threshold = 7.5
            for i, entropy in enumerate(chunk_entropies):
                if entropy > high_entropy_threshold:
                    ax.axvspan(i - 0.5, i + 0.5, color='red', alpha=0.3)

            # Add annotations
            file_entropy = calculate_entropy(file_bytes)
            ax.text(0.02, 0.95, f'Overall entropy: {file_entropy:.2f} bits',
                    transform=ax.transAxes, color=self.colors["fg_color"],
                    bbox=dict(facecolor=self.colors["secondary_bg"], alpha=0.7))

            # Interpret the entropy
            interpretation = ""
            if file_entropy < 1:
                interpretation = "Very low entropy: likely empty, sparse, or highly repetitive data"
            elif file_entropy < 3:
                interpretation = "Low entropy: probably text, configuration files, or structured data"
            elif file_entropy < 6:
                interpretation = "Medium entropy: typical for many document formats and basic binaries"
            elif file_entropy < 7.5:
                interpretation = "High entropy: possibly compressed or media data"
            else:
                interpretation = "Very high entropy: likely encrypted or compressed data"

            ax.text(0.02, 0.89, interpretation,
                    transform=ax.transAxes, color=self.colors["fg_color"],
                    bbox=dict(facecolor=self.colors["secondary_bg"], alpha=0.7))

            # Update colors based on theme
            ax.spines['bottom'].set_color(self.colors["fg_color"])
            ax.spines['top'].set_color(self.colors["fg_color"])
            ax.spines['left'].set_color(self.colors["fg_color"])
            ax.spines['right'].set_color(self.colors["fg_color"])
            ax.tick_params(axis='x', colors=self.colors["fg_color"])
            ax.tick_params(axis='y', colors=self.colors["fg_color"])

            # Display the chart
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # Extract strings
            def extract_strings(data, min_length=4):
                strings = []
                current_string = ""
                for byte in data:
                    # Is it a printable ASCII character?
                    if 32 <= byte <= 126:
                        current_string += chr(byte)
                    else:
                        # If we have a string of minimum length, add it
                        if len(current_string) >= min_length:
                            strings.append(current_string)
                        current_string = ""

                # Don't forget the last string
                if len(current_string) >= min_length:
                    strings.append(current_string)

                return strings

            strings = extract_strings(file_bytes)

            # Update the strings display
            strings_text.delete(1.0, tk.END)
            for string in strings:
                strings_text.insert(tk.END, f"{string}\n")

            # Look for potentially suspicious strings
            suspicious_patterns = [
                r"password", r"passwd", r"pass",
                r"auth", r"login",
                r"http[s]?://", r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
                r"BEGIN.*PRIVATE KEY", r"ssh-rsa", r"exec\(", r"eval\(",
                r"powershell", r"cmd\.exe", r"shell", r"socket", r"connect\(",
                r"process", r"system\(", r"bin/sh", r"bin/bash"
            ]

            # Highlight suspicious strings
            for pattern in suspicious_patterns:
                start_index = "1.0"
                while True:
                    start_index = strings_text.search(pattern, start_index, tk.END, regexp=True)
                    if not start_index:
                        break

                    end_index = f"{start_index}+{len(pattern)}c"
                    strings_text.tag_add("suspicious", start_index, end_index)
                    start_index = end_index

            strings_text.tag_configure("suspicious", background="red", foreground="white")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze file: {str(e)}", parent=analysis_dialog)

        # Button frame
        button_frame = tk.Frame(analysis_dialog, bg=self.colors["bg_color"])
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        close_button = tk.Button(
            button_frame,
            text="Close",
            command=analysis_dialog.destroy,
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=10,
            pady=5
        )
        close_button.pack(side=tk.RIGHT)

    def inject_pdf_script(self):
        """Inject JavaScript into a PDF file"""
        if not self.current_file:
            messagebox.showwarning("No File Selected", "Please upload a file first")
            return

        # Check if it's a PDF
        if not self.current_file.lower().endswith('.pdf'):
            messagebox.showwarning("Not a PDF", "Please select a PDF file")
            return

        # Create PDF script injector dialog
        injector_dialog = tk.Toplevel(self.root)
        injector_dialog.title("Advanced PDF Script Injector")
        injector_dialog.geometry("900x700")
        injector_dialog.configure(bg=self.colors["bg_color"])
        injector_dialog.transient(self.root)
        injector_dialog.grab_set()

        # Header
        header_frame = tk.Frame(injector_dialog, bg=self.colors["bg_color"])
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        header_label = tk.Label(
            header_frame,
            text="PDF JavaScript Injector",
            font=("Arial", 16, "bold"),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"]
        )
        header_label.pack()

        # Warning message
        warning_frame = tk.Frame(injector_dialog, bg=self.colors["bg_color"])
        warning_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        warning_label = tk.Label(
            warning_frame,
            text="⚠️ For educational purposes only. Use responsibly. ⚠️",
            font=("Arial", 10, "italic"),
            fg="orange",
            bg=self.colors["bg_color"]
        )
        warning_label.pack()

        # File info
        info_frame = tk.Frame(injector_dialog, bg=self.colors["bg_color"])
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        info_label = tk.Label(
            info_frame,
            text=f"Target PDF: {os.path.basename(self.current_file)}",
            font=("Arial", 10),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"],
            anchor="w"
        )
        info_label.pack(fill=tk.X)

        # Script selection area
        script_frame = tk.Frame(injector_dialog, bg=self.colors["bg_color"])
        script_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tabs for different script types
        script_notebook = ttk.Notebook(script_frame)
        script_notebook.pack(fill=tk.BOTH, expand=True)

        # Template scripts tab
        templates_frame = tk.Frame(script_notebook, bg=self.colors["bg_color"])
        script_notebook.add(templates_frame, text="Script Templates")

        # Custom script tab
        custom_frame = tk.Frame(script_notebook, bg=self.colors["bg_color"])
        script_notebook.add(custom_frame, text="Custom Script")

        # Template scripts list
        templates_label = tk.Label(
            templates_frame,
            text="Select a script template:",
            font=("Arial", 12),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"],
            anchor="w"
        )
        templates_label.pack(fill=tk.X, padx=10, pady=5)

        templates_frame_inner = tk.Frame(templates_frame, bg=self.colors["bg_color"])
        templates_frame_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        templates_list = tk.Listbox(
            templates_frame_inner,
            bg=self.colors["text_area_bg"],
            fg=self.colors["text_area_fg"],
            font=("Arial", 10),
            height=10
        )
        templates_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        templates_scroll = ttk.Scrollbar(templates_frame_inner, orient="vertical", command=templates_list.yview)
        templates_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        templates_list.configure(yscrollcommand=templates_scroll.set)

        # Script preview
        preview_frame = tk.Frame(templates_frame, bg=self.colors["bg_color"])
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        preview_label = tk.Label(
            preview_frame,
            text="Script Preview:",
            font=("Arial", 10, "bold"),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"],
            anchor="w"
        )
        preview_label.pack(fill=tk.X)

        preview_text = scrolledtext.ScrolledText(
            preview_frame,
            wrap=tk.WORD,
            bg=self.colors["text_area_bg"],
            fg=self.colors["text_area_fg"],
            font=("Courier New", 10),
            height=10
        )
        preview_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Custom script editor
        custom_label = tk.Label(
            custom_frame,
            text="Enter your custom JavaScript code:",
            font=("Arial", 12),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"],
            anchor="w"
        )
        custom_label.pack(fill=tk.X, padx=10, pady=5)

        custom_script = scrolledtext.ScrolledText(
            custom_frame,
            wrap=tk.WORD,
            bg=self.colors["text_area_bg"],
            fg=self.colors["text_area_fg"],
            font=("Courier New", 10)
        )
        custom_script.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Add template scripts
        templates = {
            "Simple Alert": 'app.alert("This PDF has been analyzed by the Digital Forensics Toolkit", 3);',

            "Document Information": """app.alert("PDF Document Information:");
var info = this.info;
for (var key in info) {
    app.alert(key + ": " + info[key]);
}""",

            "Page Counter": """// Count pages and display info
var numPages = this.numPages;
app.alert("This document has " + numPages + " pages.");

// Function to be called when the document is opened
function showPageCount() {
    app.alert("Document with " + numPages + " pages has been opened.");
}

// Trigger when document is opened
this.setAction("Open", "showPageCount();");""",

            "Form Data Collector": """// Create a hidden form field to collect data
try {
    var field = this.addField("hiddenData", "text", 0, [0, 0, 0, 0]);
    field.hidden = true;

    // Collect document data
    var dataToCollect = {
        title: this.info.Title,
        subject: this.info.Subject,
        author: this.info.Author,
        creator: this.info.Creator,
        producer: this.info.Producer,
        currentUser: app.viewerVersion
    };

    // Store collected data in the hidden field
    field.value = JSON.stringify(dataToCollect);

    // Send the data when the document is opened (would connect to an external server)
    this.setAction("Open", "app.alert('Data collection initialized');");
} catch(e) {
    // Silently fail
}"""
        }

        # Add templates to the list
        for template_name in templates.keys():
            templates_list.insert(tk.END, template_name)

        # Update preview when template is selected
        def on_template_select(event):
            selected_indices = templates_list.curselection()
            if selected_indices:
                selected_template = templates_list.get(selected_indices[0])
                preview_text.delete(1.0, tk.END)
                preview_text.insert(tk.END, templates[selected_template])

        templates_list.bind('<<ListboxSelect>>', on_template_select)

        # Action buttons
        button_frame = tk.Frame(injector_dialog, bg=self.colors["bg_color"])
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        def inject_script():
            try:
                # Get the script content
                if script_notebook.index(script_notebook.select()) == 0:  # Templates tab
                    selected_indices = templates_list.curselection()
                    if not selected_indices:
                        messagebox.showwarning("No Template Selected", "Please select a script template",
                                               parent=injector_dialog)
                        return

                    selected_template = templates_list.get(selected_indices[0])
                    script_content = templates[selected_template]
                else:  # Custom script tab
                    script_content = custom_script.get(1.0, tk.END).strip()
                    if not script_content:
                        messagebox.showwarning("Empty Script", "Please enter a JavaScript script",
                                               parent=injector_dialog)
                        return

                # Ask for save location
                save_path = filedialog.asksaveasfilename(
                    title="Save Modified PDF",
                    defaultextension=".pdf",
                    filetypes=[("PDF Files", "*.pdf")],
                    initialdir=os.path.dirname(self.current_file),
                    initialfile=f"scripted_{os.path.basename(self.current_file)}"
                )

                if not save_path:
                    return

                # Update status
                self.status_var.set("Injecting JavaScript into PDF...")
                self.progress.start()

                # Use PyPDF2 to add JavaScript
                with open(self.current_file, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    pdf_writer = PyPDF2.PdfWriter()

                    # Copy all pages
                    for page_num in range(len(pdf_reader.pages)):
                        pdf_writer.add_page(pdf_reader.pages[page_num])

                    # Add JavaScript action
                    pdf_writer.add_js(script_content)

                    # Save the modified PDF
                    with open(save_path, 'wb') as output_file:
                        pdf_writer.write(output_file)

                self.progress.stop()
                self.status_var.set(f"JavaScript injected into {os.path.basename(save_path)}")

                messagebox.showinfo(
                    "Success",
                    f"JavaScript successfully injected into PDF.\nSaved as: {save_path}",
                    parent=injector_dialog
                )

                # Ask if the user wants to open the modified PDF
                if messagebox.askyesno(
                        "Open Modified PDF",
                        "Would you like to open the modified PDF file?",
                        parent=injector_dialog
                ):
                    injector_dialog.destroy()
                    self.current_file = save_path
                    self.file_path_var.set(save_path)
                    self.set_image(save_path)
                    self.status_var.set(f"Loaded modified PDF: {os.path.basename(save_path)}")
                    self.check_metadata()

            except Exception as e:
                self.progress.stop()
                self.status_var.set("Error injecting JavaScript")
                messagebox.showerror("Error", f"Failed to inject JavaScript: {str(e)}", parent=injector_dialog)

        inject_button = tk.Button(
            button_frame,
            text="Inject JavaScript",
            command=inject_script,
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=10,
            pady=5
        )
        inject_button.pack(side=tk.LEFT)

        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=injector_dialog.destroy,
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=10,
            pady=5
        )
        cancel_button.pack(side=tk.RIGHT)

    def analyze_pdf(self):
        """Analyze a PDF file for hidden content or potentially malicious scripts"""
        if not self.current_file:
            messagebox.showwarning("No File Selected", "Please upload a file first")
            return

        # Check if it's a PDF
        if not self.current_file.lower().endswith('.pdf'):
            messagebox.showwarning("Not a PDF", "Please select a PDF file for analysis")
            return

        # Create PDF analyzer dialog
        pdf_dialog = tk.Toplevel(self.root)
        pdf_dialog.title("PDF Analyzer")
        pdf_dialog.geometry("800x600")
        pdf_dialog.configure(bg=self.colors["bg_color"])
        pdf_dialog.transient(self.root)
        pdf_dialog.grab_set()

        # Header
        header_frame = tk.Frame(pdf_dialog, bg=self.colors["bg_color"])
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        header_label = tk.Label(
            header_frame,
            text=f"Analyzing PDF: {os.path.basename(self.current_file)}",
            font=("Arial", 14, "bold"),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"]
        )
        header_label.pack()

        # Create notebook for tabs
        notebook = ttk.Notebook(pdf_dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        summary_frame = tk.Frame(notebook, bg=self.colors["bg_color"])
        structure_frame = tk.Frame(notebook, bg=self.colors["bg_color"])
        js_frame = tk.Frame(notebook, bg=self.colors["bg_color"])
        hidden_frame = tk.Frame(notebook, bg=self.colors["bg_color"])

        notebook.add(summary_frame, text="Summary")
        notebook.add(structure_frame, text="Structure")
        notebook.add(js_frame, text="JavaScript")
        notebook.add(hidden_frame, text="Hidden Content")

        # Analyze the PDF
        try:
            with open(self.current_file, 'rb') as f:
                pdf = PyPDF2.PdfReader(f)

                # Summary tab
                summary_text = scrolledtext.ScrolledText(
                    summary_frame,
                    wrap=tk.WORD,
                    bg=self.colors["text_area_bg"],
                    fg=self.colors["text_area_fg"],
                    font=("Arial", 10)
                )
                summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                # Add summary information
                summary_text.insert(tk.END, f"PDF VERSION: {pdf.pdf_header}\n")
                summary_text.insert(tk.END, f"NUMBER OF PAGES: {len(pdf.pages)}\n")
                summary_text.insert(tk.END, f"ENCRYPTED: {pdf.is_encrypted}\n\n")

                summary_text.insert(tk.END, "DOCUMENT INFORMATION:\n")
                if pdf.metadata:
                    for key in pdf.metadata:
                        summary_text.insert(tk.END, f"- {key}: {pdf.metadata[key]}\n")
                else:
                    summary_text.insert(tk.END, "No document information found\n")

                # Structure tab
                structure_text = scrolledtext.ScrolledText(
                    structure_frame,
                    wrap=tk.WORD,
                    bg=self.colors["text_area_bg"],
                    fg=self.colors["text_area_fg"],
                    font=("Courier New", 10)
                )
                structure_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                # Add PDF structure
                trailer = pdf.trailer
                if trailer:
                    structure_text.insert(tk.END, "PDF TRAILER:\n")
                    structure_text.insert(tk.END, f"{trailer}\n\n")

                # JavaScript tab
                js_text = scrolledtext.ScrolledText(
                    js_frame,
                    wrap=tk.WORD,
                    bg=self.colors["text_area_bg"],
                    fg=self.colors["text_area_fg"],
                    font=("Courier New", 10)
                )
                js_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                # Look for JavaScript in the PDF
                js_found = False
                potential_js_patterns = [
                    br'/JavaScript',
                    br'/JS',
                    br'eval\(',
                    br'function\(',
                    br'document\.write'
                ]

                js_text.insert(tk.END, "SEARCHING FOR JAVASCRIPT...\n\n")

                # Read the PDF as bytes to search for patterns
                with open(self.current_file, 'rb') as raw_pdf:
                    pdf_content = raw_pdf.read()

                    for pattern in potential_js_patterns:
                        matches = re.finditer(pattern, pdf_content)
                        for match in matches:
                            js_found = True
                            start_pos = max(0, match.start() - 20)
                            end_pos = min(len(pdf_content), match.end() + 100)
                            context = pdf_content[start_pos:end_pos]

                            try:
                                # Try to decode as UTF-8, if not possible, show as hex
                                decoded = context.decode('utf-8', errors='replace')
                                js_text.insert(tk.END, f"Found at position {match.start()}: \n{decoded}\n\n")
                            except:
                                js_text.insert(tk.END, f"Found at position {match.start()} (binary data)\n\n")

                if not js_found:
                    js_text.insert(tk.END, "No JavaScript found in this PDF.\n")

                # Hidden content tab
                hidden_text = scrolledtext.ScrolledText(
                    hidden_frame,
                    wrap=tk.WORD,
                    bg=self.colors["text_area_bg"],
                    fg=self.colors["text_area_fg"],
                    font=("Arial", 10)
                )
                hidden_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                # Look for potential hidden content
                hidden_text.insert(tk.END, "SEARCHING FOR HIDDEN CONTENT...\n\n")

                suspicious_patterns = {
                    "Embedded Files": br'/EmbeddedFiles',
                    "File Attachment": br'/FileAttachment',
                    "Launch Action": br'/Launch',
                    "URI Action": br'/URI',
                    "Hidden Layers": br'/OCG',
                    "AcroForm": br'/AcroForm',
                    "XFA Forms": br'/XFA'
                }

                found_suspicious = False

                for name, pattern in suspicious_patterns.items():
                    if pattern in pdf_content:
                        found_suspicious = True
                        hidden_text.insert(tk.END, f"Found {name} - This PDF contains potentially hidden content\n")

                        # For URI actions, try to extract the URLs
                        if name == "URI Action":
                            urls = re.findall(br'/URI\s*\(([^)]+)\)', pdf_content)
                            if urls:
                                hidden_text.insert(tk.END, "  URLs found:\n")
                                for url in urls:
                                    try:
                                        decoded_url = url.decode('utf-8', errors='replace')
                                        hidden_text.insert(tk.END, f"    - {decoded_url}\n")
                                    except:
                                        hidden_text.insert(tk.END, f"    - [Unable to decode URL]\n")

                if not found_suspicious:
                    hidden_text.insert(tk.END, "No suspicious hidden content detected.\n")

        except Exception as e:
            for frame in [summary_frame, structure_frame, js_frame, hidden_frame]:
                error_text = scrolledtext.ScrolledText(
                    frame,
                    wrap=tk.WORD,
                    bg=self.colors["text_area_bg"],
                    fg="red",
                    font=("Arial", 10)
                )
                error_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                error_text.insert(tk.END, f"Error analyzing PDF: {str(e)}")

        # Close button
        close_frame = tk.Frame(pdf_dialog, bg=self.colors["bg_color"])
        close_frame.pack(fill=tk.X, padx=10, pady=10)

        close_button = tk.Button(
            close_frame,
            text="Close",
            command=pdf_dialog.destroy,
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=10,
            pady=5
        )
        close_button.pack()

    def open_metadata_faker(self):
        """Open a tool to create fake metadata for images"""
        # Create metadata faker dialog
        faker_dialog = tk.Toplevel(self.root)
        faker_dialog.title("Metadata Faker")
        faker_dialog.geometry("600x700")
        faker_dialog.configure(bg=self.colors["bg_color"])
        faker_dialog.transient(self.root)
        faker_dialog.grab_set()

        # Header
        header_frame = tk.Frame(faker_dialog, bg=self.colors["bg_color"])
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        header_label = tk.Label(
            header_frame,
            text="Create Fake Image Metadata",
            font=("Arial", 16, "bold"),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"]
        )
        header_label.pack()

        # File selection
        file_frame = tk.Frame(faker_dialog, bg=self.colors["bg_color"])
        file_frame.pack(fill=tk.X, padx=10, pady=5)

        file_label = tk.Label(
            file_frame,
            text="Select Image File:",
            font=("Arial", 12),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"]
        )
        file_label.pack(side=tk.LEFT)

        file_path_var = tk.StringVar(value=self.current_file if self.current_file else "")
        file_entry = tk.Entry(
            file_frame,
            textvariable=file_path_var,
            width=40,
            bg=self.colors["text_area_bg"],
            fg=self.colors["text_area_fg"]
        )
        file_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        def browse_file():
            file_path = filedialog.askopenfilename(
                title="Select Image File",
                filetypes=[("Image Files", "*.jpg *.jpeg *.png *.tiff")]
            )
            if file_path:
                file_path_var.set(file_path)

        browse_button = tk.Button(
            file_frame,
            text="Browse",
            command=browse_file,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"]
        )
        browse_button.pack(side=tk.RIGHT)

        # Create a notebook for the different metadata sections
        notebook = ttk.Notebook(faker_dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Basic tab
        basic_frame = tk.Frame(notebook, bg=self.colors["bg_color"])
        notebook.add(basic_frame, text="Basic Info")

        # Camera tab
        camera_frame = tk.Frame(notebook, bg=self.colors["bg_color"])
        notebook.add(camera_frame, text="Camera Info")

        # GPS tab
        gps_frame = tk.Frame(notebook, bg=self.colors["bg_color"])
        notebook.add(gps_frame, text="GPS Location")

        # Add fields to basic frame
        basic_inner = tk.Frame(basic_frame, bg=self.colors["bg_color"])
        basic_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Helper function to create a label/entry pair
        def create_field(parent, label_text, default=""):
            frame = tk.Frame(parent, bg=self.colors["bg_color"])
            frame.pack(fill=tk.X, pady=5)

            label = tk.Label(
                frame,
                text=label_text,
                width=20,
                anchor="w",
                bg=self.colors["bg_color"],
                fg=self.colors["fg_color"]
            )
            label.pack(side=tk.LEFT, padx=5)

            var = tk.StringVar(value=default)
            entry = tk.Entry(
                frame,
                textvariable=var,
                bg=self.colors["text_area_bg"],
                fg=self.colors["text_area_fg"]
            )
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

            return var

        # Basic metadata fields
        date_taken_var = create_field(basic_inner, "Date Taken:", "2023:01:15 14:30:45")
        software_var = create_field(basic_inner, "Software:", "Adobe Photoshop 2023")
        artist_var = create_field(basic_inner, "Artist:")
        copyright_var = create_field(basic_inner, "Copyright:")
        description_var = create_field(basic_inner, "Description:")

        # Camera metadata fields
        camera_inner = tk.Frame(camera_frame, bg=self.colors["bg_color"])
        camera_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        make_var = create_field(camera_inner, "Camera Make:", "Canon")
        model_var = create_field(camera_inner, "Camera Model:", "EOS 5D Mark IV")
        exposure_var = create_field(camera_inner, "Exposure Time:", "1/250")
        aperture_var = create_field(camera_inner, "Aperture:", "f/2.8")
        iso_var = create_field(camera_inner, "ISO:", "400")
        focal_length_var = create_field(camera_inner, "Focal Length:", "50.0 mm")

        # GPS metadata fields
        gps_inner = tk.Frame(gps_frame, bg=self.colors["bg_color"])
        gps_inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        latitude_var = create_field(gps_inner, "Latitude:", "40.7128")
        longitude_var = create_field(gps_inner, "Longitude:", "-74.0060")
        altitude_var = create_field(gps_inner, "Altitude:", "0")

        # Map preview
        map_label = tk.Label(
            gps_inner,
            text="Map Preview (Use coordinates above):",
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"],
            anchor="w"
        )
        map_label.pack(fill=tk.X, pady=5)

        map_frame = tk.Frame(
            gps_inner,
            bg=self.colors["text_area_bg"],
            height=200
        )
        map_frame.pack(fill=tk.X, expand=True, pady=5)
        map_frame.pack_propagate(False)

        map_link_var = tk.StringVar()
        map_link = tk.Label(
            map_frame,
            textvariable=map_link_var,
            bg=self.colors["text_area_bg"],
            fg=self.colors["accent_color"],
            cursor="hand2"
        )
        map_link.pack(fill=tk.BOTH, expand=True)

        def update_map_link(*args):
            try:
                lat = float(latitude_var.get())
                lon = float(longitude_var.get())
                map_link_var.set(f"View on Map: https://www.google.com/maps?q={lat},{lon}")
            except ValueError:
                map_link_var.set("Enter valid coordinates above")

        latitude_var.trace("w", update_map_link)
        longitude_var.trace("w", update_map_link)
        update_map_link()

        # Apply button and functionality
        def apply_fake_metadata():
            image_path = file_path_var.get()
            if not image_path:
                messagebox.showwarning("No Image Selected", "Please select an image file", parent=faker_dialog)
                return

            if not os.path.exists(image_path):
                messagebox.showerror("File Error", "Selected file does not exist", parent=faker_dialog)
                return

            # Create a temporary file for the output
            try:
                # Ask for the output file path
                output_path = filedialog.asksaveasfilename(
                    title="Save Image With Fake Metadata",
                    defaultextension=".jpg",
                    filetypes=[("JPEG Image", "*.jpg"), ("All Files", "*.*")],
                    initialdir=os.path.dirname(image_path),
                    initialfile=f"fake_metadata_{os.path.basename(image_path)}"
                )

                if not output_path:
                    return

                # First, copy the original image
                with open(image_path, 'rb') as input_file:
                    image_data = input_file.read()

                with open(output_path, 'wb') as output_file:
                    output_file.write(image_data)

                # Display a message that in a real application, we would modify the metadata
                message = "In a real application, this would modify the image's metadata using techniques like:\n\n"
                message += "1. Using the piexif library to manipulate EXIF data\n"
                message += "2. Creating a custom EXIF data dictionary\n"
                message += "3. Inserting the fake metadata values into the image\n\n"
                message += "The output file has been created (currently just a copy of the original).\n\n"
                message += "Would you like to open this file to verify?"

                if messagebox.askyesno("Metadata Faker", message, parent=faker_dialog):
                    # Update main UI with the new file
                    self.current_file = output_path
                    self.file_path_var.set(output_path)
                    self.set_image(output_path)
                    self.status_var.set(f"Loaded file with fake metadata: {os.path.basename(output_path)}")
                    faker_dialog.destroy()
                    self.check_metadata()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to create fake metadata: {str(e)}", parent=faker_dialog)

        button_frame = tk.Frame(faker_dialog, bg=self.colors["bg_color"])
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        apply_button = tk.Button(
            button_frame,
            text="Apply Fake Metadata",
            command=apply_fake_metadata,
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=10,
            pady=5
        )
        apply_button.pack(side=tk.LEFT)

        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=faker_dialog.destroy,
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=10,
            pady=5
        )
        cancel_button.pack(side=tk.RIGHT)

    def open_file_spoofer(self):
        """Open a tool to change file signatures/magic numbers"""
        if not self.current_file:
            messagebox.showwarning("No File Selected", "Please upload a file first")
            return

        # Create file spoofer dialog
        spoof_dialog = tk.Toplevel(self.root)
        spoof_dialog.title("File Type Spoofer")
        spoof_dialog.geometry("700x600")
        spoof_dialog.configure(bg=self.colors["bg_color"])
        spoof_dialog.transient(self.root)
        spoof_dialog.grab_set()

        # Header
        header_frame = tk.Frame(spoof_dialog, bg=self.colors["bg_color"])
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        header_label = tk.Label(
            header_frame,
            text="Advanced File Type Signature Spoofer",
            font=("Arial", 16, "bold"),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"]
        )
        header_label.pack()

        # File info
        info_frame = tk.Frame(spoof_dialog, bg=self.colors["bg_color"])
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        info_text = f"Current File: {os.path.basename(self.current_file)}\n"
        info_text += f"Size: {self.format_file_size(os.path.getsize(self.current_file))}"

        info_label = tk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 10),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"],
            justify=tk.LEFT
        )
        info_label.pack(anchor="w")

        # Current signature
        signature_frame = tk.Frame(spoof_dialog, bg=self.colors["bg_color"])
        signature_frame.pack(fill=tk.X, padx=10, pady=5)

        signature_label = tk.Label(
            signature_frame,
            text="Current File Signature (first 16 bytes):",
            font=("Arial", 10, "bold"),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"]
        )
        signature_label.pack(anchor="w")

        # Read first 16 bytes
        current_signature = ""
        try:
            with open(self.current_file, 'rb') as f:
                first_bytes = f.read(16)
                current_signature = ' '.join([f"{b:02X}" for b in first_bytes])
        except Exception as e:
            current_signature = f"Error reading file: {str(e)}"

        current_sig_text = tk.Text(
            signature_frame,
            height=2,
            width=50,
            font=("Courier New", 10),
            bg=self.colors["text_area_bg"],
            fg=self.colors["text_area_fg"],
            state="normal"
        )
        current_sig_text.pack(fill=tk.X, pady=5)
        current_sig_text.insert(tk.END, current_signature)
        current_sig_text.config(state="disabled")

        # Common file signatures
        common_frame = tk.Frame(spoof_dialog, bg=self.colors["bg_color"])
        common_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        common_label = tk.Label(
            common_frame,
            text="Common File Type Signatures:",
            font=("Arial", 10, "bold"),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"]
        )
        common_label.pack(anchor="w")

        # Table header
        table_frame = tk.Frame(common_frame, bg=self.colors["bg_color"])
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Headers
        header_type = tk.Label(
            table_frame,
            text="File Type",
            font=("Arial", 10, "bold"),
            width=15,
            bg=self.colors["secondary_bg"],
            fg=self.colors["fg_color"]
        )
        header_type.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        header_ext = tk.Label(
            table_frame,
            text="Extension",
            font=("Arial", 10, "bold"),
            width=10,
            bg=self.colors["secondary_bg"],
            fg=self.colors["fg_color"]
        )
        header_ext.grid(row=0, column=1, sticky="nsew", padx=1, pady=1)

        header_sig = tk.Label(
            table_frame,
            text="Signature (Hex)",
            font=("Arial", 10, "bold"),
            width=20,
            bg=self.colors["secondary_bg"],
            fg=self.colors["fg_color"]
        )
        header_sig.grid(row=0, column=2, sticky="nsew", padx=1, pady=1)

        header_action = tk.Label(
            table_frame,
            text="Action",
            font=("Arial", 10, "bold"),
            width=10,
            bg=self.colors["secondary_bg"],
            fg=self.colors["fg_color"]
        )
        header_action.grid(row=0, column=3, sticky="nsew", padx=1, pady=1)

        # Common file signatures data
        signatures = [
            ("JPEG Image", ".jpg", "FF D8 FF"),
            ("PNG Image", ".png", "89 50 4E 47 0D 0A 1A 0A"),
            ("GIF Image", ".gif", "47 49 46 38"),
            ("BMP Image", ".bmp", "42 4D"),
            ("PDF Document", ".pdf", "25 50 44 46"),
            ("ZIP Archive", ".zip", "50 4B 03 04"),
            ("RAR Archive", ".rar", "52 61 72 21"),
            ("7-Zip Archive", ".7z", "37 7A BC AF 27 1C"),
            ("Windows EXE", ".exe", "4D 5A"),
            ("PHP Script", ".php", "3C 3F 70 68 70"),
            ("HTML Document", ".html", "3C 68 74 6D 6C"),
            ("MS Office Doc", ".doc", "D0 CF 11 E0"),
        ]

        # Add rows
        for i, (file_type, extension, signature) in enumerate(signatures, start=1):
            type_label = tk.Label(
                table_frame,
                text=file_type,
                font=("Arial", 9),
                bg=self.colors["text_area_bg"],
                fg=self.colors["text_area_fg"]
            )
            type_label.grid(row=i, column=0, sticky="nsew", padx=1, pady=1)

            ext_label = tk.Label(
                table_frame,
                text=extension,
                font=("Arial", 9),
                bg=self.colors["text_area_bg"],
                fg=self.colors["text_area_fg"]
            )
            ext_label.grid(row=i, column=1, sticky="nsew", padx=1, pady=1)

            sig_label = tk.Label(
                table_frame,
                text=signature,
                font=("Courier New", 9),
                bg=self.colors["text_area_bg"],
                fg=self.colors["text_area_fg"]
            )
            sig_label.grid(row=i, column=2, sticky="nsew", padx=1, pady=1)

            def create_spoof_function(sig):
                # Remove spaces and convert to bytes
                sig_bytes = bytes.fromhex(sig.replace(" ", ""))

                def spoof():
                    try:
                        # Ask for save location
                        save_path = filedialog.asksaveasfilename(
                            title="Save Spoofed File",
                            initialdir=os.path.dirname(self.current_file),
                            initialfile=f"spoofed_{os.path.basename(self.current_file)}"
                        )

                        if save_path:
                            # Read the original file
                            with open(self.current_file, 'rb') as f:
                                file_data = f.read()

                            # Create a new file with modified signature
                            with open(save_path, 'wb') as f:
                                # Write the new signature bytes
                                f.write(sig_bytes)

                                # Write the rest of the file, skipping the first len(sig_bytes)
                                if len(file_data) > len(sig_bytes):
                                    f.write(file_data[len(sig_bytes):])

                            messagebox.showinfo(
                                "Success",
                                f"File has been spoofed and saved as:\n{save_path}",
                                parent=spoof_dialog
                            )

                            # Ask if the user wants to load the spoofed file
                            if messagebox.askyesno(
                                    "Open Spoofed File",
                                    "Would you like to open the spoofed file?",
                                    parent=spoof_dialog
                            ):
                                spoof_dialog.destroy()
                                self.current_file = save_path
                                self.file_path_var.set(save_path)
                                self.set_image(save_path)
                                self.status_var.set(f"Loaded spoofed file: {os.path.basename(save_path)}")
                                self.check_metadata()

                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to spoof file: {str(e)}", parent=spoof_dialog)

                return spoof

            spoof_button = tk.Button(
                table_frame,
                text="Apply",
                command=create_spoof_function(signature),
                font=("Arial", 8),
                bg=self.colors["button_bg"],
                fg=self.colors["button_fg"]
            )
            spoof_button.grid(row=i, column=3, sticky="nsew", padx=1, pady=1)

        # Configure grid
        table_frame.grid_columnconfigure(0, weight=2)
        table_frame.grid_columnconfigure(1, weight=1)
        table_frame.grid_columnconfigure(2, weight=3)
        table_frame.grid_columnconfigure(3, weight=1)

        # Custom signature input
        custom_frame = tk.Frame(spoof_dialog, bg=self.colors["bg_color"])
        custom_frame.pack(fill=tk.X, padx=10, pady=10)

        custom_label = tk.Label(
            custom_frame,
            text="Custom Signature (Hex):",
            font=("Arial", 10),
            bg=self.colors["bg_color"],
            fg=self.colors["fg_color"]
        )
        custom_label.pack(side=tk.LEFT)

        custom_var = tk.StringVar()
        custom_entry = tk.Entry(
            custom_frame,
            textvariable=custom_var,
            width=30,
            font=("Courier New", 10),
            bg=self.colors["text_area_bg"],
            fg=self.colors["text_area_fg"]
        )
        custom_entry.pack(side=tk.LEFT, padx=5)

        def apply_custom():
            custom_hex = custom_var.get().strip()
            if not custom_hex:
                messagebox.showwarning("Empty Input", "Please enter a hex signature", parent=spoof_dialog)
                return

            try:
                # Convert to bytes to validate
                bytes.fromhex(custom_hex.replace(" ", ""))

                # Create a spoofing function and call it
                spoof_func = create_spoof_function(custom_hex)
                spoof_func()

            except ValueError:
                messagebox.showerror("Invalid Hex", "Please enter valid hexadecimal values", parent=spoof_dialog)

        custom_button = tk.Button(
            custom_frame,
            text="Apply Custom",
            command=apply_custom,
            font=("Arial", 9),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"]
        )
        custom_button.pack(side=tk.LEFT, padx=5)

        # Close button
        close_frame = tk.Frame(spoof_dialog, bg=self.colors["bg_color"])
        close_frame.pack(fill=tk.X, padx=10, pady=10)

        close_button = tk.Button(
            close_frame,
            text="Close",
            command=spoof_dialog.destroy,
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            padx=10,
            pady=5
        )
        close_button.pack()

    def show_about(self):
        """Show about dialog"""
        about_text = f"{APP_NAME} v{APP_VERSION}\n\n"
        about_text += "A powerful digital forensics toolkit for analyzing and manipulating file metadata.\n\n"
        about_text += "Features:\n"
        about_text += "- Extract detailed metadata from various file types\n"
        about_text += "- Advanced file analysis with entropy detection and suspicious string highlighting\n"
        about_text += "- Analyze PDF files for hidden content or malicious code\n"
        about_text += "- Inject JavaScript into PDF files for forensic testing\n"
        about_text += "- Spoof file types by changing file signatures\n"
        about_text += "- Create fake metadata for images\n"
        about_text += "- Compare metadata between files\n"
        about_text += "- Visualize metadata with charts\n"
        about_text += "- Light and dark theme support\n\n"
        about_text += "For educational and forensic research purposes only."

        messagebox.showinfo("About", about_text)


if __name__ == "__main__":
    root = tk.Tk()
    app = DigitalForensicsToolkit(root)
    root.mainloop()