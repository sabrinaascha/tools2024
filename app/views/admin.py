from flask import Blueprint, render_template, session, flash, redirect, url_for, make_response
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField, DateField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, StopValidation, Email
from app.models import Spinde, Zahlungen, Superusers, Html, db
from datetime import date, datetime
from functools import wraps


bp_admin = Blueprint("bp_admin", __name__, url_prefix="/admin")

# is superuser decorator
def superuser_required(view_func):
    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        if current_user.nds not in Superusers.get_all_superusers():
            return redirect(url_for('bp_error.no_superuser'))
        return view_func(*args, **kwargs)
    return decorated_view

# FORMS

# choose nds form
class NdsForm(FlaskForm):
    nds = StringField('NDS Kennung:',validators=[DataRequired()],render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    submit = SubmitField('Eingabe',render_kw={"class":"w3-button w3-white w3-border","style":"margin-top:5px"})

    # checks if nds is in database
    def validate_nds(form, field):
        if field.data not in str(Spinde.get_all_nds()) or field.data=="0":
            flash("Diese NDS existiert nicht!","nds")
            raise StopValidation('Die gewählte Eingabe existiert nicht!')

# choose spindnummer form       
class NummerForm(FlaskForm):
    nummer = StringField('Spindnummer:' ,validators=[DataRequired()],render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    submit = SubmitField('Eingabe',render_kw={"class":"w3-button w3-white w3-border","style":"margin-top:5px"})

    # checks if nummer is in database
    def validate_nummer(form, field):
        if field.data not in str(Spinde.get_all_nummer()) or field.data=="0":
            flash("Dieser Spind existiert nicht!","nummer")
            raise ValidationError('Die gewählte Eingabe existiert nicht!')
        
# choose a rented spind spindnummer form       
class RentedNummerForm(FlaskForm):
    nummer = StringField('Spindnummer:' ,validators=[DataRequired()],render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    submit = SubmitField('Eingabe',render_kw={"class":"w3-button w3-white w3-border","style":"margin-top:5px"})

    # checks if nummer is in database
    def validate_nummer(form, field):
        if field.data not in str(Spinde.get_all_nummer()) or field.data=="0":
            flash("Dieser Spind existiert nicht!","nummer")
            raise ValidationError('Die gewählte Eingabe existiert nicht!')
        if Spinde.get_spind(nummer=field.data).bestellt_am == None:
            flash("Dieser Spind ist nicht vermietet!","nummer")
            raise ValidationError("Dieser Spind ist nicht vermietet")


# choose matrikelnr form
class MatrikelForm(FlaskForm):
    matrikelnr = StringField('Matrikelnummer:',validators=[DataRequired()],render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    submit = SubmitField('Eingabe',render_kw={"class":"w3-button w3-white w3-border","style":"margin-top:5px"})

    # checks if matrikelnr is in database
    def validate_matrikelnr(form, field):
        if field.data not in str(Spinde.get_all_matrikelnr()) or field.data=="0":
            flash("Diese Matrikelnummer existiert nicht!","matrikelnr")
            raise ValidationError('Die gewählte Eingabe existiert nicht!')

# choose spind schluessel form        
class SchluesselForm(FlaskForm):
    schluessel = StringField('Schlüsselnummer:',validators=[DataRequired()],render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    submit = SubmitField('Eingabe',render_kw={"class":"w3-button w3-white w3-border","style":"margin-top:5px"})

    # checks if schluessel is in database
    def validate_schluessel(form, field):
        schluessel = field.data
        if not schluessel.isdigit() or int(schluessel) not in Spinde.get_all_schluessel() or schluessel=="0":
            flash("Dieser Schlüssel existiert nicht!", "schluessel")
            raise ValidationError('Die gewählte Eingabe existiert nicht!')

# choose a rented spind schluessel form        
class RentedSchluesselForm(FlaskForm):
    schluessel = StringField('Schlüsselnummer:',validators=[DataRequired()],render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    submit = SubmitField('Eingabe',render_kw={"class":"w3-button w3-white w3-border","style":"margin-top:5px"})

    # checks if schluessel is in database
    def validate_schluessel(form, field):
        schluessel = field.data
        if not schluessel.isdigit() or int(schluessel) not in Spinde.get_all_schluessel() or schluessel=="0":
            flash("Dieser Schlüssel existiert nicht!", "schluessel")
            raise ValidationError('Die gewählte Eingabe existiert nicht!')
        if Spinde.get_spind(schluessel=field.data).bestellt_am == None:
            flash("Dieser Spind ist nicht vermietet!","schluessel")
            raise ValidationError("Dieser Spind ist nicht vermietet")

# enter nds and the passwort form        
class AusgabeForm(FlaskForm):
    nds = StringField('NDS Kennung:',validators=[DataRequired()],render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    schluessel_passwort = StringField('Schlüssel-Passwort:',render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    submit = SubmitField('Weiter...',render_kw={"class":"w3-button w3-white w3-border","style":"margin-top:5px"})

    # checks if nds is in database
    def validate_nds(form, nds):
        if nds.data not in Spinde.get_all_nds():
            flash("Diese NDS existiert nicht!","nds")
            raise ValidationError('Die gewählte Eingabe existiert nicht!')
        if Spinde.get_spind(nds=nds.data).schluessel_ausgegeben != "0":
            flash("Für diesen Spind wurde der Schlüssel schon ausgegeben","nds")
            raise ValidationError('Für diesen Spind wurde der Schlüssel schon ausgegeben')

# enter a email and submit form
class MailSubmitForm(FlaskForm):
    mail = StringField('E-Mail Adresse:', validators=[DataRequired(), Email()],render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    submit = SubmitField("Betrag bezahlt und und Schlüssel übereicht",render_kw={"class":"w3-button w3-white w3-border","style":"margin-top:5px"})

# select how long you want to extend your rent form
class VerlaengernForm(FlaskForm):
    bis = SelectField('Miete verlängern bis:', choices=[], validate_choice=False,render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:15%"})
    submit = SubmitField("Verlängern",render_kw={"class":"w3-button w3-white w3-border","style":"margin-top:5px"})

# checkbox form
class CheckboxForm(FlaskForm):
    checkbox = BooleanField("Checkbox",default=False)
    submit = SubmitField("Miete beenden",render_kw={"class":"w3-button w3-white w3-border","style":"margin-top:5px"})

# spind_sperren form
class SperrenForm(FlaskForm):
    submit = SubmitField("Sperren",render_kw={"class":"w3-button w3-white w3-border","style":"margin-top:5px"})

# spind_freigeben form
class FreigebenForm(FlaskForm):
    submit = SubmitField("Freigeben",render_kw={"class":"w3-button w3-white w3-border","style":"margin-top:5px"})

# schluessel_eintragen form
class SchluesselEintragenForm(FlaskForm):
    schluessel = StringField("Neuer Schlüssel", validators=[DataRequired()],render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    submit = SubmitField("Speichern",render_kw={"class":"w3-button w3-white w3-border","style":"margin-top:5px"})

    # checks if schluessel is a integer
    def validate_schluessel(form, schluessel):
        if isinstance(schluessel.data, int):
            raise ValidationError('Der neue Schlüssel muss eine Zahl sein!')

# change user data form 
class AendernForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()],render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    vorname = StringField("Vorname", validators=[DataRequired()],render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    schluessel = StringField("Schlüssel", validators=[DataRequired()],render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    nds = StringField("NDS", validators=[DataRequired()],render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    matrikelnr = StringField("Matrikelnummer",render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    info = StringField("Info",render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    mail = StringField("Email", validators=[DataRequired()],render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    fak = StringField("Fakultät",render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    submit = SubmitField("Speichern",render_kw={"class":"w3-button w3-white w3-border","style":"margin-top:5px"})

    def apply_defaults(self, spind):
        self.name.default= spind.nachname
        self.vorname.default = spind.vorname
        self.schluessel.default = spind.schluessel
        self.nds.default = spind.nds
        self.matrikelnr.default = spind.matrikelnr
        self.info.default = spind.info
        self.mail.default = spind.mail
        self.fak.default = spind.fak
        self.process()

# choose spind form    
class SpindWaehlenForm(FlaskForm):
    nummer = SelectField('Neuen Spind wählen:', choices=[], validate_choice=False,render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    submit = SubmitField("Umbuchen",render_kw={"class":"w3-button w3-white w3-border","style":"margin-top:5px"})

# choose a time period form
class TimePeriodForm(FlaskForm):
    von = DateField("Von:")
    bis = DateField("Bis:")
    submit = SubmitField("Abfragen",render_kw={"class":"w3-button w3-white w3-border","style":"margin-top:5px"})

# html entries form
class OeffnungszeitenInfoForm(FlaskForm):
    headline = StringField("Öffnungszeiten Überschrift",render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%"})
    text = TextAreaField("Öffnungszeiten",render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%;height:125px"})
    aktuell = TextAreaField("Infotext",render_kw={"class":"w3-input w3-border w3-round","type":"text","style":"width:25%;height:175px"})
    submit = SubmitField("Speichern",render_kw={"class":"w3-button w3-white w3-border","style":"margin-top:5px"})

# ROUTES
    
# admin start page
@bp_admin.route("/")
@login_required
@superuser_required
def admin():
    # Statistics
    rented_lockers_amount = Spinde.get_rented_lockers().count()
    rented_unpayed_lockers_amount = Spinde.get_unpayed_lockers().count()
    free_lockers_amount = Spinde.get_free_lockers().count()
    blocked_lockers_amount = Spinde.get_blocked_lockers().count()
    all_lockers_amount = Spinde.get_all_locker().count()
    not_picked_up_amount = Spinde.get_not_picked_up_lockers().count()

    return render_template(
        "admin/admin.html",
        rented_lockers_amount=rented_lockers_amount, 
        free_lockers_amount=free_lockers_amount, 
        blocked_lockers_amount=blocked_lockers_amount, 
        rented_unpayed_lockers_amount=rented_unpayed_lockers_amount,
        all_lockers_amount=all_lockers_amount,
        not_picked_up_amount=not_picked_up_amount
        )

@bp_admin.route("/unbezahlte_spinde")
@login_required
@superuser_required
def admin_unbezahlte_spinde():
    header = "Unbezahlte/Abgelaufene Spinde"
    rented_unpayed_lockers = Spinde.get_unpayed_lockers().order_by(Spinde.bezahlt_bis.desc())
    return render_template("admin/liste_statistik.html", header=header, lockers=rented_unpayed_lockers)

@bp_admin.route("/nicht_abgeholte_spinde")
@login_required
@superuser_required
def admin_nicht_abgeholte_spinde():
    header = "Nicht abgeholte Spinde"
    not_picked_up = Spinde.get_not_picked_up_lockers().order_by(Spinde.bestellt_am.desc())
    return render_template("admin/liste_statistik.html", header=header, lockers=not_picked_up)


# ADMIN FUNCTIONS
"""
Öffnungszeiten und Info

This function handles the input for the öffnungszeiten and the info field.
!!! The function has to be split into two functions so the default values work

DATABASE ENTRIES:
Update Html
"""
@bp_admin.route("/oeffnungszeiten_und_info", methods=['GET','POST'])
@login_required
@superuser_required
def admin_oeffnungszeiten_und_info():
    # create forms
    oeffnungszeiten_info_form = OeffnungszeitenInfoForm()
    # get current html
    html = Html.get_html()
    # assign default values
    oeffnungszeiten_info_form.text.default = html.text
    oeffnungszeiten_info_form.headline.default = html.headline
    oeffnungszeiten_info_form.aktuell.default = html.aktuell
    oeffnungszeiten_info_form.process()
    
    return render_template("admin/oeffnungszeiten_und_info/auswahl.html", 
                           oeffnungszeiten_info_form=oeffnungszeiten_info_form,
                           )

@bp_admin.route("/oeffnungszeiten_und_info_bestaetigt", methods=['GET','POST'])
@login_required
@superuser_required
def admin_oeffnungszeiten_und_info_bestaetigt():
    # create forms
    oeffnungszeiten_info_form = OeffnungszeitenInfoForm()
    # get current html
    html = Html.get_html()
    # submit button pressed
    if oeffnungszeiten_info_form.validate_on_submit():
        # get data and update database
        html.headline = oeffnungszeiten_info_form.headline.data
        html.text = oeffnungszeiten_info_form.text.data
        html.aktuell = oeffnungszeiten_info_form.aktuell.data
        db.session.commit()
    return render_template("admin/oeffnungszeiten_und_info/bestaetigt.html")
"""
SCHLUESSEL_AUSGEBEN

The schluessel_ausgeben functions handle the process of giving a student the key for a locker and receiving the money

DATABASE ENTRIES:
Update Spinde
Insert Zahlungen

"""
@bp_admin.route("/schluessel_ausgeben", methods=['GET','POST'])
@login_required
@superuser_required
def admin_schluessel_ausgeben():
     # create form for entering nds and schluessel
    ausgabe_form = AusgabeForm()
    # create form for email and submit
    mail_submit_form = MailSubmitForm()
    # define spind and key
    spind = None
    correct_key = None
    # submit button pressed
    if ausgabe_form.validate_on_submit():
        # select the correct locker depending on the submitted form
        spind = Spinde.get_spind(nds=ausgabe_form.nds.data)
        # checks if the correct schluessel is given
        correct_key = spind.passwort==ausgabe_form.schluessel_passwort.data
        # put spind nummer in a session, so it can accessed later
        session["spindnummer_ausgeben"]=spind.nummer
        # give the mail_submit_form the current mail adress as default value
        mail_submit_form.mail.default = spind.mail
        mail_submit_form.process()
        # how much money
        miete = spind.saldo - 10
        return render_template("admin/schluessel_ausgeben/bestaetigen.html", miete=miete, correct_key=correct_key, spind=spind, mail_submit_form=mail_submit_form)
    return render_template("admin/schluessel_ausgeben/auswahl.html", ausgabe_form=ausgabe_form)

@bp_admin.route("/schluessel_ausgeben_bestaetigt", methods=['GET','POST'])
@login_required
@superuser_required
def admin_schluessel_ausgeben_bestaetigt():
    # create form
    mail_submit_form = MailSubmitForm()
    # submit button pressed
    if mail_submit_form.validate_on_submit():
        # get spind from session
        spind = Spinde.get_spind(nummer=session["spindnummer_ausgeben"])
        session.pop("spindnummer_ausgeben", None)
        # get mail from form
        mail = mail_submit_form.mail.data
        # Insert zahlungen
        Zahlungen.new_entry(spind.nds, 'Pfandeinnahme', spind.nummer, 10)
        Zahlungen.new_entry(spind.nds, 'Anmietung', spind.nummer, spind.saldo)
        # Update spinde
        spind.mail = mail
        spind.schluessel_ausgegeben = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        spind.saldo = 0
        db.session.commit()
    return render_template("admin/schluessel_ausgeben/bestaetigt.html")

"""
SPINDMIETE_VERLAENGERN

The spindmiete_verlaengern functions handle the process of extending the rent for a locker

DATABASE ENTRIES:
Update Spinde
Insert Zahlungen

"""
@bp_admin.route("/spindmiete_verlaengern", methods=['GET','POST'])
@login_required
@superuser_required
def admin_spindmiete_verlaengern():
    # create forms for choosing locker
    nds_form = NdsForm()
    nummer_form = RentedNummerForm()
    # creating form for choosing duration
    verlaengern_form = VerlaengernForm()
    # defining spind
    spind = None
    # submit button pressed
    if nds_form.validate_on_submit() or nummer_form.validate_on_submit():
        # select the correct locker depending on the submitted form
        if nds_form.nds.data:
            spind = Spinde.get_spind(nds=nds_form.nds.data)
        if nummer_form.nummer.data:
            spind = Spinde.get_spind(nummer=nummer_form.nummer.data)
        # put spind nummer in a session, so it can accessed later
        session["spindnummer_verlaengern"]=spind.nummer
        # creating dropdown dates depending on current 'bezahlt_bis'
        current_bis = Spinde.get_current_bezahlt_bis(spind.nummer)
        # define the new possible 'bezahlt_bis' dates
        semester_1 = None
        semester_2 = None
        if current_bis.month==3:
            semester_1 = date(current_bis.year,9,30)
            semester_2 = date(current_bis.year+1,3,31)
        if current_bis.month==9:
            semester_1 = date(current_bis.year+1,3,31)
            semester_2 = date(current_bis.year+1,9,30)
        # creating list for dropdown menu
        choices = [(semester_1,f'{semester_1} (1 Semester)'),(semester_2,f'{semester_2} (2 Semester)')]
        verlaengern_form.bis.choices = choices
        return render_template("admin/spindmiete_verlaengern/bestaetigen.html", verlaengern_form=verlaengern_form, spind=spind)
    return render_template("admin/spindmiete_verlaengern/auswahl.html", nds_form=nds_form, nummer_form=nummer_form)

@bp_admin.route("/spindmiete_verlaengern/bestaetigt", methods=['GET','POST'])
@login_required
@superuser_required
def admin_spindmiete_verlaengern_bestaetigt():
    verlaengern_form = VerlaengernForm()
    # submit button is pressed
    if verlaengern_form.validate_on_submit():
        # get spind from session
        spind = Spinde.get_spind(nummer=session['spindnummer_verlaengern'])
        session.pop("spindnummer_verlaengern", None)
        # convert date from the form from string to date format
        semester = datetime.strptime(verlaengern_form.bis.data, '%Y-%m-%d')
        # calculate the price depending on the semester amount
        if semester.month==spind.bezahlt_bis.month:
            semester_anzahl = 15
        else:
            semester_anzahl = 10    
        # update spinde
        spind.bezahlt_bis = semester
        # insert zahlung
        Zahlungen.new_entry(spind.nds, 'Verlängerung', spind.nummer, semester_anzahl)
        # commit changes
        db.session.commit()
    return render_template("admin/spindmiete_verlaengern/bestaetigt.html")

"""
MIETE_BEENDEN

The miete_beenden functions handle the process of ending the rent for a locker

DATABASE ENTRIES:
Update Spinde
Insert Zahlungen

"""
@bp_admin.route("/miete_beenden", methods=['GET','POST'])
@login_required
@superuser_required
def admin_miete_beenden():
    # create forms
    schluessel_form = RentedSchluesselForm()
    nummer_form = RentedNummerForm()
    checkbox_form = CheckboxForm()
    # define spind
    spind = None
    # submit button pressed
    if schluessel_form.validate_on_submit() or nummer_form.validate_on_submit():
        # select the correct locker depending on the submitted form
        if schluessel_form.schluessel.data:
            spind = Spinde.get_spind(nds=schluessel_form.schluessel.data)
        if nummer_form.nummer.data:
            spind = Spinde.get_spind(nummer=nummer_form.nummer.data)
        # put spind nummer in a session, so it can accessed later
        session["spindnummer_beenden"]=spind.nummer
        return render_template("admin/miete_beenden/bestaetigen.html", spind=spind, checkbox_form=checkbox_form)
    return render_template("admin/miete_beenden/auswahl.html", schluessel_form=schluessel_form, nummer_form=nummer_form)

@bp_admin.route("/miete_beenden_bestaetigt", methods=['GET','POST'])
@login_required
@superuser_required
def admin_miete_beenden_bestaetigt():
    # create checkbox form
    checkbox_form = CheckboxForm()
    # submit button pressed
    if checkbox_form.validate_on_submit():
        # get spind from session
        spind = Spinde.get_spind(nummer=session['spindnummer_beenden'])
        session.pop("spindnummer_beenden", None)
        # insert zahlung
        if checkbox_form.checkbox.data==False:
            Zahlungen.new_entry(spind.nds, "Pfandrückzahlung", spind.nummer, -10)
        # update old locker
        Spinde.reset_locker(spind.nummer)
    return render_template("admin/miete_beenden/bestaetigt.html")

"""
NUTZERDATEN_EINSEHEN

With the nutzerdaten_einsehen functions you can see the data of a user

"""
@bp_admin.route("/nutzerdaten_einsehen", methods=['GET','POST'])
@login_required
@superuser_required
def admin_nutzerdaten_einsehen():
    # create forms
    schluessel_form = RentedSchluesselForm()
    nummer_form = RentedNummerForm()
    nds_form = NdsForm()
    matrikel_form = MatrikelForm()
    # submit button pressed
    if schluessel_form.validate_on_submit() or nummer_form.validate_on_submit() or nds_form.validate_on_submit() or matrikel_form.validate_on_submit():
        # define spind
        spind = None
        # select the correct locker depending on the submitted form
        if nds_form.nds.data:
            spind = Spinde.get_spind(nds=nds_form.nds.data)
        if nummer_form.nummer.data:
            spind = Spinde.get_spind(nummer=nummer_form.nummer.data)
        if schluessel_form.schluessel.data:
            spind = Spinde.get_spind(schluessel=schluessel_form.schluessel.data)
        if matrikel_form.matrikelnr.data:
            spind = Spinde.get_spind(matrikelnr=matrikel_form.matrikelnr.data)
        return render_template("admin/nutzerdaten_einsehen/nutzer.html", spind=spind)
    return render_template("admin/nutzerdaten_einsehen/auswahl.html", schluessel_form=schluessel_form, nummer_form=nummer_form, nds_form=nds_form, matrikel_form=matrikel_form)

"""
NUTZERDATEN_AENDERN

The nutzerdaten_aendern functions can change user data

DATABASE ENTRIES:
Update Spinde

"""
@bp_admin.route("/nutzerdaten_aendern", methods=['GET','POST'])
@login_required
@superuser_required
def admin_nutzerdaten_aendern():
    # create forms
    schluessel_form = RentedSchluesselForm()
    nummer_form = RentedNummerForm()
    nds_form = NdsForm()
    matrikel_form = MatrikelForm()
    aendern_form = AendernForm()
    # define spind
    spind = None
    # submit button pressed
    if schluessel_form.validate_on_submit() or nummer_form.validate_on_submit() or nds_form.validate_on_submit() or matrikel_form.validate_on_submit():
        # select the correct locker depending on the submitted form
        if nds_form.nds.data:
            spind = Spinde.get_spind(nds=nds_form.nds.data)
        if nummer_form.nummer.data:
            spind = Spinde.get_spind(nummer=nummer_form.nummer.data)
        if schluessel_form.schluessel.data:
            spind = Spinde.get_spind(schluessel=schluessel_form.schluessel.data)
        if matrikel_form.matrikelnr.data:
            spind = Spinde.get_spind(matrikelnr=matrikel_form.matrikelnr.data)
        # put spind nummer in a session, so it can accessed later
        session["spindnummer_aendern"]=spind.nummer
        # set default values for aendern_form
        aendern_form.apply_defaults(spind)
        return render_template("admin/nutzerdaten_aendern/bestaetigen.html", aendern_form=aendern_form ,spind=spind)
            
    return render_template("admin/nutzerdaten_aendern/auswahl.html", schluessel_form=schluessel_form, nummer_form=nummer_form, nds_form=nds_form, matrikel_form=matrikel_form)
                           
@bp_admin.route("/nutzerdaten_aendern_bestaetigt", methods=['GET','POST'])
@login_required
@superuser_required
def admin_nutzerdaten_aendern_bestaetigt():
    # create form
    aendern_form = AendernForm()
    # get spind from session
    spind = Spinde.get_spind(nummer=session['spindnummer_aendern'])
    session.pop("spindnummer_aendern", None)
    # submit button pressed
    if aendern_form.validate_on_submit():
        # database entry
        spind.nachname = aendern_form.name.data
        spind.vorname = aendern_form.vorname.data
        spind.schluessel = int(aendern_form.schluessel.data)
        spind.nds = aendern_form.nds.data
        spind.matrikelnr = int(aendern_form.matrikelnr.data)
        spind.info = aendern_form.info.data
        spind.mail = aendern_form.mail.data
        spind.fak = aendern_form.fak.data
        db.session.commit()
    return render_template("admin/nutzerdaten_aendern/bestaetigt.html")

"""
SPIND_SPERREN_FREIGEBEN

The spind_sperren_freigeben functions can lock or free a locker

DATABASE ENTRIES:
Update Spinde

"""
@bp_admin.route("/spind_sperren_freigeben", methods=['GET','POST'])
@login_required
@superuser_required
def admin_spind_sperren_freigeben():
    # create forms
    schluessel_form = SchluesselForm()
    nummer_form = NummerForm()
    submit_form = None
    # define spind
    spind = None
    # get all blocked lockers
    blocked_lockers = Spinde.get_blocked_lockers()
    # submit button pressed
    if schluessel_form.validate_on_submit() or nummer_form.validate_on_submit():
        # select the correct locker depending on the submitted form
        if schluessel_form.schluessel.data:
            spind = Spinde.get_spind(schluessel=schluessel_form.schluessel.data)
        if nummer_form.nummer.data:
            spind = Spinde.get_spind(nummer=nummer_form.nummer.data)
        # put spind nummer in a session, so it can accessed later
        session["spindnummer_sperren"]=spind.nummer
        # check if the function should be sperren or freigeben
        if spind.gesperrt==0:
            submit_form=SperrenForm()
        else:
            submit_form=FreigebenForm()
        return render_template("admin/spind_sperren_freigeben/bestaetigen.html", spind=spind, submit_form=submit_form)
    return render_template("admin/spind_sperren_freigeben/auswahl.html", schluessel_form=schluessel_form, nummer_form=nummer_form, blocked_lockers=blocked_lockers)

@bp_admin.route("/spind_sperren_freigeben_bestaetigt", methods=['GET','POST'])
@login_required
@superuser_required
def admin_spind_sperren_freigeben_bestaetigt():
    # get spind from session
    spind = Spinde.get_spind(nummer=session['spindnummer_sperren'])
    session.pop("spindnummer_sperren", None)
    # create submit form
    submit_form = None
    if spind.gesperrt==0:
        submit_form=SperrenForm()
    else:
        submit_form=FreigebenForm()
    # submit button pressed
    if submit_form.validate_on_submit():
        # update database
        if spind.gesperrt==0:
            spind.gesperrt = 1
        else:
            spind.gesperrt = 0
        db.session.commit()
    return render_template("admin/spind_sperren_freigeben/bestaetigt.html")

"""
SCHLUESSEL_AUSTAUSCHEN

The schluessel_austauschen functions can change the schluessel of a spind

DATABASE ENTRIES:
Update Spinde

"""
@bp_admin.route("/schluessel_austauschen", methods=['GET','POST'])
@login_required
@superuser_required
def admin_schluessel_austauschen():
     # create forms
    nummer_form = NummerForm()
    schluessel_eintragen_form = SchluesselEintragenForm()
    # define spind
    spind = None
    # submit button pressed
    if nummer_form.validate_on_submit():
        # get locker
        spind = Spinde.get_spind(nummer=nummer_form.nummer.data)
        # put spind nummer in a session, so it can accessed later
        session["spindnummer_austauschen"]=spind.nummer
        return render_template("admin/schluessel_austauschen/bestaetigen.html", spind=spind, schluessel_eintragen_form=schluessel_eintragen_form)
    return render_template("admin/schluessel_austauschen/auswahl.html", nummer_form=nummer_form)

@bp_admin.route("/schluessel_austauschen_bestaetigt", methods=['GET','POST'])
@login_required
@superuser_required
def admin_schluessel_austauschen_bestaetigt():
    # get spind from session
    spind = Spinde.get_spind(nummer=session['spindnummer_austauschen'])
    session.pop("spindnummer_sperren", None)
    # create submit form
    schluessel_eintragen_form = SchluesselEintragenForm()
    # submit button pressed
    if schluessel_eintragen_form.validate_on_submit():
        # database entry
        spind.schluessel = schluessel_eintragen_form.schluessel.data
        db.session.commit()
    return render_template("admin/schluessel_austauschen/bestaetigt.html")

"""
STUDENT_UMBUCHEN

The student_umbuchen functions handle the process of giving a student a different locker

DATABASE ENTRIES:
Update Spinde

"""
@bp_admin.route("/student_umbuchen", methods=['GET','POST'])
@login_required
@superuser_required
def admin_student_umbuchen():
    # create forms
    nds_form = NdsForm()
    nummer_form = RentedNummerForm()
    spind_waehlen_form = SpindWaehlenForm()
    spind_waehlen_form.nummer.choices = Spinde.get_nds_of_free_lockers()
    # define spind
    spind = None
    # submit button pressed
    if nds_form.validate_on_submit() or nummer_form.validate_on_submit():
        # select the correct locker depending on the submitted form
        if nds_form.nds.data:
            spind = Spinde.get_spind(nds=nds_form.nds.data)
        if nummer_form.nummer.data:
            spind = Spinde.get_spind(nummer=nummer_form.nummer.data)
        # put spind nummer in a session, so it can accessed later
        session["spindnummer_umbuchen"]=spind.nummer
        return render_template("admin/student_umbuchen/bestaetigen.html", spind=spind, spind_waehlen_form=spind_waehlen_form)
    return render_template("admin/student_umbuchen/auswahl.html", nds_form=nds_form, nummer_form=nummer_form)

@bp_admin.route("/student_umbuchen_bestaetigt", methods=['GET','POST'])
@login_required
@superuser_required
def admin_student_umbuchen_bestaetigt():
    # get spind from session
    old_spind = Spinde.get_spind(nummer=session['spindnummer_umbuchen']) # the session will not be deleted here, so it can be used in student_umbuchen_gesperrt
    # create forms
    spind_waehlen_form = SpindWaehlenForm()
    sperren_form = SperrenForm()
    # submit button pressed
    if spind_waehlen_form.validate_on_submit():
        # get new spind
        new_spind = Spinde.get_spind(nummer=int(spind_waehlen_form.nummer.data))
        # change new spind
        new_spind.nds = old_spind.nds
        new_spind.matrikelnr = old_spind.matrikelnr
        new_spind.bezahlt_bis = old_spind.bezahlt_bis
        new_spind.vorname = old_spind.vorname
        new_spind.nachname = old_spind.nachname
        new_spind.mail = old_spind.mail
        new_spind.passwort = old_spind.passwort
        new_spind.schluessel_ausgegeben = old_spind.schluessel_ausgegeben
        new_spind.fak = old_spind.fak
        new_spind.saldo = old_spind.saldo
        new_spind.bestellt_am = old_spind.bestellt_am
        # change old spind
        old_spind.nds = '0'
        old_spind.matrikelnr = '0'
        old_spind.bezahlt_bis = None
        old_spind.vorname = None
        old_spind.nachname = None
        old_spind.mail = None
        old_spind.passwort = None
        old_spind.schluessel_ausgegeben = "0"
        old_spind.fak = None
        old_spind.saldo = 0
        old_spind.bestellt_am = None
        # commit
        db.session.commit()
    return render_template("admin/student_umbuchen/bestaetigt.html", sperren_form = sperren_form)

@bp_admin.route("/student_umbuchen_gesperrt", methods=['GET','POST'])
@login_required
@superuser_required
def admin_student_umbuchen_gesperrt():
    # create form
    sperren_form = SperrenForm()
    # get spind from session
    old_spind = Spinde.get_spind(nummer=session['spindnummer_umbuchen'])
    session.pop("spindnummer_umbuchen", None)
    # submit button pressed
    if sperren_form.validate_on_submit():
        old_spind.gesperrt = 1
        db.session.commit()
    return render_template("admin/student_umbuchen/gesperrt.html")


"""
ZAHLUNGEN_EINSEHEN

The zahlungen einsehen function handles the process of showing the payments

"""
@bp_admin.route("/zahlungen_einsehen", methods=['GET','POST'])
@login_required
@superuser_required
def admin_zahlungen_einsehen():
    # create form
    time_period_form = TimePeriodForm()
    # submit button pressed
    if time_period_form.validate_on_submit():
        von = time_period_form.von.data
        bis = time_period_form.bis.data
        zahlungen = Zahlungen.get_von_bis(von, bis)
        return render_template("admin/zahlungen_einsehen/liste.html", zahlungen=zahlungen)
    return render_template("admin/zahlungen_einsehen/auswahl.html", time_period_form=time_period_form)


"""
DATEN_EXPORTIEREN

With the csv_export function you can download the spind data as csv

"""
@bp_admin.route("/daten_exportieren")
@login_required
@superuser_required
def csv_export():
    # get all lockers
    data = Spinde.get_all_locker()
    # create the csv
    csv_data = "nummer,gruppe,schluessel,nds,matrikelnr,bezahlt_bis,gesperrt,vorname,nachname,mail,passwort,schluessel_ausgegeben,fak,saldo,bestellt_am,info"
    for entry in data:
        csv_data += f"\n{entry.nummer},{entry.gruppe},{entry.schluessel},{entry.nds},{entry.matrikelnr},{entry.bezahlt_bis},{entry.gesperrt},{entry.vorname},{entry.nachname},{entry.mail},{entry.passwort},{entry.schluessel_ausgegeben},{entry.fak},{entry.saldo},{entry.bestellt_am},{entry.info}"
    # create flask answer
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = "attachment; filename=spinde.csv" 
    response.headers["Content-type"] = "text/csv"
    return response       