
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template
import os

app = Flask(__name__,
            static_folder='static',  # Папка для статических файлов
            template_folder='templates')  # Папка для шаблонов

@app.route('/')
def home():
    return render_template('index.html')  # Загружаем главную страницу

if __name__ == "__main__":
    app.run(debug=True)

# Настройка Flask и базы данных
app = Flask(__name__)

# Секретный ключ для работы с сессиями
app.secret_key = 'zXPl2PQh1TXDX7fdBKq4ueke'

# Настройка URI для подключения к базе данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite база данных
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключение уведомлений о модификациях

# Инициализация SQLAlchemy
db = SQLAlchemy(app)

# Модель пользователя
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Создание таблиц в базе данных (если они еще не существуют)
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))  # Перенаправление на панель пользователя
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Проверяем, существует ли пользователь с таким email в базе данных
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user'] = email  # Сохраняем email пользователя в сессии
            return redirect(url_for('dashboard'))  # Перенаправление на панель пользователя
        else:
            return 'Неверный email или пароль'
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return f"Добро пожаловать, {session['user']}!"  # Панель пользователя
    return redirect(url_for('login'))  # Если пользователь не авторизован, перенаправляем на страницу входа

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')

        # Проверяем, существует ли пользователь с таким email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return 'Пользователь с таким email уже существует!'

        # Создаем нового пользователя и сохраняем его в базе данных
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))  # После регистрации перенаправляем на страницу входа
    return render_template('register.html')

if __name__ == "__main__":
    app.run(debug=True)
