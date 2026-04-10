from flask import Flask, request, jsonify, render_template
from parser import extract_text_from_upload
from scorer import compute_score
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload

UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/screen', methods=['POST'])
def screen():
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file uploaded'}), 400

    resume_file = request.files['resume']
    job_description = request.form.get('job_description', '').strip()

    if not job_description:
        return jsonify({'error': 'Job description is required'}), 400

    if resume_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    allowed_extensions = {'.pdf', '.txt'}
    ext = os.path.splitext(resume_file.filename)[1].lower()
    if ext not in allowed_extensions:
        return jsonify({'error': 'Only PDF and TXT files are supported'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, resume_file.filename)
    resume_file.save(filepath)

    try:
        resume_text = extract_text_from_upload(filepath, ext)
        result = compute_score(resume_text, job_description)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


@app.route('/health')
def health():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
