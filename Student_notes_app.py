# =========================
# Flask Student Notes App
# =========================
# Features:
# - SQLite database
# - Course units
# - Add text notes
# - Upload files (with working download)
# - View notes grouped by course
# - Coursework reminders with deadlines

# --------- app.py ---------
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///notes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# --------- MODELS ---------
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    file_path = db.Column(db.String(200))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

class Coursework(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    deadline = db.Column(db.String(50))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

# --------- ROUTES ---------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/add', methods=['GET', 'POST'])
def add():
    courses = Course.query.all()

    if request.method == 'POST':
        if 'course_name' in request.form:
            new_course = Course(name=request.form['course_name'])
            db.session.add(new_course)
            db.session.commit()

        elif 'note_content' in request.form:
            note = Note(
                content=request.form['note_content'],
                course_id=request.form['course_id']
            )
            db.session.add(note)
            db.session.commit()

        elif 'file' in request.files:
            file = request.files['file']
            if file.filename:
                filename = file.filename
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)

                note = Note(file_path=filename, course_id=request.form['course_id'])
                db.session.add(note)
                db.session.commit()

        return redirect(url_for('add'))

    return render_template('add.html', courses=courses)

@app.route('/view', methods=['GET', 'POST'])
def view():
    courses = Course.query.all()
    notes = Note.query.all()
    coursework = Coursework.query.all()

    if request.method == 'POST':
        cw = Coursework(
            title=request.form['title'],
            deadline=request.form['deadline'],
            course_id=request.form['course_id']
        )
        db.session.add(cw)
        db.session.commit()
        return redirect(url_for('view'))

    return render_template('view.html', courses=courses, notes=notes, coursework=coursework)

# --------- INIT DB ---------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)


# --------- templates/base.html ---------
"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Notes App</title>

    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
</head>
<body class="bg-gradient-to-br from-gray-100 to-gray-200 min-h-screen">

<div class="container mx-auto p-6">
    <div class="bg-white rounded-xl shadow-lg p-6 mb-6">
        <h1 class="text-3xl font-bold text-gray-800">
            <i class="fas fa-book mr-2 text-indigo-500"></i> Student Notes App
        </h1>
        <nav class="mt-4 space-x-4">
            <a href="/" class="text-indigo-600 hover:underline">Home</a>
            <a href="/add" class="text-indigo-600 hover:underline">Add Notes</a>
            <a href="/view" class="text-indigo-600 hover:underline">View Notes</a>
        </nav>
    </div>

    {% block content %}{% endblock %}
</div>

</body>
</html>
"""

# --------- templates/home.html ---------
"""
{% extends 'base.html' %}
{% block content %}
<div class="bg-white p-6 rounded-xl shadow-md">
    <h2 class="text-2xl font-bold text-gray-700 mb-3">
        <i class="fas fa-tachometer-alt mr-2 text-indigo-500"></i> Dashboard
    </h2>
    <p class="text-gray-600">Manage your courses, notes, and coursework efficiently.</p>
</div>
{% endblock %}
"""

# --------- templates/add.html ---------
"""
{% extends 'base.html' %}
{% block content %}

<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

    <!-- Add Course -->
    <div class="bg-white p-6 rounded-xl shadow-md">
        <h2 class="text-xl font-bold mb-4 text-gray-700">
            <i class="fas fa-plus-circle mr-2 text-green-500"></i> Add Course Unit
        </h2>
        <form method="POST" class="space-y-3">
            <input type="text" name="course_name" placeholder="Course name" class="w-full p-2 border rounded">
            <button class="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700">Add</button>
        </form>
    </div>

    <!-- Courses -->
    <div class="bg-white p-6 rounded-xl shadow-md">
        <h2 class="text-xl font-bold mb-4 text-gray-700">
            <i class="fas fa-book-open mr-2 text-indigo-500"></i> Courses
        </h2>

        {% for course in courses %}
        <div class="mb-4 p-4 border rounded-lg hover:shadow-md transition">
            <h3 class="font-semibold text-lg text-gray-800">{{ course.name }}</h3>

            <!-- Add Note -->
            <form method="POST" class="mt-2 space-y-2">
                <input type="hidden" name="course_id" value="{{ course.id }}">
                <textarea name="note_content" placeholder="Write notes" class="w-full p-2 border rounded"></textarea>
                <button class="bg-blue-500 text-white px-3 py-1 rounded">Add Note</button>
            </form>

            <!-- Upload -->
            <form method="POST" enctype="multipart/form-data" class="mt-2">
                <input type="hidden" name="course_id" value="{{ course.id }}">
                <input type="file" name="file" class="mb-2">
                <button class="bg-green-500 text-white px-3 py-1 rounded">Upload</button>
            </form>
        </div>
        {% endfor %}

    </div>

</div>

{% endblock %}
"""

# --------- templates/view.html ---------
"""
{% extends 'base.html' %}
{% block content %}

<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

    <!-- Notes Section -->
    <div class="bg-white p-6 rounded-xl shadow-md">
        <h2 class="text-xl font-bold mb-4 text-gray-700">
            <i class="fas fa-book mr-2 text-indigo-500"></i> Notes by Course
        </h2>

        {% for course in courses %}
        <div class="mb-4">
            <h3 class="font-semibold text-lg text-gray-800">{{ course.name }}</h3>
            <ul class="ml-4 list-disc">
                {% for note in notes %}
                    {% if note.course_id == course.id %}
                    <li class="mb-1">
                        {{ note.content }}
                        {% if note.file_path %}
                        - <a class="text-blue-500 underline" href="{{ url_for('uploaded_file', filename=note.file_path) }}">Download</a>
                        {% endif %}
                    </li>
                    {% endif %}
                {% endfor %}
            </ul>
        </div>
        {% endfor %}
    </div>

    <!-- Coursework Section -->
    <div class="bg-white p-6 rounded-xl shadow-md">
        <h2 class="text-xl font-bold mb-4 text-gray-700">
            <i class="fas fa-tasks mr-2 text-green-500"></i> Coursework
        </h2>

        <form method="POST" class="space-y-3 mb-4">
            <input type="text" name="title" placeholder="Coursework" class="w-full p-2 border rounded">
            <input type="date" name="deadline" class="w-full p-2 border rounded">
            <select name="course_id" class="w-full p-2 border rounded">
                {% for course in courses %}
                <option value="{{ course.id }}">{{ course.name }}</option>
                {% endfor %}
            </select>
            <button class="bg-indigo-600 text-white px-4 py-2 rounded">Add Reminder</button>
        </form>

        <ul>
        {% for cw in coursework %}
            <li class="mb-2 p-2 border rounded flex justify-between">
                <span>{{ cw.title }}</span>
                <span class="text-sm text-gray-500">Due: {{ cw.deadline }}</span>
            </li>
        {% endfor %}
        </ul>

    </div>

</div>

{% endblock %}
"""

# =========================
# - Add delete/edit functionality
# - Add authentication (login system)
# - Use Bootstrap for better UI
# - Add notifications for deadlines
