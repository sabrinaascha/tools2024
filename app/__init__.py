from flask import Flask
from app.views.auth import loginManager
from app.models import db
from urllib.parse import quote_plus


# initialize app
app = Flask(__name__)

# DATABASE
# add and configure database
db_user = 'masterapp'
db_password ='@2023PSpinde'
# the encoded password is needed because the @-sign in the password messes with the connector below
db_coded_password = quote_plus(db_password)
db_database = 'spindeFlask'
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql://{db_user}:{db_coded_password}@localhost/{db_database}"
app.config["SECRET_KEY"] = "psc9BNcMna6mQx41zNILLaYY4xlTVXIJ"

# initialize database, get's created in models.py
db.init_app(app)
with app.app_context():  # throws error without 'app.app_context():'
    db.create_all()

# AUTHENTICATION
# initialize login manager, get's created in auth.py
loginManager.init_app(app)


# BLUEPRINTS
# import blueprints
from app.views.index import bp_index
from app.views.index import bp_layout
from app.views.index import bp_profile
from app.views.index import bp_preise
from app.views.index import bp_info
from app.views.index import bp_error
from app.views.mieten import bp_mieten
from app.views.admin import bp_admin
from app.views.auth import bp_auth
from app.views.themen import bp_themen

# register blueprints
app.register_blueprint(bp_index, url_prefix="")
app.register_blueprint(bp_layout, url_prefix="/layout")
app.register_blueprint(bp_profile, url_prefix="/profile")
app.register_blueprint(bp_preise, url_prefix="/preise")
app.register_blueprint(bp_info, url_prefix="/info")
app.register_blueprint(bp_error, url_prefix="/error")
app.register_blueprint(bp_mieten, url_prefix="/mieten")
app.register_blueprint(bp_admin, url_prefix="/admin")
app.register_blueprint(bp_auth, url_prefix="/auth")
app.register_blueprint(bp_themen, url_prefix="/themen")
