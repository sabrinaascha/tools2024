from flask import Blueprint, render_template, jsonify, request, url_for
from flask_login import current_user, login_required
from app.models import Spinde, Html
from datetime import date
from random import randrange
from .index import (
    getStudentInformationList,
    getLockerInformationHTML,
    checkStudentReservation,
)
import logging
import subprocess


bp_mieten = Blueprint("bp_mieten", __name__)

# Configure the logging module
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@bp_mieten.route("/")
@login_required
def mieten():
    # Gets all Student data
    studentData = getStudentInformationList()

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
        "mieten/mieten.html",
        studentName=studentData[0],
        studentPrivateData=studentData[1:],
        lockerNumber=lockerData[0],
        lockerInformation=lockerData[1:],
        studentHasReservationVis=hasReservationVis,
        studentHasNoReservationVis=hasNoReservationVis,
        areaOptionsHTML=areaOptionsHTML,
    )


# MIETEN PAGE START & DYNAMIC UPDATE
# Updates all area dropdowns on the page
@bp_mieten.route("/_setAreaOptions")
def setAreaOptions():
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

    return jsonify(areaOptionsHTML=areaOptionsHTML)


# Updates all locker dropdowns on the page
@bp_mieten.route("/_updateLockerOptions")
def updateLockerOptions():
    # The value of the first dropdown (selected by the user)
    selectedArea = request.args.get("selectedArea", type=int)

    # Gets values for the second dropdown
    lockerOptions = Spinde.get_group_and_locker(Spinde)[selectedArea]

    # Creates the value options for the dropdown as a html string
    lockerOptionsHTML = ""
    for entry in lockerOptions:
        lockerOptionsHTML += '<option value="{}">Spind {}</option>'.format(entry, entry)

    return jsonify(lockerOptionsHTML=lockerOptionsHTML, selectedArea=selectedArea)


# MIETEN PROCESS
# Renders the confirmation page for the reservation
@bp_mieten.route("/confirm/<selectedArea>/<selectedLocker>")
def confirm(selectedArea, selectedLocker):
    html = Html.get_html()
    headline = html.headline
    oeffnungszeiten = html.text

    # Gets all Student data
    studentData = getStudentInformationList()

    return render_template(
        "mieten/confirm.html",
        selectedArea=selectedArea,
        selectedLocker=selectedLocker,
        headline=headline,
        oeffnungszeiten=oeffnungszeiten,
        studentName=studentData[0],
        studentPrivateData=studentData[1:],
    )


# Gets selected Dropdown values from HTML and gives back a formatted url_for
@bp_mieten.route("/_showConfirmationPage")
def showConfirmationPage():
    # Get values from html
    selectedArea = request.args.get("selectedArea", type=str)
    selectedLocker = request.args.get("selectedLocker", type=str)

    # Creates url_for
    url = url_for(
        "bp_mieten.confirm", selectedArea=selectedArea, selectedLocker=selectedLocker
    )

    return jsonify(url=url)
    # return render_template(
    #     "mieten/confirm.html",
    #     selectedArea=selectedArea,
    #     selectedLocker=selectedLocker,
    # )


@bp_mieten.route("/_confirmReservation")
def confirmReservation():

    # Get values from html
    gruppe = request.args.get("selectedArea", type=str)
    nummer = request.args.get("selectedLocker", type=int)
    selectedDuration = request.args.get("selectedDuration", type=int)


    # get user values
    # rent time
    today = date.today()
    bezahlt_bis = None
    if selectedDuration == 1:
        if today < date(today.year, 3, 1):
            bezahlt_bis = date(today.year, 3, 31)
        if today >= date(today.year, 3, 1) and today < date(today.year, 9, 1):
            bezahlt_bis = date(today.year, 9, 30)
        if today > date(today.year, 9, 1):
            bezahlt_bis = date(today.year + 1, 3, 31)
    if selectedDuration == 2:
        if today < date(today.year, 3, 1):
            bezahlt_bis = date(today.year, 9, 30)
        if today >= date(today.year, 3, 1) and today < date(today.year, 9, 1):
            bezahlt_bis = date(today.year + 1, 3, 31)
        if today > date(today.year, 9, 1):
            bezahlt_bis = date(today.year + 1, 9, 30)
    # other data
    nds = current_user.nds
    matrikelnr = 0
    vorname = current_user.vorname
    nachname = current_user.nachname
    mail = current_user.mail
    passwort = randrange(100000, 999999)
    fak = None
    if selectedDuration == 1:
        saldo = 20
    elif selectedDuration == 2:
        saldo = 25
    else:
        saldo = 0
    bestellt_am = date.today()

    # New Database entry
    Spinde.reserve_locker(
        nummer,
        nds,
        matrikelnr,
        bezahlt_bis,
        vorname,
        nachname,
        mail,
        passwort,
        fak,
        saldo,
        bestellt_am,
    )

    # Check if reservation was succesfull
    isSuccessfull = Spinde.confirm_reservation(nummer, nds)

    # send confirmation email
    if isSuccessfull:
        try:
            email_recipient = current_user.mail
            email_subject = "Wiwi-Spindreservierung Bestaetigung"
            email_body = f"""
            Ihr Passwort zur Schluesselausgabe: {passwort}\n
            Bitte gehen Sie zur Schlüsselausgabe in Raum RWS 109a und geben Sie Ihre NDS Kennung und das Passwort an um den Schlüssel zu erhalten!
            Die Bezahlung erfolgt ausschließlich über die Mensacard im Raum RWS 109a. Sie haben 30 Tage Zeit nach der Reservierung den Schlüssel abzuholen. 
            Nach dieser Frist/Stichtag wird Ihre Buchung storniert und der Spind andersweitig vergeben.
            """
            command = (
                f'echo "{email_body}" | mailx -s "{email_subject}" {email_recipient}'
            )
            subprocess.run(command, shell=True, check=True)
        except Exception as e:
            print(e)

    logger.debug('_confirmReservation reservation finished')

    return jsonify(
        isConfirmed=isSuccessfull, selectedArea=gruppe, selectedLocker=nummer
    )


# EXAMPLE function for canceling the reservation
# @bp_mieten.route("/_cancelReservation")
# def cancelReservation():
#     # Get values from html
#     selectedArea = request.args.get("selectedArea", type=str)
#     selectedLocker = request.args.get("selectedLocker", type=str)
#     Spinde.reset_locker(int(selectedLocker.strip()[6]))
#     isCanceled = True
#     return jsonify(
#         isCanceled=isCanceled, selectedArea=selectedArea, selectedLocker=selectedLocker
#     )
