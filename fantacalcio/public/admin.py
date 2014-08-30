# -*- coding: utf-8 -*-
'''Admin section, including site setup.'''
from flask import (Blueprint, request, render_template, flash, url_for,
                    redirect, session)
from flask.ext.login import login_user, login_required, logout_user
from flask.views import View
from fantacalcio.extensions import login_manager
from fantacalcio.utils import flash_errors
from fantacalcio.database import db

blueprint = Blueprint('admin', __name__, static_folder="../static")

class Settings(View):

     def get(self):
         users = User.query.all()

     def post(self):
         user = User.from_form_data(request.form)

simple_page .add_url_rule('/', view_func=UserAPI.as_view('users'))



@blueprint.route("/", methods=["GET", "POST"])
def home():
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", 'success')
            redirect_url = request.args.get("next") or url_for("user.members")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template("public/home.html", form=form)

@blueprint.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You are logged out.', 'info')
    return redirect(url_for('public.home'))

@blueprint.route("/register/", methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form, csrf_enabled=False)
    import pdb;pdb.set_trace()
    if form.validate_on_submit():
        new_user = User.create(username=form.username.data,
                        picture=form.picture.data,
                        password=form.password.data,
                        active=True)
        flash("Thank you for registering. You can now log in.", 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)

@blueprint.route("/about/")
def about():
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)
