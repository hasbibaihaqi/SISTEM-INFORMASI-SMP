import json
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
app = Flask(__name__)

app = Flask(__name__)
app.secret_key = 'hondajazz09'  # ganti dengan sesuatu yang acak dan aman


# --- Flask-Login setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Halaman yang akan dituju jika belum login

# Dummy user storage (for demonstration, replace with a database in production)
# We'll use a simple JSON file for persistence
USERS_FILE = 'users.json'

# --- User Model ---
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def get(user_id):
        users = load_users()
        for user_data in users:
            if user_data['id'] == user_id:
                return User(user_data['id'], user_data['username'], user_data['password_hash'])
        return None

    @staticmethod
    def find_by_username(username):
        users = load_users()
        for user_data in users:
            if user_data['username'] == username:
                return User(user_data['id'], user_data['username'], user_data['password_hash'])
        return None

def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# --- Forms ---
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Konfirmasi Password', validators=[DataRequired()])
    submit = SubmitField('Daftar Akun')

    def validate_username(self, username):
        user = User.find_by_username(username.data)
        if user:
            raise ValidationError('Username sudah ada. Pilih username lain.')

    def validate_email(self, email):
        users = load_users()
        for user_data in users:
            if user_data.get('email') == email.data:
                raise ValidationError('Email sudah terdaftar. Gunakan email lain.')

# --- Data dummy untuk aplikasi (tetap sama) ---
students_data = [
    {'nis': '001', 'nama': 'Ayu Lestari', 'kelas': '7A', 'alamat': 'Jl. Kenanga No. 10', 'telepon': '081234567890', 'email': 'ayu.l@smp.sch.id'},
    {'nis': '002', 'nama': 'Bima Satria', 'kelas': '7B', 'alamat': 'Jl. Mawar No. 5', 'telepon': '081345678901', 'email': 'bima.s@smp.sch.id'},
    {'nis': '003', 'nama': 'Citra Dewi', 'kelas': '8A', 'alamat': 'Jl. Melati No. 22', 'telepon': '081456789012', 'email': 'citra.d@smp.sch.id'},
    {'nis': '004', 'nama': 'Doni Pratama', 'kelas': '9C', 'alamat': 'Jl. Anggrek No. 15', 'telepon': '081567890123', 'email': 'doni.p@smp.sch.id'}
]

teachers_data = [
    {'nip': 'G001', 'nama': 'Bapak Andi Permana', 'jabatan': 'Kepala Sekolah', 'mengajar': 'Matematika', 'telepon': '087654321098', 'email': 'andi.p@smp.sch.id'},
    {'nip': 'G002', 'nama': 'Ibu Ani Setiawati', 'jabatan': 'Guru', 'mengajar': 'Bahasa Indonesia', 'telepon': '087765432109', 'email': 'ani.s@smp.sch.id'},
    {'nip': 'G003', 'nama': 'Bapak Rio Pratama', 'jabatan': 'Guru', 'mengajar': 'Ilmu Pengetahuan Alam', 'telepon': '087876543210', 'email': 'rio.p@smp.sch.id'}
]

subjects_data = [
    {'kode': 'MTK', 'nama': 'Matematika', 'deskripsi': 'Studi tentang angka, kuantitas, ruang, dan struktur.'},
    {'kode': 'BIN', 'nama': 'Bahasa Indonesia', 'deskripsi': 'Studi tentang tata bahasa, sastra, dan kemampuan berbahasa Indonesia.'},
    {'kode': 'IPA', 'nama': 'Ilmu Pengetahuan Alam', 'deskripsi': 'Studi tentang fenomena alam, fisika, kimia, dan biologi dasar.'},
    {'kode': 'IPS', 'nama': 'Ilmu Pengetahuan Sosial', 'deskripsi': 'Studi tentang masyarakat, sejarah, geografi, dan ekonomi.'},
    {'kode': 'BIG', 'nama': 'Bahasa Inggris', 'deskripsi': 'Studi tentang bahasa Inggris, meliputi percakapan, tata bahasa, dan membaca.'}
]

schedule_data = {
    'Senin': [
        {'jam': '07:30 - 08:15', 'pelajaran': 'Matematika', 'kelas': '7A'},
        {'jam': '08:15 - 09:00', 'pelajaran': 'Bahasa Indonesia', 'kelas': '7A'}
    ],
    'Selasa': [
        {'jam': '07:30 - 08:15', 'pelajaran': 'IPA', 'kelas': '7A'},
        {'jam': '08:15 - 09:00', 'pelajaran': 'Bahasa Inggris', 'kelas': '7A'}
    ]
}

# --- Routes ---

@app.route('/')
@login_required # Hanya bisa diakses setelah login
def index():
    """Halaman utama portal sekolah."""
    return render_template('index.html',
                           total_students=len(students_data),
                           total_teachers=len(teachers_data),
                           total_subjects=len(subjects_data))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.find_by_username(username)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login berhasil!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Login gagal. Periksa username dan password Anda.', 'error')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        users = load_users()
        new_id = str(len(users) + 1) # Simple ID generation
        new_user = {
            'id': new_id,
            'username': username,
            'email': email,
            'password_hash': hashed_password
        }
        users.append(new_user)
        save_users(users)

        flash('Akun berhasil dibuat! Silakan login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))


# --- Protected routes (require login) ---
@app.route('/students')
@login_required
def students():
    """Menampilkan daftar semua siswa."""
    return render_template('students.html', students=students_data)

@app.route('/student/<string:nis>')
@login_required
def student_detail(nis):
    """Menampilkan detail profil siswa berdasarkan NIS."""
    student = next((s for s in students_data if s['nis'] == nis), None)
    if student:
        return render_template('student_detail.html', student=student)
    flash(f'Siswa dengan NIS {nis} tidak ditemukan.', 'error')
    return redirect(url_for('students'))

@app.route('/teachers')
@login_required
def teachers():
    """Menampilkan daftar semua guru."""
    return render_template('teachers.html', teachers=teachers_data)

@app.route('/teacher/<string:nip>')
@login_required
def teacher_detail(nip):
    """Menampilkan detail profil guru berdasarkan NIP."""
    teacher = next((t for t in teachers_data if t['nip'] == nip), None)
    if teacher:
        return render_template('teacher_detail.html', teacher=teacher)
    flash(f'Guru dengan NIP {nip} tidak ditemukan.', 'error')
    return redirect(url_for('teachers'))

@app.route('/subjects')
@login_required
def subjects():
    """Menampilkan daftar semua mata pelajaran."""
    return render_template('subjects.html', subjects=subjects_data)

@app.route('/schedule')
@login_required
def schedule():
    """Menampilkan jadwal pelajaran."""
    return render_template('schedule.html', schedule=schedule_data)

if __name__ == '__main__':
    app.run(debug=True)