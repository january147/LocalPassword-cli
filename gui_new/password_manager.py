#!/usr/bin/env python3
"""
Modern Password Manager GUI
A beautiful and user-friendly interface for the Password Manager CLI
"""

import subprocess
import os
import json
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import Dict, List, Optional
import re


class PasswordManagerGUI:
    def __init__(self):
        """Initialize the Password Manager GUI"""
        # Configure CustomTkinter
        ctk.set_appearance_mode("dark")  # dark/light/system
        ctk.set_default_color_theme("blue")  # blue/green/dark-blue

        # Create main window
        self.root = ctk.CTk()
        self.root.title("Password Manager")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        # State variables
        self.master_password = ""
        self.passwords = []
        self.current_page = "login"

        # Create UI
        self.setup_login_page()

    def run(self):
        """Start the GUI"""
        self.root.mainloop()

    # ==================== Page Setup ====================

    def setup_login_page(self):
        """Setup the login page"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create frame
        self.login_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        title_label = ctk.CTkLabel(
            self.login_frame,
            text="Password Manager",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=(0, 10))

        subtitle_label = ctk.CTkLabel(
            self.login_frame,
            text="Secure • Simple • Fast",
            font=ctk.CTkFont(size=14),
            text_color=("gray70", "gray30")
        )
        subtitle_label.pack(pady=(0, 30))

        # Password input
        self.password_entry = ctk.CTkEntry(
            self.login_frame,
            placeholder_text="Master Password",
            show="•",
            width=300,
            height=45,
            font=ctk.CTkFont(size=14)
        )
        self.password_entry.pack(pady=10)
        self.password_entry.bind("<Return>", lambda e: self.on_login())

        # Login button
        login_btn = ctk.CTkButton(
            self.login_frame,
            text="Unlock",
            width=300,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.on_login
        )
        login_btn.pack(pady=10)

        # Show password toggle
        self.show_password_var = ctk.BooleanVar(value=False)
        show_password_cb = ctk.CTkCheckBox(
            self.login_frame,
            text="Show password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility
        )
        show_password_cb.pack(pady=5)

        # Bind Enter key to password entry
        self.password_entry.focus()

    def setup_main_page(self):
        """Setup the main dashboard page"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create sidebar
        self.sidebar = ctk.CTkFrame(
            self.root,
            width=200,
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")

        # App title in sidebar
        app_title = ctk.CTkLabel(
            self.sidebar,
            text="🔐\nPassword\nManager",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="center"
        )
        app_title.pack(pady=20)

        # Sidebar buttons
        self.create_sidebar_button(
            "📋",
            "Passwords",
            "list",
            self.show_passwords_page
        )
        self.create_sidebar_button(
            "➕",
            "Add New",
            "add",
            self.show_add_password_page
        )
        self.create_sidebar_button(
            "🔍",
            "Search",
            "search",
            self.show_search_page
        )
        self.create_sidebar_button(
            "⚙️",
            "Generator",
            "generate",
            self.show_generator_page
        )
        self.create_sidebar_button(
            "📤",
            "Export",
            "export",
            self.export_passwords
        )
        self.create_sidebar_button(
            "📥",
            "Import",
            "import",
            self.import_passwords
        )

        # Spacer
        ctk.CTkFrame(self.sidebar, height=20).pack()

        # Logout button
        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="🔒 Lock",
            width=180,
            height=40,
            fg_color=("gray80", "gray30"),
            command=self.logout
        )
        logout_btn.pack(side="bottom", pady=20)

        # Create main content area
        self.main_content = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_content.pack(side="left", fill="both", expand=True)

        # Show passwords page by default
        self.show_passwords_page()

    # ==================== Helper Methods ====================

    def create_sidebar_button(self, icon: str, text: str, name: str, command):
        """Create a sidebar button with icon"""
        btn = ctk.CTkButton(
            self.sidebar,
            text=f"{icon} {text}",
            width=180,
            height=45,
            anchor="w",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            command=command
        )
        btn.pack(pady=5, padx=10)

    def run_pm_command(self, args: List[str]) -> tuple:
        """Execute PM CLI command and return (success, stdout, stderr)"""
        env = os.environ.copy()
        env['PM_MASTER_PASSWORD'] = self.master_password

        try:
            result = subprocess.run(
                ['pm', '--non-interactive'] + args,
                capture_output=True,
                text=True,
                env=env,
                timeout=30
            )
            return (result.returncode == 0, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            return (False, "", "Command timeout")
        except Exception as e:
            return (False, "", str(e))

    def parse_passwords(self, output: str) -> List[Dict]:
        """Parse PM CLI output to extract password entries"""
        entries = []
        current_entry = {}

        patterns = {
            'title': r'📌\s+(.+)',
            'username': r'Username:\s+(.+)',
            'password': r'Password:\s+(.+)',
            'url': r'URL:\s+(.+)',
            'category': r'Category:\s+(.+)',
            'notes': r'Notes:\s+(.+)',
        }

        for line in output.split('\n'):
            for key, pattern in patterns.items():
                match = re.search(pattern, line)
                if match:
                    value = match.group(1).strip()

                    if key == 'title':
                        if current_entry:
                            entries.append(current_entry)
                        current_entry = {'title': value}
                    else:
                        current_entry[key] = value

        if current_entry:
            entries.append(current_entry)

        return entries

    def show_loading(self, message: str = "Loading..."):
        """Show loading indicator"""
        self.loading_window = ctk.CTkToplevel(self.root)
        self.loading_window.title("Loading")
        self.loading_window.geometry("300x150")

        loading_label = ctk.CTkLabel(
            self.loading_window,
            text=message,
            font=ctk.CTkFont(size=16)
        )
        loading_label.place(relx=0.5, rely=0.5, anchor="center")

        self.loading_window.transient(self.root)
        self.loading_window.grab_set()

    def hide_loading(self):
        """Hide loading indicator"""
        if hasattr(self, 'loading_window'):
            self.loading_window.destroy()

    # ==================== Login Page Methods ====================

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="•")

    def on_login(self):
        """Handle login button click"""
        self.master_password = self.password_entry.get()

        if not self.master_password:
            messagebox.showerror("Error", "Please enter your master password")
            return

        # Test the password
        success, stdout, stderr = self.run_pm_command(['list', '--log-level', 'off'])

        if not success:
            messagebox.showerror("Error", "Failed to unlock database. Check your master password.")
            return

        # Setup main page
        self.setup_main_page()

    def logout(self):
        """Logout and return to login page"""
        self.master_password = ""
        self.passwords = []
        self.setup_login_page()

    # ==================== Main Page Methods ====================

    def clear_main_content(self):
        """Clear the main content area"""
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def show_passwords_page(self):
        """Show the passwords list page"""
        self.clear_main_content()

        # Title
        title = ctk.CTkLabel(
            self.main_content,
            text="📋 Passwords",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)

        # Search box
        search_frame = ctk.CTkFrame(self.main_content)
        search_frame.pack(fill="x", padx=20, pady=10)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Search passwords...",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        # Add button
        add_btn = ctk.CTkButton(
            search_frame,
            text="➕ Add",
            width=80,
            height=40,
            command=self.show_add_password_page
        )
        add_btn.pack(side="right", padx=10, pady=10)

        # Scrollable frame for passwords
        self.passwords_frame = ctk.CTkScrollableFrame(
            self.main_content,
            label_text="",
            height=400
        )
        self.passwords_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Load passwords
        self.load_passwords()

    def load_passwords(self, search_query: str = ""):
        """Load and display passwords"""
        self.show_loading("Loading passwords...")

        def load_thread():
            success, stdout, stderr = self.run_pm_command(['list', '--log-level', 'off'])

            if not success:
                self.hide_loading()
                messagebox.showerror("Error", f"Failed to load passwords: {stderr}")
                return

            self.passwords = self.parse_passwords(stdout)

            # Filter if search query provided
            if search_query:
                query = search_query.lower()
                self.passwords = [
                    p for p in self.passwords
                    if query in p.get('title', '').lower()
                    or query in p.get('username', '').lower()
                    or query in p.get('url', '').lower()
                ]

            # Update UI
            self.root.after(0, self.update_passwords_list)

        threading.Thread(target=load_thread, daemon=True).start()

    def update_passwords_list(self):
        """Update the passwords list UI"""
        self.hide_loading()

        # Clear existing entries
        for widget in self.passwords_frame.winfo_children():
            widget.destroy()

        if not self.passwords:
            no_passwords_label = ctk.CTkLabel(
                self.passwords_frame,
                text="No passwords found",
                font=ctk.CTkFont(size=16),
                text_color=("gray60", "gray40")
            )
            no_passwords_label.pack(pady=40)
            return

        # Add password entries
        for pwd in self.passwords:
            self.create_password_entry(pwd)

    def create_password_entry(self, pwd: Dict):
        """Create a password entry card"""
        entry_frame = ctk.CTkFrame(self.passwords_frame)
        entry_frame.pack(fill="x", pady=5)

        # Title
        title_label = ctk.CTkLabel(
            entry_frame,
            text=pwd.get('title', 'Unknown'),
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        title_label.pack(fill="x", padx=10, pady=(5, 0))

        # Details
        details_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        details_frame.pack(fill="x", padx=10, pady=5)

        username_label = ctk.CTkLabel(
            details_frame,
            text=f"👤 {pwd.get('username', '')}",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        username_label.pack(side="left", padx=(0, 20))

        if pwd.get('url'):
            url_label = ctk.CTkLabel(
                details_frame,
                text=f"🔗 {pwd.get('url', '')}",
                font=ctk.CTkFont(size=12),
                anchor="w",
                text_color=("gray60", "gray40")
            )
            url_label.pack(side="left", padx=(0, 20))

        # Buttons
        button_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(0, 5))

        copy_btn = ctk.CTkButton(
            button_frame,
            text="📋 Copy",
            width=100,
            height=30,
            fg_color=("gray70", "gray30"),
            command=lambda p=pwd: self.copy_password(p)
        )
        copy_btn.pack(side="left", padx=(0, 5))

        edit_btn = ctk.CTkButton(
            button_frame,
            text="✏️ Edit",
            width=100,
            height=30,
            fg_color=("gray70", "gray30"),
            command=lambda p=pwd: self.show_edit_password_page(p)
        )
        edit_btn.pack(side="left", padx=(0, 5))

        delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Delete",
            width=100,
            height=30,
            fg_color=("red", "darkred"),
            hover_color=("darkred", "red"),
            command=lambda p=pwd: self.delete_password(p)
        )
        delete_btn.pack(side="right")

    def on_search(self, event):
        """Handle search box input"""
        query = self.search_entry.get()
        self.load_passwords(query)

    def copy_password(self, pwd: Dict):
        """Copy password to clipboard"""
        # In a real app, you would use clipboard module
        password = pwd.get('password', '******')

        # Try using clipboard
        try:
            import pyperclip
            pyperclip.copy(password)
            messagebox.showinfo("Success", f"Password for '{pwd.get('title')}' copied to clipboard!")
        except ImportError:
            # Fallback to echo command
            messagebox.showinfo("Info", f"Password: {password}\n\nInstall pyperclip for automatic copying:\npip install pyperclip")

    # ==================== Add/Edit Password Methods ====================

    def show_add_password_page(self):
        """Show the add password page"""
        self.show_password_form(mode="add", password_data={})

    def show_edit_password_page(self, pwd: Dict):
        """Show the edit password page"""
        self.show_password_form(mode="edit", password_data=pwd)

    def show_password_form(self, mode: str, password_data: Dict):
        """Show password add/edit form"""
        self.clear_main_content()

        # Title
        title = ctk.CTkLabel(
            self.main_content,
            text=f"{'➕ Add' if mode == 'add' else '✏️ Edit'} Password",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)

        # Form frame
        form_frame = ctk.CTkFrame(self.main_content)
        form_frame.pack(padx=40, pady=20, fill="both", expand=True)

        # Title field
        ctk.CTkLabel(form_frame, text="Title *", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.form_title = ctk.CTkEntry(form_frame, height=40, placeholder_text="e.g., GitHub")
        self.form_title.pack(fill="x", pady=(0, 10))
        if mode == "edit":
            self.form_title.insert(0, password_data.get('title', ''))

        # Username field
        ctk.CTkLabel(form_frame, text="Username *", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.form_username = ctk.CTkEntry(form_frame, height=40, placeholder_text="e.g., user@example.com")
        self.form_username.pack(fill="x", pady=(0, 10))
        if mode == "edit":
            self.form_username.insert(0, password_data.get('username', ''))

        # Password field
        ctk.CTkLabel(form_frame, text="Password *", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10, 5))
        password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_frame.pack(fill="x", pady=(0, 10))

        self.form_password = ctk.CTkEntry(password_frame, height=40, show="•", placeholder_text="Enter password")
        self.form_password.pack(side="left", fill="x", expand=True)

        if mode == "edit":
            self.form_password.insert(0, password_data.get('password', ''))

        generate_btn = ctk.CTkButton(
            password_frame,
            text="🔢 Generate",
            width=120,
            height=40,
            fg_color=("gray70", "gray30"),
            command=self.show_generator_page
        )
        generate_btn.pack(side="right", padx=(10, 0))

        # URL field
        ctk.CTkLabel(form_frame, text="URL", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        self.form_url = ctk.CTkEntry(form_frame, height=40, placeholder_text="e.g., https://github.com")
        self.form_url.pack(fill="x", pady=(0, 10))
        if mode == "edit":
            self.form_url.insert(0, password_data.get('url', ''))

        # Category field
        ctk.CTkLabel(form_frame, text="Category", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        self.form_category = ctk.CTkEntry(form_frame, height=40, placeholder_text="e.g., Work, Personal")
        self.form_category.pack(fill="x", pady=(0, 10))
        if mode == "edit":
            self.form_category.insert(0, password_data.get('category', ''))

        # Notes field
        ctk.CTkLabel(form_frame, text="Notes", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        self.form_notes = ctk.CTkTextbox(form_frame, height=100)
        self.form_notes.pack(fill="x", pady=(0, 10))
        if mode == "edit" and password_data.get('notes'):
            self.form_notes.insert("1.0", password_data.get('notes', ''))

        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=150,
            height=40,
            fg_color=("gray70", "gray30"),
            command=self.show_passwords_page
        )
        cancel_btn.pack(side="left", padx=(0, 10))

        save_btn = ctk.CTkButton(
            button_frame,
            text=f"{'Add' if mode == 'add' else 'Save'} Password",
            width=150,
            height=40,
            command=lambda: self.save_password(mode)
        )
        save_btn.pack(side="right")

    def save_password(self, mode: str):
        """Save password (add or edit)"""
        title = self.form_title.get().strip()
        username = self.form_username.get().strip()
        password = self.form_password.get()
        url = self.form_url.get().strip()
        category = self.form_category.get().strip()
        notes = self.form_notes.get("1.0", "end").strip()

        # Validation
        if not title or not username or not password:
            messagebox.showerror("Error", "Title, username, and password are required")
            return

        self.show_loading(f"{'Adding' if mode == 'add' else 'Saving'} password...")

        def save_thread():
            args = ['add']
            args.extend(['--title', title])
            args.extend(['--username', username])
            args.extend(['--password', password])
            if url:
                args.extend(['--url', url])
            if category:
                args.extend(['--category', category])
            if notes:
                args.extend(['--notes', notes])

            success, stdout, stderr = self.run_pm_command(args)

            self.hide_loading()

            if success:
                self.root.after(0, self.show_passwords_page)
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to save password: {stderr}"))

        threading.Thread(target=save_thread, daemon=True).start()

    def delete_password(self, pwd: Dict):
        """Delete a password"""
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{pwd.get('title')}'?"):
            return

        self.show_loading("Deleting password...")

        def delete_thread():
            args = ['delete', pwd.get('title', ''), '--force']
            success, stdout, stderr = self.run_pm_command(args)

            self.hide_loading()

            if success:
                self.root.after(0, self.load_passwords)
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to delete password: {stderr}"))

        threading.Thread(target=delete_thread, daemon=True).start()

    # ==================== Generator Page ====================

    def show_generator_page(self):
        """Show the password generator page"""
        self.clear_main_content()

        # Title
        title = ctk.CTkLabel(
            self.main_content,
            text="🔢 Password Generator",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=20)

        # Generator frame
        gen_frame = ctk.CTkFrame(self.main_content)
        gen_frame.pack(padx=40, pady=20, fill="both", expand=True)

        # Length
        ctk.CTkLabel(gen_frame, text="Password Length", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.length_slider = ctk.CTkSlider(gen_frame, from_=8, to=64, number_of_steps=56)
        self.length_slider.set(20)
        self.length_slider.pack(fill="x", pady=(0, 5))

        self.length_value = ctk.CTkLabel(gen_frame, text="20", font=ctk.CTkFont(size=20, weight="bold"))
        self.length_value.pack(pady=(0, 20))
        self.length_slider.configure(command=lambda v: self.length_value.configure(text=str(int(v))))

        # Generated password
        ctk.CTkLabel(gen_frame, text="Generated Password", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.generated_password = ctk.CTkEntry(gen_frame, height=50, font=ctk.CTkFont(size=18))
        self.generated_password.pack(fill="x", pady=(0, 20))

        # Buttons
        button_frame = ctk.CTkFrame(gen_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)

        generate_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Generate",
            width=150,
            height=40,
            command=self.generate_password
        )
        generate_btn.pack(side="left", padx=(0, 10))

        copy_btn = ctk.CTkButton(
            button_frame,
            text="📋 Copy",
            width=150,
            height=40,
            command=self.copy_generated_password
        )
        copy_btn.pack(side="left")

        use_btn = ctk.CTkButton(
            button_frame,
            text="✅ Use This",
            width=150,
            height=40,
            fg_color=("green", "darkgreen"),
            command=self.use_generated_password
        )
        use_btn.pack(side="right")

        # Generate initial password
        self.generate_password()

    def generate_password(self):
        """Generate a new password"""
        self.show_loading("Generating password...")

        def gen_thread():
            length = int(self.length_slider.get())
            args = ['generate', '--length', str(length)]

            success, stdout, stderr = self.run_pm_command(args)

            self.hide_loading()

            if success:
                # Extract password from output
                for line in stdout.split('\n'):
                    if line.strip() and not line.startswith('Generated') and not line.startswith('Strength'):
                        self.root.after(0, lambda p=line: self.generated_password.delete(0, "end") or self.generated_password.insert(0, p))
                        break
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to generate password: {stderr}"))

        threading.Thread(target=gen_thread, daemon=True).start()

    def copy_generated_password(self):
        """Copy generated password to clipboard"""
        password = self.generated_password.get()
        try:
            import pyperclip
            pyperclip.copy(password)
            messagebox.showinfo("Success", "Password copied to clipboard!")
        except ImportError:
            messagebox.showinfo("Info", f"Password: {password}\n\nInstall pyperclip for automatic copying:\npip install pyperclip")

    def use_generated_password(self):
        """Use the generated password in the form"""
        password = self.generated_password.get()
        if hasattr(self, 'form_password'):
            self.form_password.delete(0, "end")
            self.form_password.insert(0, password)
            self.show_passwords_page()

    # ==================== Search Page ====================

    def show_search_page(self):
        """Show the search page (reuses passwords page with search focused)"""
        self.show_passwords_page()
        self.search_entry.focus()

    # ==================== Import/Export ====================

    def export_passwords(self):
        """Export passwords to JSON file"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not filepath:
            return

        self.show_loading("Exporting passwords...")

        def export_thread():
            args = ['export', filepath, '--log-level', 'off']
            success, stdout, stderr = self.run_pm_command(args)

            self.hide_loading()

            if success:
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Passwords exported to {filepath}"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to export: {stderr}"))

        threading.Thread(target=export_thread, daemon=True).start()

    def import_passwords(self):
        """Import passwords from JSON file"""
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not filepath:
            return

        if not messagebox.askyesno("Confirm Import", "This will add passwords from the file to your database. Continue?"):
            return

        self.show_loading("Importing passwords...")

        def import_thread():
            args = ['import', filepath, '--log-level', 'off']
            success, stdout, stderr = self.run_pm_command(args)

            self.hide_loading()

            if success:
                self.root.after(0, lambda: self.load_passwords())
                self.root.after(0, lambda: messagebox.showinfo("Success", "Passwords imported successfully!"))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to import: {stderr}"))

        threading.Thread(target=import_thread, daemon=True).start()


def main():
    """Main entry point"""
    app = PasswordManagerGUI()
    app.run()


if __name__ == "__main__":
    main()
