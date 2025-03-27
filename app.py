from flask import Flask, flash, render_template, request, url_for,redirect
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from collections import defaultdict
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash , check_password_hash
from sqlalchemy.sql import func
plt.switch_backend('Agg')

app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizmine.db'
app.config['SECRET_KEY'] = '28d5972b820e8fe04b048c698fee0e7a'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    qualification = db.Column(db.String(120))
    dob = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False)
    quiz_scores = db.relationship('Score', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    chapters = db.relationship('Chapter', backref='subject', cascade="all, delete",lazy=True)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    quizzes = db.relationship('Quiz', backref='chapter',cascade="all, delete", lazy=True)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz = db.Column(db.DateTime, nullable=False)
    time_duration = db.Column(db.Integer)  # Duration in minutes
    remarks = db.Column(db.Text)
    questions = db.relationship('Question', backref='quiz',cascade="all, delete", lazy=True)
    scores = db.relationship('Score', backref='quiz',cascade="all, delete", lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)  # 1-4 representing the correct option

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    total_scored = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_admin():
    with app.app_context():
        admin = User.query.filter_by(email='admin@quizmaster.com').first()
        if not admin:
            admin = User(
                email='admin@quizmaster.com',
                full_name='Quizer Admin',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admindash'))
            else:
                return redirect(url_for('user_dash'))
        else:
            flash('Invalid Username or Password')
            return redirect(url_for('landing'))
    return render_template('login.html')

@app.route('/admindash')
@login_required
def admindash():
    if not current_user.is_admin:
        return redirect(url_for('landing'))
    subjects = Subject.query.all()
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admindash.html',subjects=subjects,users=users)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = User(
            email=request.form['email'],
            full_name=request.form['name'],
            qualification=request.form['Qualification'],
            dob=datetime.strptime(request.form['dob'], '%Y-%m-%d')
        )
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/admindash/subject/new', methods=['GET', 'POST'])
@login_required
def new_subject():
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('landing'))
    if request.method == 'POST':
        subject = Subject(
            name=request.form['name'],
            description=request.form['description']
        )
        db.session.add(subject)
        db.session.commit()
        flash('Subject created successfully!')
        return redirect(url_for('admindash'))
    return render_template('new_subject.html')

@app.route('/admindash/chapter/new/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def new_chapter(subject_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('landing'))

    subject = Subject.query.get(subject_id)  # Fetch subject from DB
    if not subject:
        return "Subject not found", 404  # Handle invalid subject_id

    if request.method == 'POST':
        chapter = Chapter(
            name=request.form['name'],
            description=request.form['description'],
            subject_id=subject_id
        )
        db.session.add(chapter)
        db.session.commit()  # Save changes to DB
        flash("Chapter created successfully!", "success")
        return redirect(url_for('admindash'))  # Redirect to subject page
    return render_template('new_chapter.html', subject=subject)

@app.route('/admindash/quiz/new', methods=['GET', 'POST'])
@login_required
def new_quiz():
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('landing'))
    chapters = Chapter.query.all()
    if request.method == 'POST':
        chapter_id = request.form['chapter_id']
        date_of_quiz = datetime.strptime(request.form['date_of_quiz'], '%Y-%m-%d')
        time_duration = int(request.form['time_duration'])
        remarks = request.form['remarks']

        quiz = Quiz(
            chapter_id=chapter_id,
            date_of_quiz=date_of_quiz,
            time_duration=time_duration,
            remarks=remarks
        )

        db.session.add(quiz)
        db.session.commit()

        # Save questions
        question_statements = request.form.getlist('question_statement[]')
        options1 = request.form.getlist('option1[]')
        options2 = request.form.getlist('option2[]')
        options3 = request.form.getlist('option3[]')
        options4 = request.form.getlist('option4[]')
        correct_options = request.form.getlist('correct_option[]')

        for i in range(len(question_statements)):
            question = Question(
                quiz_id=quiz.id,
                question_statement=question_statements[i],
                option1=options1[i],
                option2=options2[i],
                option3=options3[i],
                option4=options4[i],
                correct_option=int(correct_options[i])
            )
            db.session.add(question)

        db.session.commit()

        flash("Quiz created successfully!", "success")
        return redirect(url_for('admindash'))

    return render_template('new_quiz.html', chapters=chapters)

@app.route('/delete_subject/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('admindash'))
    
    subject = Subject.query.get(subject_id)
    if subject:
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully!', 'success')

    return redirect(url_for('admindash'))

@app.route('/update_subject/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def update_subject(subject_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('admindash'))
    subject = Subject.query.get(subject_id)

    if not subject:
        flash("Subject not found!", "danger")
        return redirect(url_for('admindash'))

    if request.method == 'POST':
        subject.name = request.form['subject_name']
        subject.description = request.form['subject_desc']
        db.session.commit()
        flash("Subject updated successfully!", "success")
        return redirect(url_for('admindash'))

    return render_template('update_subject.html', subject=subject)


@app.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
@login_required
def delete_chapter(chapter_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('landing'))
    
    chapter = Chapter.query.get(chapter_id)
    if chapter:
        db.session.delete(chapter)
        db.session.commit()
        flash('Chapter deleted successfully!', 'success')

    return redirect(url_for('admindash'))

@app.route('/admindash/chapter/edit/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
def edit_chapter(chapter_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('landing'))
    chapter = Chapter.query.get_or_404(chapter_id)  # Fetch chapter details

    if request.method == 'POST':
        chapter.name = request.form['name']
        chapter.description = request.form['description']
        db.session.commit()  # Save changes in DB

        flash("Chapter updated successfully!", "success")
        return redirect(url_for('admindash'))  # Redirect back to admin dashboard

    return render_template('edit_chapter.html', chapter=chapter)

@app.route('/admindash/quiz/delete/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('landing'))

    quiz = Quiz.query.get_or_404(quiz_id) 
    # Delete all related questions and scores
    Question.query.filter_by(quiz_id=quiz.id).delete()
    Score.query.filter_by(quiz_id=quiz.id).delete()
    
    db.session.delete(quiz)
    db.session.commit()

    flash("Quiz and all related data deleted successfully!", "danger")
    return redirect(url_for('admindash'))

@app.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def edit_quiz(quiz_id):
    if not current_user.is_admin:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('landing'))
    quiz = Quiz.query.get_or_404(quiz_id)
    chapters = Chapter.query.all()  # Fetch all chapters

    if request.method == 'POST':
        # Update quiz details
        quiz.chapter_id = request.form['chapter_id']
        quiz.date_of_quiz = datetime.strptime(request.form['date_of_quiz'], '%Y-%m-%d')
        quiz.time_duration = int(request.form['time_duration'])
        quiz.remarks = request.form['remarks']

        # Clear existing questions before adding new ones
        Question.query.filter_by(quiz_id=quiz.id).delete()

        # Add updated questions
        question_statements = request.form.getlist('question_statement[]')
        option1_list = request.form.getlist('option1[]')
        option2_list = request.form.getlist('option2[]')
        option3_list = request.form.getlist('option3[]')
        option4_list = request.form.getlist('option4[]')
        correct_options = request.form.getlist('correct_option[]')

        for i in range(len(question_statements)):
            new_question = Question(
                quiz_id=quiz.id,
                question_statement=question_statements[i],
                option1=option1_list[i],
                option2=option2_list[i],
                option3=option3_list[i],
                option4=option4_list[i],
                correct_option=int(correct_options[i])
            )
            db.session.add(new_question)

        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('admindash'))  # Redirect to dashboard

    return render_template('edit_quiz.html', quiz=quiz, chapters=chapters)

@app.route('/user')
@login_required
def user_dash():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
    subjects = Subject.query.all()
    user_scores = Score.query.filter_by(user_id=current_user.id).all()
    recent_scores = (
        Score.query.filter_by(user_id=current_user.id)
        .join(Quiz)  # Join to access Quiz details
        .join(Chapter)  # Join to access Chapter details
        .join(Subject) 
        .order_by(Score.timestamp.desc())  # Order by latest first
        .limit(5)
        .all()
    )
    return render_template('user_dash.html', subjects=subjects, user_scores=user_scores, recent_scores=recent_scores)

@app.route('/view_quiz/<int:quiz_id>')
@login_required
def view_quiz(quiz_id):
    quiz=Quiz.query.filter_by(id=quiz_id).first()
    return render_template('view_quiz.html',quiz=quiz)

@app.route("/quiz/<int:quiz_id>", methods=["GET"])
@login_required
def take_quiz(quiz_id):
    """Route to display and start a quiz"""
    quiz = Quiz.query.get_or_404(quiz_id)  # Fetch the quiz from DB
    return render_template("runquiz.html", quiz=quiz)

@app.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    score = 0
    for question in quiz.questions:
        answer = request.form.get(f'q{question.id}', '').strip()
        if answer.isdigit() and int(answer) == question.correct_option:
            score += 1
    
    quiz_score = Score(
        quiz_id=quiz_id,
        user_id=current_user.id,
        total_scored=score,
        total_questions=len(quiz.questions)
    )
    db.session.add(quiz_score)
    db.session.commit()
    
    flash(f'Quiz submitted! Your score: {score}/{len(quiz.questions)}', 'success')
    return redirect(url_for('user_dash'))

@app.route('/quiz-scores')
@login_required  
def view_scores():
    subjects = Subject.query.all()
    user_id = current_user.id 
    # Fetch all scores for each quiz that the user attempted
    user_scores = {}
    scores = Score.query.filter_by(user_id=user_id).all()

    for score in scores:
        if score.quiz_id not in user_scores:
            user_scores[score.quiz_id] = []
        user_scores[score.quiz_id].append(score.total_scored)

    return render_template('view_scores.html', subjects=subjects, user_scores=user_scores)


@app.route('/quiz_stats')
@login_required
def quiz_stats():
    """Generate quiz statistics charts."""

    # Get all scores
    user_scores = Score.query.filter_by(user_id=current_user.id).all()

    # Dictionaries to store counts
    subject_count = defaultdict(int)
    month_count = defaultdict(int)

    for score in user_scores:
        # Fetch subject via quiz → chapter → subject
        subject_name = score.quiz.chapter.subject.name
        subject_count[subject_name] += 1

        # Extract month from timestamp
        month = score.timestamp.strftime('%Y-%m')  # Format: YYYY-MM
        month_count[month] += 1

    # Convert data for plotting
    subjects = list(subject_count.keys())
    subject_values = list(subject_count.values())

    months = sorted(month_count.keys())  # Sort by date
    month_labels = [datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in months]  # Convert to readable format
    month_values = [month_count[m] for m in months]

    # File paths for saving images
    subject_chart_path = os.path.join("static/charts", "subject_chart.png")
    month_chart_path = os.path.join("static/charts", "month_chart.png")

    # **Bar Chart (Subjects)**
    plt.figure(figsize=(6, 4))
    plt.bar(subjects, subject_values, color="blue")
    plt.xlabel("Subjects")
    plt.ylabel("Quizzes Attempted")
    plt.title("Quiz Attempts by Subject")
    plt.xticks(rotation=30)
    plt.savefig(subject_chart_path)
    plt.close()

    # **Pie Chart (Months)**
    plt.figure(figsize=(4, 4))
    plt.pie(month_values, labels=month_labels, autopct="%1.1f%%", colors=["red", "blue", "green", "orange"])
    plt.title("Quiz Attempts by Month")
    plt.savefig(month_chart_path)
    plt.close()

    return render_template("quiz_stats.html", 
                           subject_chart=subject_chart_path, 
                           month_chart=month_chart_path)


# Use non-interactive backend to avoid Tkinter errors and using different

@app.route('/admin/quiz_stats')
@login_required
def admin_quiz_stats():
    subjects = Subject.query.all()
    # Data Storage
    top_scores = {}
    user_attempts = {}
    for subject in subjects:
        # Max score for subject
        highest_score = db.session.query(func.max(Score.total_scored)) \
            .join(Quiz).join(Chapter) \
            .filter(Chapter.subject_id == subject.id).scalar() or 0

        # Total attempts for subject
        total_attempts = db.session.query(func.count(Score.id)) \
            .join(Quiz).join(Chapter) \
            .filter(Chapter.subject_id == subject.id).scalar() or 0

        top_scores[subject.name] = highest_score
        user_attempts[subject.name] = total_attempts

    # Generate and save charts
    top_score_chart = generate_bar_chart(top_scores, "Top Scores by Subject", "top_scores.png")
    attempts_chart = generate_pie_chart(user_attempts, "Quiz Attempts by Subject", "quiz_attempts_pie.png")

    return render_template('admin_quiz_stats.html', 
                           top_score_chart=top_score_chart, 
                           attempts_chart=attempts_chart)

# Function to generate bar chart for top scores
def generate_bar_chart(data, title, filename):
    if not data:
        return None  # No data to plot
    subjects = list(data.keys())
    values = list(data.values())

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(subjects, values, color=['#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8'])
    ax.set_title(title)
    ax.set_ylabel('Score')
    ax.set_xlabel('Subjects')
    plt.xticks(rotation=45, ha="right")
    # Save Image
    img_path = os.path.join("static", filename)
    plt.savefig(img_path, bbox_inches="tight")
    plt.close()
    return url_for('static', filename=filename)

# Function to generate pie chart for quiz attempts
def generate_pie_chart(data, title, filename):
    if not data or sum(data.values()) == 0:
        return None  # No data to plot
    subjects = list(data.keys())
    values = list(data.values())
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(values, labels=subjects, autopct='%1.1f%%', colors=['#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8'],
           startangle=90, wedgeprops={'edgecolor': 'black'})
    ax.set_title(title)

    # Save Image
    img_path = os.path.join("static", filename)
    plt.savefig(img_path, bbox_inches="tight")
    plt.close()
    return url_for('static', filename=filename)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

if __name__=='__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True)