from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from . import db, photos
from .models import User, Link
from .forms import RegisterForm, LoginForm, LinkForm
import os

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return redirect(url_for('main.dashboard')) if current_user.is_authenticated else redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful.')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid credentials')
    return render_template('login.html', form=form)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    links = Link.query.filter_by(user_id=current_user.id)
    return render_template('dashboard.html', links=links)

@main.route('/add', methods=['GET', 'POST'])
@login_required
def add_link():
    form = LinkForm()
    if form.validate_on_submit():
        filename = photos.save(form.image.data) if form.image.data else None
        link = Link(url=form.url.data, title=form.title.data, notes=form.notes.data,
                    image_filename=filename, owner=current_user)
        db.session.add(link)
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return render_template('add_link.html', form=form)

@main.route('/edit/<int:link_id>', methods=['GET', 'POST'])
@login_required
def edit_link(link_id):
    link = Link.query.get_or_404(link_id)
    form = LinkForm(obj=link)
    if form.validate_on_submit():
        link.url = form.url.data
        link.title = form.title.data
        link.notes = form.notes.data
        if form.image.data:
            link.image_filename = photos.save(form.image.data)
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return render_template('edit_link.html', form=form, link=link)

@main.route('/delete/<int:link_id>')
@login_required
def delete_link(link_id):
    link = Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()
    return redirect(url_for('main.dashboard'))


@main.route('/dashboard/<username>')  # Add this new route
def public_dashboard(username):
    user = User.query.filter_by(username=username).first_or_404()
    links = Link.query.filter_by(user_id=user.id).all()
    return render_template('public_dashboard.html', links=links, user=user)

@main.route('/dashboard')  # Keep your existing private dashboard
@login_required
def private_dashboard():
    links = Link.query.filter_by(user_id=current_user.id)
    return render_template('dashboard.html', links=links)