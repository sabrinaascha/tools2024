from flask import Blueprint, render_template, jsonify
from flask_login import current_user, login_required
from app.models import Html, Spinde, Superusers , Mitarbeiter
from app.helpers import get_mitarbeiter

# BLUEPRINT "bp_index"
bp_index = Blueprint("bp_index", __name__)


@bp_index.route("/")
def index():
    html = Html.get_html()
    aktuell = html.aktuell
    headline = html.headline
    oeffnungszeiten = html.text
    return render_template(
        "index/index.html",
        aktuell=aktuell,
        headline=headline,
        oeffnungszeiten=oeffnungszeiten,
    )


# BLUEPRINT "bp_layout"
bp_layout = Blueprint("bp_layout", __name__)


# USER INFORMATION
# Checks if user is an admin or not
@bp_layout.route("/_checkUserAdmin")
def checkUserAdmin():
    if current_user.is_authenticated:
        isUserAdmin = current_user.nds in Superusers.get_all_superusers()
        return jsonify(isUserAdmin=isUserAdmin)
    return jsonify(False)


# STUDENT INFORMATION
def getStudentInformationList():
    prename = current_user.vorname
    surname = current_user.nachname
    mail = current_user.mail
    nds = current_user.nds

    studentPrivateInformation = [prename + " " + surname, mail, nds]
    return studentPrivateInformation


# LOCKER INFORMATION
# return a list of all Locker Informations
def getLockerInformationList():
    spind = str(Spinde.get_spind(nds=current_user.nds).nummer)
    gruppe = str(Spinde.get_spind(nds=current_user.nds).gruppe)
    schluessel = str(Spinde.get_spind(nds=current_user.nds).schluessel)
    bezahltBis = str(Spinde.get_spind(nds=current_user.nds).bezahlt_bis)
    # nds = str(Spinde.get_spind(nds=current_user.nds).nds)

    lockerData = [
        spind,
        gruppe,
        schluessel,
        bezahltBis
        # nds
    ]
    return lockerData


# returns the lockerInformation in a HTML format
def getLockerInformationHTML():
    lockerData = getLockerInformationList()

    lockerData[0] = "Spind <b>" + lockerData[0] + "</b>"
    lockerData[1] = "Bereich: <b>" + lockerData[1] + "</b>"
    lockerData[2] = "Schlüssel: <b>" + lockerData[2] + "</b>"
    lockerData[3] = "Bezahlt bis: <b>" + lockerData[3] + "</b>"
    # lockerData[3] = "NDS: <b>" + lockerData[3] + "</b>"

    return lockerData


# BLUEPRINT "bp_profile"
bp_profile = Blueprint("bp_profile", __name__, url_prefix="/profile")


@bp_profile.route("/")
@login_required
def profile():
    mitarbeiter = get_mitarbeiter()
    #is_mitarbeiter = mitarbeiter is not None
    namemitarbeiter = mitarbeiter.nachname
    is_mitarbeiter = Mitarbeiter.query.filter_by(nds=current_user.nds).first() is not None
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

    return render_template(
        "profile/profile.html",
        studentName=studentData[0],
        studentPrivateData=studentData[1:],
        lockerNumber=lockerData[0],
        lockerInformation=lockerData[1:],
        studentHasReservationVis=hasReservationVis,
        studentHasNoReservationVis=hasNoReservationVis,
        is_mitarbeiter=is_mitarbeiter,  # Übergeben des Flag für Mitarbeiterstatus an die Vorlage
        mitarbeiter=mitarbeiter,
        namemitarbeiter=namemitarbeiter
    )


# Checks if user has a reservation or not
def checkStudentReservation():
    # Does the user already have a locker
    if current_user.nds in Spinde.get_all_nds():
        return True
    else:
        return False


# BLUEPRINT "bp_preise"
bp_preise = Blueprint("bp_preise", __name__, url_prefix="/preise")


@bp_preise.route("/")
def preise():
    return render_template("preise/preise.html")


# BLUEPRINT "bp_info"
bp_info = Blueprint("bp_info", __name__)


@bp_info.route("/")
def info():
    return render_template("info/info.html")


@bp_info.route("/impressum")
def impressum():
    return render_template("info/impressum.html")


@bp_info.route("/agb")
def agb():
    return render_template("info/agb.html")


# BLUEPRINT "bp_error"
bp_error = Blueprint("bp_error", __name__)


@bp_error.route("/")
def error():
    return render_template("error/error.html")


@bp_error.route("/no_access")
def not_superuser():
    return render_template("error/no_superuser.html")
