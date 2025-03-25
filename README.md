# 🎤 Voice Attendance System

A **Python-based** attendance system using **voice recognition** with **PyQt5 GUI** and **MongoDB** database.

![Demo](demo.gif) *(Optional: Add a demo GIF later)*

## **Features**
✔ Voice-based attendance marking  
✔ Student enrollment with voice samples  
✔ Manual attendance option  
✔ MongoDB database storage  
✔ Excel report generation  
✔ Secure admin login  

## **Technologies Used**
- Python
- PyQt5 (GUI)
- MongoDB (Database)
- SpeechRecognition + PyAudio (Voice Processing)
- scikit-learn (Voice Matching)
- pandas (Excel Export)

## **Setup Instructions**

### **1. Prerequisites**
- Python 3.7+
- MongoDB (Local or Cloud)
- Git (for cloning)

### **2. Installation**

1. **Clone the repo:**
   ```sh
   git clone https://github.com/your-username/voice-attendance-system.git
   cd voice-attendance-system
   ```

2. **Create & activate a virtual environment:**
   ```sh
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up MongoDB:**
   - Install MongoDB Community Server
   - Update .env with your MONGO_URI:
     ```env
     MONGO_URI=mongodb://localhost:27017/
     ADMIN_USERNAME=admin
     ADMIN_PASSWORD=admin123
     ```

5. **Run the application:**
   ```sh
   python main.py
   ```

## **Contributing**
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## **License**
Distributed under the MIT License. See `LICENSE` for more information.

## **Contact**
Ankit Sharma - [@your-twitter-handle](https://twitter.com/your-twitter-handle) - ankitsharma7805@gmail.com

Project Link: [https://github.com/ankitsharma38/voice-attendance-system](https://github.com/ankitsharma38/voice-attendance-system)
