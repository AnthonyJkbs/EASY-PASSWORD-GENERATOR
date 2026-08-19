
import secrets
import string
import sys

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
    from tkinter import font as tkfont
except Exception:
    import sys
    sys.stderr.write(
        "ERROR: tkinter is not available.\n"
        "On Fedora:  sudo dnf install python3-tkinter\n"
        "On Debian:  sudo apt-get install python3-tk\n"
    )
    raise
# Theme (light & minimal)
BG           = "#f7f7f8"
FG           = "#1a1a1a"
ACCENT       = "#2f6feb"
ACCENT_HOVER = "#1f55c9"
MUTED        = "#8a8a8e"
FIELD_BG     = "#ffffff"
FIELD_BORDER = "#d8d8dc"
DANGER       = "#d94848"
DANGER_HOVER = "#b93a3a"
NEUTRAL      = "#3f7a4a"
NEUTRAL_HV   = "#2f5e39"
COPY_BG      = "#ececef"
COPY_HOVER   = "#dedee2"
SAVE_BG      = "#e7f0e8"
SAVE_HOVER   = "#d2e6d5"

PASSWORD_LENGTH = 18
MIN_LEN = 6
MAX_LEN = 48
COPY_ICON  = "📋"
EYE_ON     = "👁"
EYE_OFF    = "🙈"
EXPORT_FILE = "passwords.txt"


# Password generation

def generate_password(length: int = PASSWORD_LENGTH) -> str:
    """Build a strong random password from a balanced character pool.

    Uses `secrets` (cryptographically secure) rather than `random`,
    and guarantees at least one character from each class.
    """
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+[]{};:,.<>?/~"

    required = [
        secrets.choice(lower),
        secrets.choice(upper),
        secrets.choice(digits),
        secrets.choice(symbols),
    ]
    rest = [
        secrets.choice(lower + upper + digits + symbols)
        for _ in range(max(0, length - len(required)))
    ]
    chars = required + rest
    secrets.SystemRandom().shuffle(chars)  # scramble the guaranteed characters
    return "".join(chars)


#interface
class PasswordApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("EASY PASSWORD GENERATOR")
        self.root.geometry("480x300")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)
        self.root.eval("tk::PlaceWindow . center")

        self.length = tk.IntVar(value=PASSWORD_LENGTH)
        self.showing = tk.BooleanVar(value=False)

        self._build_ui()

        root.bind("<Return>", lambda e: self.new_password())
        root.bind("<space>", lambda e: self.new_password())
        root.bind("<Escape>", lambda e: self.root.destroy())
        root.bind("<Control-c>", lambda e: self.copy_password())

        self.new_password()

    # --- widgets -
    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)

        title_font = tkfont.Font(family="Helvetica", size=15, weight="bold")

        tk.Label(self.root, text="🔐", bg=BG, fg=FG,
                 font=("Helvetica", 20)).grid(row=0, column=0, pady=(16, 0))
        tk.Label(self.root, text="EASY PASSWORD GENERATOR",
                 bg=BG, fg=FG, font=title_font).grid(row=1, column=0)

        # Password field
        self.password_var = tk.StringVar()
        self.field = tk.Entry(
            self.root, textvariable=self.password_var,
            font=("Courier", 14, "bold"), justify="center",
            bg=FIELD_BG, fg=FG, relief="flat", highlightthickness=1,
            highlightbackground=FIELD_BORDER, highlightcolor=ACCENT,
        )
        self.set_visibility()
        self.field.grid(row=2, column=0, padx=28, pady=(14, 2), sticky="ew")
        self.field.configure(state="readonly")

        # Length slider row
        slider_row = tk.Frame(self.root, bg=BG)
        slider_row.grid(row=3, column=0, padx=28, sticky="ew")
        slider_row.columnconfigure(1, weight=1)

        tk.Label(slider_row, text="Length", bg=BG, fg=MUTED,
                 font=("Helvetica", 10)).grid(row=0, column=0, padx=(0, 6))
        self.len_label = tk.Label(slider_row, text=f"{self.length.get()}",
                                  bg=BG, fg=ACCENT, font=("Helvetica", 11, "bold"))
        self.len_label.grid(row=0, column=2, padx=(6, 0))

        tk.Scale(
            slider_row, variable=self.length, from_=MIN_LEN, to=MAX_LEN,
            orient="horizontal", bg=BG, fg=MUTED, troughcolor="#e2e2e6",
            highlightthickness=0, sliderrelief="flat", length=300,
            command=self._on_length_change,
        ).grid(row=0, column=1, sticky="ew")

        # Buttons row:  NEW | COPY(📋) | SHOW/HIDE(👁) | SAVE | EXIT
        row = tk.Frame(self.root, bg=BG)
        row.grid(row=4, column=0, pady=(8, 0))

        self._flat_button(row, text="NEW", bg=ACCENT, fg="#ffffff",
                          hover=ACCENT_HOVER, command=self.new_password,
                          padx=16).pack(side="left", padx=4)
        self._flat_button(row, text=COPY_ICON, bg=COPY_BG, fg=FG,
                          hover=COPY_HOVER, command=self.copy_password,
                          padx=8).pack(side="left", padx=4)
        self.eye_btn = self._flat_button(
            row, text=EYE_OFF, bg=COPY_BG, fg=FG, hover=COPY_HOVER,
            command=self.toggle_visibility, padx=8)
        self.eye_btn.pack(side="left", padx=4)
        self._flat_button(row, text="SAVE", bg=SAVE_BG, fg=NEUTRAL,
                          hover=SAVE_HOVER, command=self.export_password,
                          padx=14).pack(side="left", padx=4)
        self._flat_button(row, text="EXIT", bg=DANGER, fg="#ffffff",
                          hover=DANGER_HOVER, command=self.root.destroy,
                          padx=16).pack(side="left", padx=4)

        tk.Label(self.root,
                 text="Enter = new  ·  Ctrl+C = copy  ·  Esc = exit",
                 bg=BG, fg=MUTED, font=("Helvetica", 9)
                 ).grid(row=5, column=0, pady=(6, 10))

    def _flat_button(self, parent, text, bg, fg, hover, command, padx):
        btn = tk.Button(
            parent, text=text, bg=bg, fg=fg, relief="flat",
            activebackground=hover, activeforeground=fg,
            command=command, padx=padx, pady=6, cursor="hand2",
            font=("Helvetica", 11, "bold"),
        )
        btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=hover))
        btn.bind("<Leave>", lambda e, b=btn, c=bg: b.configure(bg=c))
        return btn

    # --- behaviour 
    def _on_length_change(self, _event=None) -> None:
        self.len_label.configure(text=f"{self.length.get()}")
        self.new_password()

    def set_visibility(self) -> None:
        self.field.configure(show="" if self.showing.get() else "•")

    def toggle_visibility(self) -> None:
        self.showing.set(not self.showing.get())
        self.set_visibility()
        self.eye_btn.configure(text=EYE_ON if self.showing.get() else EYE_OFF)

    # --- actions 
    def new_password(self) -> None:
        self.password_var.set(generate_password(self.length.get()))

    def copy_password(self) -> None:
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.root.update()  # keep clipboard data after the app closes

    def export_password(self) -> None:
        """Save the current password to a file (chosen by the user)."""
        password = self.password_var.get()
        if not password:
            return
        path = filedialog.asksaveasfilename(
            title="Save password",
            initialfile=EXPORT_FILE,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "a", encoding="utf-8") as fh:
                fh.write(f"{password}\n")
            messagebox.showinfo("Saved", f"Password saved to:\n{path}")
        except OSError as exc:
            messagebox.showerror("Error", f"Could not save file:\n{exc}")


# Entry point--------
def main() -> None:
    root = tk.Tk()
    PasswordApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
