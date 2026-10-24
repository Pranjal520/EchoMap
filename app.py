
import json
from pathlib import Path
from datetime import datetime

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# EchoMap: evidence mapping prototype
evidence = []


def add_evidence():
    text = observation.get().strip()
    source = source_type.get()

    if not text:
        messagebox.showwarning("Missing evidence", "Enter an observation first.")
        return

    item = {
        "id": f"E{len(evidence) + 1}",
        "source": source,
        "observation": text,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    evidence.append(item)
    tree.insert("", "end", values=(
        item["id"], item["source"], item["observation"]
    ))
    observation.delete(0, tk.END)
    status.set(f"{len(evidence)} evidence item(s) added.")


def upload_files():
    files = filedialog.askopenfilenames(
        title="Select scene evidence",
        filetypes=[
            ("Evidence files", "*.txt *.md *.json *.csv *.jpg *.jpeg *.png *.pdf"),
            ("All files", "*.*"),
        ],
    )
    for filename in files:
        path = Path(filename)
        evidence.append({
            "id": f"E{len(evidence) + 1}",
            "source": "Uploaded file",
            "observation": f"File: {path.name}",
            "file_path": str(path),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        })
        item = evidence[-1]
        tree.insert("", "end", values=(
            item["id"], item["source"], item["observation"]
        ))
    status.set(f"{len(evidence)} evidence item(s) recorded.")


def analyse():
    if not evidence:
        messagebox.showinfo("No evidence", "Add observations or upload files first.")
        return

    # This initial version identifies shared keywords only.
    # It does not claim to perform AI reasoning.
    stopwords = {
        "the", "and", "for", "with", "from", "that", "this",
        "was", "were", "has", "have", "there", "near", "into",
        "visible", "image", "photo", "appears", "observation",
    }

    result = []
    for i, first in enumerate(evidence):
        for second in evidence[i + 1:]:
            words_a = {
                w.strip(".,!?():;").lower()
                for w in first["observation"].split()
            } - stopwords
            words_b = {
                w.strip(".,!?():;").lower()
                for w in second["observation"].split()
            } - stopwords
            shared = words_a & words_b
            if shared:
                result.append(
                    f"{first['id']} ↔ {second['id']}: "
                    f"shared terms: {', '.join(sorted(shared))}"
                )

    report.delete("1.0", tk.END)
    report.insert(tk.END, "ECHOMAP — EVIDENCE ANALYSIS\n")
    report.insert(tk.END, "=" * 36 + "\n\n")
    report.insert(tk.END, f"Evidence items: {len(evidence)}\n\n")
    report.insert(tk.END, "OBSERVATIONS\n")
    for item in evidence:
        report.insert(
            tk.END,
            f"{item['id']} [{item['source']}]: "
            f"{item['observation']}\n"
        )

    report.insert(tk.END, "\nPOSSIBLE KEYWORD LINKS\n")
    if result:
        for link in result:
            report.insert(tk.END, f"• {link}\n")
    else:
        report.insert(tk.END, "No shared keywords found.\n")

    report.insert(
        tk.END,
        "\nLIMITATION: Keyword overlap is not proof of a real-world "
        "relationship or contradiction. Gemma reasoning is not connected yet.\n"
    )
    status.set("Basic analysis complete.")


def export_report():
    if not evidence:
        messagebox.showinfo("No evidence", "Add evidence before exporting.")
        return

    filename = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON report", "*.json")],
        initialfile="echomap_report.json",
    )
    if not filename:
        return

    with open(filename, "w", encoding="utf-8") as file:
        json.dump({
            "project": "EchoMap",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "evidence": evidence,
            "note": "Keyword matching only; no AI conclusions generated.",
        }, file, indent=2, ensure_ascii=False)

    status.set(f"Report exported: {Path(filename).name}")


root = tk.Tk()
root.title("EchoMap | Evidence Intelligence")
root.geometry("1050x700")
root.minsize(850, 550)

style = ttk.Style()
style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

header = tk.Frame(root, bg="#14213D", padx=20, pady=16)
header.pack(fill="x")
tk.Label(
    header, text="ECHOMAP", font=("Segoe UI", 23, "bold"),
    fg="white", bg="#14213D"
).pack(anchor="w")
tk.Label(
    header,
    text="Multi-source evidence mapping • Prototype",
    font=("Segoe UI", 10), fg="#D8E4FF", bg="#14213D"
).pack(anchor="w")

main = ttk.Frame(root, padding=16)
main.pack(fill="both", expand=True)

ttk.Label(main, text="Add an evidence observation",
          font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 8))

entry_row = ttk.Frame(main)
entry_row.pack(fill="x", pady=(0, 12))

source_type = tk.StringVar(value="Written observation")
ttk.Label(entry_row, text="Source:").pack(side="left", padx=(0, 6))
ttk.Combobox(
    entry_row, textvariable=source_type, state="readonly", width=20,
    values=["Written observation", "Scene photo", "Floor plan",
            "Document", "Witness note"]
).pack(side="left", padx=(0, 12))

observation = ttk.Entry(entry_row)
observation.pack(side="left", fill="x", expand=True, padx=(0, 8))
observation.bind("<Return>", lambda event: add_evidence())
ttk.Button(entry_row, text="Add evidence",
           command=add_evidence).pack(side="left")

actions = ttk.Frame(main)
actions.pack(fill="x", pady=(0, 12))
ttk.Button(actions, text="Upload files", command=upload_files).pack(side="left")
ttk.Button(actions, text="Analyse evidence", command=analyse).pack(
    side="left", padx=8
)
ttk.Button(actions, text="Export JSON report",
           command=export_report).pack(side="left")

ttk.Label(main, text="Evidence register",
          font=("Segoe UI", 12, "bold")).pack(anchor="w")

columns = ("id", "source", "observation")
tree = ttk.Treeview(main, columns=columns, show="headings", height=8)
tree.heading("id", text="ID")
tree.heading("source", text="Source")
tree.heading("observation", text="Observation / file")
tree.column("id", width=65, stretch=False)
tree.column("source", width=180, stretch=False)
tree.column("observation", width=600)
tree.pack(fill="both", expand=True, pady=(6, 12))

ttk.Label(main, text="Analysis report",
          font=("Segoe UI", 12, "bold")).pack(anchor="w")
report = tk.Text(main, height=8, wrap="word", font=("Consolas", 10))
report.pack(fill="both", expand=True, pady=(6, 8))

status = tk.StringVar(value="Ready — add your first evidence item.")
ttk.Label(root, textvariable=status, relief="sunken",
          anchor="w", padding=6).pack(fill="x")

root.mainloop()
