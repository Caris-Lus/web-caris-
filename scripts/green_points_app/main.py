"""
Green Points - CO2 Emission Tracker Application
Main entry point with Tkinter GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
from PIL import Image, ImageTk

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_BG,
    PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, ERROR_COLOR,
    SUCCESS_COLOR, TEXT_COLOR, LIGHT_TEXT, CARD_BG, SIDEBAR_BG,
    FONT_LARGE, FONT_MEDIUM, FONT_SMALL, FONT_BUTTON, FONT_TITLE,
    POINTS_CONFIG, POINTS_PER_RUPEE
)
from modules.utils import initialize_csv_files, format_points, format_co2
from modules.auth import AuthManager
from modules.transport import TransportManager
from modules.recycling import RecyclingManager
from modules.drives import DrivesManager
from modules.admin import AdminManager
from modules.rewards import RewardsManager
from modules.charts import ChartsManager


class GreenPointsApp:
    """Main application class"""
    
    def __init__(self):
        # Initialize CSV files
        initialize_csv_files()
        
        # Initialize managers
        self.auth = AuthManager()
        self.transport = TransportManager()
        self.recycling = RecyclingManager()
        self.drives = DrivesManager()
        self.admin = AdminManager()
        self.rewards = RewardsManager()
        self.charts = ChartsManager()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=WINDOW_BG)
        self.root.resizable(True, True)
        
        # Center window
        self.center_window()
        
        # Current frame reference
        self.current_frame = None
        
        # Show welcome animation, then login
        self.show_welcome_animation()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - WINDOW_WIDTH) // 2
        y = (self.root.winfo_screenheight() - WINDOW_HEIGHT) // 2
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
    
    def clear_frame(self):
        """Clear current frame"""
        if self.current_frame:
            self.current_frame.destroy()
        self.charts.close_figures()
    
    def show_welcome_animation(self):
        """Show welcome screen with turtle-style animation"""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg=PRIMARY_COLOR)
        self.current_frame.pack(fill='both', expand=True)
        
        # Canvas for animation
        canvas = tk.Canvas(self.current_frame, width=400, height=300, 
                          bg=PRIMARY_COLOR, highlightthickness=0)
        canvas.pack(pady=50)
        
        # Draw a simple tree animation
        self.animate_tree(canvas)
        
        # App title
        title_label = tk.Label(self.current_frame, text=APP_NAME,
                              font=FONT_LARGE, fg=LIGHT_TEXT, bg=PRIMARY_COLOR)
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle = tk.Label(self.current_frame, 
                           text="Track your carbon footprint. Earn rewards.",
                           font=FONT_MEDIUM, fg=ACCENT_COLOR, bg=PRIMARY_COLOR)
        subtitle.pack()
        
        # Loading text
        loading = tk.Label(self.current_frame, text="Loading...",
                          font=FONT_SMALL, fg=LIGHT_TEXT, bg=PRIMARY_COLOR)
        loading.pack(pady=30)
        
        # Auto-proceed to login after 2 seconds
        self.root.after(2000, self.show_login)
    
    def animate_tree(self, canvas):
        """Draw animated tree on canvas"""
        cx, cy = 200, 250  # Center bottom
        
        # Draw trunk
        canvas.create_rectangle(185, 180, 215, 250, fill='#8B4513', outline='#5D2906')
        
        # Draw leaves (circles forming tree shape)
        leaf_positions = [
            (200, 80, 60),   # Top
            (150, 120, 50),  # Left
            (250, 120, 50),  # Right
            (130, 160, 45),  # Far left
            (200, 140, 55),  # Center
            (270, 160, 45),  # Far right
        ]
        
        for i, (x, y, r) in enumerate(leaf_positions):
            # Animate by drawing with delay
            def draw_leaf(x=x, y=y, r=r):
                canvas.create_oval(x-r, y-r, x+r, y+r, 
                                  fill=SECONDARY_COLOR, outline=PRIMARY_COLOR, width=2)
            self.root.after(i * 150, draw_leaf)
    
    # ==================== LOGIN / REGISTER ====================
    
    def show_login(self):
        """Show login screen"""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg=WINDOW_BG)
        self.current_frame.pack(fill='both', expand=True)
        
        # Center container
        container = tk.Frame(self.current_frame, bg=CARD_BG, padx=40, pady=40)
        container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title
        tk.Label(container, text="Welcome Back!", font=FONT_LARGE,
                fg=PRIMARY_COLOR, bg=CARD_BG).pack(pady=(0, 10))
        
        tk.Label(container, text="Login to your Green Points account",
                font=FONT_SMALL, fg='gray', bg=CARD_BG).pack(pady=(0, 30))
        
        # Username
        tk.Label(container, text="Username", font=FONT_MEDIUM,
                fg=TEXT_COLOR, bg=CARD_BG, anchor='w').pack(fill='x')
        username_entry = tk.Entry(container, font=FONT_MEDIUM, width=30)
        username_entry.pack(pady=(5, 15), ipady=8)
        
        # Password
        tk.Label(container, text="Password", font=FONT_MEDIUM,
                fg=TEXT_COLOR, bg=CARD_BG, anchor='w').pack(fill='x')
        password_entry = tk.Entry(container, font=FONT_MEDIUM, width=30, show="*")
        password_entry.pack(pady=(5, 20), ipady=8)
        
        # Error label
        error_label = tk.Label(container, text="", font=FONT_SMALL,
                              fg=ERROR_COLOR, bg=CARD_BG)
        error_label.pack()
        
        # Login button
        def do_login():
            result = self.auth.login(username_entry.get(), password_entry.get())
            if result['success']:
                self.show_dashboard()
            else:
                error_label.config(text=result['message'])
        
        login_btn = tk.Button(container, text="Login", font=FONT_BUTTON,
                             bg=PRIMARY_COLOR, fg=LIGHT_TEXT, width=20,
                             command=do_login, cursor='hand2')
        login_btn.pack(pady=20, ipady=8)
        
        # Register link
        register_frame = tk.Frame(container, bg=CARD_BG)
        register_frame.pack(pady=10)
        tk.Label(register_frame, text="Don't have an account?", 
                font=FONT_SMALL, fg='gray', bg=CARD_BG).pack(side='left')
        register_link = tk.Label(register_frame, text=" Sign up", 
                                font=FONT_SMALL, fg=PRIMARY_COLOR, bg=CARD_BG,
                                cursor='hand2')
        register_link.pack(side='left')
        register_link.bind('<Button-1>', lambda e: self.show_register())
        
        # Bind Enter key
        password_entry.bind('<Return>', lambda e: do_login())
    
    def show_register(self):
        """Show registration screen"""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg=WINDOW_BG)
        self.current_frame.pack(fill='both', expand=True)
        
        # Center container
        container = tk.Frame(self.current_frame, bg=CARD_BG, padx=40, pady=40)
        container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title
        tk.Label(container, text="Create Account", font=FONT_LARGE,
                fg=PRIMARY_COLOR, bg=CARD_BG).pack(pady=(0, 10))
        
        tk.Label(container, text="Join Green Points and start earning rewards",
                font=FONT_SMALL, fg='gray', bg=CARD_BG).pack(pady=(0, 30))
        
        # Username
        tk.Label(container, text="Username", font=FONT_MEDIUM,
                fg=TEXT_COLOR, bg=CARD_BG, anchor='w').pack(fill='x')
        username_entry = tk.Entry(container, font=FONT_MEDIUM, width=30)
        username_entry.pack(pady=(5, 15), ipady=8)
        
        # Email
        tk.Label(container, text="Email", font=FONT_MEDIUM,
                fg=TEXT_COLOR, bg=CARD_BG, anchor='w').pack(fill='x')
        email_entry = tk.Entry(container, font=FONT_MEDIUM, width=30)
        email_entry.pack(pady=(5, 15), ipady=8)
        
        # Password
        tk.Label(container, text="Password", font=FONT_MEDIUM,
                fg=TEXT_COLOR, bg=CARD_BG, anchor='w').pack(fill='x')
        password_entry = tk.Entry(container, font=FONT_MEDIUM, width=30, show="*")
        password_entry.pack(pady=(5, 20), ipady=8)
        
        # Message label
        msg_label = tk.Label(container, text="", font=FONT_SMALL, bg=CARD_BG)
        msg_label.pack()
        
        # Register button
        def do_register():
            result = self.auth.register(
                username_entry.get(), 
                password_entry.get(),
                email_entry.get()
            )
            if result['success']:
                msg_label.config(text=result['message'], fg=SUCCESS_COLOR)
                self.root.after(1500, self.show_login)
            else:
                msg_label.config(text=result['message'], fg=ERROR_COLOR)
        
        register_btn = tk.Button(container, text="Create Account", font=FONT_BUTTON,
                                bg=PRIMARY_COLOR, fg=LIGHT_TEXT, width=20,
                                command=do_register, cursor='hand2')
        register_btn.pack(pady=20, ipady=8)
        
        # Login link
        login_frame = tk.Frame(container, bg=CARD_BG)
        login_frame.pack(pady=10)
        tk.Label(login_frame, text="Already have an account?", 
                font=FONT_SMALL, fg='gray', bg=CARD_BG).pack(side='left')
        login_link = tk.Label(login_frame, text=" Login", 
                             font=FONT_SMALL, fg=PRIMARY_COLOR, bg=CARD_BG,
                             cursor='hand2')
        login_link.pack(side='left')
        login_link.bind('<Button-1>', lambda e: self.show_login())
    
    # ==================== MAIN DASHBOARD ====================
    
    def show_dashboard(self):
        """Show main dashboard with sidebar navigation"""
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg=WINDOW_BG)
        self.current_frame.pack(fill='both', expand=True)
        
        # Sidebar
        sidebar = tk.Frame(self.current_frame, bg=SIDEBAR_BG, width=200)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # User info
        user = self.auth.get_current_user()
        tk.Label(sidebar, text=f"Hi, {user['username']}!", font=FONT_TITLE,
                fg=LIGHT_TEXT, bg=SIDEBAR_BG).pack(pady=(30, 5))
        tk.Label(sidebar, text=f"{format_points(user['total_points'])} points",
                font=FONT_MEDIUM, fg=ACCENT_COLOR, bg=SIDEBAR_BG).pack()
        
        # Navigation buttons
        nav_frame = tk.Frame(sidebar, bg=SIDEBAR_BG)
        nav_frame.pack(pady=30, fill='x')
        
        nav_buttons = [
            ("Dashboard", self.show_dashboard_content),
            ("Transport", self.show_transport),
            ("Recycling", self.show_recycling),
            ("Drives", self.show_drives),
            ("Rewards", self.show_rewards),
            ("Statistics", self.show_statistics),
        ]
        
        # Add admin button if admin
        if self.auth.is_admin():
            nav_buttons.append(("Admin Panel", self.show_admin))
        
        for text, command in nav_buttons:
            btn = tk.Button(nav_frame, text=text, font=FONT_MEDIUM,
                           bg=SIDEBAR_BG, fg=LIGHT_TEXT, bd=0,
                           activebackground=PRIMARY_COLOR,
                           command=lambda c=command: self.load_content(c),
                           cursor='hand2', anchor='w', padx=20)
            btn.pack(fill='x', pady=2, ipady=10)
        
        # Logout button
        logout_btn = tk.Button(sidebar, text="Logout", font=FONT_BUTTON,
                              bg=ERROR_COLOR, fg=LIGHT_TEXT,
                              command=self.logout, cursor='hand2')
        logout_btn.pack(side='bottom', pady=30, padx=20, fill='x', ipady=5)
        
        # Content area
        self.content_frame = tk.Frame(self.current_frame, bg=WINDOW_BG)
        self.content_frame.pack(side='right', fill='both', expand=True, padx=20, pady=20)
        
        # Show dashboard content by default
        self.show_dashboard_content()
    
    def load_content(self, content_func):
        """Load content into content area"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.charts.close_figures()
        
        # Load new content
        content_func()
    
    def logout(self):
        """Logout and return to login"""
        self.auth.logout()
        self.show_login()
    
    def show_dashboard_content(self):
        """Show dashboard home content"""
        user = self.auth.get_current_user()
        stats = self.charts.create_summary_stats(user['user_id'])
        
        # Title
        tk.Label(self.content_frame, text="Dashboard", font=FONT_LARGE,
                fg=PRIMARY_COLOR, bg=WINDOW_BG).pack(anchor='w')
        
        # Stats cards
        cards_frame = tk.Frame(self.content_frame, bg=WINDOW_BG)
        cards_frame.pack(fill='x', pady=20)
        
        card_data = [
            ("Total Points", format_points(user['total_points']), PRIMARY_COLOR),
            ("CO2 Saved", format_co2(user['total_co2_saved']), SECONDARY_COLOR),
            ("Trips Taken", str(stats['total_trips']), ACCENT_COLOR),
            ("Items Recycled", str(stats['total_recycling']), "#2196F3"),
        ]
        
        for i, (title, value, color) in enumerate(card_data):
            card = tk.Frame(cards_frame, bg=CARD_BG, padx=20, pady=15)
            card.pack(side='left', padx=10, pady=5, fill='both', expand=True)
            
            tk.Label(card, text=title, font=FONT_SMALL, fg='gray', bg=CARD_BG).pack()
            tk.Label(card, text=value, font=FONT_TITLE, fg=color, bg=CARD_BG).pack()
        
        # Quick actions
        tk.Label(self.content_frame, text="Quick Actions", font=FONT_TITLE,
                fg=TEXT_COLOR, bg=WINDOW_BG).pack(anchor='w', pady=(20, 10))
        
        actions_frame = tk.Frame(self.content_frame, bg=WINDOW_BG)
        actions_frame.pack(fill='x')
        
        actions = [
            ("Log a Trip", self.show_transport, PRIMARY_COLOR),
            ("Recycle Waste", self.show_recycling, "#2196F3"),
            ("Join a Drive", self.show_drives, "#FF9800"),
            ("Redeem Points", self.show_rewards, "#9C27B0"),
        ]
        
        for text, command, color in actions:
            btn = tk.Button(actions_frame, text=text, font=FONT_BUTTON,
                           bg=color, fg=LIGHT_TEXT, width=15,
                           command=lambda c=command: self.load_content(c),
                           cursor='hand2')
            btn.pack(side='left', padx=10, pady=10, ipady=10)
    
    # ==================== TRANSPORT ====================
    
    def show_transport(self):
        """Show transport module"""
        tk.Label(self.content_frame, text="Log Your Trip", font=FONT_LARGE,
                fg=PRIMARY_COLOR, bg=WINDOW_BG).pack(anchor='w')
        
        tk.Label(self.content_frame, 
                text="Enter your route and choose eco-friendly transport to earn points!",
                font=FONT_SMALL, fg='gray', bg=WINDOW_BG).pack(anchor='w', pady=(5, 20))
        
        # Route input
        input_frame = tk.Frame(self.content_frame, bg=CARD_BG, padx=30, pady=20)
        input_frame.pack(fill='x')
        
        # Source
        tk.Label(input_frame, text="From (Source)", font=FONT_MEDIUM,
                fg=TEXT_COLOR, bg=CARD_BG).pack(anchor='w')
        source_entry = tk.Entry(input_frame, font=FONT_MEDIUM, width=40)
        source_entry.pack(pady=(5, 15), ipady=5)
        
        # Destination
        tk.Label(input_frame, text="To (Destination)", font=FONT_MEDIUM,
                fg=TEXT_COLOR, bg=CARD_BG).pack(anchor='w')
        dest_entry = tk.Entry(input_frame, font=FONT_MEDIUM, width=40)
        dest_entry.pack(pady=(5, 15), ipady=5)
        
        # Available locations hint
        locations = self.transport.get_available_locations()
        hint = f"Available: {', '.join(locations[:8])}..."
        tk.Label(input_frame, text=hint, font=FONT_SMALL, fg='gray', bg=CARD_BG,
                wraplength=400).pack(anchor='w')
        
        # Results frame
        results_frame = tk.Frame(self.content_frame, bg=WINDOW_BG)
        results_frame.pack(fill='both', expand=True, pady=20)
        
        # Calculate button
        def calculate_route():
            # Clear previous results
            for widget in results_frame.winfo_children():
                widget.destroy()
            
            result = self.transport.calculate_route(source_entry.get(), dest_entry.get())
            
            if not result['success']:
                tk.Label(results_frame, text=result['message'], font=FONT_MEDIUM,
                        fg=ERROR_COLOR, bg=WINDOW_BG).pack(pady=20)
                return
            
            data = result['data']
            
            # Show route info
            tk.Label(results_frame, 
                    text=f"{data['source']} to {data['destination']} ({data['distance_km']:.2f} km)",
                    font=FONT_TITLE, fg=TEXT_COLOR, bg=WINDOW_BG).pack(anchor='w')
            
            tk.Label(results_frame,
                    text=f"Car would emit: {data['car_co2_baseline']:.0f}g CO2",
                    font=FONT_SMALL, fg='gray', bg=WINDOW_BG).pack(anchor='w', pady=(5, 15))
            
            # Transport options
            for option in data['options']:
                opt_frame = tk.Frame(results_frame, bg=CARD_BG, padx=15, pady=10)
                opt_frame.pack(fill='x', pady=5)
                
                # Left side - info
                info_frame = tk.Frame(opt_frame, bg=CARD_BG)
                info_frame.pack(side='left', fill='x', expand=True)
                
                tk.Label(info_frame, text=option['name'], font=FONT_BUTTON,
                        fg=PRIMARY_COLOR, bg=CARD_BG).pack(anchor='w')
                tk.Label(info_frame, 
                        text=f"{option['time_mins']} mins | CO2 saved: {option['co2_saved']:.0f}g",
                        font=FONT_SMALL, fg='gray', bg=CARD_BG).pack(anchor='w')
                
                # Right side - points and button
                right_frame = tk.Frame(opt_frame, bg=CARD_BG)
                right_frame.pack(side='right')
                
                tk.Label(right_frame, text=f"+{option['points']} pts", font=FONT_TITLE,
                        fg=SUCCESS_COLOR, bg=CARD_BG).pack(side='left', padx=10)
                
                def select_mode(mode=option['mode'], dist=data['distance_km'],
                               src=data['source'], dst=data['destination'],
                               pts=option['points'], co2=option['co2_saved']):
                    user = self.auth.get_current_user()
                    result = self.transport.record_trip(user['user_id'], mode, dist, src, dst)
                    if result['success']:
                        self.auth.update_user_points(user['user_id'], pts, co2)
                        messagebox.showinfo("Success", result['message'])
                        self.load_content(self.show_dashboard_content)
                
                tk.Button(right_frame, text="Select", font=FONT_SMALL,
                         bg=PRIMARY_COLOR, fg=LIGHT_TEXT,
                         command=select_mode, cursor='hand2').pack(side='left', ipadx=10, ipady=3)
        
        calc_btn = tk.Button(input_frame, text="Find Routes", font=FONT_BUTTON,
                            bg=PRIMARY_COLOR, fg=LIGHT_TEXT, width=20,
                            command=calculate_route, cursor='hand2')
        calc_btn.pack(pady=15, ipady=5)
    
    # ==================== RECYCLING ====================
    
    def show_recycling(self):
        """Show recycling module"""
        tk.Label(self.content_frame, text="Recycle Waste", font=FONT_LARGE,
                fg=PRIMARY_COLOR, bg=WINDOW_BG).pack(anchor='w')
        
        tk.Label(self.content_frame,
                text="Select waste type and upload proof of proper disposal",
                font=FONT_SMALL, fg='gray', bg=WINDOW_BG).pack(anchor='w', pady=(5, 20))
        
        # Categories grid
        categories = self.recycling.get_categories()
        
        cat_frame = tk.Frame(self.content_frame, bg=WINDOW_BG)
        cat_frame.pack(fill='x')
        
        selected_category = tk.StringVar()
        
        for cat_key, cat_info in categories.items():
            card = tk.Frame(cat_frame, bg=CARD_BG, padx=15, pady=15)
            card.pack(side='left', padx=5, pady=5, fill='both', expand=True)
            
            tk.Radiobutton(card, text=cat_info['name'], variable=selected_category,
                          value=cat_key, font=FONT_BUTTON, bg=CARD_BG,
                          activebackground=CARD_BG).pack(anchor='w')
            
            tk.Label(card, text=f"+{cat_info['points']} points", font=FONT_SMALL,
                    fg=SUCCESS_COLOR, bg=CARD_BG).pack(anchor='w')
            
            tk.Label(card, text=cat_info['description'], font=FONT_SMALL,
                    fg='gray', bg=CARD_BG, wraplength=150).pack(anchor='w', pady=5)
        
        # Image upload
        upload_frame = tk.Frame(self.content_frame, bg=CARD_BG, padx=20, pady=20)
        upload_frame.pack(fill='x', pady=20)
        
        selected_image = tk.StringVar()
        
        tk.Label(upload_frame, text="Upload Proof Image", font=FONT_TITLE,
                fg=TEXT_COLOR, bg=CARD_BG).pack(anchor='w')
        
        image_label = tk.Label(upload_frame, text="No image selected", font=FONT_SMALL,
                              fg='gray', bg=CARD_BG)
        image_label.pack(anchor='w', pady=10)
        
        def select_image():
            file_path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
            )
            if file_path:
                selected_image.set(file_path)
                image_label.config(text=f"Selected: {os.path.basename(file_path)}")
        
        tk.Button(upload_frame, text="Choose Image", font=FONT_SMALL,
                 bg=SECONDARY_COLOR, fg=LIGHT_TEXT,
                 command=select_image, cursor='hand2').pack(anchor='w', ipadx=10, ipady=3)
        
        # Submit button
        msg_label = tk.Label(self.content_frame, text="", font=FONT_MEDIUM, bg=WINDOW_BG)
        msg_label.pack()
        
        def submit_recycling():
            if not selected_category.get():
                msg_label.config(text="Please select a waste category", fg=ERROR_COLOR)
                return
            if not selected_image.get():
                msg_label.config(text="Please upload a proof image", fg=ERROR_COLOR)
                return
            
            user = self.auth.get_current_user()
            result = self.recycling.submit_recycling(
                user['user_id'], user['username'],
                selected_category.get(), selected_image.get()
            )
            
            if result['success']:
                msg_label.config(text=result['message'], fg=SUCCESS_COLOR)
            else:
                msg_label.config(text=result['message'], fg=ERROR_COLOR)
        
        tk.Button(self.content_frame, text="Submit for Approval", font=FONT_BUTTON,
                 bg=PRIMARY_COLOR, fg=LIGHT_TEXT, width=25,
                 command=submit_recycling, cursor='hand2').pack(pady=10, ipady=8)
    
    # ==================== DRIVES ====================
    
    def show_drives(self):
        """Show community drives module"""
        tk.Label(self.content_frame, text="Community Drives", font=FONT_LARGE,
                fg=PRIMARY_COLOR, bg=WINDOW_BG).pack(anchor='w')
        
        tk.Label(self.content_frame,
                text="Participate in environmental and social drives to earn points",
                font=FONT_SMALL, fg='gray', bg=WINDOW_BG).pack(anchor='w', pady=(5, 20))
        
        # Drive types
        drives = self.drives.get_drive_types()
        
        drive_frame = tk.Frame(self.content_frame, bg=WINDOW_BG)
        drive_frame.pack(fill='x')
        
        selected_drive = tk.StringVar()
        
        for drive_key, drive_info in drives.items():
            card = tk.Frame(drive_frame, bg=CARD_BG, padx=20, pady=15)
            card.pack(side='left', padx=5, pady=5, fill='both', expand=True)
            
            tk.Radiobutton(card, text=drive_info['name'], variable=selected_drive,
                          value=drive_key, font=FONT_BUTTON, bg=CARD_BG,
                          activebackground=CARD_BG).pack(anchor='w')
            
            tk.Label(card, text=f"+{drive_info['points']} points", font=FONT_MEDIUM,
                    fg=SUCCESS_COLOR, bg=CARD_BG).pack(anchor='w')
            
            tk.Label(card, text=drive_info['description'], font=FONT_SMALL,
                    fg='gray', bg=CARD_BG, wraplength=180).pack(anchor='w', pady=5)
            
            # Tips
            for tip in drive_info['tips'][:2]:
                tk.Label(card, text=f"- {tip}", font=FONT_SMALL,
                        fg='gray', bg=CARD_BG, wraplength=180).pack(anchor='w')
        
        # Image upload
        upload_frame = tk.Frame(self.content_frame, bg=CARD_BG, padx=20, pady=20)
        upload_frame.pack(fill='x', pady=20)
        
        selected_image = tk.StringVar()
        
        tk.Label(upload_frame, text="Upload Proof Image", font=FONT_TITLE,
                fg=TEXT_COLOR, bg=CARD_BG).pack(anchor='w')
        
        image_label = tk.Label(upload_frame, text="No image selected", font=FONT_SMALL,
                              fg='gray', bg=CARD_BG)
        image_label.pack(anchor='w', pady=10)
        
        def select_image():
            file_path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
            )
            if file_path:
                selected_image.set(file_path)
                image_label.config(text=f"Selected: {os.path.basename(file_path)}")
        
        tk.Button(upload_frame, text="Choose Image", font=FONT_SMALL,
                 bg=SECONDARY_COLOR, fg=LIGHT_TEXT,
                 command=select_image, cursor='hand2').pack(anchor='w', ipadx=10, ipady=3)
        
        # Submit
        msg_label = tk.Label(self.content_frame, text="", font=FONT_MEDIUM, bg=WINDOW_BG)
        msg_label.pack()
        
        def submit_drive():
            if not selected_drive.get():
                msg_label.config(text="Please select a drive type", fg=ERROR_COLOR)
                return
            if not selected_image.get():
                msg_label.config(text="Please upload a proof image", fg=ERROR_COLOR)
                return
            
            user = self.auth.get_current_user()
            result = self.drives.submit_drive(
                user['user_id'], user['username'],
                selected_drive.get(), selected_image.get()
            )
            
            if result['success']:
                msg_label.config(text=result['message'], fg=SUCCESS_COLOR)
            else:
                msg_label.config(text=result['message'], fg=ERROR_COLOR)
        
        tk.Button(self.content_frame, text="Submit for Approval", font=FONT_BUTTON,
                 bg=PRIMARY_COLOR, fg=LIGHT_TEXT, width=25,
                 command=submit_drive, cursor='hand2').pack(pady=10, ipady=8)
    
    # ==================== REWARDS ====================
    
    def show_rewards(self):
        """Show rewards/redemption module"""
        user = self.auth.get_current_user()
        
        tk.Label(self.content_frame, text="Redeem Rewards", font=FONT_LARGE,
                fg=PRIMARY_COLOR, bg=WINDOW_BG).pack(anchor='w')
        
        # Current balance
        balance_frame = tk.Frame(self.content_frame, bg=CARD_BG, padx=30, pady=20)
        balance_frame.pack(fill='x', pady=20)
        
        tk.Label(balance_frame, text="Your Balance", font=FONT_MEDIUM,
                fg='gray', bg=CARD_BG).pack()
        tk.Label(balance_frame, text=f"{format_points(user['total_points'])} points",
                font=FONT_LARGE, fg=PRIMARY_COLOR, bg=CARD_BG).pack()
        
        rupee_value = self.rewards.calculate_rupee_value(user['total_points'])
        tk.Label(balance_frame, text=f"Worth Rs. {rupee_value:.2f}",
                font=FONT_MEDIUM, fg=SECONDARY_COLOR, bg=CARD_BG).pack()
        
        # Exchange rate info
        info = self.rewards.get_redemption_info()
        tk.Label(self.content_frame, text=f"Exchange Rate: {info['rate_display']}",
                font=FONT_SMALL, fg='gray', bg=WINDOW_BG).pack(pady=10)
        
        # Redemption options
        tk.Label(self.content_frame, text="Quick Redeem", font=FONT_TITLE,
                fg=TEXT_COLOR, bg=WINDOW_BG).pack(anchor='w', pady=(20, 10))
        
        options_frame = tk.Frame(self.content_frame, bg=WINDOW_BG)
        options_frame.pack(fill='x')
        
        options = self.rewards.get_available_redemption_options(user['total_points'])
        
        msg_label = tk.Label(self.content_frame, text="", font=FONT_MEDIUM, bg=WINDOW_BG)
        msg_label.pack(pady=10)
        
        if not options:
            tk.Label(options_frame, 
                    text=f"You need at least {info['min_redemption_points']} points to redeem",
                    font=FONT_MEDIUM, fg='gray', bg=WINDOW_BG).pack()
        else:
            for opt in options[:6]:  # Show max 6 options
                def redeem(pts=opt['points']):
                    result = self.rewards.redeem_points(user['user_id'], pts)
                    if result['success']:
                        messagebox.showinfo("Success", result['message'])
                        self.auth.current_user['total_points'] = result['remaining_points']
                        self.load_content(self.show_rewards)
                    else:
                        msg_label.config(text=result['message'], fg=ERROR_COLOR)
                
                btn = tk.Button(options_frame, text=opt['display'], font=FONT_MEDIUM,
                               bg=CARD_BG, fg=TEXT_COLOR, width=25,
                               command=redeem, cursor='hand2')
                btn.pack(pady=3, ipady=5)
        
        # Custom redemption
        custom_frame = tk.Frame(self.content_frame, bg=CARD_BG, padx=20, pady=15)
        custom_frame.pack(fill='x', pady=20)
        
        tk.Label(custom_frame, text="Custom Amount", font=FONT_TITLE,
                fg=TEXT_COLOR, bg=CARD_BG).pack(anchor='w')
        
        entry_frame = tk.Frame(custom_frame, bg=CARD_BG)
        entry_frame.pack(fill='x', pady=10)
        
        points_entry = tk.Entry(entry_frame, font=FONT_MEDIUM, width=15)
        points_entry.pack(side='left', ipady=5)
        tk.Label(entry_frame, text=" points", font=FONT_MEDIUM, bg=CARD_BG).pack(side='left')
        
        def custom_redeem():
            try:
                pts = int(points_entry.get())
                result = self.rewards.redeem_points(user['user_id'], pts)
                if result['success']:
                    messagebox.showinfo("Success", result['message'])
                    self.auth.current_user['total_points'] = result['remaining_points']
                    self.load_content(self.show_rewards)
                else:
                    msg_label.config(text=result['message'], fg=ERROR_COLOR)
            except ValueError:
                msg_label.config(text="Please enter a valid number", fg=ERROR_COLOR)
        
        tk.Button(entry_frame, text="Redeem", font=FONT_BUTTON,
                 bg=PRIMARY_COLOR, fg=LIGHT_TEXT,
                 command=custom_redeem, cursor='hand2').pack(side='left', padx=10, ipadx=10)
    
    # ==================== STATISTICS ====================
    
    def show_statistics(self):
        """Show statistics and charts"""
        user = self.auth.get_current_user()
        
        tk.Label(self.content_frame, text="Your Statistics", font=FONT_LARGE,
                fg=PRIMARY_COLOR, bg=WINDOW_BG).pack(anchor='w')
        
        # CO2 Savings Chart
        chart1_frame = tk.Frame(self.content_frame, bg=CARD_BG)
        chart1_frame.pack(fill='x', pady=10)
        
        canvas1 = self.charts.create_co2_savings_chart(user['user_id'], chart1_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill='x', padx=10, pady=10)
        
        # Points Breakdown Chart
        chart2_frame = tk.Frame(self.content_frame, bg=CARD_BG)
        chart2_frame.pack(fill='x', pady=10)
        
        canvas2 = self.charts.create_points_breakdown_chart(user['user_id'], chart2_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill='x', padx=10, pady=10)
    
    # ==================== ADMIN PANEL ====================
    
    def show_admin(self):
        """Show admin approval panel"""
        if not self.auth.is_admin():
            return
        
        tk.Label(self.content_frame, text="Admin Panel", font=FONT_LARGE,
                fg=PRIMARY_COLOR, bg=WINDOW_BG).pack(anchor='w')
        
        # Stats
        stats = self.admin.get_submission_stats()
        stats_frame = tk.Frame(self.content_frame, bg=WINDOW_BG)
        stats_frame.pack(fill='x', pady=10)
        
        for label, value in [("Pending", stats['pending']), 
                            ("Approved", stats['approved']),
                            ("Rejected", stats['rejected'])]:
            card = tk.Frame(stats_frame, bg=CARD_BG, padx=20, pady=10)
            card.pack(side='left', padx=5)
            tk.Label(card, text=label, font=FONT_SMALL, fg='gray', bg=CARD_BG).pack()
            tk.Label(card, text=str(value), font=FONT_TITLE, fg=PRIMARY_COLOR, bg=CARD_BG).pack()
        
        # Pending approvals
        tk.Label(self.content_frame, text="Pending Approvals", font=FONT_TITLE,
                fg=TEXT_COLOR, bg=WINDOW_BG).pack(anchor='w', pady=(20, 10))
        
        # Scrollable frame
        canvas = tk.Canvas(self.content_frame, bg=WINDOW_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=WINDOW_BG)
        
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        pending = self.admin.get_pending_approvals()
        
        if not pending:
            tk.Label(scrollable, text="No pending approvals", font=FONT_MEDIUM,
                    fg='gray', bg=WINDOW_BG).pack(pady=20)
        else:
            for item in pending:
                item_frame = tk.Frame(scrollable, bg=CARD_BG, padx=15, pady=10)
                item_frame.pack(fill='x', pady=5, padx=5)
                
                # Info
                info_frame = tk.Frame(item_frame, bg=CARD_BG)
                info_frame.pack(side='left', fill='x', expand=True)
                
                tk.Label(info_frame, text=f"User: {item['username']}", font=FONT_BUTTON,
                        fg=TEXT_COLOR, bg=CARD_BG).pack(anchor='w')
                tk.Label(info_frame, 
                        text=f"Type: {item['activity_type']} - {item['category']}",
                        font=FONT_SMALL, fg='gray', bg=CARD_BG).pack(anchor='w')
                tk.Label(info_frame, text=f"Points: {item['points']}",
                        font=FONT_SMALL, fg=SUCCESS_COLOR, bg=CARD_BG).pack(anchor='w')
                
                # View image button
                def view_image(path=item['image_path']):
                    if os.path.exists(path):
                        try:
                            import subprocess
                            subprocess.Popen(['xdg-open', path])  # Linux
                        except:
                            messagebox.showinfo("Image Path", path)
                
                # Buttons
                btn_frame = tk.Frame(item_frame, bg=CARD_BG)
                btn_frame.pack(side='right')
                
                tk.Button(btn_frame, text="View", font=FONT_SMALL,
                         bg='gray', fg=LIGHT_TEXT,
                         command=view_image, cursor='hand2').pack(side='left', padx=2)
                
                def approve(aid=item['approval_id']):
                    result = self.admin.approve_submission(aid)
                    messagebox.showinfo("Result", result['message'])
                    self.load_content(self.show_admin)
                
                def reject(aid=item['approval_id']):
                    result = self.admin.reject_submission(aid)
                    messagebox.showinfo("Result", result['message'])
                    self.load_content(self.show_admin)
                
                tk.Button(btn_frame, text="Approve", font=FONT_SMALL,
                         bg=SUCCESS_COLOR, fg=LIGHT_TEXT,
                         command=approve, cursor='hand2').pack(side='left', padx=2)
                
                tk.Button(btn_frame, text="Reject", font=FONT_SMALL,
                         bg=ERROR_COLOR, fg=LIGHT_TEXT,
                         command=reject, cursor='hand2').pack(side='left', padx=2)
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


# Entry point
if __name__ == "__main__":
    app = GreenPointsApp()
    app.run()
