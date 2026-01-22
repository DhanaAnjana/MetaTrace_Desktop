import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import json
from pathlib import Path
from core.extracter import extract_file_metadata, extract_multiple_files, scan_folder, detect_anomalies
from core.hash_utils import calculate_all_hashes
from core.case_manager import create_case, export_case_json, generate_summary
from core.report_generator import export_csv, export_pdf, export_html
from core.logger import log_action, export_logs, get_logs_summary, get_all_logs
from core.email_sender import send_report_email
from core.project_info import get_info_text


def start_gui():
    root = tk.Tk()
    root.title("MetaTrace Desktop")
    root.geometry("1000x800")
    
    selected_files = []
    case_data = None
    
    def browse_files():
        nonlocal selected_files
        files = filedialog.askopenfilenames()
        if files:
            selected_files = list(files)
            update_file_list()
    
    def browse_folder():
        nonlocal selected_files
        folder = filedialog.askdirectory()
        if folder:
            recursive = messagebox.askyesno("Scan Folder", "Scan subfolders recursively?")
            results = scan_folder(folder, recursive=recursive)
            if isinstance(results, dict) and "error" in results:
                messagebox.showerror("Error", results["error"])
                return
            selected_files = [f["file_path"] for f in results]
            update_file_list()
    
    def remove_selected_file():
        nonlocal selected_files
        selection = file_list.curselection()
        if not selection:
            messagebox.showerror("Error", "No file selected to remove")
            return
        
        idx = selection[0]
        removed_file = selected_files.pop(idx)
        update_file_list()
        messagebox.showinfo("Removed", f"Removed: {Path(removed_file).name}")
    
    def update_file_list():
        file_list.delete(0, tk.END)
        for file_path in selected_files:
            file_list.insert(tk.END, Path(file_path).name)
    
    def load_files_data():
        nonlocal case_data
        if not selected_files:
            messagebox.showerror("Error", "No files selected")
            return
        
        files_data = extract_multiple_files(selected_files)
        case_data = create_case("Auto Case", files_data)
        
        log_action("ANALYZE", files=[f.get("file_path", "") for f in files_data])
        
        tree.delete(*tree.get_children())
        summary = generate_summary(case_data)
        
        tree.insert("", "end", values=("CASE SUMMARY", ""))
        tree.insert("", "end", values=("Case ID", summary["case_id"]))
        tree.insert("", "end", values=("Total Files", summary["total_files"]))
        tree.insert("", "end", values=("Total Anomalies", summary["total_anomalies"]))
        tree.insert("", "end", values=("Critical Anomalies", summary["critical_anomalies"]))
        tree.insert("", "end", values=("Files with Signature Issues", summary["files_with_signature_issues"]))
        tree.insert("", "end", values=("Correlations Found", case_data.get("correlation_count", 0)))
        tree.insert("", "end", values=("", ""))
        
        if case_data.get("correlations"):
            tree.insert("", "end", values=("CORRELATIONS", ""))
            for corr in case_data["correlations"]:
                tree.insert("", "end", values=(f"[{corr['type'].upper()}]", ""))
                tree.insert("", "end", values=("  Type", corr["type"]))
                tree.insert("", "end", values=("  Matched Value", str(corr["matched_value"])[:60]))
                tree.insert("", "end", values=("  File Count", corr["file_count"]))
                tree.insert("", "end", values=("  Confidence", f"{corr['confidence']}%"))
                tree.insert("", "end", values=("  Explanation", corr["explanation"]))
                tree.insert("", "end", values=("", ""))
        
        for file_idx, file_entry in enumerate(case_data["files"], 1):
            tree.insert("", "end", values=(f"FILE {file_idx}", ""))
            tree.insert("", "end", values=("Name", file_entry["metadata"].get("file_name", "N/A")))
            tree.insert("", "end", values=("Size", file_entry["metadata"].get("file_size", "N/A")))
            tree.insert("", "end", values=("Author", file_entry["metadata"].get("author", "N/A")))
            tree.insert("", "end", values=("Created Time", file_entry["metadata"].get("created_time", "N/A")))
            tree.insert("", "end", values=("Modified Time", file_entry["metadata"].get("modified_time", "N/A")))
            tree.insert("", "end", values=("Signature Valid", file_entry["metadata"].get("signature_valid", "N/A")))
            
            if file_entry["metadata"].get("signature_warning"):
                tree.insert("", "end", values=("⚠ WARNING", file_entry["metadata"]["signature_warning"]))
            
            if file_entry.get("anomalies"):
                tree.insert("", "end", values=("ANOMALIES", ""))
                for anomaly in file_entry["anomalies"]:
                    tree.insert("", "end", values=(f"  [{anomaly['severity'].upper()}]", anomaly["message"]))
            
            tree.insert("", "end", values=("Hashes", ""))
            for algo, hash_val in file_entry["hashes"].items():
                tree.insert("", "end", values=(f"  {algo.upper()}", hash_val[:32] + "..."))
            
            tree.insert("", "end", values=("", ""))
    
    def export_json():
        nonlocal case_data
        if case_data is None:
            messagebox.showerror("Error", "No case data to export")
            return
        
        export_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if export_path:
            result = export_case_json(case_data, export_path)
            if result["success"]:
                messagebox.showinfo("Success", result["message"])
            else:
                messagebox.showerror("Error", result["error"])
    
    def export_csv_report():
        nonlocal case_data
        if case_data is None:
            messagebox.showerror("Error", "No case data to export")
            return
        
        export_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if export_path:
            result = export_csv(case_data, export_path)
            if result["success"]:
                messagebox.showinfo("Success", result["message"])
            else:
                messagebox.showerror("Error", result["error"])
    
    def export_pdf_report():
        nonlocal case_data
        if case_data is None:
            messagebox.showerror("Error", "No case data to export")
            return
        
        export_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if export_path:
            result = export_pdf(case_data, export_path)
            if result["success"]:
                messagebox.showinfo("Success", result["message"])
            else:
                messagebox.showerror("Error", result["error"])
    
    def export_html_report():
        nonlocal case_data
        if case_data is None:
            messagebox.showerror("Error", "No case data to export")
            return
        
        export_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if export_path:
            result = export_html(case_data, export_path)
            if result["success"]:
                log_action("EXPORT_HTML", files=[export_path])
                messagebox.showinfo("Success", result["message"])
            else:
                messagebox.showerror("Error", result["error"])
    
    def send_email_report():
        nonlocal case_data
        if case_data is None:
            messagebox.showerror("Error", "No case data to export")
            return
        
        report_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not report_path:
            return
        
        report_type = Path(report_path).suffix.lower()
        
        if report_type == ".html":
            result = export_html(case_data, report_path)
        elif report_type == ".pdf":
            result = export_pdf(case_data, report_path)
        else:
            messagebox.showerror("Error", "Only HTML and PDF reports can be emailed")
            return
        
        if not result["success"]:
            messagebox.showerror("Error", result["error"])
            return
        
        email_window = tk.Toplevel(root)
        email_window.title("Send Report via Email")
        email_window.geometry("400x300")
        
        tk.Label(email_window, text="Gmail Address:", font=("Arial", 10, "bold")).pack(pady=5)
        sender_entry = tk.Entry(email_window, width=40)
        sender_entry.pack(pady=5)
        
        tk.Label(email_window, text="Gmail App Password:", font=("Arial", 10, "bold")).pack(pady=5)
        password_entry = tk.Entry(email_window, show="*", width=40)
        password_entry.pack(pady=5)
        
        tk.Label(email_window, text="Recipient Email:", font=("Arial", 10, "bold")).pack(pady=5)
        recipient_entry = tk.Entry(email_window, width=40)
        recipient_entry.pack(pady=5)
        
        def send():
            sender = sender_entry.get()
            password = password_entry.get()
            recipient = recipient_entry.get()
            
            if not sender or not password or not recipient:
                messagebox.showerror("Error", "All fields required")
                return
            
            send_result = send_report_email(recipient, report_path, sender, password)
            
            if send_result["success"]:
                log_action("SEND_EMAIL", files=[report_path, f"TO: {recipient}"])
                messagebox.showinfo("Success", send_result["message"])
                email_window.destroy()
            else:
                messagebox.showerror("Error", send_result["error"])
        
        tk.Button(email_window, text="Send", command=send, bg="#4CAF50", fg="white", width=20).pack(pady=20)
        
        def open_apppassword_link():
            import webbrowser
            webbrowser.open("https://myaccount.google.com/apppasswords")
        
        tk.Button(email_window, text="Create App Password for Mail Service", 
                 command=open_apppassword_link, fg="#0066CC", bg=email_window.cget("bg"), 
                 relief="flat", cursor="hand2", font=("Arial", 8, "underline")).pack(pady=10)
    
    def show_project_info():
        import webbrowser
        import os
        
        html_path = Path(__file__).parent.parent / "PROJECT_INFO.html"
        webbrowser.open(f"file://{html_path.absolute()}")
    
    def view_logs():
        logs_window = tk.Toplevel(root)
        logs_window.title("Activity Logs - MetaTrace")
        logs_window.geometry("800x500")
        
        logs = get_all_logs()
        summary = get_logs_summary()
        
        summary_frame = tk.Frame(logs_window)
        summary_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(summary_frame, text=f"Total Entries: {summary['total_entries']}", font=("Arial", 10, "bold")).pack(anchor="w")
        tk.Label(summary_frame, text=f"Log Hash (SHA256): {summary['sha256_hash']}", font=("Arial", 8), fg="#666").pack(anchor="w")
        
        text_widget = scrolledtext.ScrolledText(logs_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        for log in logs:
            text_widget.insert(tk.END, f"[{log['timestamp']}] {log['action']}\n")
            if log['files']:
                text_widget.insert(tk.END, f"  Files: {', '.join(log['files'][:2])}\n")
            if log['error']:
                text_widget.insert(tk.END, f"  Error: {log['error']}\n")
            text_widget.insert(tk.END, "\n")
        
        text_widget.config(state=tk.DISABLED)
        
        def export_logs_click():
            export_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if export_path:
                result = export_logs(export_path)
                messagebox.showinfo("Success", result["message"])
        
        tk.Button(logs_window, text="Export Logs", command=export_logs_click, bg="#2196F3", fg="white").pack(pady=10)
    
    frame_top = tk.Frame(root)
    frame_top.pack(pady=10, padx=10, fill="x")
    
    tk.Button(frame_top, text="Select Files", command=browse_files, bg="#4CAF50", fg="white").pack(side="left", padx=5)
    tk.Button(frame_top, text="Scan Folder", command=browse_folder, bg="#2196F3", fg="white").pack(side="left", padx=5)
    tk.Button(frame_top, text="Remove Selected", command=remove_selected_file, bg="#f44336", fg="white").pack(side="left", padx=5)
    tk.Button(frame_top, text="Analyze", command=load_files_data, bg="#FF9800", fg="white").pack(side="left", padx=5)
    
    frame_export = tk.Frame(root)
    frame_export.pack(pady=5, padx=10, fill="x")
    
    tk.Label(frame_export, text="Export:", font=("Arial", 10, "bold")).pack(side="left", padx=5)
    tk.Button(frame_export, text="JSON", command=export_json, bg="#9C27B0", fg="white", width=8).pack(side="left", padx=3)
    tk.Button(frame_export, text="CSV", command=export_csv_report, bg="#00BCD4", fg="white", width=8).pack(side="left", padx=3)
    tk.Button(frame_export, text="PDF", command=export_pdf_report, bg="#FF5722", fg="white", width=8).pack(side="left", padx=3)
    tk.Button(frame_export, text="HTML", command=export_html_report, bg="#4CAF50", fg="white", width=8).pack(side="left", padx=3)
    tk.Button(frame_export, text="📧 Email", command=send_email_report, bg="#FF9800", fg="white", width=8).pack(side="left", padx=3)
    tk.Button(frame_export, text="📋 Logs", command=view_logs, bg="#607D8B", fg="white", width=8).pack(side="left", padx=3)
    tk.Button(frame_export, text="ℹ️ Info", command=show_project_info, bg="#9C27B0", fg="white", width=8).pack(side="left", padx=3)
    
    frame_files = tk.Frame(root)
    frame_files.pack(pady=5, padx=10, fill="x")
    
    tk.Label(frame_files, text="Selected Files:").pack(anchor="w")
    file_list = tk.Listbox(frame_files, height=4)
    file_list.pack(fill="x", padx=5)
    
    columns = ("Property", "Value")
    tree = ttk.Treeview(root, columns=columns, height=25)
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("Property", anchor=tk.W, width=250)
    tree.column("Value", anchor=tk.W, width=700)
    
    tree.heading("#0", text="", anchor=tk.W)
    tree.heading("Property", text="Property", anchor=tk.W)
    tree.heading("Value", text="Value", anchor=tk.W)
    
    tree.pack(padx=10, pady=10, fill="both", expand=True)
    
    root.mainloop()