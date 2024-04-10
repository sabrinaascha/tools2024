from flask_login import current_user
from app.models import Mitarbeiter


def get_mitarbeiter():
    if current_user.is_authenticated and current_user.nds:
        mitarbeiter = Mitarbeiter.query.filter_by(nds=current_user.nds).first()
        return mitarbeiter
    return None
