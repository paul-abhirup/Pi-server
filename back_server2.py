from flask import Flask, send_file, jsonify, Response, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Base path where all patient folders are stored
BASE_PATH = '/home/Scan1/Desktop/Clock_Drawing'

# Helper to get the latest patient folder (e.g., 'P14')
def get_latest_patient_folder():
    try:
        folders = [f for f in os.listdir(BASE_PATH) if f.startswith('P') and f[1:].isdigit()]
        folders.sort(key=lambda x: int(x[1:]))  # Sort numerically
        return folders[-1] if folders else None
    except Exception as e:
        print(f"Error getting patient folder: {e}")
        return None

# Helper to get patient folder from query or latest
def get_patient_folder_from_request():
    patientid = request.args.get('patientid')
    if patientid:
        patientid = patientid.upper()
        if patientid.startswith('P') and patientid[1:].isdigit():
            folder_path = os.path.join(BASE_PATH, patientid)
            if os.path.exists(folder_path):
                return patientid
    # fallback to latest
    return get_latest_patient_folder()

# ✅ GET /spiral/latest-patient-id → returns latest folder name
@app.route('/spiral/latest-patient-id')
def latest_patient():
    latest = get_latest_patient_folder()
    if latest:
        return jsonify({'latest_patient_id': latest})
    return jsonify({'error': 'No patient folders found'}), 404

# ✅ GET /spiral/similarity → returns similarity.txt content as plain text
@app.route('/spiral/similarity')
def get_similarity():
    folder = get_patient_folder_from_request()
    if not folder:
        return jsonify({'error': 'No patient folder found'}), 404

    path = os.path.join(BASE_PATH, folder, 'drawing_similarity.txt')
    if os.path.exists(path):
        with open(path, 'r') as f:
            content = f.read()
        return Response(content, mimetype='text/plain')
    return jsonify({'error': 'drawing_similarity.txt not found'}), 404

# ✅ GET /spiral/graph → returns pressure_time_plot.png image
@app.route('/spiral/graph')
def get_graph():
    folder = get_patient_folder_from_request()
    if not folder:
        return jsonify({'error': 'No patient folder found'}), 404

    path = os.path.join(BASE_PATH, folder, 'pressure_time_plot.png')
    if os.path.exists(path):
        return send_file(path, mimetype='image/png')
    return jsonify({'error': 'pressure_time_plot.png not found'}), 404

# ✅ Run server on all IPs (for LAN access), port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
