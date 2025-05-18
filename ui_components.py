import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import file_utils
from visualizers import MetadataVisualizer, ComparisonVisualizer
from constants import LIGHT_THEME, DARK_THEME, EXPORT_FORMATS, FILE_TYPES


class Header(tk.Frame):

    def __init__(self, parent, app_name, theme_callback):
        try:
            self.theme = parent.theme
        except AttributeError:

            self.theme = "light"
        colors = LIGHT_THEME if self.theme == "light" else DARK_THEME

        super().__init__(parent, bg=colors["bg_color"])
        self.pack(fill=tk.X, padx=10, pady=10)


        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)


        title_label = tk.Label(
            self,
            text=app_name,
            font=("Arial", 24, "bold"),
            bg=colors["bg_color"],
            fg=colors["fg_color"],
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w")

        theme_text = "🌙 Dark" if self.theme == "light" else "☀️ Light"
        self.theme_button = tk.Button(
            self,
            text=theme_text,
            command=theme_callback,
            font=("Arial", 10),
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            padx=10
        )
        self.theme_button.grid(row=0, column=1, sticky="e")

    def update_theme(self, theme):
        self.theme = theme
        colors = LIGHT_THEME if theme == "light" else DARK_THEME


        self.configure(bg=colors["bg_color"])


        for child in self.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg=colors["bg_color"], fg=colors["fg_color"])
            elif isinstance(child, tk.Button):
                child.configure(bg=colors["button_bg"], fg=colors["button_fg"])


        theme_text = "🌙 Dark" if theme == "light" else "☀️ Light"
        self.theme_button.configure(text=theme_text)


class FileUploadPanel(tk.Frame):

    def __init__(self, parent, upload_callback, batch_callback):
        try:
            self.theme = parent.theme
        except AttributeError:

            self.theme = "light"
        colors = LIGHT_THEME if self.theme == "light" else DARK_THEME

        super().__init__(parent, bg=colors["bg_color"])
        self.pack(fill=tk.X, padx=10, pady=10)

        self.upload_callback = upload_callback
        self.batch_callback = batch_callback


        upload_frame = tk.Frame(self, bg=colors["bg_color"])
        upload_frame.pack(fill=tk.X)


        upload_button = tk.Button(
            upload_frame,
            text="Upload File",
            command=self.upload_file,
            font=("Arial", 12),
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            padx=10,
            pady=5
        )
        upload_button.grid(row=0, column=0, padx=5)


        batch_button = tk.Button(
            upload_frame,
            text="Batch Process",
            command=self.upload_batch,
            font=("Arial", 12),
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            padx=10,
            pady=5
        )
        batch_button.grid(row=0, column=1, padx=5)


        filter_label = tk.Label(
            upload_frame,
            text="File Type:",
            bg=colors["bg_color"],
            fg=colors["fg_color"],
            font=("Arial", 12)
        )
        filter_label.grid(row=0, column=2, padx=(20, 5))

        self.file_type_var = tk.StringVar(value="All Files")
        file_types = ["All Files"] + list(FILE_TYPES.keys())

        file_type_dropdown = ttk.Combobox(
            upload_frame,
            textvariable=self.file_type_var,
            values=file_types,
            state="readonly",
            width=15,
            font=("Arial", 11)
        )
        file_type_dropdown.grid(row=0, column=3, padx=5)


        self.file_path_var = tk.StringVar(value="No file selected")
        file_path_label = tk.Label(
            self,
            textvariable=self.file_path_var,
            bg=colors["secondary_bg"],
            fg=colors["fg_color"],
            font=("Arial", 10),
            anchor="w",
            padx=10,
            pady=5,
            relief=tk.GROOVE
        )
        file_path_label.pack(fill=tk.X, pady=(10, 0))

    def upload_file(self):
        file_type = self.file_type_var.get()

        if file_type == "All Files":
            filetypes = [("All Files", "*.*")]
        else:
            extensions = FILE_TYPES.get(file_type, [])
            if extensions:
                filetypes = [(file_type, " ".join(extensions))]
            else:
                filetypes = [("All Files", "*.*")]

        file_path = filedialog.askopenfilename(
            title="Select a File",
            filetypes=filetypes
        )

        if file_path:
            self.file_path_var.set(file_path)
            self.upload_callback(file_path)

    def upload_batch(self):
        file_type = self.file_type_var.get()

        if file_type == "All Files":
            filetypes = [("All Files", "*.*")]
        else:
            extensions = FILE_TYPES.get(file_type, [])
            if extensions:
                filetypes = [(file_type, " ".join(extensions))]
            else:
                filetypes = [("All Files", "*.*")]

        file_paths = filedialog.askopenfilenames(
            title="Select Files for Batch Processing",
            filetypes=filetypes
        )

        if file_paths:
            self.file_path_var.set(f"Selected {len(file_paths)} files for batch processing")
            self.batch_callback(file_paths)

    def update_theme(self, theme):
        self.theme = theme
        colors = LIGHT_THEME if theme == "light" else DARK_THEME


        self.configure(bg=colors["bg_color"])


        for child in self.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=colors["bg_color"])
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Label):
                        subchild.configure(bg=colors["bg_color"], fg=colors["fg_color"])
                    elif isinstance(subchild, tk.Button):
                        subchild.configure(bg=colors["button_bg"], fg=colors["button_fg"])
            elif isinstance(child, tk.Label):
                if "file_path_label" in str(child):
                    child.configure(bg=colors["secondary_bg"], fg=colors["fg_color"])
                else:
                    child.configure(bg=colors["bg_color"], fg=colors["fg_color"])


class ImagePreviewPanel(tk.Frame):

    def __init__(self, parent):
        try:
            self.theme = parent.theme
        except AttributeError:

            self.theme = "light"
        colors = LIGHT_THEME if self.theme == "light" else DARK_THEME

        super().__init__(parent, bg=colors["bg_color"])
        self.pack(fill=tk.X, padx=10, pady=5)


        self.title_label = tk.Label(
            self,
            text="File Preview",
            font=("Arial", 14, "bold"),
            bg=colors["bg_color"],
            fg=colors["fg_color"]
        )
        self.title_label.pack(anchor="w", pady=(0, 5))


        self.preview_frame = tk.Frame(
            self,
            bg=colors["secondary_bg"],
            width=300,
            height=300,
            relief=tk.GROOVE,
            bd=1
        )
        self.preview_frame.pack(pady=5)
        self.preview_frame.pack_propagate(False)


        self.preview_label = tk.Label(
            self.preview_frame,
            text="No preview available",
            bg=colors["secondary_bg"],
            fg=colors["fg_color"],
            font=("Arial", 10)
        )
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        self.image_reference = None

    def set_image(self, image_path):
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        if image_path and os.path.exists(image_path):
            try:
                from PIL import Image, ImageTk


                if file_utils.get_file_type_category(image_path) == "Images":
                    img = Image.open(image_path)
                    img = img.resize((280, 280), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)

                    self.preview_label = tk.Label(
                        self.preview_frame,
                        image=img_tk,
                        bg=self.preview_frame["bg"]
                    )
                    self.preview_label.image = img_tk
                    self.preview_label.pack(fill=tk.BOTH, expand=True)
                    self.image_reference = img_tk
                else:
                    file_type = file_utils.get_file_type_category(image_path)
                    self.preview_label = tk.Label(
                        self.preview_frame,
                        text=f"{file_type} File\n\n{os.path.basename(image_path)}",
                        bg=self.preview_frame["bg"],
                        fg=LIGHT_THEME["fg_color"] if self.theme == "light" else DARK_THEME["fg_color"],
                        font=("Arial", 12)
                    )
                    self.preview_label.pack(fill=tk.BOTH, expand=True)
            except Exception as e:
                self.preview_label = tk.Label(
                    self.preview_frame,
                    text=f"Preview error:\n{str(e)}",
                    bg=self.preview_frame["bg"],
                    fg=LIGHT_THEME["fg_color"] if self.theme == "light" else DARK_THEME["fg_color"],
                    font=("Arial", 10)
                )
                self.preview_label.pack(fill=tk.BOTH, expand=True)
        else:
            self.preview_label = tk.Label(
                self.preview_frame,
                text="No preview available",
                bg=self.preview_frame["bg"],
                fg=LIGHT_THEME["fg_color"] if self.theme == "light" else DARK_THEME["fg_color"],
                font=("Arial", 10)
            )
            self.preview_label.pack(fill=tk.BOTH, expand=True)

    def clear(self):
        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        self.preview_label = tk.Label(
            self.preview_frame,
            text="No preview available",
            bg=self.preview_frame["bg"],
            fg=LIGHT_THEME["fg_color"] if self.theme == "light" else DARK_THEME["fg_color"],
            font=("Arial", 10)
        )
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        self.image_reference = None

    def update_theme(self, theme):
        self.theme = theme
        colors = LIGHT_THEME if theme == "light" else DARK_THEME

        self.configure(bg=colors["bg_color"])
        self.title_label.configure(bg=colors["bg_color"], fg=colors["fg_color"])
        self.preview_frame.configure(bg=colors["secondary_bg"])

        for widget in self.preview_frame.winfo_children():
            if isinstance(widget, tk.Label) and not widget.image:
                widget.configure(bg=colors["secondary_bg"], fg=colors["fg_color"])


class MetadataDisplayPanel(tk.Frame):

    def __init__(self, parent):
        try:
            self.theme = parent.theme
        except AttributeError:
            self.theme = "light"
        colors = LIGHT_THEME if self.theme == "light" else DARK_THEME

        super().__init__(parent, bg=colors["bg_color"])
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        header_frame = tk.Frame(self, bg=colors["bg_color"])
        header_frame.pack(fill=tk.X)

        title_label = tk.Label(
            header_frame,
            text="Metadata Results",
            font=("Arial", 14, "bold"),
            bg=colors["bg_color"],
            fg=colors["fg_color"]
        )
        title_label.pack(side=tk.LEFT, anchor="w")

        search_frame = tk.Frame(header_frame, bg=colors["bg_color"])
        search_frame.pack(side=tk.RIGHT)

        search_label = tk.Label(
            search_frame,
            text="Search:",
            bg=colors["bg_color"],
            fg=colors["fg_color"],
            font=("Arial", 10)
        )
        search_label.pack(side=tk.LEFT, padx=5)

        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search)

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=20,
            font=("Arial", 10),
            bg=colors["text_area_bg"],
            fg=colors["text_area_fg"],
        )
        search_entry.pack(side=tk.LEFT)

        self.metadata_display = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg=colors["text_area_bg"],
            fg=colors["text_area_fg"],
            insertbackground=colors["fg_color"]
        )
        self.metadata_display.pack(fill=tk.BOTH, expand=True, pady=5)
        self.metadata_display.config(state="disabled")

        self.original_metadata = {}

    def display_metadata(self, metadata):
        self.original_metadata = metadata
        self._update_display(metadata)

    def _update_display(self, metadata):
        self.metadata_display.config(state="normal")
        self.metadata_display.delete(1.0, tk.END)

        if isinstance(metadata, dict):
            for key, value in sorted(metadata.items()):
                if key == 'GPS Coordinates' and value and isinstance(value, str) and ',' in value:
                    lat, lon = value.split(',')
                    lat, lon = lat.strip(), lon.strip()
                    self.metadata_display.insert(tk.END, f"{key}: https://www.google.com/maps?q={lat},{lon}\n")
                else:
                    self.metadata_display.insert(tk.END, f"{key}: {value}\n")
        else:
            self.metadata_display.insert(tk.END, "No metadata available.")

        self.metadata_display.config(state="disabled")

    def _on_search(self, *args):
        if not self.original_metadata:
            return

        search_query = self.search_var.get().lower()

        if not search_query:
            self._update_display(self.original_metadata)
            return

        filtered_metadata = {}
        for key, value in self.original_metadata.items():
            if (search_query in key.lower() or
                    (isinstance(value, str) and search_query in value.lower())):
                filtered_metadata[key] = value

        self._update_display(filtered_metadata)

    def clear(self):
        self.metadata_display.config(state="normal")
        self.metadata_display.delete(1.0, tk.END)
        self.metadata_display.config(state="disabled")
        self.original_metadata = {}

    def update_theme(self, theme):
        self.theme = theme
        colors = LIGHT_THEME if theme == "light" else DARK_THEME

        self.configure(bg=colors["bg_color"])

        for child in self.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=colors["bg_color"])
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Label):
                        subchild.configure(bg=colors["bg_color"], fg=colors["fg_color"])
                    elif isinstance(subchild, tk.Entry):
                        subchild.configure(bg=colors["text_area_bg"], fg=colors["text_area_fg"])

        self.metadata_display.configure(
            bg=colors["text_area_bg"],
            fg=colors["text_area_fg"],
            insertbackground=colors["fg_color"]
        )


class ActionButtonsPanel(tk.Frame):

    def __init__(self, parent, check_callback, remove_callback, save_callback, compare_callback, visualize_callback):
        try:
            self.theme = parent.theme
        except AttributeError:
            self.theme = "light"
        colors = LIGHT_THEME if self.theme == "light" else DARK_THEME

        super().__init__(parent, bg=colors["bg_color"])
        self.pack(fill=tk.X, padx=10, pady=10)

        self.check_button = tk.Button(
            self,
            text="Check Metadata",
            command=check_callback,
            font=("Arial", 12),
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            padx=10,
            pady=5
        )
        self.check_button.pack(side=tk.LEFT, padx=5)

        self.remove_button = tk.Button(
            self,
            text="Remove Metadata",
            command=remove_callback,
            font=("Arial", 12),
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            padx=10,
            pady=5
        )
        self.remove_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(
            self,
            text="Save Metadata",
            command=save_callback,
            font=("Arial", 12),
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            padx=10,
            pady=5
        )
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.compare_button = tk.Button(
            self,
            text="Compare Files",
            command=compare_callback,
            font=("Arial", 12),
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            padx=10,
            pady=5
        )
        self.compare_button.pack(side=tk.LEFT, padx=5)

        self.visualize_button = tk.Button(
            self,
            text="Visualize Data",
            command=visualize_callback,
            font=("Arial", 12),
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            padx=10,
            pady=5
        )
        self.visualize_button.pack(side=tk.LEFT, padx=5)

    def update_theme(self, theme):
        self.theme = theme
        colors = LIGHT_THEME if theme == "light" else DARK_THEME

        self.configure(bg=colors["bg_color"])

        for child in self.winfo_children():
            if isinstance(child, tk.Button):
                child.configure(bg=colors["button_bg"], fg=colors["button_fg"])


class StatusBar(tk.Frame):

    def __init__(self, parent):
        try:
            self.theme = parent.theme
        except AttributeError:
            self.theme = "light"
        colors = LIGHT_THEME if self.theme == "light" else DARK_THEME

        super().__init__(parent, bg=colors["secondary_bg"])
        self.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(
            self,
            textvariable=self.status_var,
            bg=colors["secondary_bg"],
            fg=colors["fg_color"],
            font=("Arial", 10),
            anchor="w",
            padx=10,
            pady=5
        )
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(side=tk.RIGHT, padx=10, pady=5)

    def set_status(self, message):
        self.status_var.set(message)

    def set_progress(self, value):
        self.progress["value"] = value

    def start_progress(self):
        self.progress["mode"] = "indeterminate"
        self.progress.start()

    def stop_progress(self):
        if self.progress["mode"] == "indeterminate":
            self.progress.stop()
        self.progress["mode"] = "determinate"
        self.progress["value"] = 0

    def update_theme(self, theme):
        self.theme = theme
        colors = LIGHT_THEME if theme == "light" else DARK_THEME

        self.configure(bg=colors["secondary_bg"])

        for child in self.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(bg=colors["secondary_bg"], fg=colors["fg_color"])


class BatchProcessingDialog(tk.Toplevel):

    def __init__(self, parent, file_paths, process_callback):
        try:
            self.theme = parent.theme
        except AttributeError:
            self.theme = "light"
        colors = LIGHT_THEME if self.theme == "light" else DARK_THEME

        super().__init__(parent)
        self.title("Batch Processing")
        self.geometry("600x500")
        self.configure(bg=colors["bg_color"])

        self.file_paths = file_paths
        self.process_callback = process_callback

        self.transient(parent)
        self.grab_set()

        self._create_ui(colors)

    def _create_ui(self, colors):
        title_label = tk.Label(
            self,
            text="Batch Processing",
            font=("Arial", 16, "bold"),
            bg=colors["bg_color"],
            fg=colors["fg_color"],
            pady=10
        )
        title_label.pack(fill=tk.X)

        files_label = tk.Label(
            self,
            text=f"Selected {len(self.file_paths)} files for processing",
            font=("Arial", 12),
            bg=colors["bg_color"],
            fg=colors["fg_color"],
            pady=5
        )
        files_label.pack(fill=tk.X)

        files_frame = tk.Frame(self, bg=colors["bg_color"])
        files_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.files_listbox = tk.Listbox(
            files_frame,
            bg=colors["text_area_bg"],
            fg=colors["text_area_fg"],
            font=("Arial", 10),
            selectbackground=colors["accent_color"],
            selectforeground="white",
            relief=tk.SUNKEN,
            bd=1,
            highlightthickness=0
        )
        files_scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.files_listbox.yview)
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)

        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for path in self.file_paths:
            self.files_listbox.insert(tk.END, os.path.basename(path))

        options_frame = tk.Frame(self, bg=colors["bg_color"], pady=10)
        options_frame.pack(fill=tk.X, padx=10)

        self.calc_checksums_var = tk.BooleanVar(value=True)
        checksums_check = tk.Checkbutton(
            options_frame,
            text="Calculate Checksums (MD5, SHA1, SHA256)",
            variable=self.calc_checksums_var,
            bg=colors["bg_color"],
            fg=colors["fg_color"],
            selectcolor=colors["secondary_bg"],
            font=("Arial", 10)
        )
        checksums_check.pack(anchor="w")

        progress_frame = tk.Frame(self, bg=colors["bg_color"], pady=10)
        progress_frame.pack(fill=tk.X, padx=10)

        self.progress_var = tk.StringVar(value="Ready to process")
        progress_label = tk.Label(
            progress_frame,
            textvariable=self.progress_var,
            bg=colors["bg_color"],
            fg=colors["fg_color"],
            font=("Arial", 10)
        )
        progress_label.pack(fill=tk.X)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient=tk.HORIZONTAL,
            length=580,
            mode="determinate"
        )
        self.progress_bar.pack(fill=tk.X, pady=5)

        buttons_frame = tk.Frame(self, bg=colors["bg_color"], pady=10)
        buttons_frame.pack(fill=tk.X, padx=10)

        process_button = tk.Button(
            buttons_frame,
            text="Start Processing",
            command=self._start_processing,
            font=("Arial", 12),
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            padx=10,
            pady=5
        )
        process_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(
            buttons_frame,
            text="Cancel",
            command=self.destroy,
            font=("Arial", 12),
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            padx=10,
            pady=5
        )
        cancel_button.pack(side=tk.LEFT, padx=5)

    def _start_processing(self):
        calc_checksums = self.calc_checksums_var.get()
        self.process_callback(self.file_paths, calc_checksums, self._update_progress)

    def _update_progress(self, progress, current, total, finished=False):
        self.progress_bar["value"] = progress
        self.progress_var.set(f"Processing {current}/{total} files ({progress:.1f}%)")

        if current <= len(self.file_paths):
            self.files_listbox.itemconfig(current - 1, {'bg': '#e6ffe6'})

        if finished:
            self.progress_var.set(f"Completed processing {total} files")
            messagebox.showinfo("Batch Processing", f"Successfully processed {total} files")
            self.destroy()


class ComparisonDialog(tk.Toplevel):

    def __init__(self, parent, compare_callback):
        try:
            self.theme = parent.theme
        except AttributeError:
            self.theme = "light"
        colors = LIGHT_THEME if self.theme == "light" else DARK_THEME

        super().__init__(parent)
        self.title("Compare Files")
        self.geometry("600x300")
        self.configure(bg=colors["bg_color"])

        self.compare_callback = compare_callback
        self.file1_path = None
        self.file2_path = None

        self.transient(parent)
        self.grab_set()

        self._create_ui(colors)

    def _create_ui(self, colors):
        title_label = tk.Label(
            self,
            text="Compare Metadata Between Files",
            font=("Arial", 16, "bold"),
            bg=colors["bg_color"],
            fg=colors["fg_color"],
            pady=10
        )
        title_label.pack(fill=tk.X)

        selection_frame = tk.Frame(self, bg=colors["bg_color"])
        selection_frame.pack(fill=tk.X, padx=20, pady=10)

        file1_frame = tk.Frame(selection_frame, bg=colors["bg_color"])
        file1_frame.pack(fill=tk.X, pady=5)

        file1_label = tk.Label(
            file1_frame,
            text="File 1:",
            bg=colors["bg_color"],
            fg=colors["fg_color"],
            font=("Arial", 11),
            width=8,
            anchor="w"
        )
        file1_label.pack(side=tk.LEFT)

        self.file1_var = tk.StringVar(value="No file selected")
        file1_path = tk.Label(
            file1_frame,
            textvariable=self.file1_var,
            bg=colors["secondary_bg"],
            fg=colors["fg_color"],
            font=("Arial", 10),
            anchor="w",
            padx=5,
            pady=2,
            relief=tk.GROOVE,
            width=40
        )
        file1_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        file1_button = tk.Button(
            file1_frame,
            text="Browse",
            command=self._select_file1,
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            font=("Arial", 10)
        )
        file1_button.pack(side=tk.LEFT)

        file2_frame = tk.Frame(selection_frame, bg=colors["bg_color"])
        file2_frame.pack(fill=tk.X, pady=5)

        file2_label = tk.Label(
            file2_frame,
            text="File 2:",
            bg=colors["bg_color"],
            fg=colors["fg_color"],
            font=("Arial", 11),
            width=8,
            anchor="w"
        )
        file2_label.pack(side=tk.LEFT)

        self.file2_var = tk.StringVar(value="No file selected")
        file2_path = tk.Label(
            file2_frame,
            textvariable=self.file2_var,
            bg=colors["secondary_bg"],
            fg=colors["fg_color"],
            font=("Arial", 10),
            anchor="w",
            padx=5,
            pady=2,
            relief=tk.GROOVE,
            width=40
        )
        file2_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        file2_button = tk.Button(
            file2_frame,
            text="Browse",
            command=self._select_file2,
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            font=("Arial", 10)
        )
        file2_button.pack(side=tk.LEFT)

        info_text = """
Select two files to compare their metadata. 
The comparison will show differences, similarities, and unique fields between the files.
        """
        info_label = tk.Label(
            self,
            text=info_text,
            bg=colors["bg_color"],
            fg=colors["fg_color"],
            font=("Arial", 10),
            justify=tk.LEFT,
            wraplength=550
        )
        info_label.pack(padx=20, pady=10, anchor="w")


        buttons_frame = tk.Frame(self, bg=colors["bg_color"], pady=10)
        buttons_frame.pack(fill=tk.X, padx=20)


        self.compare_button = tk.Button(
            buttons_frame,
            text="Compare Files",
            command=self._compare_files,
            font=("Arial", 12),
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            padx=10,
            pady=5,
            state=tk.DISABLED
        )
        self.compare_button.pack(side=tk.LEFT, padx=5)


        cancel_button = tk.Button(
            buttons_frame,
            text="Cancel",
            command=self.destroy,
            font=("Arial", 12),
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            padx=10,
            pady=5
        )
        cancel_button.pack(side=tk.LEFT, padx=5)

    def _select_file1(self):
        file_path = filedialog.askopenfilename(
            title="Select First File for Comparison",
            filetypes=[("All Files", "*.*")]
        )

        if file_path:
            self.file1_path = file_path
            self.file1_var.set(os.path.basename(file_path))
            self._check_files()

    def _select_file2(self):
        file_path = filedialog.askopenfilename(
            title="Select Second File for Comparison",
            filetypes=[("All Files", "*.*")]
        )

        if file_path:
            self.file2_path = file_path
            self.file2_var.set(os.path.basename(file_path))
            self._check_files()

    def _check_files(self):
        if self.file1_path and self.file2_path:
            self.compare_button.config(state=tk.NORMAL)
        else:
            self.compare_button.config(state=tk.DISABLED)

    def _compare_files(self):
        if self.file1_path and self.file2_path:
            self.compare_callback(self.file1_path, self.file2_path)
            self.destroy()


class VisualizationDialog(tk.Toplevel):

    def __init__(self, parent, metadata, visualize_callback):
        try:
            self.theme = parent.theme
        except AttributeError:
            self.theme = "light"
        colors = LIGHT_THEME if self.theme == "light" else DARK_THEME

        super().__init__(parent)
        self.title("Visualize Metadata")
        self.geometry("400x300")
        self.configure(bg=colors["bg_color"])

        self.metadata = metadata
        self.visualize_callback = visualize_callback

        self.transient(parent)
        self.grab_set()

        self._create_ui(colors)

    def _create_ui(self, colors):
        title_label = tk.Label(
            self,
            text="Select Visualization Type",
            font=("Arial", 16, "bold"),
            bg=colors["bg_color"],
            fg=colors["fg_color"],
            pady=10
        )
        title_label.pack(fill=tk.X)

        info_text = "Choose how you want to visualize your metadata:"
        info_label = tk.Label(
            self,
            text=info_text,
            bg=colors["bg_color"],
            fg=colors["fg_color"],
            font=("Arial", 11),
            pady=5
        )
        info_label.pack(fill=tk.X, padx=20)

        options_frame = tk.Frame(self, bg=colors["bg_color"])
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        try:
            import matplotlib
            has_matplotlib = True
        except ImportError:
            has_matplotlib = False

        if has_matplotlib:

            type_button = tk.Button(
                options_frame,
                text="File Type Distribution",
                command=lambda: self._select_visualization("file_type"),
                font=("Arial", 11),
                bg=colors["button_bg"],
                fg=colors["button_fg"],
                padx=10,
                pady=5,
                width=25,
                anchor="w"
            )
            type_button.pack(fill=tk.X, pady=5)


            size_button = tk.Button(
                options_frame,
                text="File Size Comparison",
                command=lambda: self._select_visualization("file_size"),
                font=("Arial", 11),
                bg=colors["button_bg"],
                fg=colors["button_fg"],
                padx=10,
                pady=5,
                width=25,
                anchor="w"
            )
            size_button.pack(fill=tk.X, pady=5)


            heatmap_button = tk.Button(
                options_frame,
                text="Metadata Availability Heatmap",
                command=lambda: self._select_visualization("heatmap"),
                font=("Arial", 11),
                bg=colors["button_bg"],
                fg=colors["button_fg"],
                padx=10,
                pady=5,
                width=25,
                anchor="w"
            )
            heatmap_button.pack(fill=tk.X, pady=5)


            timeline_button = tk.Button(
                options_frame,
                text="File Timeline View",
                command=lambda: self._select_visualization("timeline"),
                font=("Arial", 11),
                bg=colors["button_bg"],
                fg=colors["button_fg"],
                padx=10,
                pady=5,
                width=25,
                anchor="w"
            )
            timeline_button.pack(fill=tk.X, pady=5)
        else:

            no_viz_label = tk.Label(
                options_frame,
                text="Matplotlib library is not available.\nVisualization features require matplotlib.",
                bg=colors["bg_color"],
                fg=colors["fg_color"],
                font=("Arial", 11),
                pady=20
            )
            no_viz_label.pack(fill=tk.BOTH, expand=True)


        cancel_button = tk.Button(
            self,
            text="Cancel",
            command=self.destroy,
            font=("Arial", 11),
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            padx=10,
            pady=5
        )
        cancel_button.pack(pady=10)

    def _select_visualization(self, viz_type):
        self.visualize_callback(viz_type, self.metadata)
        self.destroy()


class ExportDialog(tk.Toplevel):

    def __init__(self, parent, metadata, export_callback):
        try:
            self.theme = parent.theme
        except AttributeError:
            self.theme = "light"
        colors = LIGHT_THEME if self.theme == "light" else DARK_THEME

        super().__init__(parent)
        self.title("Export Metadata")
        self.geometry("400x300")
        self.configure(bg=colors["bg_color"])

        self.metadata = metadata
        self.export_callback = export_callback

        self.transient(parent)
        self.grab_set()

        self._create_ui(colors)

    def _create_ui(self, colors):

        title_label = tk.Label(
            self,
            text="Export Metadata",
            font=("Arial", 16, "bold"),
            bg=colors["bg_color"],
            fg=colors["fg_color"],
            pady=10
        )
        title_label.pack(fill=tk.X)

        options_frame = tk.Frame(self, bg=colors["bg_color"])
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        format_label = tk.Label(
            options_frame,
            text="Select Export Format:",
            bg=colors["bg_color"],
            fg=colors["fg_color"],
            font=("Arial", 11),
            anchor="w"
        )
        format_label.pack(fill=tk.X, pady=(0, 5))

        self.format_var = tk.StringVar(value=".json")

        for name, ext in EXPORT_FORMATS.items():
            format_radio = tk.Radiobutton(
                options_frame,
                text=name,
                variable=self.format_var,
                value=ext,
                bg=colors["bg_color"],
                fg=colors["fg_color"],
                selectcolor=colors["secondary_bg"],
                font=("Arial", 10)
            )
            format_radio.pack(anchor="w", pady=2)

        options_label = tk.Label(
            options_frame,
            text="Export Options:",
            bg=colors["bg_color"],
            fg=colors["fg_color"],
            font=("Arial", 11),
            anchor="w",
            pady=(10, 5)
        )
        options_label.pack(fill=tk.X)

        self.timestamp_var = tk.BooleanVar(value=True)
        timestamp_check = tk.Checkbutton(
            options_frame,
            text="Include timestamp in filename",
            variable=self.timestamp_var,
            bg=colors["bg_color"],
            fg=colors["fg_color"],
            selectcolor=colors["secondary_bg"],
            font=("Arial", 10)
        )
        timestamp_check.pack(anchor="w", pady=2)

        buttons_frame = tk.Frame(self, bg=colors["bg_color"], pady=10)
        buttons_frame.pack(fill=tk.X, padx=20)

        export_button = tk.Button(
            buttons_frame,
            text="Export",
            command=self._export_metadata,
            font=("Arial", 12),
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            padx=10,
            pady=5
        )
        export_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(
            buttons_frame,
            text="Cancel",
            command=self.destroy,
            font=("Arial", 12),
            bg=colors["button_bg"],
            fg=colors["button_fg"],
            padx=10,
            pady=5
        )
        cancel_button.pack(side=tk.LEFT, padx=5)

    def _export_metadata(self):
        format_type = self.format_var.get()
        include_timestamp = self.timestamp_var.get()

        if isinstance(self.metadata, dict):
            file_name = self.metadata.get('File Name', 'metadata')
            base_name = os.path.splitext(file_name)[0]
        else:
            base_name = "batch_metadata"

        if include_timestamp:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"{base_name}_{timestamp}"

        base_name = os.path.splitext(base_name)[0]

        suggested_name = f"{base_name}{format_type}"

        file_path = filedialog.asksaveasfilename(
            title="Save Metadata",
            initialfile=suggested_name,
            defaultextension=format_type,
            filetypes=[(f"{ext.upper()[1:]} File", f"*{ext}") for ext in EXPORT_FORMATS.values()]
        )

        if file_path:
            self.export_callback(file_path, format_type)
            self.destroy()
