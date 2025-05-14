import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip


def calculate_chmod():
    user = (user_read.get() << 2) | (user_write.get() << 1) | user_exec.get()
    group = (group_read.get() << 2) | (group_write.get() << 1) | group_exec.get()
    other = (other_read.get() << 2) | (other_write.get() << 1) | other_exec.get()
    special = (suid.get() << 2) | (sgid.get() << 1) | sticky.get()
    return int(f"{special}{user}{group}{other}", 8)


def permission_string_to_octal(perm_str):
    if len(perm_str) != 10:
        raise ValueError("Permission string must be 10 characters long.")

    special = 0
    mapping = {'r': 4, 'w': 2, 'x': 1, '-': 0, 's': 1, 'S': 0, 't': 1, 'T': 0}
    modes = []
    for i in range(1, 10, 3):
        modes.append(sum(mapping.get(perm_str[j], 0) for j in range(i, i + 3)))

    if perm_str[3] in ['s', 'S']:
        special += 4
    if perm_str[6] in ['s', 'S']:
        special += 2
    if perm_str[9] in ['t', 'T']:
        special += 1

    return int(f"{special}{modes[0]}{modes[1]}{modes[2]}", 8)


def generate_commands(target, mode):
    chmod_octal = f"{mode:o}"
    cmds = {
        "Files in folder": f"find '{target}' -maxdepth 1 -type f -exec chmod {chmod_octal} {{}} +",
        "Folders in folder": f"find '{target}' -maxdepth 1 -type d -exec chmod {chmod_octal} {{}} +",
        "Folders and subfolders (recursive)": f"find '{target}' -type d -exec chmod {chmod_octal} {{}} +",
        "Files in subfolders": f"find '{target}' -mindepth 2 -type f -exec chmod {chmod_octal} {{}} +",
        "Everything recursively (files and folders)": f"chmod -R {chmod_octal} '{target}'"
    }
    return cmds


def show_commands(frame, cmds):
    for widget in frame.winfo_children():
        widget.destroy()

    ttk.Label(frame, text="Ready-to-copy chmod commands:").pack(anchor="w", pady=(5, 3))
    for label, cmd in cmds.items():
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=2)
        ttk.Label(row, text=label + ":").pack(side="left")
        entry = ttk.Entry(row, width=80)
        entry.insert(0, cmd)
        entry.config(state="readonly")
        entry.pack(side="left", padx=5)

        def copy_cmd(c=cmd):
            pyperclip.copy(c)
            messagebox.showinfo("Copied", f"Command copied:\n{c}")

        ttk.Button(row, text="Copy", command=copy_cmd).pack(side="left")


app = tk.Tk()
app.title("Chmod GUI Tool")

notebook = ttk.Notebook(app)
notebook.pack(padx=10, pady=10, fill="both", expand=True)

# Tab 1: Manual Mode
tab_manual = ttk.Frame(notebook)
notebook.add(tab_manual, text="Manual Mode")

perm_frame = ttk.LabelFrame(tab_manual, text="Permissions")
perm_frame.pack(padx=10, pady=10, fill="x")

user_read = tk.IntVar()
user_write = tk.IntVar()
user_exec = tk.IntVar()
group_read = tk.IntVar()
group_write = tk.IntVar()
group_exec = tk.IntVar()
other_read = tk.IntVar()
other_write = tk.IntVar()
other_exec = tk.IntVar()
suid = tk.IntVar()
sgid = tk.IntVar()
sticky = tk.IntVar()

entities = [("User", user_read, user_write, user_exec),
            ("Group", group_read, group_write, group_exec),
            ("Other", other_read, other_write, other_exec)]

for i, (label, r, w, x) in enumerate(entities):
    ttk.Label(perm_frame, text=label).grid(row=i, column=0)
    ttk.Checkbutton(perm_frame, text="Read", variable=r).grid(row=i, column=1)
    ttk.Checkbutton(perm_frame, text="Write", variable=w).grid(row=i, column=2)
    ttk.Checkbutton(perm_frame, text="Execute", variable=x).grid(row=i, column=3)

ttk.Label(perm_frame, text="Special Bits").grid(row=3, column=0)

ttk.Checkbutton(perm_frame, text="Set UID", variable=suid).grid(row=3, column=1)
ttk.Checkbutton(perm_frame, text="Set GID", variable=sgid).grid(row=3, column=2)
ttk.Checkbutton(perm_frame, text="Sticky Bit", variable=sticky).grid(row=3, column=3)

file_entry = ttk.Entry(tab_manual, width=80)
file_entry.pack(pady=5)
file_entry.insert(0, "/your/path/here")

command_frame = ttk.Frame(tab_manual)
command_frame.pack(padx=10, pady=10, fill="x")

ttks_btn = ttk.Button(tab_manual, text="Generate chmod commands",
                     command=lambda: show_commands(command_frame, generate_commands(file_entry.get().strip(), calculate_chmod())))
ttks_btn.pack(pady=5)

# Tab 2: String Mode
tab_string = ttk.Frame(notebook)
notebook.add(tab_string, text="Permission String Mode")

string_entry = ttk.Entry(tab_string, width=30)
string_entry.pack(pady=5)
string_entry.insert(0, "drwxrwsr-x")

string_path = ttk.Entry(tab_string, width=80)
string_path.pack(pady=5)
string_path.insert(0, "/your/path/here")

command_frame2 = ttk.Frame(tab_string)
command_frame2.pack(padx=10, pady=10, fill="x")

string_btn = ttk.Button(tab_string, text="Generate chmod commands",
                        command=lambda: show_commands(command_frame2, generate_commands(string_path.get().strip(), permission_string_to_octal(string_entry.get().strip()))))
string_btn.pack(pady=5)

app.mainloop()
