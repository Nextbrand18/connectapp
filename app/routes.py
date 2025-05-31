from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from . import db, photos
from .models import User, Link
from .forms import RegisterForm, LoginForm, LinkForm, ProfileForm  # Make sure ProfileForm is imported
import os

main = Blueprint('main', __name__)

@main.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))  # Changed to main.dashboard
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
            current_app.logger.error(f'Registration error: {str(e)}')
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data if hasattr(form, 'remember') else False)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    if form.validate_on_submit():
        try:
            current_user.bio = form.bio.data
            
            if form.picture.data:
                # Remove old profile picture if exists
                if current_user.profile_picture:
                    old_pic = os.path.join(current_app.root_path, 'static', 'profile_pics', current_user.profile_picture)
                    if os.path.exists(old_pic):
                        os.remove(old_pic)
                
                # Save new picture
                filename = secure_filename(f"{current_user.id}_{form.picture.data.filename}")
                filepath = os.path.join(current_app.root_path, 'static', 'profile_pics', filename)
                form.picture.data.save(filepath)
                current_user.profile_picture = filename
                
            db.session.commit()
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'danger')
            current_app.logger.error(f'Profile update error: {str(e)}')
    
    elif request.method == 'GET':
        form.bio.data = current_user.bio
    
    return render_template('profile.html', form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    links = Link.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', links=links)

@main.route('/dashboard/<username>')
def public_dashboard(username):
    user = User.query.filter_by(username=username).first_or_404()
    links = Link.query.filter_by(user_id=user.id).all()
    return render_template('public_dashboard.html', links=links, user=user)

@main.route('/add', methods=['GET', 'POST'])
@login_required
def add_link():
    form = LinkForm()
    if form.validate_on_submit():
        try:
            filename = photos.save(form.image.data) if form.image.data else None
            link = Link(
                url=form.url.data, 
                title=form.title.data, 
                notes=form.notes.data,
                image_filename=filename, 
                user_id=current_user.id
            )
            db.session.add(link)
            db.session.commit()
            flash('Link added successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding link. Please try again.', 'danger')
            current_app.logger.error(f'Link add error: {str(e)}')
    return render_template('add_link.html', form=form)

@main.route('/edit/<int:link_id>', methods=['GET', 'POST'])
@login_required
def edit_link(link_id):
    link = Link.query.get_or_404(link_id)
    if link.user_id != current_user.id:
        flash('You can only edit your own links.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    form = LinkForm(obj=link)
    if form.validate_on_submit():
        try:
            link.url = form.url.data
            link.title = form.title.data
            link.notes = form.notes.data
            if form.image.data:
                if link.image_filename:  # Remove old image if exists
                    old_img = os.path.join(current_app.root_path, 'app', 'static', 'uploads', link.image_filename)
                    if os.path.exists(old_img):
                        os.remove(old_img)
                link.image_filename = photos.save(form.image.data)
            db.session.commit()
            flash('Link updated successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating link. Please try again.', 'danger')
            current_app.logger.error(f'Link edit error: {str(e)}')
    return render_template('edit_link.html', form=form, link=link)

@main.route('/delete/<int:link_id>')
@login_required
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    if link.user_id != current_user.id:
        flash('You can only delete your own links.', 'danger')
        return redirect(url_for('main.dashboard'))
        
    try:
        if link.image_filename:  # Delete associated image
            img_path = os.path.join(current_app.root_path, 'app', 'static', 'uploads', link.image_filename)
            if os.path.exists(img_path):
                os.remove(img_path)
        db.session.delete(link)
        db.session.commit()
        flash('Link deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting link. Please try again.', 'danger')
        current_app.logger.error(f'Link delete error: {str(e)}')
    return redirect(url_for('main.dashboard'))