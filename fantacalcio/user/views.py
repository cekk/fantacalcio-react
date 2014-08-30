# -*- coding: utf-8 -*-
from flask import (Blueprint, request, render_template, flash, url_for,
                    redirect, session, make_response, jsonify, abort)
from flask.ext.login import login_required
from fantacalcio.user.models import User
from fantacalcio.players.models import Player
import json
from fantacalcio.database import db

blueprint = Blueprint("user", __name__, url_prefix='/users',
                        static_folder="../static")


from functools import wraps
from flask import g, request, redirect, url_for

def user_can_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logged_user = User.query.filter_by(id=session.get('user_id')).first()
        view_user = request.view_args.get('user')
        if logged_user.username != view_user and not logged_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@blueprint.route("/")
@login_required
def members():
    return render_template("users/members.html", members=User.query.order_by('username'))

@blueprint.route("/<user>")
@login_required
@user_can_access
def user(user):
    result = User.query.filter_by(username=user)
    try:
        member = result.first_or_404()
        return render_template("users/member.html", member=member)
    except Exception as e:
        abort(404)


@blueprint.route("/auction/<user>")
@login_required
@user_can_access
def member_players(user):
    user = User.query.filter_by(username=user).first()
    response = make_response()

    if not user:
        response.data= {}
    else:
        gk = [x.to_json() for x in user.players.filter_by(role="P")]
        d = [x.to_json() for x in user.players.filter_by(role="D")]
        m = [x.to_json() for x in user.players.filter_by(role="C")]
        s = [x.to_json() for x in user.players.filter_by(role="A")]
        response.data = json.dumps({'auction_budget': user.auction_budget,
                                    'n_players': user.players.count(),
                                    'goalkeepers': gk,
                                    'defenders': d,
                                    'midfielders': m,
                                    'strikers': s})
    return response


@blueprint.route("/sell", methods=['POST'])
@login_required
@user_can_access
def sell():
    errors = {}
    player_id = request.form.get('player')
    if not player_id:
        errors['player'] = True
    player = Player.query.filter_by(id=player_id).first()
    if not player.fantacalcio_team:
        errors['message'] = "Il giocatore non appartiene a nessuno"
    user = User.query.filter_by(username=player.fantacalcio_team).first()
    if not user:
        errors['message'] = "Utente non trovato"
    if errors:
        return make_response(jsonify(errors), 400)
    print "Rimuovo il giocatore: %s (%s)" % (player.name, player_id)
    user.players.remove(player)
    if not player.auction_price:
        player.auction_price = 0
    user.auction_budget = user.auction_budget + player.auction_price
    player.auction_price = 0
    db.session.add(user)
    db.session.add(player)
    db.session.commit()
    response = make_response()
    response.data = json.dumps({'message': 'Giocatore rimosso'})
    return response
