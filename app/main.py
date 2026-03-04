from flask import Flask
from app.routes.submitTeacher import teacher_bp
from app.routes.submitStudent import student_bp
from app.routes.quiz import quiz_bp
from app.routes.serverAlive import alive_bp


def create_app():
    app = Flask(__name__)

    #show all exceptions
    app.config["PROPAGATE_EXCEPTIONS"]=True
    app.config["TRAP_HTTP_EXCEPTIONS"]=True
    app.config["DEBUG"]=False

    app.register_blueprint(alive_bp, url_prefix="/server")
    app.register_blueprint(teacher_bp, url_prefix="/teacher")
    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(quiz_bp, url_prefix="/quiz")

    @app.route("/")
    def home():
        return "Cognito Quiz API is running"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0",port=5000,debug=False,use_reloader=False)
