from mood_track import mood_bp
from sleep_track import sleep_bp
from flask import Flask, session
from health_profile import health_bp
from remedies import remedies_bp

app = Flask(__name__)

app.secret_key = "health_profile_secret_key"
app.register_blueprint(sleep_bp)
app.register_blueprint(health_bp)
app.register_blueprint(mood_bp)
app.register_blueprint(remedies_bp)

# Temporary login for testing
@app.route("/test-login")
def test_login():
    session["user_id"] = 1

    return {
        "success": True,
        "message": "Test login successful",
        "user_id": 1
    }


if __name__ == "__main__":
    app.run(debug=True)