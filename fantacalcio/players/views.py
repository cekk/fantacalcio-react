# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, abort, request, flash, url_for, redirect, current_app
from flask.ext.login import login_required
from fantacalcio.players.models import Player
from fantacalcio.user.models import User
from fantacalcio.database import db
from werkzeug.exceptions import NotFound
from sqlalchemy import desc

blueprint = Blueprint("player", __name__, url_prefix='/players',
                        static_folder="../static")


@blueprint.route("/")
@login_required
def players():
    players = Player.query.filter_by(auction_price=0)
    gk = [x for x in players.filter_by(role="P").order_by(desc(Player.original_price))]
    d = [x for x in players.filter_by(role="D").order_by(desc(Player.original_price))]
    m = [x for x in players.filter_by(role="C").order_by(desc(Player.original_price))]
    s = [x for x in players.filter_by(role="A").order_by(desc(Player.original_price))]
    players = {'goalkeepers': gk,
                'defenders': d,
                'midfielders': m,
                'strikers': s,
                'users': [x.username for x in User.query.order_by('username')]}
    return render_template("players/players.html", players=players)

@blueprint.route("/<player>")
@login_required
def player(player):
    result = Player.query.filter_by(name=player.upper())
    try:
        player = result.first_or_404()
        return render_template("players/player.html", player=player)
    except Exception as e:
        abort(404)

@blueprint.route("/admin_buy", methods=['POST'])
@login_required
def admin_buy():
    errors = {}
    player_id = request.form.get('player')
    price = request.form.get('price')
    if price:
        price = int(price)
    else:
        price = 0
    team = request.form.get('team')
    errors = False
    if not player_id:
        errors = True
        flash('Non hai selezionato un giocatore', 'danger')
    if not price:
        errors = True
        flash('Non hai inserito un prezzo', 'danger')
    if not team:
        errors = True
        flash('Non hai selezionato una squadra', 'danger')
    user = User.query.filter_by(username=team).first()
    player = Player.query.filter_by(id=player_id).first()
    if user and user.auction_budget < price:
        errors = True
        flash("La squadra %s non ha abbastanza crediti per acquistare %s" % (team, player.name), 'danger')
    max_players = current_app.config['%s_LIMIT' % player.role]
    if user.players.filter_by(role=player.role).count() == max_players:
        errors = True
        flash(u"La squadra %s ha già tutti i giocatori per questo ruolo." % team, 'danger')
    if not errors:
        user.players.append(player)
        user.auction_budget = user.auction_budget - price
        player.auction_price = price
        db.session.add(user)
        db.session.add(player)
        db.session.commit()
        flash("%s acquistato" % player.name, 'success')
    return redirect(url_for('player.players'))
