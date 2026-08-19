import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from config.defaults import (
    OUTPUT_DIR,
    BROWSERS,
    DEFAULT_BROWSER,
    VIEWPORTS,
    DEFAULT_VIEWPORT,
)


class ConfigForm:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Spider Generator")
        self.root.resizable(False, False)

        self._build_form()
        self._center_window()

    def _center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    def _build_form(self):
        pad = {"padx": 12, "pady": 6}
        self.root.configure(bg="#f5f5f5")

        main = tk.Frame(self.root, bg="#f5f5f5")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        self._build_basic_section(main, pad)
        self._build_output_section(main, pad)
        self._build_advanced_section(main, pad)
        self._build_submit(main, pad)

    # --- Basic section ---

    def _build_basic_section(self, parent, pad):
        self._section_label(parent, "Basic Configuration")

        self.source_name = self._labeled_entry(parent, "Source name", pad)
        self.initial_url = self._labeled_entry(parent, "Initial URL", pad)

        row = tk.Frame(parent, bg="#f5f5f5")
        row.pack(fill="x", **pad)
        tk.Label(row, text="Browser", bg="#f5f5f5", width=16, anchor="w").pack(side="left")
        self.browser_var = tk.StringVar(value=DEFAULT_BROWSER)
        ttk.Combobox(
            row, textvariable=self.browser_var, values=BROWSERS,
            state="readonly", width=20,
        ).pack(side="left")

        row2 = tk.Frame(parent, bg="#f5f5f5")
        row2.pack(fill="x", **pad)
        tk.Label(row2, text="Output directory", bg="#f5f5f5", width=16, anchor="w").pack(side="left")
        self.output_dir_var = tk.StringVar(value=OUTPUT_DIR)
        tk.Entry(row2, textvariable=self.output_dir_var, width=36).pack(side="left", padx=(0, 6))
        tk.Button(row2, text="Browse", command=self._pick_output_dir).pack(side="left")

    def _pick_output_dir(self):
        path = filedialog.askdirectory(title="Select output directory")
        if path:
            self.output_dir_var.set(path)

    # --- Output section ---

    def _build_output_section(self, parent, pad):
        self._section_label(parent, "Output")

        self.out_logs = tk.BooleanVar(value=True)
        self.out_requests = tk.BooleanVar(value=False)
        self.out_playwright = tk.BooleanVar(value=False)

        frame = tk.Frame(parent, bg="#f5f5f5")
        frame.pack(fill="x", padx=12, pady=(0, 6))

        tk.Checkbutton(
            frame, text="Logs  (navigation, curls, responses)",
            variable=self.out_logs, bg="#f5f5f5",
        ).pack(anchor="w")
        tk.Checkbutton(
            frame, text="Spider — requests  (experimental)",
            variable=self.out_requests, bg="#f5f5f5",
        ).pack(anchor="w")
        tk.Checkbutton(
            frame, text="Spider — Playwright  (experimental)",
            variable=self.out_playwright, bg="#f5f5f5",
        ).pack(anchor="w")
        tk.Checkbutton(
            frame, text="Spider — Scrapy  (coming in v2)",
            bg="#f5f5f5", state="disabled",
        ).pack(anchor="w")

    # --- Advanced section ---

    def _build_advanced_section(self, parent, pad):
        self._advanced_visible = tk.BooleanVar(value=False)

        toggle_row = tk.Frame(parent, bg="#f5f5f5")
        toggle_row.pack(fill="x", padx=12, pady=(8, 0))

        self._adv_toggle_btn = tk.Button(
            toggle_row, text="▶  Advanced settings",
            bg="#f5f5f5", relief="flat", anchor="w",
            command=self._toggle_advanced,
        )
        self._adv_toggle_btn.pack(fill="x")

        self._adv_frame = tk.Frame(parent, bg="#f5f5f5")

        self._build_capture_scope(self._adv_frame, pad)
        self._build_domain_scope(self._adv_frame, pad)
        self._build_noise_filter(self._adv_frame, pad)
        self._build_viewport(self._adv_frame, pad)
        self._build_user_agent(self._adv_frame, pad)

    def _toggle_advanced(self):
        if self._advanced_visible.get():
            self._adv_frame.pack_forget()
            self._advanced_visible.set(False)
            self._adv_toggle_btn.config(text="▶  Advanced settings")
        else:
            self._adv_frame.pack(fill="x")
            self._advanced_visible.set(True)
            self._adv_toggle_btn.config(text="▼  Advanced settings")
        self._center_window()

    def _build_capture_scope(self, parent, pad):
        tk.Label(parent, text="Capture scope", bg="#f5f5f5", anchor="w").pack(
            fill="x", padx=12, pady=(8, 2)
        )
        frame = tk.Frame(parent, bg="#f5f5f5")
        frame.pack(fill="x", padx=24, pady=(0, 4))

        self.scope_all = tk.BooleanVar(value=True)
        self.scope_fetch_xhr = tk.BooleanVar(value=False)
        self.scope_document = tk.BooleanVar(value=False)
        self.scope_script = tk.BooleanVar(value=False)

        self._scope_checks = {
            "fetch_xhr": self.scope_fetch_xhr,
            "document": self.scope_document,
            "script": self.scope_script,
        }

        tk.Checkbutton(
            frame, text="All", variable=self.scope_all,
            bg="#f5f5f5", command=self._on_scope_all,
        ).pack(anchor="w")
        tk.Checkbutton(
            frame, text="Fetch / XHR", variable=self.scope_fetch_xhr,
            bg="#f5f5f5", command=self._on_scope_specific,
        ).pack(anchor="w")
        tk.Checkbutton(
            frame, text="Document", variable=self.scope_document,
            bg="#f5f5f5", command=self._on_scope_specific,
        ).pack(anchor="w")
        tk.Checkbutton(
            frame, text="Script (JS)", variable=self.scope_script,
            bg="#f5f5f5", command=self._on_scope_specific,
        ).pack(anchor="w")

    def _on_scope_all(self):
        if self.scope_all.get():
            for var in self._scope_checks.values():
                var.set(False)

    def _on_scope_specific(self):
        if any(v.get() for v in self._scope_checks.values()):
            self.scope_all.set(False)
        else:
            self.scope_all.set(True)

    def _build_domain_scope(self, parent, pad):
        tk.Label(parent, text="Domain scope", bg="#f5f5f5", anchor="w").pack(
            fill="x", padx=12, pady=(8, 2)
        )
        frame = tk.Frame(parent, bg="#f5f5f5")
        frame.pack(fill="x", padx=24, pady=(0, 4))

        self.domain_scope_var = tk.StringVar(value="main")
        tk.Radiobutton(
            frame, text="Main domain only", variable=self.domain_scope_var,
            value="main", bg="#f5f5f5",
        ).pack(anchor="w")
        tk.Radiobutton(
            frame, text="Include subdomains", variable=self.domain_scope_var,
            value="subdomains", bg="#f5f5f5",
        ).pack(anchor="w")

    def _build_noise_filter(self, parent, pad):
        row = tk.Frame(parent, bg="#f5f5f5")
        row.pack(fill="x", padx=12, pady=(8, 4))
        self.noise_filter_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            row,
            text="Filter noise  (analytics, tracking, CDN)",
            variable=self.noise_filter_var,
            bg="#f5f5f5",
        ).pack(anchor="w")

    def _build_viewport(self, parent, pad):
        row = tk.Frame(parent, bg="#f5f5f5")
        row.pack(fill="x", padx=12, pady=6)
        tk.Label(row, text="Viewport", bg="#f5f5f5", width=16, anchor="w").pack(side="left")
        self.viewport_var = tk.StringVar(value=DEFAULT_VIEWPORT)
        ttk.Combobox(
            row, textvariable=self.viewport_var, values=VIEWPORTS,
            state="readonly", width=20,
        ).pack(side="left")

    def _build_user_agent(self, parent, pad):
        row = tk.Frame(parent, bg="#f5f5f5")
        row.pack(fill="x", padx=12, pady=6)
        tk.Label(row, text="User agent", bg="#f5f5f5", width=16, anchor="w").pack(side="left")
        self.user_agent_var = tk.StringVar(value="")
        tk.Entry(row, textvariable=self.user_agent_var, width=36).pack(side="left")

    # --- Submit ---

    def _build_submit(self, parent, pad):
        ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=12)
        tk.Button(
            parent, text="Start", command=self._on_submit,
            bg="#2b7de9", fg="white", relief="flat",
            padx=24, pady=8, font=("Helvetica", 10, "bold"),
        ).pack(anchor="e")

    def _on_submit(self):
        source = self.source_name.get().strip()
        url = self.initial_url.get().strip()

        if not source:
            messagebox.showerror("Validation error", "Source name is required.")
            return
        if not url:
            messagebox.showerror("Validation error", "Initial URL is required.")
            return
        if not url.startswith(("http://", "https://")):
            messagebox.showerror("Validation error", "Initial URL must start with http:// or https://")
            return
        if not any([self.out_logs.get(), self.out_requests.get(), self.out_playwright.get()]):
            messagebox.showerror("Validation error", "Select at least one output option.")
            return

        config = self._build_config()
        self.root.destroy()
        self._on_config_ready(config)

    def _build_config(self):
        if self.scope_all.get():
            scope = ["all"]
        else:
            scope = [k for k, v in self._scope_checks.items() if v.get()]

        vp = self.viewport_var.get().split("x")

        return {
            "source_name": self.source_name.get().strip(),
            "initial_url": self.initial_url.get().strip(),
            "browser": self.browser_var.get(),
            "output_dir": self.output_dir_var.get(),
            "output": {
                "logs": self.out_logs.get(),
                "spider_requests": self.out_requests.get(),
                "spider_playwright": self.out_playwright.get(),
            },
            "capture_scope": scope,
            "domain_scope": self.domain_scope_var.get(),
            "filter_noise": self.noise_filter_var.get(),
            "viewport": {"width": int(vp[0]), "height": int(vp[1])},
            "user_agent": self.user_agent_var.get().strip() or None,
        }

    def _on_config_ready(self, config):
        # Phase 3 hook — browser will be launched here
        print(config)

    # --- Helpers ---

    def _section_label(self, parent, text):
        tk.Label(
            parent, text=text, bg="#f5f5f5",
            font=("Helvetica", 10, "bold"), anchor="w",
        ).pack(fill="x", padx=12, pady=(12, 2))
        ttk.Separator(parent, orient="horizontal").pack(fill="x", padx=12, pady=(0, 4))

    def _labeled_entry(self, parent, label, pad):
        row = tk.Frame(parent, bg="#f5f5f5")
        row.pack(fill="x", **pad)
        tk.Label(row, text=label, bg="#f5f5f5", width=16, anchor="w").pack(side="left")
        var = tk.StringVar()
        tk.Entry(row, textvariable=var, width=36).pack(side="left")
        return var

    def run(self):
        self.root.mainloop()
