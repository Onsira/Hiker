from flask_app import app
from flask import render_template, redirect, request, flash, session
from flask_app.models.user import User
from flask_app.models.location import Location
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('index.html')

@app.route("/users/register", methods=["POST"])
def register():
    if not User.validate_data(request.form):
        return redirect('/')
    hashed_pass = bcrypt.generate_password_hash(request.form['password'])
    data = {
        **request.form,
        'password' : hashed_pass,
        'confirm_password' : hashed_pass
    }
    logged_user_id = User.create(data)
    session['user_id'] = logged_user_id
    return redirect('/dashboard')

@app.route('/users/login', methods=['POST'])
def login_user():
    data = {
        'email' : request.form ['email']
    }
    potential_user = User.get_by_email(data)
    if not potential_user:
        flash ('Invalid credentials', 'login')
        return redirect ('/')
    if not bcrypt.check_password_hash(potential_user.password, request.form['password']):
        flash ('Invalid credentials', 'login')
        return redirect ('/')
    session['user_id'] = potential_user.id
    return redirect ('/dashboard')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id' : session['user_id']
    }
    logged_user = User.get_by_id(data)
    all_locations = Location.get_all_locations()
    return render_template('dashboard.html', logged_user = logged_user, all_locations=all_locations, request=request)

# View current user info
@app.route('/users/view/<int:id>')
def view_user(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id' : session['user_id']
    }
    logged_user = User.get_by_id(data)
    one_user = User.get_by_id(data)
    return render_template('user_info.html', one_user=one_user, logged_user= logged_user)

# action route to update user
@app.route('/users/update/<int:id>', methods=['POST'])
def update_user(id):
    if 'user_id' not in session:
        return redirect('/')
    if not User.validate_data(request.form):
        return redirect(f'/users/view/{id}')
    update_data = {
        **request.form,
        'id' : id
    }
    User.update_user(update_data)
    return redirect ('/dashboard')

@app.route('/users/logout')
def logout():
    session.clear()
    return redirect('/')
