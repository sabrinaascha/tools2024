from flask import Blueprint, render_template, jsonify, request, url_for
from flask_login import current_user, login_required
from app.models import Projekt, Spinde, Html
from datetime import date
from random import randrange
from .index import (
    getStudentInformationList,
    getLockerInformationHTML,
    checkStudentReservation,
)
import logging
import subprocess

bp_themen = Blueprint('bp_themen', __name__)

@bp_themen.route('/themen')
def themen():
    projekte = Projekt.get_all_projekte()
    return render_template('themen/themen.html', projekte=projekte)