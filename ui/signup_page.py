import tkinter as tk
from tkinter import messagebox, font, ttk
import os
import sys
import datetime

from database import register_user, check_username_exists

class SignupPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#f0f0f0")
        self.master = master

        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=3)
        
        self.create_header()
        self.create_signup_form()
        self.create_footer()
        self.update_clock()
    
    def create_header(self):
        header_frame = tk.Frame(self, bg="#1a237e", height=100)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="new")
        header_frame.grid_propagate(False)

        title_font = font.Font(family="Arial", size=24, weight="bold")
        title_label = tk.Label(header_frame, text="RUET Hall Management System", 
                              font=title_font, bg="#1a237e", fg="white")
        title_label.pack(pady=20)
        self.datetime_label = tk.Label(header_frame, text="", font=("Arial", 12), 
                                     bg="#1a237e", fg="white")
        self.datetime_label.pack(side=tk.RIGHT, padx=20)
    
    def update_clock(self):
        now = datetime.datetime.now()
        date_str = now.strftime("%B %d, %Y")
        time_str = now.strftime("%I:%M:%S %p")
        self.datetime_label.config(text=f"{date_str}\n{time_str}")
        self.after(1000, self.update_clock)
    
    def create_signup_form(self):
        signup_frame = tk.Frame(self, bg="#ffffff", padx=40, pady=40)
        signup_frame.grid(row=1, column=0, columnspan=2, padx=300, pady=50, sticky="n")

        signup_frame.config(highlightbackground="#1a237e", highlightthickness=2)

        signup_title = tk.Label(signup_frame, text="Sign Up", font=("Arial", 20, "bold"), 
                              bg="#ffffff", fg="#1a237e")
        signup_title.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        fullname_label = tk.Label(signup_frame, text="Full Name:", font=("Arial", 12), 
                                bg="#ffffff", fg="#333333")
        fullname_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.fullname_entry = tk.Entry(signup_frame, font=("Arial", 12), width=25)
        self.fullname_entry.grid(row=1, column=1, pady=5, padx=10)

        username_label = tk.Label(signup_frame, text="Username:", font=("Arial", 12), 
                                bg="#ffffff", fg="#333333")
        username_label.grid(row=2, column=0, sticky="w", pady=5)
        
        self.username_entry = tk.Entry(signup_frame, font=("Arial", 12), width=25)
        self.username_entry.grid(row=2, column=1, pady=5, padx=10)

        password_label = tk.Label(signup_frame, text="Password:", font=("Arial", 12), 
                                bg="#ffffff", fg="#333333")
        password_label.grid(row=3, column=0, sticky="w", pady=5)
        
        self.password_entry = tk.Entry(signup_frame, font=("Arial", 12), width=25, show="*")
        self.password_entry.grid(row=3, column=1, pady=5, padx=10)

        confirm_password_label = tk.Label(signup_frame, text="Confirm Password:", font=("Arial", 12), 
                                       bg="#ffffff", fg="#333333")
        confirm_password_label.grid(row=4, column=0, sticky="w", pady=5)
        
        self.confirm_password_entry = tk.Entry(signup_frame, font=("Arial",12),width=25,show="*")
        self.confirm_password_entry.grid(row=4, column=1, pady=5, padx=10)
        
        user_type_label = tk.Label(signup_frame, text="User Type:", font=("Arial", 12), 
                                 bg="#ffffff", fg="#333333")
        user_type_label.grid(row=5, column=0, sticky="w", pady=5)
        
        self.user_type = tk.StringVar(value="student")
        user_type_frame = tk.Frame(signup_frame, bg="#ffffff")
        user_type_frame.grid(row=5, column=1, sticky="w", pady=5)
        
        student_radio = tk.Radiobutton(user_type_frame, text="Student", variable=self.user_type, 
                                      value="student", bg="#ffffff", command=self.toggle_student_fields)
        student_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        admin_radio = tk.Radiobutton(user_type_frame, text="Admin",variable=self.user_type, 
                                    value="admin", bg="#ffffff",command=self.toggle_student_fields)
        admin_radio.pack(side=tk.LEFT)

        self.student_frame = tk.Frame(signup_frame, bg="#ffffff")
        self.student_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky="ew")

        roll_label = tk.Label(self.student_frame, text="Roll Number:", font=("Arial", 12), 
                            bg="#ffffff", fg="#333333")
        roll_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.roll_entry = tk.Entry(self.student_frame, font=("Arial", 12), width=25)
        self.roll_entry.grid(row=0, column=1, pady=5, padx=10)

        dept_label = tk.Label(self.student_frame, text="Department:", font=("Arial", 12), 
                            bg="#ffffff", fg="#333333")
        dept_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.dept_entry = tk.Entry(self.student_frame, font=("Arial", 12), width=25)
        self.dept_entry.grid(row=1, column=1, pady=5, padx=10)

        signup_button = tk.Button(signup_frame, text="Sign Up", font=("Arial", 12, "bold"), 
                                bg="#1a237e", fg="white", padx=20, pady=5,
                                command=self.signup)
        signup_button.grid(row=7, column=0, columnspan=2, pady=20)

        login_text = tk.Label(signup_frame, text="Already have an account?", 
                             font=("Arial", 10), bg="#ffffff")
        login_text.grid(row=8, column=0, pady=5)
        
        login_link = tk.Label(signup_frame, text="Login", font=("Arial", 10, "bold"), 
                             bg="#ffffff", fg="blue", cursor="hand2")
        login_link.grid(row=8, column=1, sticky="w", pady=5)
        login_link.bind("<Button-1>", lambda e: self.master.show_login_page())
    
    def toggle_student_fields(self):
        if self.user_type.get() == "student":
            self.student_frame.grid(row=6, column=0, columnspan=2, pady=10, sticky="ew")
        else:
            self.student_frame.grid_forget()
    
    def create_footer(self):
        footer_frame = tk.Frame(self, bg="#1a237e", height=50)
        footer_frame.grid(row=2, column=0, columnspan=2, sticky="sew")
        footer_frame.grid_propagate(False)
        
        footer_text = tk.Label(footer_frame, text="© 2025 RUET Hall Management System", 
                              font=("Arial", 10), bg="#1a237e", fg="white")
        footer_text.pack(pady=15)
    
    def signup(self):
        full_name = self.fullname_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        user_type = self.user_type.get()
        
        if not full_name or not username or not password or not confirm_password:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        if check_username_exists(username):
            messagebox.showerror("Error", "Username already exists")
            return

        roll_number = None
        department = None
        if user_type == "student":
            roll_number = self.roll_entry.get()
            department = self.dept_entry.get()
            if not roll_number or not department:
                messagebox.showerror("Error", "Please fill in all student details")
                return

        success, message = register_user(username, password, full_name, user_type, roll_number, department)
        
        if success:
            messagebox.showinfo("Success", message)
            self.master.show_login_page()
        else:
            messagebox.showerror("Error", message)