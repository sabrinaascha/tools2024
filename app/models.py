from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, timedelta

db = SQLAlchemy()

# Tables
class Art(db.Model):
    art_id = db.Column(db.Integer, primary_key=True)
    art_typ = db.Column(db.String(50))


class Projekt(db.Model):
    __tablename__ = 'projekt'
    projekt_id = db.Column(db.Integer, primary_key=True)
    titel = db.Column(db.String(100))
    beschreibung = db.Column(db.String(200))
    max_anzahl = db.Column(db.Integer)
    studiengang = db.Column(db.Integer)
    fach = db.Column(db.Integer)
    semester = db.Column(db.Integer)
    neu = db.Column(db.Integer)
    Art_art_id = db.Column(db.Integer, db.ForeignKey('art.art_id'), nullable=False)
    Lehrstuhl_lehrstuhl_id = db.Column(db.Integer, db.ForeignKey('lehrstuhl.lehrstuhl_id'), nullable=False)

    art = db.relationship('Art', backref=db.backref('projekte', lazy=True))
    lehrstuhl = db.relationship('Lehrstuhl', backref=db.backref('projekte', lazy=True))

    #betreuer = db.relationship('Projekt_Betreuer', backref=db.backref('projekt', lazy='subquery'))
    betreute_projekte = db.relationship('Projekt_Betreuer', backref='projekt', lazy=True)


    def __init__(self, titel, beschreibung, max_anzahl, studiengang, fach, semester, neu, Art_art_id):
        self.titel = titel
        self.beschreibung = beschreibung
        self.max_anzahl = max_anzahl
        self.studiengang = studiengang
        self.fach = fach
        self.semester = semester
        self.neu = neu
        self.Art_art_id = Art_art_id
        self.Lehrstuhl_lehrstuhl_id = Lehrstuhl_lehrstuhl_id
        self.betreute_projekte = []

    def show_all_values(self):
        return Projekt
    
    def get_all_projekte():
        query = Projekt.query
        return query  

    @staticmethod
    def get_projekte_by_lehrstuhl(lehrstuhl_id):
        return Projekt.query.filter_by(Lehrstuhl_lehrstuhl_id=lehrstuhl_id).all()
            

class Lehrstuhl(db.Model):
    __tablename__ = 'lehrstuhl'
    
    lehrstuhl_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    homepage = db.Column(db.String(50))

    def __init__(self, name, homepage):
        self.name = name
        self.homepage = homepage
        

class Mitarbeiter(db.Model):
    __tablename__ = 'mitarbeiter'
    
    ma_id = db.Column(db.Integer, primary_key=True)
    vorname = db.Column(db.String(20))
    nachname = db.Column(db.String(20))
    nds = db.Column(db.String(10))
    email = db.Column(db.String(30))
    rolle = db.Column(db.Integer)
    Lehrstuhl_lehrstuhl_id = db.Column(db.Integer, db.ForeignKey('lehrstuhl.lehrstuhl_id'), nullable=False)
    lehrstuhl = db.relationship('Lehrstuhl', backref=db.backref('mitarbeiter', lazy=True))

    betreute_projekte = db.relationship('Projekt_Betreuer', backref=db.backref('betreuer', lazy='subquery'))

        
    def __init__(self, vorname, nachname, nds, email, rolle, Lehrstuhl_lehrstuhl_id):
        self.vorname = vorname
        self.nachname = nachname
        self.nds = nds
        self.email = email
        self.rolle = rolle
        self.Lehrstuhl_lehrstuhl_id = Lehrstuhl_lehrstuhl_id  

    @staticmethod
    def get_all_Mitarbeiter():
        return Mitarbeiter.query.all()

    def get_mitarbeiter(nds=""):
        if nds != "":
            mitarbeiter = Mitarbeiter.query.filter_by(nds=nds).first()
        return mitarbeiter 

    def get_all_nds():
        query = Mitarbeiter.query.filter(Mitarbeiter.nds != "0").all()
        all_nds = []
        for entry in query:
            all_nds.append(entry.nds)
        return all_nds

class Projekt_Betreuer(db.Model):
    __tablename__ = 'projekt_betreuer'
    pb_id = db.Column(db.Integer, primary_key=True)
    Mitarbeiter_ma_id = db.Column(db.Integer, db.ForeignKey('mitarbeiter.ma_id'))
    Projekt_projekt_id = db.Column(db.Integer, db.ForeignKey('projekt.projekt_id'))    

    __table_args__ = {'extend_existing': True}

def get_all_projekt_betreuer():
    betreuer = Projekt_Betreuer.query.all()
    return betreuer


class Spinde(db.Model):
    nummer = db.Column(db.Integer, primary_key=True)
    gruppe = db.Column(db.Integer)
    schluessel = db.Column(db.Integer)
    nds = db.Column(db.String(8))
    matrikelnr = db.Column(db.Integer)
    bezahlt_bis = db.Column(db.Date)
    gesperrt = db.Column(db.Integer)
    vorname = db.Column(db.String(50))
    nachname = db.Column(db.String(50))
    mail = db.Column(db.String(100))
    passwort = db.Column(db.String(6))
    schluessel_ausgegeben = db.Column(db.String(20))  # in database it's varchar(20)
    fak = db.Column(db.String(100))
    saldo = db.Column(db.Integer)
    bestellt_am = db.Column(db.Date)
    info = db.Column(db.String(200))

    def __init__(
        self,
        nummer,
        gruppe,
        schluessel,
        nds,
        matrikelnr,
        bezahlt_bis,
        gesperrt,
        vorname,
        nachname,
        mail,
        passwort,
        schluessel_ausgegeben,
        fak,
        saldo,
        bestellt_am,
        info,
    ):
        self.nummer = nummer
        self.gruppe = gruppe
        self.schluessel = schluessel
        self.nds = nds
        self.matrikelnr = matrikelnr
        self.bezahlt_bis = bezahlt_bis
        self.gesperrt = gesperrt
        self.vorname = vorname
        self.nachname = nachname
        self.mail = mail
        self.passwort = passwort
        self.schluessel_ausgegeben = schluessel_ausgegeben
        self.fak = fak
        self.saldo = saldo
        self.bestellt_am = bestellt_am
        self.info = info

    def show_all_values(self):
        return Spinde
    
    def get_all_locker():
        query = Spinde.query
        return query

    def add_data_to_locker(
        nummer,
        gruppe,
        schluessel,
        nds,
        matrikelnr,
        bezahlt_bis,
        gesperrt,
        vorname,
        nachname,
        mail,
        passwort,
        schluessel_ausgegeben,
        fak,
        saldo,
        bestellt_am,
        info,
    ):
        new_entry = Spinde(
            nummer=nummer,
            gruppe=gruppe,
            schluessel=schluessel,
            nds=nds,
            matrikelnr=matrikelnr,
            bezahlt_bis=bezahlt_bis,
            gesperrt=gesperrt,
            vorname=vorname,
            nachname=nachname,
            mail=mail,
            passwort=passwort,
            schluessel_ausgegeben=schluessel_ausgegeben,
            fak=fak,
            saldo=saldo,
            bestellt_am=bestellt_am,
            info=info,
        )
        db.session.add(new_entry)
        db.session.commit()

    def reserve_locker(
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
    ):
        # get spind
        spind = Spinde.query.filter_by(nummer=nummer).first()
        # add data
        spind.nds = nds
        spind.matrikelnr = matrikelnr
        spind.bezahlt_bis = bezahlt_bis
        spind.vorname = vorname
        spind.nachname = nachname
        spind.mail = mail
        spind.passwort = passwort
        spind.fak = fak
        spind.saldo = saldo
        spind.bestellt_am = bestellt_am
        spind.schluessel_ausgegeben = "0"
        db.session.commit()

    def reset_locker(nummer):
        # get spind
        spind = Spinde.query.filter_by(nummer=nummer).first()
        # cancel reservation
        spind.nds = '0'
        spind.matrikelnr = '0'
        spind.bezahlt_bis = None
        spind.vorname = None
        spind.nachname = None
        spind.mail = None
        spind.passwort = None
        spind.schluessel_ausgegeben = "0"
        spind.fak = None
        spind.saldo = 0
        spind.bestellt_am = None
        # commit changes
        db.session.commit()

    def confirm_reservation(nummer, nds):
        # get spind
        spind = Spinde.query.filter_by(nummer=nummer).first()
        return spind.nds == nds

    # returns a dictionary which contains all areas and their available lockers
    def get_group_and_locker(self):
        groups = [1, 2, 3, 4, 5]
        # groups_and_lockers = {'Überblick':[]}
        groups_and_lockers = {}

        for group in groups:
            query = self.query.filter_by(gruppe=group, gesperrt=0, nds=0).all()
            lockers = []
            for locker in query:
                lockers.append(locker.nummer)

            groups_and_lockers[group] = lockers
        return groups_and_lockers

    # GET ALL FUNCTIONS
    # returns all nds which have a locker
    def get_all_nds():
        query = Spinde.query.filter(Spinde.nds != "0").all()
        all_nds = []
        for entry in query:
            all_nds.append(entry.nds)
        return all_nds

    # returns all matrikelnr which have a locker
    def get_all_matrikelnr():
        query = Spinde.query.filter(Spinde.matrikelnr != 0).all()
        all_matrikelnr = []
        for entry in query:
            all_matrikelnr.append(entry.matrikelnr)
        return all_matrikelnr

    # returns all nummer which have a locker
    def get_all_nummer():
        query = Spinde.query.filter(Spinde.nummer != 0).all()
        all_nummer = []
        for entry in query:
            all_nummer.append(entry.nummer)
        return all_nummer

    # returns all schluessel which have a locker
    def get_all_schluessel():
        query = Spinde.query.filter(Spinde.schluessel != 0).all()
        all_schluessel = []
        for entry in query:
            all_schluessel.append(entry.schluessel)
        return all_schluessel

    # returns the locker which belongs to the given parameter
    def get_spind(nds="", nummer=0, matrikelnr="", schluessel=0):
        spind = None
        if nds != "":
            spind = Spinde.query.filter_by(nds=nds).first()
        if nummer != 0:
            spind = Spinde.query.filter_by(nummer=nummer).first()
        if matrikelnr != "":
            spind = Spinde.query.filter_by(matrikelnr=matrikelnr).first()
        if schluessel != 0:
            spind = Spinde.query.filter_by(schluessel=schluessel).first()
        return spind

    # get current 'bezahlt_bis'
    def get_current_bezahlt_bis(nummer):
        current_bis = Spinde.query.filter_by(nummer=nummer).first()
        return current_bis.bezahlt_bis

    # get all free lockers
    def get_nds_of_free_lockers():
        query = Spinde.query.filter_by(gesperrt=0, nds=0).all()
        lockers = []
        for entry in query:
            lockers.append(entry.nummer)
        return lockers
    
    def get_blocked_lockers():
        query = Spinde.query.filter_by(gesperrt=1)
        return query
    
    def get_expired_lockers():
        query = Spinde.query.filter(Spinde.bezahlt_bis<date.today())
        return query
    
    def get_free_lockers():
        query = Spinde.query.filter_by(gesperrt=0, nds=0)
        return query
    
    def get_rented_lockers():
        query = Spinde.query.filter(Spinde.nds!=0, Spinde.saldo==0)
        return query
    
    def get_unpayed_lockers():
        query = Spinde.query.filter(Spinde.bezahlt_bis<date.today())
        return query
    
    def get_not_picked_up_lockers():
        query = Spinde.query.filter(Spinde.bestellt_am<date.today()-timedelta(days=1), Spinde.saldo!=0)
        return query
    
class Zahlungen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nds = db.Column(db.String(20))  # here it's 20 and in 'Spinde' it's 8???
    grund = db.Column(db.String(50))
    spind = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)  # in database it's timestamp
    wert = db.Column(db.Float)
    datum = db.Column(db.Date)

    def __init__(self, id, nds, grund, spind, timestamp, wert, datum):
        self.id = id
        self.nds = nds
        self.grund = grund
        self.spind = spind
        self.timestamp = timestamp
        self.wert = wert
        self.datum = datum

    def new_entry(nds, grund, spind, wert):
        # create id
        query = Zahlungen.query.all()
        id_zahlungen = []
        for entry in query:
            id_zahlungen.append(entry.id)
        if id_zahlungen == []:
            id_zahlungen = [0]
        id = max(id_zahlungen) + 1
        # create dates
        timestamp = datetime.now()
        datum = date.today()
        # new entry
        zahlung = Zahlungen(id, nds, grund, spind, timestamp, wert, datum)
        db.session.add(zahlung)
        db.session.commit()

    def get_von_bis(von, bis):
        query = Zahlungen.query.filter(Zahlungen.datum >= von, Zahlungen.datum <= bis)
        return query

class Superusers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nds = db.Column(db.String(8))

    def get_all_superusers():
        query = Superusers.query.filter().all()
        all_users = []
        for entry in query:
            all_users.append(entry.nds)
        return all_users
    
class Html(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aktuell = db.Column(db.Text)
    headline = db.Column(db.String(255))
    text = db.Column(db.Text)  

    def get_html():
        query = Html.query.first()
        return query   

        

