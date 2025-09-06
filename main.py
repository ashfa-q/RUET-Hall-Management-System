import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from database import setup_database
from ui.login_page import LoginPage
from ui.signup_page import SignupPage
from ui.hall_selection_page import HallSelectionPage
from ui.admin_dashboard import AdminDashboard
from ui.student_dashboard import StudentDashboard

class HallManagementSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RUET Hall Management System")
        self.geometry("1200x700")
        self.configure(bg="#f0f0f0")
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda event: self.attributes("-fullscreen", False))
        
        setup_database()
        self.frames = {}
        self.current_user = None
        self.user_type = None
        self.last_activity = datetime.now()
        self.session_timeout = timedelta(minutes=2)
        self.show_login_page()
        self.check_inactivity()
    
    def check_inactivity(self):
        now = datetime.now()
        if (now - self.last_activity) >= self.session_timeout and self.current_user:
            self.logout()
        else:
            self.after(1000,self.check_inactivity)
    
    def record_activity(self, event=None):
        self.last_activity = datetime.now()
    
    def bind_activity_tracking(self):
        for child in self.winfo_children():
            child.bind("<Button-1>", self.record_activity)
            child.bind("<Key>", self.record_activity)
            for widget in child.winfo_children():
                self._bind_to_children(widget)
    
    def _bind_to_children(self, widget):
        widget.bind("<Button-1>", self.record_activity)
        widget.bind("<Key>", self.record_activity)
        for child in widget.winfo_children():
            self._bind_to_children(child)
    
    def logout(self):
        self.current_user=None
        self.user_type=None
        self.show_login_page()
        messagebox.showinfo("Session Expired","You have been automatically logged out due to inactivity")
    
    def show_login_page(self):
        print("DEBUG: Entering show_login_page()")
        for frame in self.winfo_children():
            frame.destroy()
        login_page = LoginPage(self)
        login_page.pack(fill="both", expand=True)
    
    def show_signup_page(self):
        print("DEBUG: Entering show_signup_page()")
        for frame in self.winfo_children():
            frame.destroy()
        signup_page = SignupPage(self)
        signup_page.pack(fill="both", expand=True)
    
    def show_hall_selection(self, user_data, user_type):
        self.current_user = user_data
        self.user_type = user_type
        self.last_activity = datetime.now()
        
        for frame in self.winfo_children():
            frame.destroy()

        hall_selection = HallSelectionPage(self)
        hall_selection.pack(fill="both", expand=True)
        self.bind_activity_tracking()
    
    def show_dashboard(self, hall_name):
        self.last_activity = datetime.now()
        for frame in self.winfo_children():
            frame.destroy()
        if self.user_type == "admin":
            dashboard = AdminDashboard(self, hall_name)
        else:
            dashboard = StudentDashboard(self, hall_name)
        dashboard.pack(fill="both", expand=True)
        self.bind_activity_tracking()

if __name__ == "__main__":
    app = HallManagementSystem()
    app.mainloop()