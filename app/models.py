from . import db

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    city = db.Column(db.String(80), nullable=True)

    # relationships to matches and players
    home_matches = db.relationship(
        'Match',
        foreign_keys='Match.team1_id',
        backref='team1',
        lazy=True
    )
    away_matches = db.relationship(
        'Match',
        foreign_keys='Match.team2_id',
        backref='team2',
        lazy=True
    )
    players = db.relationship('Player', backref='team', lazy=True)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    venue = db.Column(db.String(120), nullable=True)
    team1_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    team2_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)

    # relationship to performances
    performances = db.relationship('Performance', backref='match', lazy=True)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)

    # relationship to performances
    performances = db.relationship('Performance', backref='player', lazy=True)

class Performance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    runs_scored = db.Column(db.Integer, default=0)
    balls_faced = db.Column(db.Integer, default=0)
    wickets = db.Column(db.Integer, default=0)
    overs_bowled = db.Column(db.Float, default=0.0)
