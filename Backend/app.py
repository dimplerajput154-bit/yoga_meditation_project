from mood_track import mood_bp
from sleep_track import sleep_bp
from flask import Flask
from health_profile import health_bp
from remedies import remedies_bp

app = Flask(__name__)

app.secret_key = "health_profile_secret_key"
app.register_blueprint(sleep_bp)
app.register_blueprint(health_bp)
app.register_blueprint(mood_bp)
app.register_blueprint(remedies_bp)

if __name__ == "__main__":
    app.run(debug=True)