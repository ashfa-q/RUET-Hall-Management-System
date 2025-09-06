import tkinter as tk
from tkinter import messagebox, font, ttk
import datetime

from database import (
    get_hall_by_name,
    get_student_room,
    apply_for_room,
    get_student_payments,
    make_payment,
    get_student_meal_tokens,
    buy_meal_token,
    calculate_student_dues,
    get_application
)

class StudentDashboard(tk.Frame):
    def __init__(self, master, hall_name):
        super().__init__(master, bg="#f0f0f0")
        self.master = master
        self.hall_name = hall_name
        self.hall = get_hall_by_name(hall_name)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3)
        self.grid_rowconfigure(2, weight=1)
        
        self.create_header()
        
        self.create_main_content()
        self.create_footer()
        self.update_clock()
    
    def create_header(self):
        header_frame = tk.Frame(self, bg="#1a237e", height=100)
        header_frame.grid(row=0, column=0, sticky="new")
        header_frame.grid_propagate(False)

        title_font = font.Font(family="Arial", size=24, weight="bold")
        title_label = tk.Label(header_frame, text=f"{self.hall_name} Hall Dashboard", 
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

        room_frame = tk.Frame(notebook, bg="#ffffff", padx=20, pady=20)
        self.setup_room_application_tab(room_frame)
        notebook.add(room_frame, text="Room Application")

        payment_frame = tk.Frame(notebook, bg="#ffffff", padx=20, pady=20)
        self.setup_payment_tab(payment_frame)
        notebook.add(payment_frame, text="Payment Management")

        meal_frame = tk.Frame(notebook, bg="#ffffff",padx=20,pady=20)
        self.setup_meal_token_tab(meal_frame)
        notebook.add(meal_frame, text="Meal Token")
    
    def setup_room_application_tab(self, parent_frame):
        status_frame = tk.Frame(parent_frame, bg="#ffffff")
        status_frame.pack(fill="x", pady=(0, 20))
        
        room_info = get_student_room(self.master.current_user['id'], self.hall['id'])
        if room_info:
            status_text = f"Your Room Number: {room_info['room_number']}"
            tk.Label(status_frame, text=status_text, font=("Arial",20, "bold"),
                    bg="#ffffff", fg="#1a237e").pack()
        else:
            tk.Label(status_frame, text=f"Available Rooms: {self.hall['available_rooms']}",
                    font=("Arial",20), bg="#ffffff").pack()
       
            b=False
            for j in range (1,6):
                room_info = get_student_room(self.master.current_user['id'],j)
                if room_info:
                    b=True
                    break
            app=get_application(self.master.current_user['id'])
            if app:
                tk.Label(status_frame, text=f"Your Application Is Pending",
                    font=("Arial",20), bg="#ffffff").pack()

            elif self.hall['available_rooms'] > 0 and b==False:
                form_frame = tk.Frame(parent_frame, bg="#ffffff")
                form_frame.pack(fill="x", pady=20)
                
                tk.Button(form_frame, text="Apply for Room", font=("Arial",20, "bold"),
                          bg="#1a237e", fg="white", command=self.apply_for_room).pack()
            else:
                tk.Label(status_frame, text=f"Your Are Already Allocated",
                    font=("Arial",20), bg="#ffffff").pack()
    
    def setup_payment_tab(self, parent_frame):
        status_frame = tk.Frame(parent_frame, bg="#ffffff")
        status_frame.pack(fill="x", pady=(0, 20))

        dues = calculate_student_dues(self.master.current_user['id'], self.hall['id'])
        
        tk.Label(status_frame, text=f"Current Dues: ৳{dues:,.2f}",
                font=("Arial", 14, "bold"), bg="#ffffff", fg="red" if dues > 0 else "green").pack()
        
        if dues > 0:
            payment_frame = tk.Frame(parent_frame, bg="#ffffff")
            payment_frame.pack(fill="x", pady=20)
            
            tk.Label(payment_frame, text="Enter Payment Amount:",
                    font=("Arial", 12), bg="#ffffff").pack()
            
            self.payment_amount = tk.Entry(payment_frame, font=("Arial", 12), width=20)
            self.payment_amount.pack(pady=10)
            
            tk.Button(payment_frame, text="Make Payment", font=("Arial", 12, "bold"),
                      bg="#1a237e", fg="white", command=self.make_payment).pack()

        history_frame = tk.Frame(parent_frame, bg="#ffffff")
        history_frame.pack(fill="both", expand=True, pady=20)
        
        tk.Label(history_frame, text="Payment History",
                font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=(0, 10))
        
        columns = ("Date","Amount")
        tree = ttk.Treeview(history_frame, columns=columns,show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        payments = get_student_payments(self.master.current_user['id'])
        for payment in payments:
            tree.insert("", "end", values=(
                payment['payment_date'].strftime("%Y-%m-%d %H:%M"),
                f"৳{payment['amount']:,.2f}"
            ))
    
    def setup_meal_token_tab(self, parent_frame):
        now = datetime.datetime.now()
        date_str = now.strftime("%B %d, %Y")
        
        tk.Label(parent_frame, text=f"Buy Token for Tomorrow   ;   Today: {date_str}",
                font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=(0, 20))
        
        button_frame = tk.Frame(parent_frame, bg="#ffffff")
        button_frame.pack(fill="x", pady=20)

        tokens = get_student_meal_tokens(
            self.master.current_user['id'],
            self.hall['id'],
            now.date()
        )
        
        lunch_bought = any(t['meal_type'] == 'lunch' for t in tokens)
        dinner_bought = any(t['meal_type'] == 'dinner' for t in tokens)

        lunch_btn = tk.Button(button_frame, text="Buy Lunch Token",
                            font=("Arial", 12, "bold"), bg="#1a237e" if not lunch_bought else "#cccccc",
                            fg="white", padx=20, pady=10,
                            command=lambda: self.buy_token('lunch') if not lunch_bought else None)
        lunch_btn.pack(side="left", expand=True, padx=10)

        dinner_btn = tk.Button(button_frame, text="Buy Dinner Token",
                             font=("Arial", 12, "bold"), bg="#1a237e" if not dinner_bought else "#cccccc",
                             fg="white", padx=20, pady=10,
                             command=lambda: self.buy_token('dinner') if not dinner_bought else None)
        dinner_btn.pack(side="left", expand=True, padx=10)

        history_frame = tk.Frame(parent_frame, bg="#ffffff")
        history_frame.pack(fill="both", expand=True, pady=20)
        
        tk.Label(history_frame, text="Token History",
                font=("Arial", 14, "bold"), bg="#ffffff").pack(pady=(0, 10))

        columns = ("Date", "Meal Type")
        tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
  
        all_tokens = get_student_meal_tokens(
            self.master.current_user['id'],
            self.hall['id']
        )
        for token in all_tokens:
            tree.insert("", "end", values=(
                token['token_date'].strftime("%Y-%m-%d"),
                token['meal_type'].title()
            ))
    
    def create_footer(self):
        footer_frame = tk.Frame(self, bg="#1a237e", height=50)
        footer_frame.grid(row=2, column=0, sticky="sew")
        footer_frame.grid_propagate(False)
        
        footer_text = tk.Label(footer_frame, text="© 2025 RUET Hall Management System", 
                              font=("Arial", 10), bg="#1a237e", fg="white")
        footer_text.pack(pady=15)
    
    def apply_for_room(self):
        success=apply_for_room(
            self.master.current_user['id'],
            self.hall['id']
        )
        
        if success:
            messagebox.showinfo("Success","Room application submitted successfully!")
            self.master.show_dashboard(self.hall_name)
        else:
            messagebox.showerror("Error","Failed to submit room application")
    
    def make_payment(self):
        try:
            amount = float(self.payment_amount.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error","Please enter a valid payment amount")
            return
        
        success = make_payment(
            self.master.current_user['id'],
            amount
        )
        
        if success:
            messagebox.showinfo("Success","Payment processed successfully!")
            self.master.show_dashboard(self.hall_name)
        else:
            messagebox.showerror("Error","Failed to process payment")
    
    def buy_token(self, meal_type):
        success = buy_meal_token(
            self.master.current_user['id'],
            self.hall['id'],
            meal_type
        )
        
        if success:
            messagebox.showinfo("Success", f"{meal_type.title()} token purchased successfully!")
            self.master.show_dashboard(self.hall_name)
        else:
            messagebox.showerror("Error", f"Failed to purchase {meal_type} token")