import os
import io
import pytest

from app.models import Team, Player, Match, Performance
from datetime import date
from app import db


def test_upload_and_list(client):
    # Path to your sample CSV in the tests folder
    sample_path = os.path.join(os.path.dirname(__file__), "sample_cricket.csv")
    assert os.path.exists(sample_path), f"CSV not found at {sample_path}"

    # Upload the real sample file
    with open(sample_path, "rb") as f:
        data = {"file": (f, "sample_cricket.csv")}
        rv = client.post(
            "/upload",
            data=data,
            content_type="multipart/form-data"
        )
    assert b"Upload and import successful" in rv.data

    # After import, /matches should list at least one table cell
    rv = client.get("/matches")
    assert rv.status_code == 200
    assert b"<td>" in rv.data


def test_api_performances(client):
    # Seed one performance directly for isolation
    t1 = Team(name="Team X"); t2 = Team(name="Team Y")
    db.session.add_all([t1, t2]); db.session.commit()
    m = Match(date=date.today(), venue="TestVenue", team1_id=t1.id, team2_id=t2.id)
    db.session.add(m); db.session.commit()
    p = Player(name="TestPlayer", team_id=t1.id); db.session.add(p); db.session.commit()
    perf = Performance(match_id=m.id, player_id=p.id, runs_scored=25, balls_faced=15, wickets=2, overs_bowled=3)
    db.session.add(perf); db.session.commit()

    # Test runs metric
    rv = client.get("/api/performances?metric=runs")
    json = rv.get_json()
    assert json["metric"] == "runs"
    assert any(d["player"] == "TestPlayer" and d["value"] == 25 for d in json["data"])

    # Test wickets metric
    rv = client.get("/api/performances?metric=wickets")
    json = rv.get_json()
    assert json["metric"] == "wickets"
    assert any(d["player"] == "TestPlayer" and d["value"] == 2 for d in json["data"])


def test_chart_views(client):
    for path in ["/batting", "/bowling"]:
        rv = client.get(path)
        assert rv.status_code == 200
        assert b"<canvas" in rv.data
