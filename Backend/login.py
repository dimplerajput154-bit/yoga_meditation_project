from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
LoginManager,
UserMixin,
login_user,
current_user,
logout_user
)
from flask_cors import CORS
from werkzeug.security import check_password_hash

#=========================================================

#Flask Application

#=========================================================

app = Flask(__name__)

CORS(
app,
supports_credentials=True
)

app.config["SECRET_KEY"] = "wellness_secret_key_12345"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wellness.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

#=========================================================

#Login Manager

#=========================================================

login_manager = LoginManager()

login_manager.init_app(app)

#=========================================================

#User Model

#=========================================================

class User(UserMixin, db.Model):

 __tablename__ = "users"

 id = db.Column(
    db.Integer,
    primary_key=True
 )

 name = db.Column(
    db.String(100),
    nullable=False
 )

 email = db.Column(
    db.String(120),
    unique=True,
    nullable=False
 )

 password = db.Column(
    db.String(200),
    nullable=False
 )

#=========================================================

#Load User

#=========================================================

@login_manager.user_loader
def load_user(user_id):

 return db.session.get(
    User,
    int(user_id)
)

#=========================================================

#Home / Test

#=========================================================

@app.route("/")
def home():

 return jsonify({

    "status": "success",

    "message": "Login Server is running.",

    "login": "/login",

    "logout": "/logout"

})

#=========================================================

#Login

#=========================================================

@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == "GET":
        return jsonify({
            "status": "success",
            "message": "Login API is working.",
            "method": "POST",
            "required_fields": [
                "email",
                "password"
            ]
        })

  data = request.get_json()

  if not data:

    return jsonify({

        "status": "error",

        "message": "JSON data is required."

    }), 400


  email = data.get("email")

  password = data.get("password")


# Validate input

  if not email or not password:

    return jsonify({

        "status": "error",

        "message": "Email and password are required."

    }), 400


# Find user

  user = User.query.filter_by(
    email=email
  ).first()


 # User not found
  if user is None:

    return jsonify({

        "status": "error",

        "message": "User not found. Please register first."

    }), 404


# Check password

  if not check_password_hash(
    user.password,
    password
):

    return jsonify({

        "status": "error",

        "message": "Invalid email or password."

    }), 401


 # Create login session

  login_user(user)


  return jsonify({

    "status": "success",

    "message": "Login successful.",

    "user": {

        "id": user.id,

        "name": user.name,

        "email": user.email

    },

    "next": "http://127.0.0.1:5000/api/dashboard-data"

})

#=========================================================

#Check Login

#=========================================================

@app.route("/check-login", methods=["GET"])
def check_login():

 if current_user.is_authenticated:

    return jsonify({

        "status": "success",

        "logged_in": True,

        "user": {

            "id": current_user.id,

            "name": current_user.name,

            "email": current_user.email

        }

    })


 return jsonify({

    "status": "success",

    "logged_in": False,

    "message": "User is not logged in."

})

#=========================================================

#Logout

#=========================================================

@app.route("/logout", methods=["GET", "POST"])
def logout():

 if current_user.is_authenticated:

    logout_user()

    return jsonify({

        "status": "success",

        "message": "Logout successful."

    })


 return jsonify({

    "status": "success",

    "message": "No active login session."

})

#=========================================================

#Run Application

#=========================================================

if __name__ == "main":

 with app.app_context():

    db.create_all()


print("=" * 55)

print("             AI WELLNESS LOGIN")

print("=" * 55)

print("Login Server: http://127.0.0.1:5001")

print("Login API:    http://127.0.0.1:5001/login")

print("=" * 55)


app.run(

    debug=True,

    port=5001

)