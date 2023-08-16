from flask_app import app
from flask import render_template, redirect, request, flash, session
from flask_app.models.user import User
from flask_app.models.location import Location
from flask_app.models.comment import Comment

# route for form to create new location
@app.route('/locations/create', methods = ['POST'])
def create_location():
    if 'user_id' not in session:
        return redirect('/')
    if not Location.validate_data(request.form):
        return redirect('/dashboard')
    location_data = {
        **request.form,
        'user_id' : session['user_id']
    }
    print(location_data)
    Location.create(location_data)
    return redirect('/dashboard')

# route to view one location
@app.route('/locations/view/<int:id>')
def view_one_location(id):
    if 'user_id' not in session:
        return redirect ('/')
    logged_data = {
        'id' : session['user_id']
    }
    logged_user = User.get_by_id(logged_data)
    data = {
        'id' : id
    }
    all_comments = Comment.get_all_comments_from_location(data)
    one_location = Location.get_one_location(data)
    user_favorite_ids = User.get_favorite_location_id(session['user_id'])
    return render_template ('location_one.html', one_location = one_location, logged_user=logged_user, all_comments=all_comments, user_favorite_ids=user_favorite_ids)

# action route to add to favorites
@app.route('/locations/favorites',methods=['POST'])
def add_favorites():
    location_id = request.form['location_id']
    user_id = session['user_id']
    data = {
        'location_id': location_id,
        'user_id' : user_id
    }
    Location.add_to_favorites(data)
    return redirect(f'/locations/view/{location_id}')


# route to view all favorites
@app.route('/locations/favorites')
def favorites():
    if 'user_id' not in session:
        return redirect('/')
    logged_data = {
        'id' : session['user_id']
    }
    logged_user = User.get_by_id(logged_data)
    favorite_locations = logged_user.get_users_with_locations(logged_data)
    return render_template('favorites.html', logged_user = logged_user, favorite_locations=favorite_locations, request=request)

# route to view edit form
@app.route('/locations/edit/<int:id>')
def view_edit_location(id):
    if 'user_id' not in session:
        return redirect('/')
    logged_data = {
        'id' : session['user_id']
    }
    logged_user = User.get_by_id(logged_data)
    data = {
        'id' : id
    }
    one_location = Location.get_one_location(data)
    if session['user_id'] != one_location.user_id:
        flash ('This is not your post, you did not post this.')
        return redirect ('/dashboard')
    return render_template ('location_edit.html', one_location = one_location, logged_user=logged_user)

# action route to update the form
@app.route('/locations/update/<int:id>', methods=['POST'])
def update_location(id):
    if 'user_id' not in session:
        return redirect('/')
    if not Location.validate_data(request.form):
        return redirect(f'/locations/edit/{id}')
    update_data = {
        **request.form,
        'id' : id
    }
    Location.update_location(update_data)
    return redirect (f'/locations/view/{id}')

# action route to delete location
@app.route('/locations/delete/<int:id>')
def delete(id):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id' : id
    }
    Location.delete_location(data)
    return redirect('/dashboard')

# action route to create new comment
@app.route('/comments/create', methods=['POST'])
def create():
    if 'user_id' not in session:
        return redirect('/')
    print(app.logger)
    location_id = request.form['location_id']
    comment_data = {
        **request.form,
        'user_id' : session['user_id']
    }
    print(request.form)
    Comment.create_comment(comment_data)
    return redirect(f'/locations/view/{location_id}')

# action to delete user comment
@app.route('/comments/delete/<int:id>')
def delete_comment(id):
    if 'user_id' not in session:
        return redirect('/')
    location_id = Comment.get_location_id({'id': id})
    data = {
        'id' : id
    }
    Comment.delete_comment(data)
    return redirect(f'/locations/view/{location_id}')