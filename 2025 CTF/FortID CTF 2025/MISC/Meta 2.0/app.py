import json
import os
import pathlib
import shutil
import subprocess
import tarfile
import uuid
import zipfile

from flask import Flask, abort, jsonify, render_template, request
from werkzeug.utils import secure_filename
import magic

app = Flask(__name__)
TMP_PARENT = pathlib.Path("/tmp/metabox")


def run(cmd, cwd=None, timeout=20):
    """Return (stdout, stderr, exit_code)."""
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
        env=os.environ,
    )
    return proc.stdout, proc.stderr, proc.returncode


def handle_pdf(file_path: pathlib.Path):
    stdout, _stderr, code = run(["pdfinfo", str(file_path)])
    if code != 0:
        return {"error": "pdfinfo failed"}, 415

    meta = {}
    for line in stdout.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return {"metadata": meta}, 200


def is_node_project(path: pathlib.Path) -> bool:
    return (path / "package.json").is_file()


def handle_node_project(extract_dir: pathlib.Path):
    try:
        with open(extract_dir / "package.json", encoding="utf-8") as f:
            pkg = json.load(f)
    except Exception as e:
        return {"error": "package.json parse failed"}, 400

    subset = {
        k: pkg[k]
        for k in ("name", "version", "description", "scripts", "dependencies")
        if k in pkg
    }
    return {"metadata": subset}, 200


def is_rust_crate(path: pathlib.Path) -> bool:
    return (path / "Cargo.toml").is_file()


def handle_rust_crate(extract_dir: pathlib.Path):
    stdout, _stderr, code = run(
        ["cargo", "metadata", "--locked", "--offline", "--format-version", "1"],
        cwd=extract_dir,
    )

    if code != 0:
        return {"error": f"Internal Server Error (exit code: {code})"}, 500

    try:
        meta = json.loads(stdout)
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON"}, 500

    return {"metadata": meta}, 200


def handle_image(file_path: pathlib.Path):
    stdout, _stderr, _ = run(["exiftool", "-json", str(file_path)])
    try:
        meta = json.loads(stdout or "null")
    except json.JSONDecodeError:
        meta = "No metadata found"
    return {"metadata": meta}, 200


def handle_media(file_path: pathlib.Path):
    stdout, _stderr, code = run(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(file_path),
        ]
    )
    if code != 0:
        return {"error": "ffprobe failed"}, 415

    try:
        meta = json.loads(stdout or "null")
    except json.JSONDecodeError:
        meta = {"raw": stdout.strip()}
    return {"metadata": meta}, 200


def save_and_probe(upload):
    workdir = TMP_PARENT / str(uuid.uuid4())
    workdir.mkdir(parents=True, exist_ok=False)

    try:
        fname = secure_filename(upload.filename) or "upload.bin"
        raw_path = workdir / fname
        raw_path.write_bytes(upload.read())

        mime = magic.from_file(str(raw_path), mime=True)

        if mime in {
            "application/x-tar",
            "application/gzip",
            "application/x-bzip2",
            "application/zip",
        }:
            extract_dir = workdir / "unpack"
            extract_dir.mkdir()
            try:
                if mime == "application/zip":
                    with zipfile.ZipFile(raw_path) as zf:
                        zf.extractall(extract_dir)
                else:
                    with tarfile.open(raw_path) as tf:
                        tf.extractall(extract_dir)
            except Exception as e:
                return {"error": f"archive extraction failed: {e}"}, 400

            if is_node_project(extract_dir):
                return handle_node_project(extract_dir)

            if is_rust_crate(extract_dir):
                return handle_rust_crate(extract_dir)

            listing = sorted(
                str(p.relative_to(extract_dir)) for p in extract_dir.rglob("*")
            )
            return {"listing": listing}, 200

        if mime.startswith("image/"):
            return handle_image(raw_path)

        if mime == "application/pdf":
            return handle_pdf(raw_path)

        if mime.startswith("audio/") or mime.startswith("video/"):
            return handle_media(raw_path)

        return {"error": f"unsupported MIME: {mime}"}, 415

    finally:
        shutil.rmtree(workdir, ignore_errors=True)


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        abort(400, "multipart/form-data with field 'file' required")
    result, code = save_and_probe(request.files["file"])
    return jsonify(result), code


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
