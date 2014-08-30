# -*- coding: utf-8 -*-
'''Public section, including homepage and signup.'''
from flask import (Blueprint, request, render_template, flash, url_for,
                    redirect, session, make_response, jsonify)
from flask.ext.login import login_user, login_required, logout_user

from fantacalcio.extensions import login_manager
from fantacalcio.user.models import User
from fantacalcio.user.views import user_can_access
from fantacalcio.public.forms import LoginForm
from fantacalcio.user.forms import RegisterForm
from fantacalcio.players.models import Player
from fantacalcio.utils import flash_errors
from fantacalcio.database import db
from  sqlalchemy.sql.expression import func
import json
from sqlalchemy import desc

blueprint = Blueprint('public', __name__, static_folder="../static")
auction_blueprint = Blueprint("auction", __name__, url_prefix='/auction',
                        static_folder="../static")

@login_manager.user_loader
def load_user(id):
    return User.get_by_id(int(id))


@blueprint.route("/", methods=["GET", "POST"])
def home():
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", 'success')
            redirect_url = request.args.get("next") or url_for("user.user", user=form.user.username)
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
    if form.validate_on_submit():
        picture = request.files.get('picture')
        import pdb;pdb.set_trace()
        new_user = User.create(username=form.username.data,
                        picture=picture,
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

#ASTA

@auction_blueprint.route("/")
@login_required
@user_can_access
def auction():
    return render_template("public/auction.html")

@auction_blueprint.route("/extract")
@login_required
@user_can_access
def extract():
    cleanSelection()
    session = db.session()
    random_players = session.query(Player).filter_by(extracted=False).order_by(func.random())
    print "%s Players left to extract." % random_players.count()
    player = random_players.first()
    if not player:
        return {}
    response = make_response()
    data = player.to_json()
    data['users'] = [x.username for x in User.query.order_by('username')]
    response.data = json.dumps(data)
    player.currently_selected = True
    db.session.add(player)
    db.session.commit()
    return response

@auction_blueprint.route("/selected")
@login_required
def selected():
    session = db.session()
    player = session.query(Player).filter_by(currently_selected=True).first()
    response = make_response()
    if not player:
        response.data= {}
    else:
        data = player.to_json()
        data['users'] = [x.username for x in User.query.order_by('username')]
        response.data = json.dumps(data)
    return response

@auction_blueprint.route("/buy", methods=['POST'])
@login_required
@user_can_access
def buy():
    errors = {}
    player_id = request.form.get('player')
    price = request.form.get('price')
    if price:
        price = int(price)
    else:
        price = 0
    team = request.form.get('team')
    if not player_id:
        errors['player'] = True
    if not price:
        errors['price'] = True
    if not team:
        errors['team'] = True
    user = User.query.filter_by(username=team).first()
    player = Player.query.filter_by(id=player_id).first()
    if user and user.auction_budget < price:
        errors['price'] = True
        errors['team'] = True
        errors['msg'] = "La squadra %s non ha abbastanza crediti per acquistare %s" % (team, player.name)
    if errors:
        return make_response(jsonify(errors), 400)
    user.players.append(player)
    user.auction_budget = user.auction_budget - price
    player.auction_price = price
    db.session.add(user)
    db.session.add(player)
    db.session.commit()
    return extract()

def cleanSelection():
    session = db.session()
    selected_player = session.query(Player).filter_by(currently_selected=True).first()
    if selected_player:
        selected_player.currently_selected = False
        db.session.add(selected_player)
        db.session.commit()
