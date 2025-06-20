import csv
import traceback
from io import TextIOWrapper
from flask import Blueprint, render_template, request, current_app
from dateutil import parser

from . import db
from .models import Team, Player, Match, Performance

# Blueprint for stats upload and processing
stats_bp = Blueprint(
    "stats_bp",
    __name__,
    template_folder="templates",
)

@stats_bp.route("/upload", methods=["GET", "POST"])
def upload_stats():
    """
    Route: /upload
    GET: Render upload form
    POST: Process uploaded CSV and insert stats into DB
    """
    message = None

    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            message = "No file selected."
            return render_template("upload.html", message=message)

        try:
            stream = TextIOWrapper(file.stream, encoding="utf-8")
            reader = csv.DictReader(stream)

            for row in reader:
                raw_date = row.get("date") or row.get("Date")
                date = parser.parse(raw_date).date()
                venue = row.get("venue") or row.get("Venue")

                team1_name = row.get("team1") or row.get("Team1")
                team2_name = row.get("team2") or row.get("Team2")
                t1 = Team.query.filter_by(name=team1_name).first() or Team(name=team1_name)
                t2 = Team.query.filter_by(name=team2_name).first() or Team(name=team2_name)
                db.session.add_all([t1, t2])
                db.session.commit()

                match = Match(
                    date=date,
                    venue=venue,
                    team1_id=t1.id,
                    team2_id=t2.id
                )
                db.session.add(match)
                db.session.commit()

                player_name = row.get("player") or row.get("Player")
                player = Player.query.filter_by(name=player_name).first()
                if not player:
                    player = Player(name=player_name, team_id=t1.id)
                    db.session.add(player)
                    db.session.commit()

                perf = Performance(
                    match_id=match.id,
                    player_id=player.id,
                    runs_scored=int(row.get("runs", 0)),
                    balls_faced=int(row.get("balls", 0)),
                    wickets=int(row.get("wickets", 0)),
                    overs_bowled=float(row.get("overs", 0.0)),
                )
                db.session.add(perf)

            db.session.commit()
            message = "✅ Upload and import successful!"

        except Exception as e:
            current_app.logger.error(traceback.format_exc())
            message = f"Error processing CSV: {e.__class__.__name__}: {e}"

    return render_template("upload.html", message=message)

@stats_bp.route('/matches')
def list_matches():
    """
    Route: /matches
    GET: Show a list of imported matches
    """
    try:
        matches = Match.query.order_by(Match.date.desc()).all()
        return render_template('matches.html', matches=matches)
    except Exception as e:
        current_app.logger.error(traceback.format_exc())
        return f"Error rendering matches: {e.__class__.__name__}: {e}", 500

@stats_bp.route('/api/performances')
def api_performances():
    """
    Route: /api/performances
    GET: Return aggregated performance data as JSON
    """
    metric = request.args.get('metric', 'runs')
    if metric == 'wickets':
        agg = db.func.sum(Performance.wickets)
        label = 'Total Wickets'
    else:
        agg = db.func.sum(Performance.runs_scored)
        label = 'Total Runs'

    results = db.session.query(
        Player.name,
        agg.label('value')
    ).join(Performance).group_by(Player.id).all()
    data = [{'player': name, 'value': val} for name, val in results]
    return {
        'metric': metric,
        'label': label,
        'data': data
    }

@stats_bp.route('/batting')
def batting_view():
    """Renders a bar chart of total runs by player."""
    return render_template('batting.html')

@stats_bp.route('/bowling')
def bowling_view():
    """Renders a bar chart of total wickets by player."""
    return render_template('bowling.html')
