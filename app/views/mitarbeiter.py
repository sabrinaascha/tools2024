from flask import Blueprint, render_template, jsonify, request, url_for
from flask_login import current_user, login_required
from app.models import Spinde, Html , Mitarbeiter , Lehrstuhl , Projekt , Projekt_Betreuer , get_all_projekt_betreuer
from app.helpers import get_mitarbeiter
from datetime import date
from random import randrange
from .index import (
    getStudentInformationList,
    getLockerInformationHTML,
    checkStudentReservation,
    checkMitarbeiter,
)
import logging
import subprocess


bp_mitarbeiter = Blueprint("bp_mitarbeiter", __name__)

# Configure the logging module
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@bp_mitarbeiter.route("/")
@login_required
def mitarbeiter():
    mitarbeiter, lehrstuhl = get_mitarbeiter()
    lehrstuhl_id = lehrstuhl.lehrstuhl_id
    lehrstuhl = Lehrstuhl.query.get(mitarbeiter.Lehrstuhl_lehrstuhl_id)
    is_mitarbeiter = Mitarbeiter.query.filter_by(nds=current_user.nds).first() is not None
    alle_mitarbeiter = Mitarbeiter.query.filter_by(Lehrstuhl_lehrstuhl_id=lehrstuhl.lehrstuhl_id).all()
    # Gets all Student data
    studentData = getStudentInformationList()
    projekte = Projekt.get_all_projekte()
    projekte_lehrstuhl = Projekt.get_projekte_by_lehrstuhl(lehrstuhl_id)

    projekt_betreuer = get_all_projekt_betreuer()
    betreuer_info = []
    for pb in projekt_betreuer:
        betreuer_info.append({
            'Projekt Betreuer ID': pb.pb_id,
            'Mitarbeiter ID': pb.Mitarbeiter_ma_id,
            'Projekt ID': pb.Projekt_projekt_id
        })


    

    # Gets all Locker data
    if current_user.nds in Spinde.get_all_nds():
        lockerData = getLockerInformationHTML()
    else:
        lockerData = ["", ""]

    # Checks if user has reservation or not and set the visibility tags for HTML
    if checkStudentReservation():
        hasReservationVis = ""
        hasNoReservationVis = "hidden"
    else:
        hasReservationVis = "hidden"
        hasNoReservationVis = ""

    # Gets values for the second dropdown
    areaOptions = Spinde.get_group_and_locker(Spinde)

    # Creates the value options for the dropdown as a html string
    areaOptionsHTML = '<option value="Überblick">Überblick</option>'
    for entry in areaOptions:
        ug_og = "UG"
        if entry == 2 or entry == 5:
            ug_og = "OG"
        areaOptionsHTML += '<option value="{}">Bereich {} ({})</option>'.format(
            entry, entry, ug_og
        )

    return render_template(
        "mitarbeiter/mitarbeiter.html",
        studentName=studentData[0],
        studentPrivateData=studentData[1:],
        lockerNumber=lockerData[0],
        lockerInformation=lockerData[1:],
        studentHasReservationVis=hasReservationVis,
        studentHasNoReservationVis=hasNoReservationVis,
        areaOptionsHTML=areaOptionsHTML,
        is_mitarbeiter=is_mitarbeiter,  # Übergeben des Flag für Mitarbeiterstatus an die Vorlage
        mitarbeiter=mitarbeiter,
        alle_mitarbeiter=alle_mitarbeiter,
        projekte=projekte_lehrstuhl,
        betreuer_info=betreuer_info
            )


# MIETEN PAGE START & DYNAMIC UPDATE
# Updates all area dropdowns on the page
@bp_mitarbeiter.route("/_setAreaOptions")
def setAreaOptions():
    # Gets values for the second dropdown
    areaOptions = Spinde.get_group_and_locker(Spinde)

    # Creates the value options for the dropdown as a html string
    areaOptionsHTML = '<option value="Überblick">Überblicke</option>'
    for entry in areaOptions:
        ug_og = "UG"
        if entry == 2 or entry == 5:
            ug_og = "OkkG"
        areaOptionsHTML += '<option value="{}">Bereich {} ({})</option>'.format(
            entry, entry, ug_og
        )

    return jsonify(areaOptionsHTML=areaOptionsHTML)


