/**
* @jsx React.DOM
*/
var UserAuctionBox = React.createClass({
    getInitialState: function() {
        return {data: []}
    },
    loadSelectedPlayer: function() {
        $.ajax({
            url: '/auction/selected',
            dataType: 'json',
            success: function (data) {
                this.setState({data: data});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error("/auction", status, err.toString());
            }.bind(this)
        });
    },
    componentWillMount: function() {
        this.loadSelectedPlayer();
        setInterval(this.loadSelectedPlayer, this.props.pollInterval);
    },
    render: function() {
        return (
            <PlayerInfos data={this.state.data} showStatistics={false} />
            );
    }
});

var UserAuctionTeamBox = React.createClass({
    getInitialState: function() {
        return {data: []}
    },
    loadUserTeam: function(infos) {
        $.ajax({
            url: '/users/auction/' + this.props.currentUser,
            dataType: 'json',
            success: function (data) {
                this.setState({data: data,
                               infos: infos});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error("/auction", status, err.toString());
            }.bind(this)
        });
    },
    componentWillMount: function() {
        this.loadUserTeam();
        setInterval(this.loadUserTeam, this.props.pollInterval);
    },
    render: function() {
        var goalkeepers, defenders, midfielders, strikers, message;
        if (this.state.infos !== undefined) {
            message = <div className="alert alert-success" role="alert">{this.state.infos.message}</div>
        }
        if (this.state.data.goalkeepers !== undefined && (this.state.data.goalkeepers.length !== 0)) {
            goalkeepers = <TeamRoles deleteUsers={this.props.deleteUsers} loadUserTeam={this.loadUserTeam} data={this.state.data.goalkeepers} name="Portieri"/>
        }
        if (this.state.data.defenders !== undefined && (this.state.data.defenders.length !== 0)) {
            defenders = <TeamRoles deleteUsers={this.props.deleteUsers} loadUserTeam={this.loadUserTeam} data={this.state.data.defenders} name="Difensori"/>
        }
        if (this.state.data.midfielders !== undefined && (this.state.data.midfielders.length !== 0)) {
            midfielders = <TeamRoles deleteUsers={this.props.deleteUsers} loadUserTeam={this.loadUserTeam} data={this.state.data.midfielders} name="Centrocampisti"/>
        }
        if (this.state.data.strikers !== undefined && (this.state.data.strikers.length !== 0)) {
            strikers = <TeamRoles deleteUsers={this.props.deleteUsers} loadUserTeam={this.loadUserTeam} data={this.state.data.strikers} name="Attaccanti"/>
        }
        var budget = Math.round((this.state.data.auction_budget/350) * 100);
        var n_players = Math.round((this.state.data.n_players/25) * 100);
        var budget_style = {width: budget + "%"};
        var players_style = {width: n_players + "%"};
        return (
            <div className="teamInfo">
                <div className="teamPlayers well">
                    <div className="row">
                        <div className="col-xs-12 col-sm-6">
                            <div className="panel">
                              <div className="panel-heading">
                                <h3 className="panel-title">
                                    <i className="fa fa-euro"></i> Budget attuale: {this.state.data.auction_budget}/350
                                </h3>
                              </div>
                              <div className="panel-body">
                                <div className="progress">
                                  <div className={budget === 100 ? 'progress-bar progress-bar-success' : 'progress-bar'}
                                       role="progressbar" aria-valuenow={budget} aria-valuemin="0" aria-valuemax="100" style={budget_style}>
                                    {budget}%
                                  </div>
                                </div>
                              </div>
                            </div>
                        </div>
                        <div className="col-xs-12 col-sm-6">
                            <div className="panel">
                              <div className="panel-heading">
                                <h3 className="panel-title">
                                    <i className="fa fa-users"></i> Giocatori acquistati: {this.state.data.n_players}/25
                                </h3>
                              </div>
                              <div className="panel-body">
                                    <div className="progress">
                                        <div className={n_players === 100 ? 'progress-bar progress-bar-success' : 'progress-bar'}
                                            role="progressbar" aria-valuenow={n_players} aria-valuemin="0" aria-valuemax="100" style={players_style}>
                                            {n_players}%
                                        </div>
                                    </div>
                              </div>
                            </div>
                        </div>
                    </div>
                    {message}
                    {goalkeepers}
                    {defenders}
                    {midfielders}
                    {strikers}
                </div>
            </div>
            );
    }
});

var AdminAuctionBox = React.createClass({
    getInitialState: function() {
        return {data: []}
    },
    loadSelectedPlayer: function() {
        $.ajax({
            url: '/auction/selected',
            dataType: 'json',
            success: function (data) {
                this.setState({data: data});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error("/auction", status, err.toString());
            }.bind(this)
        });
    },
    buyPlayer: function(e) {
        e.preventDefault();
        var player = this.refs.player.getDOMNode().value.trim();
        var price = this.refs.price.getDOMNode().value.trim();
        var team = $("input[name=team]:checked", ".auctionForm").val();
        this.onBuySubmit({player: player, price: price, team: team});
        this.refs.player.getDOMNode().value = '';
        $("input[name=team]:checked", ".auctionForm").attr('checked', false);
        this.refs.price.getDOMNode().value = 0;
        return false;
    },
    onBuySubmit: function(auction) {
        $.ajax({
            url: '/auction/buy',
            type:'POST',
            data:auction,
            dataType: 'json',
            success: function (data) {
                data['message'] = 'Giocatore acquistato';
                this.replaceState({data: data});
            }.bind(this),
            error: function (xhr, status, err) {
                this.setState({'error': JSON.parse(xhr.responseText)});
                console.error("/auction", status, err.toString());
            }.bind(this)
        });
    },
    extractPlayer: function() {
        this.setState({data: this.state.data}, function() {
          // `setState` accepts a callback. To avoid (improbable) race condition,
          // `we'll send the ajax request right after we optimistically set the new
          // `state.
            $.ajax({
                url: '/auction/extract',
                dataType: 'json',
                success: function (data) {
                    this.replaceState({data: data});
                }.bind(this),
                error: function (xhr, status, err) {
                    console.error("/auction", status, err.toString());
                }.bind(this)
            });
        });
    },
    componentWillMount: function() {
        this.loadSelectedPlayer();
    },
    render: function() {
        var errors = this.state.error;
        var partial, users;
        if (errors !== undefined) {
            partial = <div className="alert alert-warning" role="alert">{(this.state.error !== undefined && this.state.error.msg !== undefined) ? this.state.error.msg : 'Correggi gli errori evidenziati'}</div>
        }
        else if (this.state.data.message !== undefined) {
            partial = <div className="alert alert-success" role="alert">{this.state.data.message}</div>
        }
        if (this.state.data.users !== undefined) {
            users = this.state.data.users.map(function(result) {
                var avatar_url = "url(" + result.avatar + ")";
                var avatar_style = {"background-image": avatar_url};
                return (
                    <div key={result.id}
                       className="radioUser radio-inline">
                        <input type="radio"
                               name="team"
                               ref="team"
                               value={result.username} id={result.username} />
                        <div className={(this.state.error !== undefined && this.state.error.team === true) ? 'thumbnail hasError' : 'thumbnail'}
                             style={avatar_style}>
                            <label htmlFor={result.username}>{result.username}</label>
                        </div>
                    </div>
                    )
                }, this);
        }
        return (
            <div className="adminExtraction">
            {partial}
            <PlayerInfos data={this.state.data}/>
            <form className="auctionForm form-horizontal" onSubmit={this.buyPlayer}>
                <div className="form-group teamUsers">
                    {users}
                </div>
                <input id="player"
                       name="player"
                       ref="player"
                       type="hidden"
                       value={this.state.data.id} />
                <div className={(this.state.error !== undefined && this.state.error.price === true) ? 'input-group inputPrice has-error' : 'input-group inputPrice'}>
                  <div className="input-group-addon">€</div>
                  <input id="price"
                         name="price"
                         ref="price"
                         className="form-control"
                         type="number"
                         placeholder="Prezzo" />
                </div>
                <button type="submit" className="btn btn-success">Acquista</button>
                <button type="button" className="btn btn-info"
                        onClick={this.extractPlayer}>
                    <span className="glyphicon glyphicon-refresh"></span> Estrai
                </button>
            </form>
            </div>
            );
    }
});

var PlayerInfos = React.createClass({
    render: function() {
        var statistics;
        // console.log(this.props);
        if (this.props.data.statistics !== undefined && this.props.showStatistics === true) {
            statistics = <div className="pull-right">
                            <p>Giocatori estratti: {this.props.data.statistics.extracted_players}</p>
                            <p>Giocatori rimanenti: {this.props.data.statistics.players_left}</p>
                        </div>
        }
        var team_url = this.props.data.team !== undefined ? "static/images/" + this.props.data.team + ".png" : "";
        var role_class = "";
        if (this.props.data.role === 'P') {
            role_class = "label label-warning";
        }
        else if (this.props.data.role === 'D') {
            role_class = "label label-success";
        }
        else if (this.props.data.role === 'C') {
            role_class = "label label-primary";
        }
        else if (this.props.data.role === 'A') {
            role_class = "label label-danger";
        }
        return (
            <div className="jumbotron">
              {statistics}
                <div className="row">
                    <div className="col-xs-8 col-md-10">
                        <h1>{this.props.data.name}</h1>
                        <span className={role_class}>{this.props.data.role}</span>
                        <span className="label label-default">{this.props.data.team}</span>
                        <span className="label label-default">{this.props.data.original_price}€</span>
                    </div>
                    <div className="col-xs-4 col-md-2">
                        <img className="img-responsive center-block" src={team_url} />
                    </div>
                </div>
            </div>
        );
    }
});

var TeamRoles = React.createClass({
    render: function() {
        var rows;
        if (this.props.deleteUsers) {
            rows = this.props.data.map(function(result) {
                return (
                    <tr key={result.id}>
                        <td>
                            <DeleteForm loadUserTeam={this.props.loadUserTeam} data={result}/>
                        </td>
                        <td>{result.name} ({result.team})</td>
                        <td>{result.auction_price}</td>
                    </tr>
                    )
            }, this);
        }
        else {
            rows = this.props.data.map(function(result) {
                return (
                    <tr key={result.id}>
                        <td></td>
                        <td>{result.name} ({result.team})</td>
                        <td>{result.auction_price}</td>
                    </tr>
                    )
            }, this);
        }
        return (
            <div className="panel panel-primary">
                <div className="panel-heading">
                    <h3 className="panel-title">
                    {this.props.name}<span className="badge pull-right">{this.props.data.length}</span>
                    </h3>
                </div>
                <table className="table table-striped">
                    <thead>
                      <tr>
                        <th className="removeColumn"></th>
                        <th>Nome</th>
                        <th className="priceColumn">Prezzo</th>
                      </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        );
    }
});

var DeleteForm = React.createClass({
    sellPlayer: function(e) {
        var player = this.props.data.id;
        this.onSellSubmit({player: player});
        return false;
    },
    onSellSubmit: function(player) {
        $.ajax({
            url: '/users/sell',
            type:'POST',
            data:player,
            dataType: 'json',
            success: function (data) {
                this.props.loadUserTeam(data);
            }.bind(this),
            error: function (xhr, status, err) {
                alert("ERRORE");
                this.setState({'error': JSON.parse(xhr.responseText)});
                console.error("/auction", status, err.toString());
            }.bind(this)
        });
    },
    render: function() {
        return (
            <div className="deleteForm" key={this.props.data.id}>
                <form ref="form" onSubmit={this.sellPlayer}>
                    <input name="player"
                           ref="player"
                           type="hidden"
                           value={this.props.data.id} />
                    <button type="submit" className="btn btn-danger btn-xs">
                        <span className="glyphicon glyphicon-trash"></span>
                    </button>
                </form>
            </div>
        );
    }
});


if (document.getElementById('user-content') !== null) {
    React.renderComponent(
        <UserAuctionBox url="/auction" pollInterval={2000} />,
        document.getElementById('user-content')
    );
}
else if (document.getElementById('content') !== null) {
    React.renderComponent(
        <AdminAuctionBox url="/auction" pollInterval={2000} />,
        document.getElementById('content')
    );
}

if (document.getElementById('user-team') !== null) {
    React.renderComponent(
        <UserAuctionTeamBox url="/auction" currentUser={document.getElementById('user-team').dataset.currentUser} pollInterval={2000} deleteUsers={false} />,
        document.getElementById('user-team')
    );
}

$.each($('div.teamList div.userTeam'), function() {
    React.renderComponent(
        <UserAuctionTeamBox url="/auction" currentUser={this.dataset.user} pollInterval={2000} deleteUsers={true}/>,
        this
    );
});
