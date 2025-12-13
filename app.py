import os
import io
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from werkzeug.utils import secure_filename
try:
    from google.cloud import storage
except Exception:
    storage = None


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

    ADMIN_USER = os.environ.get("APP_USER", "admin")
    ADMIN_PASS = os.environ.get("APP_PASS", "password")

    GCS_BUCKET = os.environ.get("GCS_BUCKET")

    gcs_client = None
    bucket = None
    if storage and GCS_BUCKET:
        try:
            gcs_client = storage.Client()
            bucket = gcs_client.bucket(GCS_BUCKET)
        except Exception:
            gcs_client = None
            bucket = None

    LOCAL_UPLOAD_DIR = os.environ.get("LOCAL_UPLOAD_DIR", "uploads")
    os.makedirs(LOCAL_UPLOAD_DIR, exist_ok=True)

    def list_files():
        if bucket:
            blobs = list(bucket.list_blobs())
            return [(b.name, b.size, b.updated) for b in blobs]
        else:
            res = []
            for fname in os.listdir(LOCAL_UPLOAD_DIR):
                fpath = os.path.join(LOCAL_UPLOAD_DIR, fname)
                st = os.stat(fpath)
                res.append((fname, st.st_size, datetime.fromtimestamp(st.st_mtime)))
            return res

    def save_file_to_storage(file, filename):
        if bucket:
            blob = bucket.blob(filename)
            blob.upload_from_file(file)
        else:
            file_path = os.path.join(LOCAL_UPLOAD_DIR, filename)
            file.seek(0)
            with open(file_path, "wb") as f:
                f.write(file.read())

    @app.route("/")
    def home():
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        files = list_files()
        return render_template("index.html", files=files)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            if username == ADMIN_USER and password == ADMIN_PASS:
                session["logged_in"] = True
                return redirect(url_for("home"))
            flash("Invalid credentials", "danger")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/upload", methods=["POST"])
    def upload():
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        file = request.files.get("file")
        if not file:
            flash("No file selected", "warning")
            return redirect(url_for("home"))
        filename = secure_filename(file.filename)
        if filename == "":
            flash("Invalid filename", "warning")
            return redirect(url_for("home"))
        file_stream = io.BytesIO(file.read())
        file_stream.seek(0)
        save_file_to_storage(file_stream, filename)
        flash("Uploaded successfully", "success")
        return redirect(url_for("home"))

    @app.route("/download/<path:filename>")
    def download(filename):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        if bucket:
            blob = bucket.blob(filename)
            data = blob.download_as_bytes()
            return send_file(io.BytesIO(data), as_attachment=True, download_name=filename)
        else:
            path = os.path.join(LOCAL_UPLOAD_DIR, filename)
            if not os.path.exists(path):
                flash("File not found", "warning")
                return redirect(url_for("home"))
            # read and return bytes to avoid keeping file open
            with open(path, 'rb') as f:
                data = f.read()
            return send_file(io.BytesIO(data), as_attachment=True, download_name=filename)

    @app.route("/delete/<path:filename>")
    def delete(filename):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        if bucket:
            blob = bucket.blob(filename)
            blob.delete()
        else:
            path = os.path.join(LOCAL_UPLOAD_DIR, filename)
            if os.path.exists(path):
                os.remove(path)
        flash("Deleted successfully", "info")
        return redirect(url_for("home"))

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
