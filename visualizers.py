import tkinter as tk
from tkinter import ttk
import os

try:
    import matplotlib

    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class MetadataVisualizer:

    def __init__(self, parent_frame, bg_color):
        self.parent = parent_frame
        self.bg_color = bg_color
        self.frame = tk.Frame(parent_frame, bg=bg_color)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.current_data = None
        self.current_view = None


        self.placeholder = tk.Label(
            self.frame,
            text="Select files and extract metadata to visualize",
            bg=bg_color,
            font=("Arial", 12)
        )
        self.placeholder.pack(pady=50)

    def clear(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def show_file_type_distribution(self, metadata_dict):
        self.current_data = metadata_dict
        self.current_view = "file_type"
        self.clear()

        if not HAS_MATPLOTLIB:
            lbl = tk.Label(
                self.frame,
                text="Matplotlib not available. Cannot create visualization.",
                bg=self.bg_color,
                font=("Arial", 12)
            )
            lbl.pack(pady=50)
            return


        file_types = {}
        for filepath, metadata in metadata_dict.items():
            file_type = metadata.get('File Type Category', 'Unknown')
            file_types[file_type] = file_types.get(file_type, 0) + 1

        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)


        labels = list(file_types.keys())
        values = list(file_types.values())

        if not values:
            lbl = tk.Label(
                self.frame,
                text="No data available for visualization",
                bg=self.bg_color,
                font=("Arial", 12)
            )
            lbl.pack(pady=50)
            return

        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')

        ax.set_title('File Type Distribution')

        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def show_file_size_comparison(self, metadata_dict):
        self.current_data = metadata_dict
        self.current_view = "file_size"
        self.clear()

        if not HAS_MATPLOTLIB:
            lbl = tk.Label(
                self.frame,
                text="Matplotlib not available. Cannot create visualization.",
                bg=self.bg_color,
                font=("Arial", 12)
            )
            lbl.pack(pady=50)
            return


        file_names = []
        file_sizes = []

        for filepath, metadata in metadata_dict.items():
            file_name = os.path.basename(filepath)
            file_size = metadata.get('File Size', 0)


            if len(file_names) < 10:
                file_names.append(file_name)
                file_sizes.append(file_size)

        if not file_sizes:
            lbl = tk.Label(
                self.frame,
                text="No data available for visualization",
                bg=self.bg_color,
                font=("Arial", 12)
            )
            lbl.pack(pady=50)
            return


        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)


        y_pos = range(len(file_names))
        ax.barh(y_pos, file_sizes)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(file_names)
        ax.invert_yaxis()
        ax.set_xlabel('File Size (bytes)')
        ax.set_title('File Size Comparison')


        ax.ticklabel_format(style='plain', axis='x')


        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def show_metadata_heatmap(self, metadata_dict):
        self.current_data = metadata_dict
        self.current_view = "heatmap"
        self.clear()

        if not HAS_MATPLOTLIB:
            lbl = tk.Label(
                self.frame,
                text="Matplotlib not available. Cannot create visualization.",
                bg=self.bg_color,
                font=("Arial", 12)
            )
            lbl.pack(pady=50)
            return


        all_keys = set()
        file_names = []

        for filepath, metadata in metadata_dict.items():
            file_name = os.path.basename(filepath)
            file_names.append(file_name)

            for key in metadata.keys():
                all_keys.add(key)


        key_count = {}
        for filepath, metadata in metadata_dict.items():
            for key in metadata.keys():
                key_count[key] = key_count.get(key, 0) + 1


        sorted_keys = sorted(key_count.items(), key=lambda x: x[1], reverse=True)
        top_keys = [k for k, v in sorted_keys[:10]]


        if len(file_names) > 8:
            file_names = file_names[:8]

        if not file_names or not top_keys:
            lbl = tk.Label(
                self.frame,
                text="No data available for visualization",
                bg=self.bg_color,
                font=("Arial", 12)
            )
            lbl.pack(pady=50)
            return


        import numpy as np
        data = np.zeros((len(file_names), len(top_keys)))


        for i, filepath in enumerate(list(metadata_dict.keys())[:len(file_names)]):
            metadata = metadata_dict[filepath]
            for j, key in enumerate(top_keys):
                data[i, j] = 1 if key in metadata and metadata[key] != "Not Available" else 0


        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)


        heatmap = ax.pcolor(data, cmap='YlGn')


        ax.set_yticks(np.arange(data.shape[0]) + 0.5)
        ax.set_xticks(np.arange(data.shape[1]) + 0.5)
        ax.set_yticklabels(file_names)


        shortened_keys = [k[-20:] if len(k) > 20 else k for k in top_keys]
        ax.set_xticklabels(shortened_keys, rotation=45, ha='right')


        ax.set_title('Metadata Availability Heatmap')


        fig.colorbar(heatmap)


        fig.tight_layout()


        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def show_timeline_view(self, metadata_dict):
        self.current_data = metadata_dict
        self.current_view = "timeline"
        self.clear()

        if not HAS_MATPLOTLIB:
            lbl = tk.Label(
                self.frame,
                text="Matplotlib not available. Cannot create visualization.",
                bg=self.bg_color,
                font=("Arial", 12)
            )
            lbl.pack(pady=50)
            return

        import matplotlib.dates as mdates
        import datetime


        file_names = []
        creation_dates = []
        modified_dates = []

        for filepath, metadata in metadata_dict.items():
            file_name = os.path.basename(filepath)

            try:

                creation_date_str = metadata.get('Creation Date', '')
                modified_date_str = metadata.get('Modified Date', '')

                if creation_date_str:
                    creation_date = datetime.datetime.strptime(creation_date_str, '%Y-%m-%d %H:%M:%S')
                    file_names.append(file_name)
                    creation_dates.append(creation_date)

                    if modified_date_str:
                        modified_date = datetime.datetime.strptime(modified_date_str, '%Y-%m-%d %H:%M:%S')
                        modified_dates.append(modified_date)
                    else:
                        modified_dates.append(None)
            except (ValueError, TypeError):
                continue

        if not creation_dates:
            lbl = tk.Label(
                self.frame,
                text="No timeline data available for visualization",
                bg=self.bg_color,
                font=("Arial", 12)
            )
            lbl.pack(pady=50)
            return


        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)


        ax.plot(creation_dates, range(len(file_names)), 'bo', label='Creation Date')


        valid_mod_indices = [i for i, d in enumerate(modified_dates) if d is not None]
        if valid_mod_indices:
            valid_mod_dates = [modified_dates[i] for i in valid_mod_indices]
            valid_mod_y = [valid_mod_indices[i] for i in range(len(valid_mod_indices))]
            ax.plot(valid_mod_dates, valid_mod_y, 'rx', label='Modified Date')


        ax.set_yticks(range(len(file_names)))
        ax.set_yticklabels(file_names)
        ax.set_xlabel('Date')
        ax.set_title('File Timeline')


        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()


        ax.legend()


        fig.tight_layout()


        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


class ComparisonVisualizer:

    def __init__(self, parent_frame, bg_color, fg_color):
        self.parent = parent_frame
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.frame = tk.Frame(parent_frame, bg=bg_color)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


        self.setup_ui()

    def setup_ui(self):

        title_label = tk.Label(
            self.frame,
            text="File Comparison Results",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))


        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)


        self.diff_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.diff_frame, text="Differences")


        self.sim_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.sim_frame, text="Similarities")


        self.unique_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.unique_frame, text="Unique Fields")


        self.summary_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.summary_frame, text="Summary")


        placeholder = tk.Label(
            self.diff_frame,
            text="Select two files to compare",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 12)
        )
        placeholder.pack(pady=50)

    def clear(self):
        for tab in [self.diff_frame, self.sim_frame, self.unique_frame, self.summary_frame]:
            for widget in tab.winfo_children():
                widget.destroy()

    def show_comparison(self, comparison_data):
        self.clear()


        diff = comparison_data.get("differences", {})
        sim = comparison_data.get("similarities", {})
        only_file1 = comparison_data.get("only_in_file1", {})
        only_file2 = comparison_data.get("only_in_file2", {})
        file1_name = comparison_data.get("file1", "File 1")
        file2_name = comparison_data.get("file2", "File 2")


        self._create_diff_view(diff, file1_name, file2_name)


        self._create_sim_view(sim)


        self._create_unique_view(only_file1, only_file2, file1_name, file2_name)


        self._create_summary_view(comparison_data)

    def _create_diff_view(self, diff, file1_name, file2_name):
        header_frame = tk.Frame(self.diff_frame, bg=self.bg_color)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        tk.Label(
            header_frame,
            text="Metadata Field",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11, "bold"),
            width=30,
            anchor="w"
        ).grid(row=0, column=0, padx=5)

        tk.Label(
            header_frame,
            text=file1_name,
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11, "bold"),
            width=30,
            anchor="w"
        ).grid(row=0, column=1, padx=5)

        tk.Label(
            header_frame,
            text=file2_name,
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11, "bold"),
            width=30,
            anchor="w"
        ).grid(row=0, column=2, padx=5)


        canvas_frame = tk.Frame(self.diff_frame, bg=self.bg_color)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(canvas_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)


        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


        inner_frame = tk.Frame(canvas, bg=self.bg_color)
        canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)


        row = 0
        for key, values in sorted(diff.items()):
            tk.Label(
                inner_frame,
                text=key,
                bg=self.bg_color,
                fg=self.fg_color,
                font=("Arial", 10),
                wraplength=300,
                justify=tk.LEFT,
                anchor="w"
            ).grid(row=row, column=0, sticky="w", padx=5, pady=2)

            tk.Label(
                inner_frame,
                text=str(values.get("file1", "")),
                bg=self.bg_color,
                fg=self.fg_color,
                font=("Arial", 10),
                wraplength=300,
                justify=tk.LEFT,
                anchor="w"
            ).grid(row=row, column=1, sticky="w", padx=5, pady=2)

            tk.Label(
                inner_frame,
                text=str(values.get("file2", "")),
                bg=self.bg_color,
                fg=self.fg_color,
                font=("Arial", 10),
                wraplength=300,
                justify=tk.LEFT,
                anchor="w"
            ).grid(row=row, column=2, sticky="w", padx=5, pady=2)

            row += 1


        if row == 0:
            tk.Label(
                inner_frame,
                text="No differences found",
                bg=self.bg_color,
                fg=self.fg_color,
                font=("Arial", 12),
            ).grid(row=0, column=0, columnspan=3, pady=20)


        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def _create_sim_view(self, sim):

        canvas_frame = tk.Frame(self.sim_frame, bg=self.bg_color)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(canvas_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)


        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


        inner_frame = tk.Frame(canvas, bg=self.bg_color)
        canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)


        tk.Label(
            inner_frame,
            text="Metadata Field",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11, "bold"),
            width=30,
            anchor="w"
        ).grid(row=0, column=0, padx=5, pady=(0, 10))

        tk.Label(
            inner_frame,
            text="Value",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11, "bold"),
            width=50,
            anchor="w"
        ).grid(row=0, column=1, padx=5, pady=(0, 10))


        row = 1
        for key, value in sorted(sim.items()):
            tk.Label(
                inner_frame,
                text=key,
                bg=self.bg_color,
                fg=self.fg_color,
                font=("Arial", 10),
                wraplength=300,
                justify=tk.LEFT,
                anchor="w"
            ).grid(row=row, column=0, sticky="w", padx=5, pady=2)

            tk.Label(
                inner_frame,
                text=str(value),
                bg=self.bg_color,
                fg=self.fg_color,
                font=("Arial", 10),
                wraplength=500,
                justify=tk.LEFT,
                anchor="w"
            ).grid(row=row, column=1, sticky="w", padx=5, pady=2)

            row += 1


        if row == 1:
            tk.Label(
                inner_frame,
                text="No similarities found",
                bg=self.bg_color,
                fg=self.fg_color,
                font=("Arial", 12),
            ).grid(row=1, column=0, columnspan=2, pady=20)


        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def _create_unique_view(self, only_file1, only_file2, file1_name, file2_name):

        unique_notebook = ttk.Notebook(self.unique_frame)
        unique_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


        file1_frame = tk.Frame(unique_notebook, bg=self.bg_color)
        unique_notebook.add(file1_frame, text=f"Only in {file1_name}")


        file2_frame = tk.Frame(unique_notebook, bg=self.bg_color)
        unique_notebook.add(file2_frame, text=f"Only in {file2_name}")


        if only_file1:
            self._create_unique_list(file1_frame, only_file1)
        else:
            tk.Label(
                file1_frame,
                text=f"No unique fields in {file1_name}",
                bg=self.bg_color,
                fg=self.fg_color,
                font=("Arial", 12),
            ).pack(pady=20)


        if only_file2:
            self._create_unique_list(file2_frame, only_file2)
        else:
            tk.Label(
                file2_frame,
                text=f"No unique fields in {file2_name}",
                bg=self.bg_color,
                fg=self.fg_color,
                font=("Arial", 12),
            ).pack(pady=20)

    def _create_unique_list(self, parent, fields_dict):

        canvas_frame = tk.Frame(parent, bg=self.bg_color)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(canvas_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)


        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        inner_frame = tk.Frame(canvas, bg=self.bg_color)
        canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)


        tk.Label(
            inner_frame,
            text="Metadata Field",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11, "bold"),
            width=30,
            anchor="w"
        ).grid(row=0, column=0, padx=5, pady=(0, 10))

        tk.Label(
            inner_frame,
            text="Value",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11, "bold"),
            width=50,
            anchor="w"
        ).grid(row=0, column=1, padx=5, pady=(0, 10))


        row = 1
        for key, value in sorted(fields_dict.items()):
            tk.Label(
                inner_frame,
                text=key,
                bg=self.bg_color,
                fg=self.fg_color,
                font=("Arial", 10),
                wraplength=300,
                justify=tk.LEFT,
                anchor="w"
            ).grid(row=row, column=0, sticky="w", padx=5, pady=2)

            tk.Label(
                inner_frame,
                text=str(value),
                bg=self.bg_color,
                fg=self.fg_color,
                font=("Arial", 10),
                wraplength=500,
                justify=tk.LEFT,
                anchor="w"
            ).grid(row=row, column=1, sticky="w", padx=5, pady=2)

            row += 1

        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def _create_summary_view(self, comparison_data):
        diff = comparison_data.get("differences", {})
        sim = comparison_data.get("similarities", {})
        only_file1 = comparison_data.get("only_in_file1", {})
        only_file2 = comparison_data.get("only_in_file2", {})
        file1_name = comparison_data.get("file1", "File 1")
        file2_name = comparison_data.get("file2", "File 2")


        summary_container = tk.Frame(self.summary_frame, bg=self.bg_color)
        summary_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)


        tk.Label(
            summary_container,
            text="Files Compared:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 12, "bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        tk.Label(
            summary_container,
            text=f"1. {file1_name}",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11),
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=20)

        tk.Label(
            summary_container,
            text=f"2. {file2_name}",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11),
            anchor="w",
        ).grid(row=2, column=0, sticky="w", padx=20)


        tk.Label(
            summary_container,
            text="Comparison Statistics:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 12, "bold"),
            anchor="w",
        ).grid(row=3, column=0, sticky="w", pady=(20, 5))

        tk.Label(
            summary_container,
            text=f"• Total differences found: {len(diff)}",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11),
            anchor="w",
        ).grid(row=4, column=0, sticky="w", padx=20)

        tk.Label(
            summary_container,
            text=f"• Total similarities found: {len(sim)}",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11),
            anchor="w",
        ).grid(row=5, column=0, sticky="w", padx=20)

        tk.Label(
            summary_container,
            text=f"• Fields unique to {file1_name}: {len(only_file1)}",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11),
            anchor="w",
        ).grid(row=6, column=0, sticky="w", padx=20)

        tk.Label(
            summary_container,
            text=f"• Fields unique to {file2_name}: {len(only_file2)}",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11),
            anchor="w",
        ).grid(row=7, column=0, sticky="w", padx=20)

        total_fields = len(diff) + len(sim) + len(only_file1) + len(only_file2)

        tk.Label(
            summary_container,
            text=f"• Total fields examined: {total_fields}",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 11),
            anchor="w",
        ).grid(row=8, column=0, sticky="w", padx=20)


        if total_fields > 0:
            similarity_pct = (len(sim) / total_fields) * 100
            tk.Label(
                summary_container,
                text=f"• Overall similarity: {similarity_pct:.1f}%",
                bg=self.bg_color,
                fg=self.fg_color,
                font=("Arial", 11),
                anchor="w",
            ).grid(row=9, column=0, sticky="w", padx=20)


        if HAS_MATPLOTLIB:
            self._add_summary_chart(summary_container, diff, sim, only_file1, only_file2)

    def _add_summary_chart(self, parent, diff, sim, only_file1, only_file2):


        fig = Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)


        labels = ['Differences', 'Similarities', f'Only in File 1', f'Only in File 2']
        sizes = [len(diff), len(sim), len(only_file1), len(only_file2)]
        colors = ['#ff9999', '#99ff99', '#ffcc99', '#99ccff']


        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')


        ax.set_title('Metadata Comparison')


        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().grid(row=10, column=0, pady=20)
