import sys
import os
import datetime
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QLabel, QPushButton, QTableWidget, 
                            QTableWidgetItem, QLineEdit, QMessageBox, QFileDialog,
                            QTabWidget, QGroupBox, QStackedWidget, QComboBox, QFrame)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QFont, QIcon, QColor, QPixmap, QPalette
import speech_recognition as sr
from pygame import mixer
import soundfile as sf
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
from dotenv import load_dotenv
from pymongo import MongoClient
import bcrypt
import uuid
import logging

warnings.filterwarnings("ignore")

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("voice_attendance.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LoginWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Login")
        self.setGeometry(300, 300, 800, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
            }
            QLabel {
                color: #495057;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ced4da;
                border-radius: 5px;
                min-width: 250px;
                font-size: 14px;
            }
            QPushButton {
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                background-color: #4e73df;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2e59d9;
            }
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #ddd;
            }
        """)
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Left side - Image/Graphics
        left_frame = QFrame()
        left_frame.setFixedWidth(400)
        left_layout = QVBoxLayout(left_frame)
        
        # Add a logo or image here
        logo_label = QLabel()
        logo_pixmap = QPixmap("logo.png") if os.path.exists("logo.png") else QPixmap()
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(350, 350, Qt.KeepAspectRatio))
        else:
            logo_label.setText("Voice Attendance System")
            logo_label.setFont(QFont("Arial", 24, QFont.Bold))
        
        logo_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(logo_label)
        left_layout.addStretch()
        
        # Right side - Login Form
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Welcome Back!")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #4e73df; margin-bottom: 30px;")
        
        # Form elements
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        
        # Username field
        username_layout = QVBoxLayout()
        username_label = QLabel("Username:")
        username_label.setFont(QFont("Arial", 12))
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter your username")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username)
        
        # Password field
        password_layout = QVBoxLayout()
        password_label = QLabel("Password:")
        password_label.setFont(QFont("Arial", 12))
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter your password")
        self.password.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.authenticate)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #4e73df;
                padding: 12px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2e59d9;
            }
        """)
        
        # Add elements to form
        form_layout.addLayout(username_layout)
        form_layout.addLayout(password_layout)
        form_layout.addWidget(login_btn)
        
        # Add all to right layout
        right_layout.addWidget(title)
        right_layout.addLayout(form_layout)
        right_layout.addStretch()
        
        # Add frames to main layout
        layout.addWidget(left_frame)
        layout.addWidget(right_frame)
    
    def authenticate(self):
        username = self.username.text()
        password = self.password.text()
        
        try:
            # Get stored credentials from .env
            stored_user = os.getenv("ADMIN_USERNAME")
            stored_pass = os.getenv("ADMIN_PASSWORD")
            
            if not stored_user or not stored_pass:
                QMessageBox.critical(self, "Error", "Admin credentials not configured")
                logger.error("Admin credentials not configured in environment variables")
                return
                
            # Verify credentials
            if username == stored_user and password == stored_pass:
                logger.info("Login successful")
                # Create fade out animation
                self.animation = QPropertyAnimation(self, b"windowOpacity")
                self.animation.setDuration(500)
                self.animation.setStartValue(1)
                self.animation.setEndValue(0)
                self.animation.setEasingCurve(QEasingCurve.InOutQuad)
                self.animation.finished.connect(self.parent_window.show_main_app)
                self.animation.start()
            else:
                logger.warning(f"Failed login attempt for username: {username}")
                # Shake animation for wrong credentials
                self.shake_animation = QPropertyAnimation(self, b"pos")
                self.shake_animation.setDuration(200)
                self.shake_animation.setLoopCount(2)
                self.shake_animation.setKeyValueAt(0, self.pos())
                self.shake_animation.setKeyValueAt(0.25, self.pos() + QPoint(10, 0))
                self.shake_animation.setKeyValueAt(0.75, self.pos() + QPoint(-10, 0))
                self.shake_animation.setEndValue(self.pos())
                self.shake_animation.start()
                
                QMessageBox.critical(self, "Error", "Invalid credentials")
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred during authentication: {str(e)}")

class VoiceAttendanceSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice Attendance System")
        self.setGeometry(100, 100, 1200, 800)
        
        # MongoDB connection attributes
        self.client = None
        self.db = None
        self.students_col = None
        self.attendance_col = None
        self.classes_col = None
        
        # Create stacked widget for login/main app
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create login page
        self.login_page = LoginWindow(self)
        self.stacked_widget.addWidget(self.login_page)
        
        # Initialize main app page (will be created later)
        self.main_app_page = None
        
        # Show login page first
        self.stacked_widget.setCurrentIndex(0)
    
    def connect_to_mongodb(self):
        """Connect to MongoDB and initialize collections"""
        try:
            mongodb_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
            logger.info(f"Connecting to MongoDB at: {mongodb_uri}")
            
            self.client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            # Test the connection
            self.client.server_info()
            
            self.db = self.client["voice_attendance_system"]
            self.students_col = self.db["students"]
            self.attendance_col = self.db["attendance"]
            self.classes_col = self.db["classes"]
            
            # Create indexes if they don't exist
            self.students_col.create_index("student_id", unique=True)
            self.attendance_col.create_index([("student_id", 1), ("date", 1)], unique=True)
            
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Could not connect to MongoDB: {str(e)}")
            QMessageBox.critical(self, "Database Error", f"Could not connect to MongoDB: {str(e)}")
            sys.exit(1)
    
    def show_main_app(self):
        """Show the main application after successful login"""
        try:
            if self.main_app_page is None:
                # Initialize main app only once
                self.main_app_page = QWidget()
                self.init_ui()
                self.stacked_widget.addWidget(self.main_app_page)
            
            # Connect to MongoDB
            self.connect_to_mongodb()
            
            # Set current widget to main app
            self.stacked_widget.setCurrentIndex(1)
            
            # Create fade in animation
            self.main_app_page.setWindowOpacity(0)
            self.animation = QPropertyAnimation(self.main_app_page, b"windowOpacity")
            self.animation.setDuration(500)
            self.animation.setStartValue(0)
            self.animation.setEndValue(1)
            self.animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.animation.start()
            
            # Load data
            self.load_classes()
            self.load_enrolled_students()
            
            logger.info("Main application loaded successfully")
        except Exception as e:
            logger.error(f"Error loading main application: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load application: {str(e)}")
    
    def init_ui(self):
        """Initialize the main application UI"""
        try:
            # Main widget and layout
            self.main_app_page = QWidget()
            main_layout = QVBoxLayout()
            
            # Create tabs
            self.tabs = QTabWidget()
            self.attendance_tab = QWidget()
            self.enrollment_tab = QWidget()
            self.classes_tab = QWidget()
            self.reports_tab = QWidget()
            
            # Add tabs
            self.tabs.addTab(self.attendance_tab, "Attendance")
            self.tabs.addTab(self.enrollment_tab, "Enrollment")
            self.tabs.addTab(self.classes_tab, "Classes")
            self.tabs.addTab(self.reports_tab, "Reports")
            
            # Setup tabs
            self.setup_attendance_tab()
            self.setup_enrollment_tab()
            self.setup_classes_tab()
            self.setup_reports_tab()
            
            # Add tabs to main layout
            main_layout.addWidget(self.tabs)
            self.main_app_page.setLayout(main_layout)
            
            # Apply stylesheet
            self.setStyleSheet(self.get_stylesheet())
            
            # Initialize other components
            self.create_directories()
            mixer.init()
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.adjust_microphone()
            
            logger.info("UI initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing UI: {str(e)}")
            raise
       
    def get_stylesheet(self):
        return """
            QMainWindow, QWidget {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333;
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                min-width: 200px;
            }
            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                margin-top: 5px;
            }
            QTabBar::tab {
                padding: 8px 16px;
                background: #e0e0e0;
                border: 1px solid #ddd;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #f5f5f5;
                border-bottom: 2px solid #4CAF50;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                gridline-color: #eee;
            }
            QHeaderView::section {
                background-color: #f2f2f2;
                padding: 8px;
                border: none;
            }
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
    
    def create_directories(self):
        """Create necessary directories for the application"""
        try:
            os.makedirs("enrollments", exist_ok=True)
            os.makedirs("sounds", exist_ok=True)
            os.makedirs("attendance_records", exist_ok=True)
            os.makedirs("logs", exist_ok=True)
            logger.info("Created necessary directories")
        except Exception as e:
            logger.error(f"Error creating directories: {str(e)}")
            raise
    
    def setup_attendance_tab(self):
        """Setup the attendance tab UI"""
        try:
            layout = QVBoxLayout()
            
            # Class selection
            class_layout = QHBoxLayout()
            class_layout.addWidget(QLabel("Select Class:"))
            
            self.class_combo = QComboBox()
            self.class_combo.currentIndexChanged.connect(self.load_class_sections)
            class_layout.addWidget(self.class_combo)
            
            self.section_combo = QComboBox()
            self.section_combo.currentIndexChanged.connect(self.load_class_students)
            class_layout.addWidget(QLabel("Section:"))
            class_layout.addWidget(self.section_combo)
            class_layout.addStretch()
            
            layout.addLayout(class_layout)
            
            # Current time display
            self.time_label = QLabel()
            self.time_label.setFont(QFont("Arial", 12))
            self.update_time()
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_time)
            self.timer.start(1000)
            layout.addWidget(self.time_label)
            
            # Voice attendance section
            voice_group = QGroupBox("Voice Attendance")
            voice_layout = QVBoxLayout()
            
            self.voice_status = QLabel("Ready to record attendance")
            self.record_btn = QPushButton("Start Voice Attendance")
            self.record_btn.clicked.connect(self.start_attendance)
            
            voice_layout.addWidget(self.voice_status)
            voice_layout.addWidget(self.record_btn, 0, Qt.AlignCenter)
            voice_group.setLayout(voice_layout)
            layout.addWidget(voice_group)
            
            # Manual attendance section
            manual_group = QGroupBox("Manual Attendance")
            manual_layout = QVBoxLayout()
            
            self.student_combo = QComboBox()
            self.mark_btn = QPushButton("Mark Present")
            self.mark_btn.clicked.connect(self.mark_manual_attendance)
            
            manual_layout.addWidget(QLabel("Select Student:"))
            manual_layout.addWidget(self.student_combo)
            manual_layout.addWidget(self.mark_btn, 0, Qt.AlignCenter)
            manual_group.setLayout(manual_layout)
            layout.addWidget(manual_group)
            
            # Attendance table
            self.attendance_table = QTableWidget()
            self.attendance_table.setColumnCount(5)
            self.attendance_table.setHorizontalHeaderLabels(["ID", "Name", "Class", "Time", "Status"])
            layout.addWidget(self.attendance_table)
            
            # Buttons
            btn_layout = QHBoxLayout()
            self.export_btn = QPushButton("Export to Excel")
            self.export_btn.clicked.connect(self.export_to_excel)
            self.clear_btn = QPushButton("Clear Today's Attendance")
            self.clear_btn.clicked.connect(self.clear_attendance)
            
            btn_layout.addWidget(self.export_btn)
            btn_layout.addWidget(self.clear_btn)
            layout.addLayout(btn_layout)
            
            self.attendance_tab.setLayout(layout)
            logger.info("Attendance tab setup completed")
        except Exception as e:
            logger.error(f"Error setting up attendance tab: {str(e)}")
            raise
    
    def load_class_sections(self):
        """Load sections for the selected class"""
        try:
            class_id = self.class_combo.currentData()
            if not class_id:
                return
                
            # Clear existing sections
            self.section_combo.clear()
            
            # Find the selected class
            selected_class = next((cls for cls in self.classes if cls['_id'] == class_id), None)
            if selected_class:
                # Add all sections of this class
                for section in selected_class['sections']:
                    self.section_combo.addItem(section)
                
                logger.info(f"Loaded sections for class {selected_class['name']}")
        except Exception as e:
            logger.error(f"Error loading class sections: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load sections: {str(e)}")
    
    def setup_enrollment_tab(self):
        """Setup the enrollment tab UI"""
        try:
            layout = QVBoxLayout()
            
            # Enrollment form
            form_group = QGroupBox("Enroll New Student")
            form_layout = QVBoxLayout()
            
            # Class selection
            class_layout = QHBoxLayout()
            class_layout.addWidget(QLabel("Class:"))
            self.enroll_class_combo = QComboBox()
            class_layout.addWidget(self.enroll_class_combo)
            class_layout.addWidget(QLabel("Section:"))
            self.enroll_section_combo = QComboBox()
            class_layout.addWidget(self.enroll_section_combo)
            form_layout.addLayout(class_layout)
            
            # Name and ID
            name_layout = QHBoxLayout()
            name_layout.addWidget(QLabel("Full Name:"))
            self.enroll_name = QLineEdit()
            name_layout.addWidget(self.enroll_name)
            form_layout.addLayout(name_layout)
            
            id_layout = QHBoxLayout()
            id_layout.addWidget(QLabel("Student ID:"))
            self.enroll_id = QLineEdit()
            id_layout.addWidget(self.enroll_id)
            form_layout.addLayout(id_layout)
            
            # Record button
            self.record_enroll_btn = QPushButton("Record Voice Sample")
            self.record_enroll_btn.clicked.connect(self.record_voice_sample)
            form_layout.addWidget(self.record_enroll_btn, 0, Qt.AlignCenter)
            
            # Status
            self.enroll_status = QLabel("Ready to record")
            form_layout.addWidget(self.enroll_status)
            
            form_group.setLayout(form_layout)
            layout.addWidget(form_group)
            
            # Enrolled students table
            self.enrolled_table = QTableWidget()
            self.enrolled_table.setColumnCount(4)
            self.enrolled_table.setHorizontalHeaderLabels(["ID", "Name", "Class", "Section"])
            layout.addWidget(self.enrolled_table)
            
            self.enrollment_tab.setLayout(layout)
            logger.info("Enrollment tab setup completed")
        except Exception as e:
            logger.error(f"Error setting up enrollment tab: {str(e)}")
            raise
    
    def setup_classes_tab(self):
        """Setup the classes tab UI"""
        try:
            layout = QVBoxLayout()
            
            # Add class form
            form_group = QGroupBox("Add New Class")
            form_layout = QVBoxLayout()
            
            # Class name
            name_layout = QHBoxLayout()
            name_layout.addWidget(QLabel("Class Name:"))
            self.new_class_name = QLineEdit()
            name_layout.addWidget(self.new_class_name)
            form_layout.addLayout(name_layout)
            
            # Sections
            section_layout = QHBoxLayout()
            section_layout.addWidget(QLabel("Sections (comma separated):"))
            self.new_class_sections = QLineEdit()
            section_layout.addWidget(self.new_class_sections)
            form_layout.addLayout(section_layout)
            
            # Add button
            self.add_class_btn = QPushButton("Add Class")
            self.add_class_btn.clicked.connect(self.add_new_class)
            form_layout.addWidget(self.add_class_btn, 0, Qt.AlignCenter)
            
            form_group.setLayout(form_layout)
            layout.addWidget(form_group)
            
            # Classes table
            self.classes_table = QTableWidget()
            self.classes_table.setColumnCount(3)
            self.classes_table.setHorizontalHeaderLabels(["Class Name", "Sections", "Students"])
            layout.addWidget(self.classes_table)
            
            self.classes_tab.setLayout(layout)
            logger.info("Classes tab setup completed")
        except Exception as e:
            logger.error(f"Error setting up classes tab: {str(e)}")
            raise
    
    def setup_reports_tab(self):
        """Setup the reports tab UI"""
        try:
            layout = QVBoxLayout()
            
            # Filters
            filter_layout = QHBoxLayout()
            filter_layout.addWidget(QLabel("Class:"))
            self.report_class_combo = QComboBox()
            filter_layout.addWidget(self.report_class_combo)
            
            filter_layout.addWidget(QLabel("Section:"))
            self.report_section_combo = QComboBox()
            filter_layout.addWidget(self.report_section_combo)
            
            filter_layout.addWidget(QLabel("Date Range:"))
            self.report_start_date = QLineEdit()
            self.report_start_date.setPlaceholderText("YYYY-MM-DD")
            filter_layout.addWidget(self.report_start_date)
            
            filter_layout.addWidget(QLabel("to"))
            self.report_end_date = QLineEdit()
            self.report_end_date.setPlaceholderText("YYYY-MM-DD")
            filter_layout.addWidget(self.report_end_date)
            
            self.generate_report_btn = QPushButton("Generate Report")
            self.generate_report_btn.clicked.connect(self.generate_report)
            filter_layout.addWidget(self.generate_report_btn)
            
            layout.addLayout(filter_layout)
            
            # Report table
            self.report_table = QTableWidget()
            self.report_table.setColumnCount(6)
            self.report_table.setHorizontalHeaderLabels(["Date", "Class", "Section", "Student ID", "Name", "Status"])
            layout.addWidget(self.report_table)
            
            # Export button
            self.export_report_btn = QPushButton("Export Report")
            self.export_report_btn.clicked.connect(self.export_report)
            layout.addWidget(self.export_report_btn, 0, Qt.AlignRight)
            
            self.reports_tab.setLayout(layout)
            logger.info("Reports tab setup completed")
        except Exception as e:
            logger.error(f"Error setting up reports tab: {str(e)}")
            raise
    
    def update_time(self):
        """Update the current time display"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(f"Current Time: {current_time}")
    
    def adjust_microphone(self):
        """Adjust microphone for ambient noise"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("Microphone adjusted for ambient noise")
        except Exception as e:
            logger.error(f"Error adjusting microphone: {str(e)}")
            QMessageBox.warning(self, "Microphone Error", f"Could not adjust microphone: {str(e)}")
    
    def load_classes(self):
        """Load classes from MongoDB and populate dropdowns"""
        try:
            self.classes = list(self.classes_col.find({}))
            logger.info(f"Loaded {len(self.classes)} classes from database")
            
            # Clear and populate class combos
            self.class_combo.clear()
            self.enroll_class_combo.clear()
            self.report_class_combo.clear()
            
            for cls in self.classes:
                self.class_combo.addItem(cls['name'], cls['_id'])
                self.enroll_class_combo.addItem(cls['name'], cls['_id'])
                self.report_class_combo.addItem(cls['name'], cls['_id'])
            
            # Update classes table
            self.update_classes_table()
        except Exception as e:
            logger.error(f"Error loading classes: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load classes: {str(e)}")
    
    def update_classes_table(self):
        """Update the classes table with current data"""
        try:
            self.classes_table.setRowCount(len(self.classes))
            
            for row, cls in enumerate(self.classes):
                # Count students in this class
                student_count = self.students_col.count_documents({"class_id": cls['_id']})
                
                self.classes_table.setItem(row, 0, QTableWidgetItem(cls['name']))
                self.classes_table.setItem(row, 1, QTableWidgetItem(", ".join(cls['sections'])))
                self.classes_table.setItem(row, 2, QTableWidgetItem(str(student_count)))
            
            self.classes_table.resizeColumnsToContents()
            logger.info("Classes table updated")
        except Exception as e:
            logger.error(f"Error updating classes table: {str(e)}")
            raise
    
    def load_class_students(self):
        """Load students for the selected class and section"""
        try:
            class_id = self.class_combo.currentData()
            section = self.section_combo.currentText()
            
            if not class_id or not section:
                return
                
            # Load students from MongoDB
            students = list(self.students_col.find({
                "class_id": class_id,
                "section": section
            }))
            logger.info(f"Loaded {len(students)} students for class {class_id} section {section}")
            
            # Update student combo
            self.student_combo.clear()
            for student in students:
                self.student_combo.addItem(f"{student['name']} ({student['student_id']})", student['student_id'])
            
            # Update attendance table for this class/section
            self.update_attendance_table()
        except Exception as e:
            logger.error(f"Error loading class students: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load students: {str(e)}")
    
    def load_enrolled_students(self):
        """Load all enrolled students from MongoDB"""
        try:
            self.students = list(self.students_col.find({}))
            logger.info(f"Loaded {len(self.students)} enrolled students")
            self.update_enrolled_table()
            
            # Also update class sections when class selection changes
            self.enroll_class_combo.currentIndexChanged.connect(self.update_class_sections)
            self.report_class_combo.currentIndexChanged.connect(self.update_report_sections)
        except Exception as e:
            logger.error(f"Error loading enrolled students: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load enrolled students: {str(e)}")
    
    def update_class_sections(self):
        """Update sections dropdown when class is selected in enrollment"""
        try:
            class_id = self.enroll_class_combo.currentData()
            if not class_id:
                return
                
            # Find the class and get its sections
            cls = next((c for c in self.classes if c['_id'] == class_id), None)
            if cls:
                self.enroll_section_combo.clear()
                for section in cls['sections']:
                    self.enroll_section_combo.addItem(section)
                logger.info(f"Updated sections for class {class_id}")
        except Exception as e:
            logger.error(f"Error updating class sections: {str(e)}")
            raise
    
    def update_report_sections(self):
        """Update sections dropdown when class is selected in reports"""
        try:
            class_id = self.report_class_combo.currentData()
            if not class_id:
                return
                
            # Find the class and get its sections
            cls = next((c for c in self.classes if c['_id'] == class_id), None)
            if cls:
                self.report_section_combo.clear()
                self.report_section_combo.addItem("All")
                for section in cls['sections']:
                    self.report_section_combo.addItem(section)
                logger.info(f"Updated report sections for class {class_id}")
        except Exception as e:
            logger.error(f"Error updating report sections: {str(e)}")
            raise
    
    def update_enrolled_table(self):
        """Update the enrolled students table"""
        try:
            self.enrolled_table.setRowCount(len(self.students))
            
            for row, student in enumerate(self.students):
                # Get class name
                class_name = next((c['name'] for c in self.classes if c['_id'] == student['class_id']), "Unknown")
                
                self.enrolled_table.setItem(row, 0, QTableWidgetItem(student['student_id']))
                self.enrolled_table.setItem(row, 1, QTableWidgetItem(student['name']))
                self.enrolled_table.setItem(row, 2, QTableWidgetItem(class_name))
                self.enrolled_table.setItem(row, 3, QTableWidgetItem(student['section']))
            
            self.enrolled_table.resizeColumnsToContents()
            logger.info("Enrolled students table updated")
        except Exception as e:
            logger.error(f"Error updating enrolled students table: {str(e)}")
            raise
    
    def extract_voice_features(self, audio_data):
        """Extract simple features from audio data for comparison"""
        try:
            features = {
                'mean': np.mean(audio_data),
                'std': np.std(audio_data),
                'length': len(audio_data)
            }
            return features
        except Exception as e:
            logger.error(f"Error extracting voice features: {str(e)}")
            raise
    
    def compare_voices(self, audio_data):
        """Compare new audio with enrolled samples"""
        try:
            new_features = self.extract_voice_features(audio_data)
            
            best_match = None
            best_score = -1
            
            # Compare with all enrolled samples
            for student in self.students:
                if 'voice_features' not in student:
                    continue
                    
                # Get stored features
                features = student['voice_features']
                
                # Calculate similarity
                vec1 = np.array([features['mean'], features['std'], features['length']])
                vec2 = np.array([new_features['mean'], new_features['std'], new_features['length']])
                
                vec1 = vec1.reshape(1, -1)
                vec2 = vec2.reshape(1, -1)
                
                score = cosine_similarity(vec1, vec2)[0][0]
                
                if score > best_score:
                    best_score = score
                    best_match = student['student_id']
            
            logger.info(f"Best voice match: {best_match} with score: {best_score}")
            
            # Return match if score is above threshold
            return (best_match, best_score) if best_score > 0.7 else (None, 0)
        except Exception as e:
            logger.error(f"Error comparing voices: {str(e)}")
            return (None, 0)
    
    def record_voice_sample(self):
        """Record voice sample for new student enrollment"""
        try:
            name = self.enroll_name.text().strip()
            student_id = self.enroll_id.text().strip()
            class_id = self.enroll_class_combo.currentData()
            section = self.enroll_section_combo.currentText()
            
            if not name or not student_id or not class_id or not section:
                QMessageBox.warning(self, "Error", "Please fill all fields")
                return
                
            # Validate student ID format
            if not student_id.isalnum():
                QMessageBox.warning(self, "Error", "Student ID should be alphanumeric")
                return
                
            # Check if student ID already exists
            if self.students_col.find_one({"student_id": student_id}):
                QMessageBox.warning(self, "Error", "Student ID already exists")
                return
                
            self.enroll_status.setText("Recording... Speak now")
            self.record_enroll_btn.setEnabled(False)
            QApplication.processEvents()
            
            with self.microphone as source:
                logger.info("Starting voice recording...")
                audio = self.recognizer.listen(source, timeout=5)
                logger.info("Voice recording completed")
            
            # Save the audio file
            filename = f"{student_id}_{name.replace(' ', '_')}.wav"
            filepath = os.path.join("enrollments", filename)
            
            with open(filepath, "wb") as f:
                f.write(audio.get_wav_data())
            
            # Extract features
            audio_data, _ = sf.read(filepath)
            features = self.extract_voice_features(audio_data)
            
            # Save to MongoDB
            student_data = {
                "student_id": student_id,
                "name": name,
                "class_id": class_id,
                "section": section,
                "voice_features": features,
                "enrollment_date": datetime.datetime.now(),
                "voice_sample_path": filepath
            }
            self.students_col.insert_one(student_data)
            logger.info(f"Student {name} ({student_id}) enrolled successfully")
            
            # Refresh UI
            self.load_enrolled_students()
            self.enroll_status.setText("Enrollment successful!")
            QMessageBox.information(self, "Success", f"Student {name} enrolled successfully")
            
            # Clear form
            self.enroll_name.clear()
            self.enroll_id.clear()
            
        except sr.WaitTimeoutError:
            self.enroll_status.setText("Recording timeout")
            QMessageBox.warning(self, "Timeout", "No speech detected during recording")
            logger.warning("Voice recording timeout - no speech detected")
        except Exception as e:
            self.enroll_status.setText("Recording failed")
            QMessageBox.critical(self, "Error", f"Recording failed: {str(e)}")
            logger.error(f"Error during voice enrollment: {str(e)}")
        finally:
            self.record_enroll_btn.setEnabled(True)
    
    def start_attendance(self):
        """Start voice attendance process"""
        try:
            class_id = self.class_combo.currentData()
            section = self.section_combo.currentText()
            
            if not class_id or not section:
                QMessageBox.warning(self, "Error", "Please select class and section")
                return
                
            self.record_btn.setEnabled(False)
            self.voice_status.setText("Listening for attendance...")
            QApplication.processEvents()
            
            with self.microphone as source:
                logger.info("Starting attendance recording...")
                audio = self.recognizer.listen(source, timeout=5)
                logger.info("Attendance recording completed")
            
            # Save temporary audio file
            temp_file = "temp_attendance.wav"
            with open(temp_file, "wb") as f:
                f.write(audio.get_wav_data())
            
            # Load audio data
            audio_data, _ = sf.read(temp_file)
            
            # Compare with enrolled voices
            student_id, score = self.compare_voices(audio_data)
            
            if student_id:
                # Get student details
                student = self.students_col.find_one({"student_id": student_id})
                if student:
                    current_time = datetime.datetime.now()
                    self.mark_attendance(
                        student_id, 
                        student['name'], 
                        class_id, 
                        section, 
                        current_time, 
                        "Present (Voice)"
                    )
                    self.voice_status.setText(f"Attendance marked for {student['name']}")
                    logger.info(f"Attendance marked for {student['name']} ({student_id})")
                else:
                    self.voice_status.setText("Student not found in database")
                    logger.warning(f"Student ID {student_id} not found in database")
            else:
                self.voice_status.setText("No matching voice found")
                logger.warning("No matching voice found for attendance")
            
            # Remove temporary file
            os.remove(temp_file)
            
        except sr.WaitTimeoutError:
            self.voice_status.setText("No speech detected")
            QMessageBox.warning(self, "Timeout", "No speech detected during attendance")
            logger.warning("Attendance recording timeout - no speech detected")
        except Exception as e:
            self.voice_status.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Attendance failed: {str(e)}")
            logger.error(f"Error during voice attendance: {str(e)}")
        finally:
            self.record_btn.setEnabled(True)
    
    def mark_manual_attendance(self):
        """Mark attendance manually for selected student"""
        try:
            student_id = self.student_combo.currentData()
            if not student_id:
                return
                
            # Get student details
            student = self.students_col.find_one({"student_id": student_id})
            if not student:
                QMessageBox.warning(self, "Error", "Student not found")
                return
                
            class_id = self.class_combo.currentData()
            section = self.section_combo.currentText()
            current_time = datetime.datetime.now()
            
            self.mark_attendance(
                student_id,
                student['name'],
                class_id,
                section,
                current_time,
                "Present (Manual)"
            )
            logger.info(f"Manual attendance marked for {student['name']} ({student_id})")
        except Exception as e:
            logger.error(f"Error marking manual attendance: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to mark attendance: {str(e)}")
    
    def mark_attendance(self, student_id, name, class_id, section, time, status):
        """Mark attendance in database and update UI"""
        try:
            # Check if already marked today
            today = datetime.datetime.combine(time.date(), datetime.time.min)
            existing = self.attendance_col.find_one({
                "student_id": student_id,
                "date": {"$gte": today}
            })
            
            if existing:
                QMessageBox.information(self, "Info", f"{name} is already marked present today")
                logger.info(f"Attendance already marked today for {name} ({student_id})")
                return
                
            # Insert attendance record
            attendance_record = {
                "student_id": student_id,
                "name": name,
                "class_id": class_id,
                "section": section,
                "date": time,
                "status": status,
                "timestamp": datetime.datetime.now()
            }
            self.attendance_col.insert_one(attendance_record)
            logger.info(f"Attendance recorded for {name} ({student_id})")
            
            # Update attendance table
            self.update_attendance_table()
        except Exception as e:
            logger.error(f"Error marking attendance: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to mark attendance: {str(e)}")
    
    def update_attendance_table(self):
        """Update the attendance table with today's records"""
        try:
            today = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time.min)
            
            # Get current selections
            class_id = self.class_combo.currentData()
            section = self.section_combo.currentText()
            
            if not class_id or not section:
                self.attendance_table.setRowCount(0)
                return
            
            query = {
                "date": {"$gte": today},
                "class_id": class_id,
                "section": section
            }
            
            attendance = list(self.attendance_col.find(query).sort("date", -1))
            logger.info(f"Found {len(attendance)} attendance records for display")
            
            self.attendance_table.setRowCount(len(attendance))
            
            for row, record in enumerate(attendance):
                # Get class name
                class_name = self.class_combo.currentText()
                
                self.attendance_table.setItem(row, 0, QTableWidgetItem(record['student_id']))
                self.attendance_table.setItem(row, 1, QTableWidgetItem(record['name']))
                self.attendance_table.setItem(row, 2, QTableWidgetItem(class_name))
                self.attendance_table.setItem(row, 3, QTableWidgetItem(record['date'].strftime("%Y-%m-%d %H:%M:%S")))
                self.attendance_table.setItem(row, 4, QTableWidgetItem(record['status']))
            
            self.attendance_table.resizeColumnsToContents()
        except Exception as e:
            logger.error(f"Error updating attendance table: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to update attendance table: {str(e)}")
    
    def add_new_class(self):
        """Add a new class to the system"""
        try:
            name = self.new_class_name.text().strip()
            sections = [s.strip() for s in self.new_class_sections.text().split(",") if s.strip()]
            
            if not name:
                QMessageBox.warning(self, "Error", "Please provide class name")
                return
                
            if not sections:
                QMessageBox.warning(self, "Error", "Please provide at least one section")
                return
                
            # Check if class already exists
            if self.classes_col.find_one({"name": name}):
                QMessageBox.warning(self, "Error", "Class already exists")
                return
                
            # Insert new class
            class_data = {
                "name": name,
                "sections": sections,
                "created_at": datetime.datetime.now()
            }
            self.classes_col.insert_one(class_data)
            logger.info(f"New class added: {name} with sections: {sections}")
            
            # Refresh UI
            self.load_classes()
            self.new_class_name.clear()
            self.new_class_sections.clear()
            
            QMessageBox.information(self, "Success", "Class added successfully")
        except Exception as e:
            logger.error(f"Error adding new class: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add class: {str(e)}")
    
    def generate_report(self):
        """Generate attendance report based on filters"""
        try:
            class_id = self.report_class_combo.currentData()
            section = self.report_section_combo.currentText() if self.report_section_combo.currentText() != "All" else None
            start_date = self.report_start_date.text().strip()
            end_date = self.report_end_date.text().strip()
            
            # Build query
            query = {}
            if class_id:
                query["class_id"] = class_id
            if section:
                query["section"] = section
            
            # Date range
            try:
                if start_date:
                    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                    query["date"] = {"$gte": start}
                if end_date:
                    end = datetime.datetime.strptime(end_date, "%Y-%m-%d") + datetime.timedelta(days=1)
                    if "date" in query:
                        query["date"]["$lt"] = end
                    else:
                        query["date"] = {"$lt": end}
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid date format. Use YYYY-MM-DD")
                return
                
            # Get attendance records
            records = list(self.attendance_col.find(query).sort("date", -1))
            logger.info(f"Generated report with {len(records)} records")
            
            # Update report table
            self.report_table.setRowCount(len(records))
            
            for row, record in enumerate(records):
                # Get class name
                class_name = next((c['name'] for c in self.classes if c['_id'] == record['class_id']), "Unknown")
                
                self.report_table.setItem(row, 0, QTableWidgetItem(record['date'].strftime("%Y-%m-%d")))
                self.report_table.setItem(row, 1, QTableWidgetItem(class_name))
                self.report_table.setItem(row, 2, QTableWidgetItem(record['section']))
                self.report_table.setItem(row, 3, QTableWidgetItem(record['student_id']))
                self.report_table.setItem(row, 4, QTableWidgetItem(record['name']))
                self.report_table.setItem(row, 5, QTableWidgetItem(record['status']))
            
            self.report_table.resizeColumnsToContents()
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
    
    def export_report(self):
        """Export the current report to Excel"""
        try:
            if self.report_table.rowCount() == 0:
                QMessageBox.warning(self, "Error", "No data to export")
                return
                
            # Get filters for filename
            class_name = self.report_class_combo.currentText() or "all_classes"
            section = self.report_section_combo.currentText() or "all_sections"
            start_date = self.report_start_date.text() or "all_dates"
            end_date = self.report_end_date.text() or start_date
            
            filename = f"attendance_report_{class_name}_{section}_{start_date}_to_{end_date}.xlsx"
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Save Report", filename, "Excel Files (*.xlsx)")
            
            if filepath:
                if not filepath.endswith('.xlsx'):
                    filepath += '.xlsx'
                
                # Prepare data for export
                data = []
                for row in range(self.report_table.rowCount()):
                    row_data = []
                    for col in range(self.report_table.columnCount()):
                        item = self.report_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)
                
                # Create DataFrame
                columns = ["Date", "Class", "Section", "Student ID", "Name", "Status"]
                df = pd.DataFrame(data, columns=columns)
                
                # Export to Excel
                df.to_excel(filepath, index=False)
                logger.info(f"Report exported to {filepath}")
                QMessageBox.information(self, "Success", f"Report exported to {filepath}")
        except Exception as e:
            logger.error(f"Error exporting report: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to export report: {str(e)}")
    
    def export_to_excel(self):
        """Export current attendance view to Excel"""
        try:
            if self.attendance_table.rowCount() == 0:
                QMessageBox.warning(self, "Error", "No attendance data to export")
                return
                
            # Get class and section for filename
            class_name = self.class_combo.currentText() or "unknown_class"
            section = self.section_combo.currentText() or "unknown_section"
            filename = f"attendance_{class_name}_{section}_{datetime.datetime.now().date()}.xlsx"
            filepath, _ = QFileDialog.getSaveFileName(
                self, "Save Attendance", filename, "Excel Files (*.xlsx)")
            
            if filepath:
                if not filepath.endswith('.xlsx'):
                    filepath += '.xlsx'
                
                # Prepare data for export
                data = []
                for row in range(self.attendance_table.rowCount()):
                    row_data = []
                    for col in range(self.attendance_table.columnCount()):
                        item = self.attendance_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)
                
                # Create DataFrame
                columns = ["ID", "Name", "Class", "Time", "Status"]
                df = pd.DataFrame(data, columns=columns)
                
                # Export to Excel
                df.to_excel(filepath, index=False)
                logger.info(f"Attendance exported to {filepath}")
                QMessageBox.information(self, "Success", f"Attendance exported to {filepath}")
        except Exception as e:
            logger.error(f"Error exporting attendance: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to export attendance: {str(e)}")
    
    def clear_attendance(self):
        """Clear today's attendance for current class/section"""
        try:
            reply = QMessageBox.question(
                self, "Confirm Clear", 
                "Are you sure you want to clear today's attendance for this class/section?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                today = datetime.datetime.combine(datetime.datetime.now().date(), datetime.time.min)
                class_id = self.class_combo.currentData()
                section = self.section_combo.currentText()
                
                query = {
                    "date": {"$gte": today},
                    "class_id": class_id
                }
                
                if section:
                    query["section"] = section
                    
                # Delete records
                result = self.attendance_col.delete_many(query)
                logger.info(f"Cleared {result.deleted_count} attendance records")
                QMessageBox.information(self, "Cleared", f"Deleted {result.deleted_count} attendance records")
                
                # Refresh table
                self.update_attendance_table()
        except Exception as e:
            logger.error(f"Error clearing attendance: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to clear attendance: {str(e)}")

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        # Check if admin credentials are set
        if not os.getenv("ADMIN_USERNAME") or not os.getenv("ADMIN_PASSWORD"):
            QMessageBox.critical(None, "Configuration Error", 
                                "Please set ADMIN_USERNAME and ADMIN_PASSWORD in .env file")
            sys.exit(1)
        
        window = VoiceAttendanceSystem()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical(f"Application error: {str(e)}")
        QMessageBox.critical(None, "Application Error", f"A critical error occurred: {str(e)}")
        sys.exit(1)