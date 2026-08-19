import queue
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox


class AnnotationPanel:
    def __init__(self, config, session, record_queue, on_finish):
        self._config = config
        self._session = session
        self._queue = record_queue
        self._on_finish = on_finish
        self._records = []
        self._selected_index = None

        self._root = tk.Tk()
        self._root.title(f"Annotation Panel — {config['source_name']}")
        self._root.geometry("700x500")
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_ui()
        self._center_window()

    def _center_window(self):
        self._root.update_idletasks()
        w = self._root.winfo_width()
        h = self._root.winfo_height()
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        self._root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    def _build_ui(self):
        bg = "#f5f5f5"
        self._root.configure(bg=bg)

        top = tk.Frame(self._root, bg=bg)
        top.pack(fill="both", expand=True, padx=12, pady=(12, 0))

        # Request list
        list_frame = tk.Frame(top, bg=bg)
        list_frame.pack(fill="both", expand=True)

        tk.Label(list_frame, text="Captured requests", bg=bg,
                 font=("Helvetica", 9, "bold"), anchor="w").pack(fill="x")

        scroll = tk.Scrollbar(list_frame, orient="vertical")
        self._listbox = tk.Listbox(
            list_frame, yscrollcommand=scroll.set,
            selectmode="single", font=("Courier", 9),
            activestyle="none",
        )
        scroll.config(command=self._listbox.yview)
        scroll.pack(side="right", fill="y")
        self._listbox.pack(side="left", fill="both", expand=True)
        self._listbox.bind("<<ListboxSelect>>", self._on_select)

        # Action buttons for selected request
        action_frame = tk.Frame(self._root, bg=bg)
        action_frame.pack(fill="x", padx=12, pady=6)

        tk.Label(action_frame, text="Selected request:", bg=bg,
                 font=("Helvetica", 9, "bold")).pack(side="left")

        self._btn_note = tk.Button(
            action_frame, text="Add note", state="disabled",
            command=self._add_request_note, relief="flat", bg="#e0e0e0",
        )
        self._btn_note.pack(side="left", padx=(8, 4))

        self._btn_exclude = tk.Button(
            action_frame, text="Exclude", state="disabled",
            command=self._toggle_exclude, relief="flat", bg="#e0e0e0",
        )
        self._btn_exclude.pack(side="left", padx=4)

        ttk.Separator(self._root, orient="horizontal").pack(fill="x", padx=12, pady=4)

        # Session note
        note_frame = tk.Frame(self._root, bg=bg)
        note_frame.pack(fill="x", padx=12, pady=(0, 6))

        tk.Label(note_frame, text="Session note:", bg=bg,
                 font=("Helvetica", 9, "bold")).pack(side="left")
        self._note_var = tk.StringVar()
        tk.Entry(note_frame, textvariable=self._note_var, width=40).pack(
            side="left", padx=(8, 4)
        )
        tk.Button(
            note_frame, text="Add", command=self._add_session_note,
            relief="flat", bg="#e0e0e0",
        ).pack(side="left")

        ttk.Separator(self._root, orient="horizontal").pack(fill="x", padx=12, pady=4)

        # Counter + Finish
        bottom = tk.Frame(self._root, bg=bg)
        bottom.pack(fill="x", padx=12, pady=(0, 12))

        self._counter_var = tk.StringVar(value="0 requests captured")
        tk.Label(bottom, textvariable=self._counter_var, bg=bg,
                 font=("Helvetica", 9), fg="#666").pack(side="left")

        self._btn_finish = tk.Button(
            bottom, text="Finish", command=self._on_finish_click,
            bg="#2b7de9", fg="white", relief="flat",
            padx=20, pady=6, font=("Helvetica", 10, "bold"),
        )
        self._btn_finish.pack(side="right")

    # --- Queue polling ---

    def _poll_queue(self):
        try:
            while True:
                record = self._queue.get_nowait()
                self._records.append(record)
                self._add_listbox_entry(record)
                self._counter_var.set(f"{len(self._records)} requests captured")
        except queue.Empty:
            pass
        self._root.after(300, self._poll_queue)

    def _add_listbox_entry(self, record):
        label = f"[{record['index']:03}] {record['method']:<6} {record['status']}  {record['url']}"
        self._listbox.insert("end", label)
        self._listbox.see("end")

    # --- Selection ---

    def _on_select(self, _event):
        sel = self._listbox.curselection()
        if not sel:
            return
        self._selected_index = sel[0]
        record = self._records[self._selected_index]
        self._btn_note.config(state="normal")
        self._btn_exclude.config(
            state="normal",
            text="Include" if record.get("excluded") else "Exclude",
        )

    # --- Request actions ---

    def _add_request_note(self):
        if self._selected_index is None:
            return
        note = simpledialog.askstring(
            "Add note", "Note for this request:", parent=self._root
        )
        if note and note.strip():
            self._records[self._selected_index]["notes"].append(note.strip())

    def _toggle_exclude(self):
        if self._selected_index is None:
            return
        record = self._records[self._selected_index]
        record["excluded"] = not record.get("excluded", False)
        self._btn_exclude.config(text="Include" if record["excluded"] else "Exclude")
        label = self._listbox.get(self._selected_index)
        if record["excluded"]:
            self._listbox.itemconfig(self._selected_index, fg="#aaaaaa", selectforeground="#aaaaaa")
        else:
            self._listbox.itemconfig(self._selected_index, fg="black", selectforeground="black")

    # --- Session notes ---

    def _add_session_note(self):
        note = self._note_var.get().strip()
        if not note:
            return
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        session_note = {
            "type": "session_note",
            "text": note,
            "timestamp": timestamp,
            "after_index": len(self._records),
        }
        self._records.append(session_note)
        self._listbox.insert("end", f"--- NOTE [{timestamp}]: {note}")
        self._listbox.itemconfig("end", fg="#0066cc")
        self._listbox.see("end")
        self._note_var.set("")

    # --- Finish ---

    def _on_finish_click(self):
        if not messagebox.askyesno("Finish session", "Stop recording and generate outputs?"):
            return
        self._btn_finish.config(state="disabled", text="Finishing...")
        self._session.stop()
        self._root.after(500, self._finalize)

    def _finalize(self):
        self._root.destroy()
        self._on_finish(self._records)

    def _on_close(self):
        if messagebox.askyesno("Close", "Close without generating outputs?"):
            self._session.stop()
            self._root.destroy()

    def run(self):
        self._root.after(300, self._poll_queue)
        self._root.mainloop()
