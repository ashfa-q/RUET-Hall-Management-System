import tkinter as tk
from tkinter import messagebox,font,ttk
import datetime

from database import (
    get_hall_by_name,
    get_pending_applications,
    approve_application,
    reject_application,
    get_meal_token_stats,
    get_payment_stats,
    get_hall_students,
    remove_student
)

class AdminDashboard(tk.Frame):
    def __init__(self,master,hall_name):
        super().__init__(master,bg="#f0f0f0")
        self.master=master
        self.hall_name=hall_name
        self.hall=get_hall_by_name(hall_name)

        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=3)
        self.grid_rowconfigure(2,weight=1)

        self.create_header()
        self.create_main_content()
        self.create_footer()
        self.update_clock()
    
    def create_header(self):
        header_frame=tk.Frame(self, bg="#1a237e", height=100)
        header_frame.grid(row=0, column=0, sticky="new")
        header_frame.grid_propagate(False)
        
        title_font = font.Font(family="Arial", size=24, weight="bold")
        title_label = tk.Label(header_frame, text=f"{self.hall_name} Hall Admin Dashboard", 
                              font=title_font, bg="#1a237e", fg="white")
        title_label.pack(pady=20)
        
        self.datetime_label = tk.Label(header_frame, text="", font=("Arial", 12), 
                                     bg="#1a237e", fg="white")
        self.datetime_label.pack(side=tk.RIGHT, padx=20)
        back_button = tk.Button(header_frame, text="Back to Hall Selection", 
                              font=("Arial", 10, "bold"), bg="#f44336", fg="white",
                              padx=10, pady=5, command=lambda: self.master.show_hall_selection(
                                  self.master.current_user, self.master.user_type))
        back_button.pack(side=tk.LEFT, padx=20)
    
    def update_clock(self):
        now = datetime.datetime.now()
        date_str = now.strftime("%B %d, %Y")
        time_str = now.strftime("%I:%M:%S %p")
        self.datetime_label.config(text=f"{date_str}\n{time_str}")
        self.after(1000, self.update_clock)
    
    def create_main_content(self):
        notebook = ttk.Notebook(self)
        notebook.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        applications_frame = tk.Frame(notebook, bg="#ffffff", padx=20, pady=20)
        self.setup_applications_tab(applications_frame)
        notebook.add(applications_frame, text="Room Applications")
        stats_frame = tk.Frame(notebook, bg="#ffffff", padx=20, pady=20)
        self.setup_statistics_tab(stats_frame)
        notebook.add(stats_frame, text="Statistics")
        students_frame = tk.Frame(notebook, bg="#ffffff", padx=20, pady=20)
        self.setup_students_tab(students_frame)
        notebook.add(students_frame, text="Student Management")
    
    def setup_applications_tab(self, parent_frame):
        applications = get_pending_applications(self.hall['id'])
        
        if not applications:
            tk.Label(parent_frame, text="No pending applications",
                    font=("Arial", 14), bg="#ffffff").pack(pady=20)
            return
        
        container = tk.Frame(parent_frame, bg="#ffffff")
        container.pack(fill="both", expand=True)
        
        columns = ("ID", "Name", "Roll Number", "Department", "Application Date", "Actions")
        tree = ttk.Treeview(container, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            if col == "Actions":
                tree.column(col, width=200)
            else:
                tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        container.grid_columnconfigure(0, weight=1)
        self.action_frames = {}
        for i, app in enumerate(applications):
            app_date = app['application_date'].strftime("%Y-%m-%d %H:%M") if isinstance(app['application_date'], datetime.datetime) else str(app['application_date'])
 
            student_name = app.get('student_name', 'Unknown')
            roll_number = app.get('roll_number', 'N/A')
            department = app.get('department', 'N/A')

            item_id = tree.insert("", "end", values=(
                app['id'],
                student_name,
                roll_number,
                department,
                app_date,
                "Double-click to Approve/Reject"
            ))
            action_frame = tk.Frame(parent_frame, bg="#ffffff")
            room_label = tk.Label(action_frame, text="Room:", bg="#ffffff")
            room_label.pack(side="left", padx=2)
            
            room_var = tk.StringVar(value="1")
            room_entry = tk.Spinbox(action_frame, from_=1, to=10, width=3, textvariable=room_var)
            room_entry.pack(side="left", padx=2)
            approve_btn = tk.Button(action_frame, text="Approve", bg="#4caf50", fg="white",
                                  command=lambda a=app, r=room_var: self.approve_application(a['id'], r.get()))
            reject_btn = tk.Button(action_frame, text="Reject", bg="#f44336", fg="white",
                                 command=lambda a=app: self.reject_application(a['id']))
            
            approve_btn.pack(side="left", padx=2)
            reject_btn.pack(side="left", padx=2)

            self.action_frames[item_id] = action_frame
            
            tree.bind('<Double-1>', self.on_tree_double_click)
        self.applications_tree = tree
        
        instructions = tk.Label(parent_frame, text="Double-click on an application to approve or reject", 
                              font=("Arial", 10, "italic"), bg="#ffffff")
        instructions.pack(pady=10)
    
    def on_tree_double_click(self, event):
        tree = self.applications_tree
        item_id = tree.identify('item', event.x, event.y)
        if item_id and item_id in self.action_frames:
            self.show_action_dialog(self.action_frames[item_id])
    
    def show_action_dialog(self, action_frame, event=None):
        dialog = tk.Toplevel(self)
        dialog.title("Application Actions")
        dialog.geometry("400x150")
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        container = tk.Frame(dialog, padx=20, pady=20)
        container.pack(fill="both", expand=True)

        action_frame_copy = tk.Frame(container)

        for widget in action_frame.winfo_children():
            if isinstance(widget, tk.Label):
                tk.Label(action_frame_copy, text=widget.cget("text"), bg="#ffffff").pack(side="left", padx=2)
            elif isinstance(widget, tk.Spinbox):
                room_var = tk.StringVar(value=widget.get())
                room_entry = tk.Spinbox(action_frame_copy, from_=1, to=10, width=3, textvariable=room_var)
                room_entry.pack(side="left", padx=2)
            elif isinstance(widget, tk.Button):
                if widget.cget("text") == "Approve":
                    cmd = widget.cget("command")
                    approve_btn = tk.Button(action_frame_copy, text="Approve", bg="#4caf50", fg="white",
                                         command=lambda: self.approve_application_from_dialog(cmd, room_var, dialog))
                    approve_btn.pack(side="left", padx=2)
                else:
                    reject_btn = tk.Button(action_frame_copy, text="Reject", bg="#f44336", fg="white",
                                        command=lambda: self.reject_application_from_dialog(widget.cget("command"), dialog))
                    reject_btn.pack(side="left", padx=2)
        
        action_frame_copy.pack(pady=20)
    
    def setup_statistics_tab(self, parent_frame):
        meal_stats = get_meal_token_stats(self.hall['id'])
        payment_stats = get_payment_stats(self.hall['id'])
        
        meal_frame = tk.LabelFrame(parent_frame, text="Today's Meal Token Statistics",
                                 font=("Arial", 12, "bold"), bg="#ffffff", padx=20, pady=20)
        meal_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(meal_frame, text=f"Lunch Tokens: {meal_stats['lunch_count']}",
                font=("Arial", 12), bg="#ffffff").pack()
        tk.Label(meal_frame, text=f"Dinner Tokens: {meal_stats['dinner_count']}",
                font=("Arial", 12), bg="#ffffff").pack()
        
        payment_frame = tk.LabelFrame(parent_frame, text="Payment Statistics",
                                    font=("Arial", 12, "bold"), bg="#ffffff", padx=20, pady=20)
        payment_frame.pack(fill="x")
        
        tk.Label(payment_frame, text=f"Total Payments Today: ৳{payment_stats['today_total']:,.2f}",
                font=("Arial", 12), bg="#ffffff").pack()
        tk.Label(payment_frame, text=f"Total Payments This Month: ৳{payment_stats['month_total']:,.2f}",
                font=("Arial", 12), bg="#ffffff").pack()
    
    def setup_students_tab(self, parent_frame):
        students = get_hall_students(self.hall['id'])
        
        if not students:
            tk.Label(parent_frame, text="No students in this hall",
                    font=("Arial", 14), bg="#ffffff").pack(pady=20)
            return

        container = tk.Frame(parent_frame, bg="#ffffff")
        container.pack(fill="both", expand=True)

        columns = ("ID", "Name", "Roll Number", "Department", "Room")
        tree = ttk.Treeview(container, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        buttons_frame = tk.Frame(container, bg="#ffffff")

        tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        buttons_frame.grid(row=0, column=2, sticky="ns", padx=(10, 0))
        
        container.grid_columnconfigure(0, weight=1)
        
        for i, student in enumerate(students):
            item_id = tree.insert("", "end", values=(
                student['id'],
                student['full_name'],
                student['roll_number'],
                student['department'],
                student['room_number']
            ))
            
            action_frame = tk.Frame(buttons_frame, bg="#ffffff")
            action_frame.grid(row=i, column=0, pady=2)
            remove_btn = tk.Button(action_frame, text="Remove", bg="#f44336", fg="white",
                                command=lambda s=student: self.remove_student(s['id']))
            remove_btn.pack(padx=2)
    
    def create_footer(self):
        footer_frame = tk.Frame(self, bg="#1a237e", height=50)
        footer_frame.grid(row=2, column=0, sticky="sew")
        footer_frame.grid_propagate(False)
        
        footer_text = tk.Label(footer_frame, text="© 2025 RUET Hall Management System", 
                              font=("Arial", 10), bg="#1a237e", fg="white")
        footer_text.pack(pady=15)
    
    def approve_application_from_dialog(self, original_cmd, room_var, dialog):
        application_id = None

        applications = get_pending_applications(self.hall['id'])
        if applications and len(applications) > 0:
            application_id = applications[0]['id']

            if hasattr(self, 'applications_tree'):
                selected = self.applications_tree.selection()
                if selected:
                    app_id = self.applications_tree.item(selected[0], 'values')[0]
                    application_id = app_id
        
        if application_id:
            room_number = room_var.get()
            success, message = approve_application(application_id, room_number)
            
            if success:
                messagebox.showinfo("Success", "Application approved successfully!")
                dialog.destroy()
                self.master.show_dashboard(self.hall_name)
            else:
                messagebox.showerror("Error", f"Failed to approve application: {message}")
                dialog.destroy()
        else:
            messagebox.showerror("Error", "Could not determine which application to approve")
            dialog.destroy()
    
    def reject_application_from_dialog(self, original_cmd, dialog):
        application_id = None

        applications = get_pending_applications(self.hall['id'])
        if applications and len(applications) > 0:
            application_id = applications[0]['id']
            
            if hasattr(self, 'applications_tree'):
                selected = self.applications_tree.selection()
                if selected:
                    app_id = self.applications_tree.item(selected[0], 'values')[0]
                    application_id = app_id
        
        if application_id:
            success = reject_application(application_id)
            
            if success:
                messagebox.showinfo("Success", "Application rejected successfully!")
                dialog.destroy()
                self.master.show_dashboard(self.hall_name)
            else:
                messagebox.showerror("Error", "Failed to reject application")
                dialog.destroy()
        else:
            messagebox.showerror("Error", "Could not determine which application to reject")
            dialog.destroy()
    
    def approve_application(self, application_id, room_number):
        success, message = approve_application(application_id, room_number)
        
        if success:
            messagebox.showinfo("Success", "Application approved successfully!")
            self.master.show_dashboard(self.hall_name)
        else:
            messagebox.showerror("Error", f"Failed to approve application: {message}")
    
    def reject_application(self, application_id):
        success = reject_application(application_id)
        
        if success:
            messagebox.showinfo("Success", "Application rejected successfully!")
            self.master.show_dashboard(self.hall_name)
        else:
            messagebox.showerror("Error", "Failed to reject application")
    
    def remove_student(self, student_id):
        if messagebox.askyesno("Confirm", "Are you sure you want to remove this student?"):
            success = remove_student(student_id, self.hall['id'])
            
            if success:
                messagebox.showinfo("Success", "Student removed successfully!")
                self.master.show_dashboard(self.hall_name)
            else:
                messagebox.showerror("Error", "Failed to remove student")