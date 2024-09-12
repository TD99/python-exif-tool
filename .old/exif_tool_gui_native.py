import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import subprocess
import datetime

class ExifToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Exif Tool GUI")
        self.root.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        # Input and Output Folders
        self.create_folder_widgets()

        # Label above tabs
        tk.Label(self.root, text="Select Function", font=("Helvetica", 16, "bold")).grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        # Create a Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=3, column=0, columnspan=3, sticky='nsew')

        # Create Rename tab
        self.rename_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.rename_tab, text='Rename')

        # Create Group tab
        self.group_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.group_tab, text='Group')

        # Rename Tab Widgets
        self.create_rename_widgets()

        # Group Tab Widgets
        self.create_group_widgets()

        # Log Console
        tk.Label(self.root, text="Console Output:", font=("Helvetica", 12, "bold")).grid(row=4, column=0, columnspan=3, padx=10, pady=5)
        self.console_output = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=90, height=15, state='disabled', bg="#1e2a33", fg="#ffffff", insertbackground='white')
        self.console_output.grid(row=5, column=0, columnspan=3, padx=10, pady=5, sticky='nsew')
        self.console_output.bind("<Button-3>", self.show_context_menu)

        # Context Menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Clear", command=self.clear_console)

        # Grid configuration
        self.root.grid_rowconfigure(5, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

    def create_folder_widgets(self):
        tk.Label(self.root, text="Input Folder:", font=("Helvetica", 12)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.input_folder_var = tk.StringVar()
        self.input_folder_entry = tk.Entry(self.root, textvariable=self.input_folder_var, width=60, font=("Helvetica", 12))
        self.input_folder_entry.grid(row=0, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_input_folder, bg="#007bff", fg="#ffffff", font=("Helvetica", 12), relief="flat").grid(row=0, column=2, padx=10, pady=5)

        tk.Label(self.root, text="Output Folder:", font=("Helvetica", 12)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.output_folder_var = tk.StringVar()
        self.output_folder_entry = tk.Entry(self.root, textvariable=self.output_folder_var, width=60, font=("Helvetica", 12))
        self.output_folder_entry.grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_output_folder, bg="#007bff", fg="#ffffff", font=("Helvetica", 12), relief="flat").grid(row=1, column=2, padx=10, pady=5)

    def create_rename_widgets(self):
        tk.Checkbutton(self.rename_tab, text="Process recursively (-r)", variable=tk.BooleanVar(), font=("Helvetica", 12)).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        tk.Label(self.rename_tab, text="Date Format:", font=("Helvetica", 12)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.date_format_var = tk.StringVar(value="%Y-%m-%d_%H-%M-%S")
        tk.Entry(self.rename_tab, textvariable=self.date_format_var, width=60, font=("Helvetica", 12)).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self.rename_tab, text="Run Rename", command=self.run_rename_tool, bg="#007bff", fg="#ffffff", font=("Helvetica", 12), relief="flat").grid(row=2, column=0, columnspan=2, pady=10)

    def create_group_widgets(self):
        tk.Checkbutton(self.group_tab, text="Process recursively (-r)", variable=tk.BooleanVar(), font=("Helvetica", 12)).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        tk.Label(self.group_tab, text="GPS Radius (e.g., '1000m', '1km'):", font=("Helvetica", 12)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.radius_var = tk.StringVar()
        tk.Entry(self.group_tab, textvariable=self.radius_var, width=60, font=("Helvetica", 12)).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self.group_tab, text="Run Group", command=self.run_group_tool, bg="#007bff", fg="#ffffff", font=("Helvetica", 12), relief="flat").grid(row=2, column=0, columnspan=2, pady=10)

    def browse_input_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.input_folder_var.set(folder_selected)

    def browse_output_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_folder_var.set(folder_selected)

    def run_rename_tool(self):
        input_folder = self.input_folder_var.get()
        output_folder = self.output_folder_var.get()
        date_format = self.date_format_var.get()
        recursive = self.get_checkbutton_value(self.rename_tab, 0)

        if not input_folder or not output_folder:
            self.log_console("Error: Please select both input and output folders.\n", error=True)
            return

        command = ["python", "../exif_tool.py", input_folder, output_folder, "--rename"]
        if recursive:
            command.append("--recursive")
        if date_format:
            command.extend(["--format", date_format])

        self.execute_command(command)

    def run_group_tool(self):
        input_folder = self.input_folder_var.get()
        output_folder = self.output_folder_var.get()
        radius = self.radius_var.get()
        recursive = self.get_checkbutton_value(self.group_tab, 0)

        if not input_folder or not output_folder:
            self.log_console("Error: Please select both input and output folders.\n", error=True)
            return

        command = ["python", "../exif_tool.py", input_folder, output_folder, "--group"]
        if recursive:
            command.append("--recursive")
        if radius:
            command.extend(["--radius", radius])

        self.execute_command(command)

    def execute_command(self, command):
        self.log_console(f"Running command: {' '.join(command)}\n")
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            while True:
                output = process.stdout.readline()
                if output:
                    self.log_console(f"{self.current_time()} - {output.strip()}\n")
                error = process.stderr.readline()
                if error:
                    self.log_console(f"{self.current_time()} - ERROR: {error.strip()}\n", error=True)
                if process.poll() is not None:
                    break
            self.log_console(f"{self.current_time()} - Process completed.\n")
        except Exception as e:
            self.log_console(f"{self.current_time()} - Error running the tool: {e}\n", error=True)

    def log_console(self, message, error=False):
        self.console_output.configure(state='normal')
        self.console_output.insert(tk.END, message)
        self.console_output.configure(state='disabled')
        self.console_output.yview(tk.END)
        if error:
            self.root.bell()  # Optional: beep on error

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def clear_console(self):
        self.console_output.configure(state='normal')
        self.console_output.delete(1.0, tk.END)
        self.console_output.configure(state='disabled')

    def current_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def get_checkbutton_value(self, tab, index):
        return tab.grid_slaves(row=index, column=0)[0].var.get()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExifToolGUI(root)
    root.mainloop()
