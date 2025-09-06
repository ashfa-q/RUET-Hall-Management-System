import tkinter as tk
from tkinter import messagebox, font
import datetime
from database import authenticate_user

class LoginPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master,bg="#f0f0f0")
        self.master=master

        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=3)
        
        self.create_header()
        self.create_login_form()
        self.create_footer()
        self.update_clock()
    
    def create_header(self):
        header_frame=tk.Frame(self,bg="#1a237e",height=100)
        header_frame.grid(row=0,column=0,columnspan=2,sticky="new")
        header_frame.grid_propagate(False)

        title_font=font.Font(family="Arial",size=24,weight="bold")
        title_label=tk.Label(header_frame,text="RUET Hall Management System", 
                              font=title_font,bg="#1a237e",fg="white")
        title_label.pack(pady=20)

        self.datetime_label=tk.Label(header_frame,text="",font=("Arial",12), 
                                     bg="#1a237e",fg="white")
        self.datetime_label.pack(side=tk.RIGHT,padx=20)
    
    def update_clock(self):
        now=datetime.datetime.now()
        date_str=now.strftime("%B %d, %Y")
        time_str=now.strftime("%I:%M:%S %p")
        self.datetime_label.config(text=f"{date_str}\n{time_str}")
        self.after(1000,self.update_clock)
    
    def create_login_form(self):
        login_frame = tk.Frame(self,bg="#ffffff",padx=40,pady=40)
        login_frame.grid(row=1,column=0,columnspan=2,padx=300,pady=50,sticky="n")

        login_frame.config(highlightbackground="#1a237e",highlightthickness=2)

        login_title=tk.Label(login_frame,text="Login",font=("Arial",20,"bold"), 
                              bg="#ffffff",fg="#1a237e")
        login_title.grid(row=0,column=0,columnspan=2,pady=(0,20))

        username_label=tk.Label(login_frame,text="Username:",font=("Arial",12), 
                                bg="#ffffff",fg="#333333")
        username_label.grid(row=1,column=0,sticky="w",pady=5)
        
        self.username_entry=tk.Entry(login_frame,font=("Arial",12),width=25)
        self.username_entry.grid(row=1,column=1,pady=5,padx=10)

        password_label=tk.Label(login_frame,text="Password:",font=("Arial",12), 
                                bg="#ffffff", fg="#333333")
        password_label.grid(row=2,column=0,sticky="w",pady=5)
        
        self.password_entry = tk.Entry(login_frame,font=("Arial",12),width=25,show="*")
        self.password_entry.grid(row=2,column=1,pady=5,padx=10)

        login_button = tk.Button(login_frame,text="Login",font=("Arial",12,"bold"), 
                               bg="#1a237e",fg="white",padx=20,pady=5,
                               command=self.login)
        login_button.grid(row=3,column=0,columnspan=2,pady=20)

        signup_text=tk.Label(login_frame,text="Don't have an account?", 
                              font=("Arial",10),bg="#ffffff")
        signup_text.grid(row=4,column=0,pady=5)
        
        signup_link=tk.Label(login_frame,text="Sign Up",font=("Arial",10,"bold"), 
                              bg="#ffffff",fg="blue",cursor="hand2")
        signup_link.grid(row=4,column=1,sticky="w",pady=5)
        #signup_link.bind("<Button-1>", lambda e: print("TEST: Click detected!"))
        signup_link.bind("<Button-1>",lambda e:self.master.show_signup_page())
    
    def create_footer(self):
        footer_frame=tk.Frame(self,bg="#1a237e",height=50)
        footer_frame.grid(row=2,column=0,columnspan=2,sticky="sew")
        footer_frame.grid_propagate(False)
        
        footer_text = tk.Label(footer_frame,text="© 2025 RUET Hall Management System", 
                              font=("Arial",10),bg="#1a237e",fg="white")
        footer_text.pack(pady=15)
    
    def login(self):
        username=self.username_entry.get()
        password=self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error","Please enter both username and password")
            return
        
        user=authenticate_user(username,password)
        if user:
            
            self.master.show_hall_selection(user,user['user_type'])
        else:
            messagebox.showerror("Error","Invalid username or password")