import tkinter as tk
from tkinter import messagebox, font
import datetime
from database import get_halls, get_hall_by_name,get_user_allocation,hall_name,get_student_room

class HallSelectionPage(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#f0f0f0")
        self.master = master

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3)
        self.grid_rowconfigure(2, weight=1)

        self.create_header()
        self.create_hall_selection()
        self.create_footer()
        self.update_clock()
    
    def create_header(self):
        header_frame = tk.Frame(self, bg="#1a237e", height=100)
        header_frame.grid(row=0, column=0, sticky="new")
        header_frame.grid_propagate(False)

        title_font = font.Font(family="Arial", size=24, weight="bold")
        title_label = tk.Label(header_frame, text="RUET Hall Management System", 
                              font=title_font, bg="#1a237e", fg="white")
        title_label.pack(pady=20)
        self.datetime_label = tk.Label(header_frame, text="", font=("Arial", 12), 
                                     bg="#1a237e", fg="white")
        self.datetime_label.pack(side=tk.RIGHT, padx=20)

        back_button = tk.Button(header_frame, text="Logout", font=("Arial", 10, "bold"),
                              bg="#f44336", fg="white", padx=10, pady=5,
                              command=self.master.show_login_page)
        back_button.pack(side=tk.LEFT, padx=20)
    
    def update_clock(self):
        now = datetime.datetime.now()
        date_str = now.strftime("%B %d, %Y")
        time_str = now.strftime("%I:%M:%S %p")
        self.datetime_label.config(text=f"{date_str}\n{time_str}")
        self.after(1000, self.update_clock)
    
    def create_hall_selection(self):
        selection_frame = tk.Frame(self, bg="#ffffff", padx=40, pady=40)
        selection_frame.grid(row=1, column=0, padx=100, pady=50, sticky="nsew")
        selection_frame.config(highlightbackground="#1a237e", highlightthickness=2)

        selection_title = tk.Label(selection_frame, text="Select a Hall(Available Room)", font=("Arial", 20, "bold"), 
                                 bg="#ffffff", fg="#1a237e")
        selection_title.pack(pady=(0, 30))

        user_type = "Administrator" if self.master.user_type == "admin" else "Student"
        welcome_text = f"Welcome, {self.master.current_user['full_name']} ({user_type})"
        welcome_label = tk.Label(selection_frame, text=welcome_text, font=("Arial",20), 
                               bg="#ffffff", fg="#333333")
        welcome_label.pack(pady=(0, 20))
        
        instruction_label = tk.Label(selection_frame, text="Please select a hall to continue:", 
                                   font=("Arial",20), bg="#ffffff", fg="#333333")
        instruction_label.pack(pady=(0, 20))

        halls = get_halls()
        halls_frame = tk.Frame(selection_frame, bg="#ffffff")
        halls_frame.pack(fill="both", expand=True)
        for i, hall in enumerate(halls):
            hall_button = tk.Button(halls_frame,text=f"{hall['name']} ({hall['available_rooms']})", font=("Arial", 12, "bold"),
                                  bg="#1a237e", fg="white", padx=20, pady=10, width=15,
                                  command=lambda name=hall['name']: self.select_hall(name))
            
            row = i // 3
            col = i % 3
            hall_button.grid(row=row, column=col, padx=20, pady=20)
            

        for i in range(3):
            halls_frame.columnconfigure(i, weight=1)

        if user_type=="Student":
            b=False
            hl=['Selim','Zia','Hamid','Shahidul','Bonggobondhu']
            for j in range (1,6):
                room_info = get_student_room(self.master.current_user['id'],j)
                if room_info:
                    b=True
                    nm=hl[j-1]
                    break
            if b:
                dash_board = tk.Button(halls_frame,text=f"Your Dashboard", font=("Arial", 12, "bold"),
                                  bg="#9F1220", fg="white", padx=20, pady=10, width=15,
                                  command=lambda:self.select_hall(nm))
                dash_board.grid(row=1, column=2, padx=20, pady=20)
    
    def create_footer(self):
        footer_frame = tk.Frame(self, bg="#1a237e", height=50)
        footer_frame.grid(row=2, column=0, sticky="sew")
        footer_frame.grid_propagate(False)
        
        footer_text = tk.Label(footer_frame, text="© 2025 RUET Hall Management System", 
                              font=("Arial", 10), bg="#1a237e", fg="white")
        footer_text.pack(pady=15)
    
    def select_hall(self, hall_name):
        hall = get_hall_by_name(hall_name)
        
        if not hall:
            messagebox.showerror("Error", f"Hall '{hall_name}' not found")
            return
        self.master.show_dashboard(hall_name)