from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import pickle
import numpy as np
import pymssql

# ======== Flask App setup ========
app = Flask(__name__)
app.secret_key = 'supersecretkey_123456'  

# ======== Login Manager setup ========
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ======== Kết nối SQL Server ========
conn = pymssql.connect(server='localhost', user='sa', password='123456',
                       database='InsurancePredictor', as_dict=True)
cursor = conn.cursor()

# ======== Load model ========
model = pickle.load(open('model/model.pkl', 'rb'))

# ======== User class ========
class User(UserMixin):
    def __init__(self, id, full_name, email, role):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.role = role

# ======== User loader cho Flask-Login ========
@login_manager.user_loader
def load_user(user_id):
    cursor.execute("SELECT * FROM Users WHERE UserID = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(user['UserID'], user['FullName'], user['Email'], user['Role'])
    return None

# ======== Routes ========

@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/history')
@login_required
def history():
    cursor.execute("SELECT Age, Gender, BMI, Smoke, Region, PredictedCost, CreatedAt FROM Predictions WHERE UserID = %s ORDER BY CreatedAt DESC", (current_user.id,))
    history_list = cursor.fetchall()
    return render_template('history.html', history=history_list)

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    if request.method == 'POST':
        age = int(request.form['age'])
        gender = 1 if request.form['gender'] == 'Nam' else 0
        bmi = float(request.form['bmi'])
        smoke = 1 if request.form['smoke'] == 'Có' else 0
        region = {'Bắc': 0, 'Trung': 1, 'Nam': 2}[request.form['region']]

        input_data = np.array([[age, gender, bmi, smoke, region]])
        predicted_cost = float(model.predict(input_data)[0])

        # Lưu dự đoán vào DB
        cursor.execute("""
            INSERT INTO Predictions (UserID, Age, Gender, BMI, Smoke, Region, PredictedCost)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (current_user.id, age, gender, bmi, smoke, region, predicted_cost))
        conn.commit()

        return render_template('predict.html', prediction=round(predicted_cost, 2))

    return render_template('predict.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor.execute("SELECT * FROM Users WHERE Email = %s AND PasswordHash = %s", (email, password))
        user = cursor.fetchone()

        if user:
            user_obj = User(user['UserID'], user['FullName'], user['Email'], user['Role'])
            login_user(user_obj)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Sai email hoặc mật khẩu')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']

        try:
            cursor.execute(
                "INSERT INTO Users (FullName, Email, PasswordHash, Role) VALUES (%s, %s, %s, %s)",
                (full_name, email, password, 'user')
            )
            conn.commit()
            return redirect(url_for('login'))
        except:
            return render_template('register.html', error='Email đã tồn tại')

    return render_template('register.html')

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form['email']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            return render_template("forgot_password.html", error="Mật khẩu không khớp")

        cursor.execute("SELECT * FROM Users WHERE Email = %s", (email,))
        user = cursor.fetchone()

        if user:
            cursor.execute("UPDATE Users SET PasswordHash = %s WHERE Email = %s", (new_password, email))
            conn.commit()
            return render_template("forgot_password.html", success="Đổi mật khẩu thành công.")
        else:
            return render_template("forgot_password.html", error="Không tìm thấy email.")

    return render_template("forgot_password.html")

@app.route('/admin')
@login_required
def admin_home():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    return render_template('admin/admin_home.html', admin=current_user)

@app.route('/admin/users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()
    return render_template('admin/manage_users.html', users=users)

@app.route('/admin/predictions')
@login_required
def manage_predictions():
    if current_user.role != 'admin':
        return redirect(url_for('index'))

    cursor.execute("""
        SELECT p.*, u.FullName FROM Predictions p
        JOIN Users u ON p.UserID = u.UserID
    """)
    predictions = cursor.fetchall()
    return render_template('admin/manage_predictions.html', predictions=predictions)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('login'))

    cursor.execute("DELETE FROM Users WHERE UserID = %s", (user_id,))
    conn.commit()
    return redirect(url_for('manage_users'))

@app.route('/admin/delete_prediction/<int:prediction_id>', methods=['POST'])
@login_required
def delete_prediction(prediction_id):
    if current_user.role != 'admin':
        return redirect(url_for('login'))

    cursor.execute("DELETE FROM Predictions WHERE PredictionID = %s", (prediction_id,))
    conn.commit()
    return redirect(url_for('manage_predictions'))

# ======== Chạy ứng dụng ========
if __name__ == '__main__':
    app.run(debug=True)
