from extentions import db
from datetime import datetime


class BacklogProbe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    backlog_timeref = db.Column(db.Integer, nullable=False)
    ticket_probed = db.Column(db.Integer, nullable=False)
    prober_username = db.Column(db.String(24), db.ForeignKey('users.username'))
    probe = db.Column(db.String(256), nullable=False)
    date_probed = db.Column(db.DateTime, default=datetime.now())

    def __init__(self, backlog_timeref, ticket_probed, probe, prober):
        self.backlog_timeref = backlog_timeref
        self.ticket_probed = ticket_probed
        self.probe = probe
        self.prober_username = prober
