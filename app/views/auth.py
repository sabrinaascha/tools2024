from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
import ldap
from app.models import Mitarbeiter

bp_auth = Blueprint("bp_auth", __name__, url_prefix="/auth")



loginManager = LoginManager()
loginManager.login_view = "bp_auth.login"
    

class User(UserMixin):
    def __init__(self, nds, vorname, nachname, mail, neuer_reiter=False):
       self.nds = nds
       self.vorname = vorname
       self.nachname = nachname
       self.mail = mail
       self.neuer_reiter = neuer_reiter
    
    def get_id(self):
        return self.nds

@loginManager.user_loader
def load_user(nds):
    user_data = extendNewUser(User(nds,"","",""))
    return User(nds,user_data.vorname,user_data.nachname,user_data.mail)

@bp_auth.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        nds = request.form.get('nds')
        password = request.form.get('psw')
        if checkPasswordOfNDS(nds, password):
            user = User(nds,"","","")
            login_user(user)
            return redirect(url_for('bp_index.index'))
        else:
            flash("NDS oder Passwort nicht korrekt", "login")
    return render_template("auth/login.html")

@bp_auth.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("auth/logout.html")

# LDAP FUNCTIONS
def getDN(nds):
    try:
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        connection = ldap.initialize("ldaps://ldapclient.uni-regensburg.de:636")
        connection.simple_bind_s("o=uni-regensburg,c=de")
        res = connection.search_s("o=uni-regensburg,c=de", ldap.SCOPE_SUBTREE, '(uid=' + nds + ')')
        for dn, entry in res:
            return dn
    except Exception as error:
        return None

def checkPassword(dn, password):
    try:
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
        ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, "etc/ssl/certs/RootCAA.pem")
        connection = ldap.initialize("ldaps://ldapclient.uni-regensburg.de:636")
        connection.simple_bind_s(dn, password)
        return True
    except Exception as error:
        return False

def checkPasswordOfNDS(nds, password):
    dn = getDN(nds)
    if(dn == None):
        return False
    return(checkPassword(dn, password))

def extendNewUser(user):
    try:
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        connection = ldap.initialize("ldaps://ldapclient.uni-regensburg.de:636")
        connection.simple_bind_s("o=uni-regensburg,c=de")
        res = connection.search_s("o=uni-regensburg,c=de", ldap.SCOPE_SUBTREE, '(uid=' + user.nds + ')')
        for dn, entry in res:
            user.vorname = entry['urrzGivenName'][0].decode('utf-8')
            user.nachname = entry['urrzSurname'][0].decode('utf-8')
            user.mail = entry['mail'][0].decode('utf-8') 
            return user
    except Exception as error:
        user.vorname = "UNBEKANNT"
        user.nachname = "UNBEKANNT"
        user.mail = "UNBEKANNT"
        return user
