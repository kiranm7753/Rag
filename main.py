from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from vectorstore.build_vectorstore import build_vectorstore
from vectorstore.query_bot import query_rag
from utils.s3_utils import upload_file_to_s3, delete_user_folder_from_s3
from auth.models import db, User
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os
import shutil

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

bcrypt = Bcrypt()
bcrypt.init_app(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from auth.routes import auth_bp

app.register_blueprint(auth_bp)

UPLOAD_FOLDER = "uploads"
VECTORSTORE_FOLDER = "vectorstores"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
@login_required
def index():
    return render_template("index.html", user=current_user)


@app.route("/upload", methods=["POST"])
@login_required
def upload():
    files = request.files.getlist("files")
    if not files:
        return jsonify({"message": "No files selected"}), 400

    user_id = str(current_user.id)
    file_paths = []

    for file in files:
        filename = secure_filename(file.filename)
        if not filename.lower().endswith(".pdf"):
            return jsonify({"message": f"{filename} is not a PDF file."}), 400

        local_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(local_path)

        s3_key = f"users/{user_id}/pdfs/{filename}"
        if upload_file_to_s3(local_path, s3_key):
            file_paths.append(local_path)

    if not file_paths:
        return jsonify({"message": "Upload failed."}), 500

    build_vectorstore(file_paths, user_id)

    return jsonify(
        {
            "message": f"{len(file_paths)} file(s) uploaded to S3 for user {user_id}.",
            "user_id": user_id,
        }
    )


@app.route("/ask", methods=["POST"])
@login_required
def ask():
    data = request.json
    query = data.get("query")
    user_id = str(current_user.id)

    if not query:
        return jsonify({"error": "Missing query"}), 400

    vector_path = os.path.join(VECTORSTORE_FOLDER, user_id)
    if not os.path.exists(vector_path):
        return jsonify(
            {"error": "No PDFs uploaded yet. Please upload a document first."}
        ), 400

    try:
        result = query_rag(query, user_id=user_id, top_k=5)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reset", methods=["POST"])
@login_required
def reset_uploads():
    user_id = str(current_user.id)

    # Delete uploaded PDFs
    for file in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Delete local vectorstore
    vectorstore_path = os.path.join(VECTORSTORE_FOLDER, user_id)
    if os.path.exists(vectorstore_path):
        shutil.rmtree(vectorstore_path)

    # Delete from S3
    delete_user_folder_from_s3(user_id)

    return jsonify({"message": "Uploads and index reset successfully."})


@app.route("/logout")
@login_required
def logout():
    user_id = str(current_user.id)

    # Delete local vectorstore
    vectorstore_path = os.path.join(VECTORSTORE_FOLDER, user_id)
    if os.path.exists(vectorstore_path):
        shutil.rmtree(vectorstore_path)

    # Delete uploaded files
    for file in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Delete from S3
    delete_user_folder_from_s3(user_id)

    from flask_login import logout_user

    logout_user()
    return render_template(
        "login.html",
        message="You have been logged out. All your uploaded files and embeddings have been deleted.",
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
