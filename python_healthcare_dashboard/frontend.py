import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from database import insert_evaluation, fetch_all_evaluations, fetch_patient_history
from engine import evaluate_ckd_status, calculate_egfr

class CKDDashboardUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CKD Clinical Dashboard")
        self.geometry("1280x820")
        
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.build_sidebar()
        self.build_main_view()
        self.show_entry_form()

    def build_sidebar(self):
        sidebar = tk.Frame(self, bg="#0f172a", width=230)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        title = tk.Label(sidebar, text="NEPHRO-DIAG", fg="#f8fafc", bg="#0f172a", font=("Helvetica", 16, "bold"))
        title.pack(pady=25)

        btn_new = tk.Button(sidebar, text="✚ New Assessment", bg="#1e293b", fg="white",
                            relief="flat", anchor="w", command=self.show_entry_form, padx=15, pady=8)
        btn_new.pack(fill="x", pady=4)

        btn_analytics = tk.Button(sidebar, text="📈 Progression Graph", bg="#1e293b", fg="white",
                                   relief="flat", anchor="w", command=self.show_analytics, padx=15, pady=8)
        btn_analytics.pack(fill="x", pady=4)

        btn_records = tk.Button(sidebar, text="📋 Dataset Records", bg="#1e293b", fg="white",
                                relief="flat", anchor="w", command=self.show_records, padx=15, pady=8)
        btn_records.pack(fill="x", pady=4)

    def build_main_view(self):
        self.main_frame = ttk.Frame(self, padding="15")
        self.main_frame.grid(row=0, column=1, sticky="nsew")

    def clear_view(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_entry_form(self):
        self.clear_view()

        header = ttk.Label(self.main_frame, text="Patient Diagnostic Evaluation", font=("Helvetica", 16, "bold"))
        header.pack(anchor="w", pady=(0, 10))

        canvas = tk.Canvas(self.main_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Section 1: Demographics & Vitals
        sec1 = ttk.LabelFrame(scroll_frame, text="1. Demographics & Vitals", padding="10")
        sec1.pack(fill="x", expand=True, pady=5)

        ttk.Label(sec1, text="Patient ID:").grid(row=0, column=0, sticky="w", padx=5)
        self.e_pid = ttk.Entry(sec1, width=12)
        self.e_pid.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(sec1, text="Age:").grid(row=0, column=2, sticky="w", padx=5)
        self.e_age = ttk.Entry(sec1, width=12)
        self.e_age.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(sec1, text="Blood Pressure (mmHg):").grid(row=0, column=4, sticky="w", padx=5)
        self.e_bp = ttk.Entry(sec1, width=12)
        self.e_bp.grid(row=0, column=5, padx=5, pady=2)

        # Section 2: Urinalysis
        sec2 = ttk.LabelFrame(scroll_frame, text="2. Urinalysis Panel", padding="10")
        sec2.pack(fill="x", expand=True, pady=5)

        ttk.Label(sec2, text="Urine Spec. Gravity:").grid(row=0, column=0, sticky="w", padx=5)
        self.e_sg = ttk.Entry(sec2, width=12)
        self.e_sg.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(sec2, text="Albumin in Urine:").grid(row=0, column=2, sticky="w", padx=5)
        self.e_al = ttk.Entry(sec2, width=12)
        self.e_al.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(sec2, text="Sugar in Urine:").grid(row=0, column=4, sticky="w", padx=5)
        self.e_su = ttk.Entry(sec2, width=12)
        self.e_su.grid(row=0, column=5, padx=5, pady=2)

        ttk.Label(sec2, text="RBC:").grid(row=1, column=0, sticky="w", padx=5)
        self.c_rbc = ttk.Combobox(sec2, values=["normal", "abnormal"], state="readonly", width=10)
        self.c_rbc.grid(row=1, column=1, padx=5, pady=2)
        self.c_rbc.current(0)

        ttk.Label(sec2, text="Pus Cells:").grid(row=1, column=2, sticky="w", padx=5)
        self.c_pc = ttk.Combobox(sec2, values=["normal", "abnormal"], state="readonly", width=10)
        self.c_pc.grid(row=1, column=3, padx=5, pady=2)
        self.c_pc.current(0)

        ttk.Label(sec2, text="Pus Cell Clumps:").grid(row=1, column=4, sticky="w", padx=5)
        self.c_pcc = ttk.Combobox(sec2, values=["absent", "present"], state="readonly", width=10)
        self.c_pcc.grid(row=1, column=5, padx=5, pady=2)
        self.c_pcc.current(0)

        ttk.Label(sec2, text="Bacteria:").grid(row=2, column=0, sticky="w", padx=5)
        self.c_ba = ttk.Combobox(sec2, values=["absent", "present"], state="readonly", width=10)
        self.c_ba.grid(row=2, column=1, padx=5, pady=2)
        self.c_ba.current(0)

        # Section 3: Blood Biochemistry
        sec3 = ttk.LabelFrame(scroll_frame, text="3. Blood Biochemistry & Electrolytes", padding="10")
        sec3.pack(fill="x", expand=True, pady=5)

        ttk.Label(sec3, text="Random Blood Glucose:").grid(row=0, column=0, sticky="w", padx=5)
        self.e_bgr = ttk.Entry(sec3, width=12)
        self.e_bgr.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(sec3, text="Blood Urea:").grid(row=0, column=2, sticky="w", padx=5)
        self.e_bu = ttk.Entry(sec3, width=12)
        self.e_bu.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(sec3, text="Serum Creatinine:").grid(row=0, column=4, sticky="w", padx=5)
        self.e_sc = ttk.Entry(sec3, width=12)
        self.e_sc.grid(row=0, column=5, padx=5, pady=2)

        ttk.Label(sec3, text="Sodium in Blood:").grid(row=1, column=0, sticky="w", padx=5)
        self.e_sod = ttk.Entry(sec3, width=12)
        self.e_sod.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(sec3, text="Potassium in Blood:").grid(row=1, column=2, sticky="w", padx=5)
        self.e_pot = ttk.Entry(sec3, width=12)
        self.e_pot.grid(row=1, column=3, padx=5, pady=2)

        # Section 4: Hematology
        sec4 = ttk.LabelFrame(scroll_frame, text="4. Hematology & Symptoms", padding="10")
        sec4.pack(fill="x", expand=True, pady=5)

        ttk.Label(sec4, text="Hemoglobin:").grid(row=0, column=0, sticky="w", padx=5)
        self.e_hemo = ttk.Entry(sec4, width=12)
        self.e_hemo.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(sec4, text="Packed Corpuscular Vol:").grid(row=0, column=2, sticky="w", padx=5)
        self.e_pcv = ttk.Entry(sec4, width=12)
        self.e_pcv.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(sec4, text="WBC Count:").grid(row=0, column=4, sticky="w", padx=5)
        self.e_wc = ttk.Entry(sec4, width=12)
        self.e_wc.grid(row=0, column=5, padx=5, pady=2)

        ttk.Label(sec4, text="RBC Count:").grid(row=1, column=0, sticky="w", padx=5)
        self.e_rc = ttk.Entry(sec4, width=12)
        self.e_rc.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(sec4, text="Appetite:").grid(row=1, column=2, sticky="w", padx=5)
        self.c_app = ttk.Combobox(sec4, values=["good", "poor"], state="readonly", width=10)
        self.c_app.grid(row=1, column=3, padx=5, pady=2)
        self.c_app.current(0)

        # Submit
        btn_eval = tk.Button(scroll_frame, text="Run CKD Diagnosis & Save", bg="#2563eb", fg="white",
                             font=("Helvetica", 11, "bold"), command=self.handle_submit, padx=10, pady=6)
        btn_eval.pack(fill="x", pady=15)

    def handle_submit(self):
        try:
            pid = int(self.e_pid.get())
            age = int(self.e_age.get())
            sc = float(self.e_sc.get())
            bu = float(self.e_bu.get() or 0)
            hb = float(self.e_hemo.get() or 14)
            al = float(self.e_al.get() or 0)

            diag, egfr, stage, reasons = evaluate_ckd_status(sc, age, bu, hb, al)

            record_data = {
                'patient_id': pid, 'age': age, 'blood_pressure': int(self.e_bp.get() or 0),
                'urine_sp_gravity': float(self.e_sg.get() or 0), 'albumin_in_urine': al,
                'sugar_in_urine': int(self.e_su.get() or 0), 'rbc': self.c_rbc.get(),
                'pus_cells': self.c_pc.get(), 'pus_cell_clumps': self.c_pcc.get(),
                'bacteria': self.c_ba.get(), 'random_blood_glucose': int(self.e_bgr.get() or 0),
                'blood_urea': bu, 'serum_creatinine': sc, 'sodium': float(self.e_sod.get() or 0),
                'potassium': float(self.e_pot.get() or 0), 'hemoglobin': hb,
                'pcv': float(self.e_pcv.get() or 0), 'wbc_count': int(self.e_wc.get() or 0),
                'rbc_count': float(self.e_rc.get() or 0), 'appetite': self.c_app.get(),
                'ckd_diagnosis': diag
            }

            insert_evaluation(record_data)

            status = "POSITIVE for CKD" if diag == "yes" else "NEGATIVE for CKD"
            msg = f"Diagnosis Result: {status}\neGFR: {egfr} mL/min/1.73m²\nKDIGO Stage: {stage}\n\nIndicators:\n" + "\n".join(f"- {r}" for r in reasons)
            messagebox.showinfo("Diagnostic Result", msg)

        except ValueError:
            messagebox.showerror("Input Error", "Ensure Patient ID, Age, and Serum Creatinine are valid numbers.")

    def show_analytics(self):
        self.clear_view()

        header = ttk.Label(self.main_frame, text="Patient eGFR Trajectory Analytics", font=("Helvetica", 16, "bold"))
        header.pack(anchor="w", pady=(0, 10))

        search_frame = ttk.Frame(self.main_frame)
        search_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(search_frame, text="Enter Patient ID:").pack(side="left", padx=5)
        entry_pid = ttk.Entry(search_frame, width=12)
        entry_pid.pack(side="left", padx=5)

        plot_container = ttk.Frame(self.main_frame)
        plot_container.pack(fill="both", expand=True)

        def plot_patient():
            for w in plot_container.winfo_children():
                w.destroy()

            try:
                pid = int(entry_pid.get())
                records = fetch_patient_history(pid)

                if not records:
                    messagebox.showinfo("No Data", f"No records found for Patient ID: {pid}")
                    return

                eval_ids = [r[0] for r in records]
                egfrs = [calculate_egfr(r[3], r[2]) for r in records]

                fig, ax = plt.subplots(figsize=(7, 3.5), dpi=100)
                ax.plot(eval_ids, egfrs, marker='o', color='#2563eb', linewidth=2, label="eGFR Trend")
                ax.axhline(60, color='orange', linestyle='--', label='CKD Threshold (<60)')
                ax.axhline(15, color='red', linestyle='--', label='Renal Failure (<15)')
                ax.set_title(f"eGFR Longitudinal Trend - Patient ID {pid}")
                ax.set_xlabel("Evaluation Session ID")
                ax.set_ylabel("eGFR (mL/min/1.73m²)")
                ax.set_ylim(0, 140)
                ax.legend(loc="upper right")
                ax.grid(True, linestyle=":", alpha=0.6)

                canvas = FigureCanvasTkAgg(fig, master=plot_container)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)

            except ValueError:
                messagebox.showerror("Error", "Enter a valid Patient ID integer.")

        btn_plot = tk.Button(search_frame, text="Plot Trajectory", bg="#2563eb", fg="white", command=plot_patient, padx=10)
        btn_plot.pack(side="left", padx=5)

    def show_records(self):
        self.clear_view()

        header = ttk.Label(self.main_frame, text="Historical Diagnostic Database", font=("Helvetica", 16, "bold"))
        header.pack(anchor="w", pady=(0, 10))

        cols = ("ID", "Patient ID", "Age", "BP", "Serum Creatinine", "Blood Urea", "Hb", "CKD Diagnosis")
        tree = ttk.Treeview(self.main_frame, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=110)

        tree.pack(fill="both", expand=True)

        for row in fetch_all_evaluations():
            tree.insert("", "end", values=row)