
import tkinter as tk
from tkinter import messagebox
import random
import string
import pyperclip  # For clipboard integration


class PasswordGenerator:
    def __init__(self, master):
        self.master = master
        self.master.title("Password Generator")

        self.label_length = tk.Label(master, text="Password Length:")
        self.label_length.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)

        self.entry_length = tk.Entry(master, width=10)
        self.entry_length.grid(row=0, column=1, padx=10, pady=10)

        self.label_complexity = tk.Label(master, text="Password Complexity:")
        self.label_complexity.grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)

        self.complexity_var = tk.StringVar()
        self.complexity_var.set("Medium")

        self.complexity_menu = tk.OptionMenu(master, self.complexity_var, "Low", "Medium", "High")
        self.complexity_menu.grid(row=1, column=1, padx=10, pady=10)

        self.check_var = tk.BooleanVar()
        self.checkbox_rules = tk.Checkbutton(master, text="Adhere to security rules", variable=self.check_var)
        self.checkbox_rules.grid(row=2, columnspan=2, padx=10, pady=10)

        self.generate_button = tk.Button(master, text="Generate Password", command=self.generate_password)
        self.generate_button.grid(row=3, columnspan=2, padx=10, pady=10)

        self.label_generated_password = tk.Label(master, text="Generated Password:")
        self.label_generated_password.grid(row=4, column=0, sticky=tk.W, padx=10, pady=10)

        self.generated_password = tk.Entry(master, width=30)
        self.generated_password.grid(row=4, column=1, padx=10, pady=10)

        self.copy_button = tk.Button(master, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_button.grid(row=5, columnspan=2, padx=10, pady=10)

    def generate_password(self):
        length = self.entry_length.get()
        try:
            length = int(length)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for password length.")
            return

        if length <= 0:
            messagebox.showerror("Error", "Password length should be greater than zero.")
            return

        complexity = self.complexity_var.get()
        include_symbols = True if complexity == "High" else False

        if self.check_var.get():
            include_symbols = True

        lower = string.ascii_lowercase
        upper = string.ascii_uppercase
        digits = string.digits
        symbols = string.punctuation if include_symbols else ""

        all_chars = lower + upper + digits + symbols

        password = "".join(random.sample(all_chars, length))
        self.generated_password.delete(0, tk.END)
        self.generated_password.insert(0, password)

    def copy_to_clipboard(self):
        password = self.generated_password.get()
        if password:
            pyperclip.copy(password)
            messagebox.showinfo("Copied", "Password copied to clipboard.")
        else:
            messagebox.showerror("Error", "No password generated to copy.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()
