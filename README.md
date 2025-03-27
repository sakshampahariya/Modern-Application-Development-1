# Modern-Application-Development-1
Quiz Management System 🎯
A Flask-based web application designed for seamless quiz management. This system enables administrators to create and manage quizzes, subjects, and track user performance, while users can attempt quizzes and monitor their scores.

🔥 Key Features
✅ User & Admin Management
Secure authentication for users and administrators

Role-based access control (Admin vs. User)

✅ Quiz & Subject Management
Admins can create, edit, and delete quizzes

Admins can manage subjects efficiently

✅ Search & Analytics
Admins can search for subjects

Performance analytics and quiz statistics for better insights

✅ User Dashboard
Users can attempt quizzes and track their scores

Quiz history and performance analytics

🏗 Tech Stack
Technology	Usage
Flask	Backend Framework
SQLite	Database
HTML/CSS	Frontend Structure
Bootstrap	UI Styling
Flask-SQLAlchemy	ORM for Database Management
Flask-Login	Authentication Handling

📂 Project Structure
bash
Copy
Edit

/quiz-management-system
│── /static             # Static files (CSS, images)
│── /templates          # HTML templates
│── app.py              # Main application logic
│── requirements.txt    # Dependencies
│── README.md           # Project documentation
│── instance/           # Database storage (SQLite)

🚀 Installation & Setup
Step 1: Clone the Repository
bash
Copy
Edit
git clone https://github.com/sakshampahariya/Modern-Application-Development-1.git
cd Modern-Application-Development-1
Step 2: Create Virtual Environment & Install Dependencies
bash
Copy
Edit
python -m venv venv  
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt  
Step 3: Run the Application
bash
Copy
Edit
python app.py  
Step 4: Open in Browser
cpp
Copy
Edit
http://127.0.0.1:5000  
🛠 Future Enhancements
🔹 Leaderboard for top quiz scorers

🔹 Advanced question types (MCQs, True/False, Fill in the Blanks)

🔹 User profile section with quiz history

🤝 Contributing
Contributions are welcome! Follow these steps to contribute:

Fork the repository

Create a feature branch (git checkout -b feature-name)

Commit changes (git commit -m "Feature added")

Push to the branch (git push origin feature-name)

Submit a Pull Request

📜 License
This project is licensed under the MIT License.

🌟 Show Your Support!
If you find this project useful, ⭐ Star this repository on GitHub!
