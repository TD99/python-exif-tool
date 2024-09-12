import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import subprocess
import datetime

class ExifToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Exif Tool GUI")
        self.root.geometry("800x600")
        ctk.set_appearance_mode("dark")  # Use dark mode
        ctk.set_default_color_theme("blue")  # Set theme color

        self.create_widgets()

    def create_widgets(self):
        # Input and Output Folders
        self.create_folder_widgets()

        # Label above tabs
        self.select_function_label = ctk.CTkLabel(self.root, text="Select Function", font=("Helvetica", 16, "bold"))
        self.select_function_label.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        # Create a Tabview (tabs) using customtkinter CTkTabview
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.grid(row=3, column=0, columnspan=3, sticky='nsew')

        # Create Rename tab
        self.rename_tab = self.tabview.add("Rename")

        # Create Group tab
        self.group_tab = self.tabview.add("Group")

        # Rename Tab Widgets
        self.create_rename_widgets()

        # Group Tab Widgets
        self.create_group_widgets()

        # Log Console
        self.console_output = ctk.CTkTextbox(self.root, wrap="word", height=15, state='disabled')
        self.console_output.grid(row=5, column=0, columnspan=3, padx=10, pady=5, sticky='nsew')
        self.console_output.bind("<Button-3>", self.show_context_menu)

        # Grid configuration
        self.root.grid_rowconfigure(5, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

    def create_folder_widgets(self):
        self.input_folder_var = ctk.StringVar()
        self.input_folder_entry = ctk.CTkEntry(self.root, textvariable=self.input_folder_var, width=300)
        self.input_folder_entry.grid(row=0, column=1, padx=10, pady=5)
        self.browse_input_button = ctk.CTkButton(self.root, text="Browse", command=self.browse_input_folder)
        self.browse_input_button.grid(row=0, column=2, padx=10, pady=5)

        self.output_folder_var = ctk.StringVar()
        self.output_folder_entry = ctk.CTkEntry(self.root, textvariable=self.output_folder_var, width=300)
        self.output_folder_entry.grid(row=1, column=1, padx=10, pady=5)
        self.browse_output_button = ctk.CTkButton(self.root, text="Browse", command=self.browse_output_folder)
        self.browse_output_button.grid(row=1, column=2, padx=10, pady=5)

        ctk.CTkLabel(self.root, text="Input Folder:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkLabel(self.root, text="Output Folder:").grid(row=1, column=0, sticky="w", padx=10, pady=5)

    def create_rename_widgets(self):
        self.recursive_var = ctk.BooleanVar()
        self.recursive_checkbox = ctk.CTkCheckBox(self.rename_tab, text="Process recursively (-r)", variable=self.recursive_var)
        self.recursive_checkbox.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(self.rename_tab, text="Date Format:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.date_format_var = ctk.StringVar(value="%Y-%m-%d_%H-%M-%S")
        self.date_format_entry = ctk.CTkEntry(self.rename_tab, textvariable=self.date_format_var, width=300)
        self.date_format_entry.grid(row=1, column=1, padx=10, pady=5)

        self.run_rename_button = ctk.CTkButton(self.rename_tab, text="Run Rename", command=self.run_rename_tool)
        self.run_rename_button.grid(row=2, column=0, columnspan=2, pady=10)

    def create_group_widgets(self):
        self.recursive_var_group = ctk.BooleanVar()
        self.recursive_checkbox_group = ctk.CTkCheckBox(self.group_tab, text="Process recursively (-r)", variable=self.recursive_var_group)
        self.recursive_checkbox_group.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(self.group_tab, text="GPS Radius (e.g., '1000m', '1km'):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.radius_var = ctk.StringVar()
        self.radius_entry = ctk.CTkEntry(self.group_tab, textvariable=self.radius_var, width=300)
        self.radius_entry.grid(row=1, column=1, padx=10, pady=5)

        self.run_group_button = ctk.CTkButton(self.group_tab, text="Run Group", command=self.run_group_tool)
        self.run_group_button.grid(row=2, column=0, columnspan=2, pady=10)

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
        recursive = self.recursive_var.get()

        if not input_folder or not output_folder:
            self.log_console("Error: Please select both input and output folders.\n", error=True)
            return

        command = ["python", "./exif_tool.py", input_folder, output_folder, "--rename"]
        if recursive:
            command.append("--recursive")
        if date_format:
            command.extend(["--format", date_format])

        self.execute_command(command)

    def run_group_tool(self):
        input_folder = self.input_folder_var.get()
        output_folder = self.output_folder_var.get()
        radius = self.radius_var.get()
        recursive = self.recursive_var_group.get()

        if not input_folder or not output_folder:
            self.log_console("Error: Please select both input and output folders.\n", error=True)
            return

        command = ["python", "./exif_tool.py", input_folder, output_folder, "--group"]
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
            self.root.bell()

    def show_context_menu(self, event):
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Clear Console", command=self.clear_console)
        context_menu.post(event.x_root, event.y_root)

    def clear_console(self):
        self.console_output.configure(state='normal')
        self.console_output.delete(1.0, tk.END)
        self.console_output.configure(state='disabled')

    def current_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

if __name__ == "__main__":
    root = ctk.CTk()
    app = ExifToolGUI(root)
    root.mainloop()
