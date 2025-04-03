from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
import shutil
import dlib
import cv2
import numpy as np
import json
from scipy.spatial.distance import cosine
import zipfile
import io
from flask import send_file

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PORTRAIT_FOLDER = os.path.join(UPLOAD_FOLDER, 'Portrait')
CANDIDS_FOLDER = os.path.join(UPLOAD_FOLDER, 'Candids')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2 GB limit
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
os.makedirs(PORTRAIT_FOLDER, exist_ok=True)
os.makedirs(CANDIDS_FOLDER, exist_ok=True)
#CORS(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


# Handle CORS preflight requests
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.route('/upload', methods=['OPTIONS'])
def options():
    return make_response(jsonify({'status': 'ok'}), 200)

# ✅ Function to check if a file is an image
def is_image_file(filename):
    valid_extensions = {".jpg", ".jpeg", ".png"}
    return os.path.splitext(filename)[1].lower() in valid_extensions

@app.route('/upload', methods=['POST'])
def upload_folders():
    if 'portrait_zip' not in request.files or 'candids_zip' not in request.files:
        return jsonify({'error': 'Portrait and candids zip files required'}), 400
    
    portrait_zip = request.files['portrait_zip']
    candids_zip = request.files['candids_zip']
    
    # Save and extract portrait zip
    portrait_zip_path = os.path.join(UPLOAD_FOLDER, 'portrait.zip')
    portrait_zip.save(portrait_zip_path)
    unzip_file(portrait_zip_path, PORTRAIT_FOLDER)
    
    # Save and extract candids zip
    candids_zip_path = os.path.join(UPLOAD_FOLDER, 'candids.zip')
    candids_zip.save(candids_zip_path)
    unzip_file(candids_zip_path, CANDIDS_FOLDER)
    
    # Process and save encodings for portraits
    encodings = process_and_save_encodings(PORTRAIT_FOLDER, "all_face_encodings.json")
    
    # Run ML processing for candids
    results = run_ml_processing(os.path.join(CANDIDS_FOLDER, 'Candids'))
    
    zip_buffer = io.BytesIO()
    output_dir = "outputs"

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, output_dir))

    zip_buffer.seek(0)

    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name="processed_images.zip")

def unzip_file(zip_path, extract_to_folder):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if "__MACOSX" in file or file.startswith("._"):
                print(f"⚠️ Skipping macOS system file: {file}")
                continue  # Skip macOS system files
            zip_ref.extract(file, extract_to_folder)

# ----------------------------------------------------------------------------------------------------------------
def process_and_save_encodings(parent_directory, output_path):
    shape_predictor_path = "model/shape_predictor_68_face_landmarks.dat"
    face_rec_model_path = "model/dlib_face_recognition_resnet_model_v1.dat"
    
    processor = FaceEncodingProcessor(shape_predictor_path, face_rec_model_path)
    encodings = processor.process_images_in_directory(parent_directory)
    
    with open(output_path, "w") as f:
        json.dump(encodings, f)
    
    return encodings

class FaceEncodingProcessor:
    def __init__(self, shape_predictor_path, face_rec_model_path):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(shape_predictor_path)
        self.face_recognizer = dlib.face_recognition_model_v1(face_rec_model_path)

    def process_images_in_directory(self, parent_directory):
        all_encodings = {}

        for root, _, files in os.walk(parent_directory):
            for filename in files:
                if not is_image_file(filename):  # ✅ Skip non-image files
                    print(f"⚠️ Skipping non-image file: {filename}")
                    continue
                
                image_path = os.path.join(root, filename)
                image = cv2.imread(image_path)

                if image is None:
                    print(f"🚨 Error: Could not read image {image_path}")
                    continue  # Skip invalid images

                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                rects = self.detector(gray, 1)
                face_encodings = []
                
                for rect in rects:
                    shape = self.predictor(gray, rect)
                    face_descriptor = self.face_recognizer.compute_face_descriptor(image, shape)
                    encoding = np.array(face_descriptor)
                    face_encodings.append(encoding.tolist())
                
                if face_encodings:
                    all_encodings[image_path] = face_encodings
        print(f"Printing encodings length for all the portraits: {len(all_encodings)}")
        return all_encodings
# --------------------------------------------------------------------------------------------------------------------------------------------
def face_recognizer(image_path):
    with open("all_face_encodings.json", "r") as f:
        print("Getting till recognition")
        stored_encodings = json.load(f)
    print(f"length of stored encodings: {len(stored_encodings)}" )

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("model/shape_predictor_68_face_landmarks.dat")
    face_recognizer = dlib.face_recognition_model_v1("model/dlib_face_recognition_resnet_model_v1.dat")

    image = cv2.imread(image_path)
    if image is None:
        print(f"🚨 Error: Cannot read image {image_path}")
        return []

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)

    if len(rects) == 0:
        print("No faces detected moving to unknown folder")
        organizer(image_path, [])

    matched_names = []
    
    for rect in rects:
        shape = predictor(gray, rect)
        face_descriptor = face_recognizer.compute_face_descriptor(image, shape)
        encoding = np.array(face_descriptor)
        
        min_distance = float('inf')
        matched_name = None

        for filename, encodings in stored_encodings.items():
            for stored_encoding in encodings:
                distance = cosine(encoding, np.array(stored_encoding))
                if distance < min_distance:
                    min_distance = distance
                    matched_name = filename        
        matched_names.append(matched_name)
        
        # Draw bounding box and label on image
        (x, y, w, h) = (rect.left(), rect.top(), rect.width(), rect.height())
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, matched_name.split(".")[0].split("/")[-1] if matched_name else "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        output_dir = "temp/labeled_faces"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, os.path.basename(image_path))
        cv2.imwrite(output_path, image)

        organizer(output_path, matched_names)
    
    return matched_names

def organizer(image_path, matched_names):
    directory = "outputs/"
    class_dict = {"104": 0, "106": 0, "108": 0}
    if not matched_names or all(name is None for name in matched_names):
        output_path = os.path.join(directory, "unknown")
        os.makedirs(output_path, exist_ok=True)
        shutil.copy(image_path, output_path)
    else: 
        for name in matched_names:
            name, _ = name.split(".")
            num = name.split("/")[-1]
            print(num)
            if int(num) > 120 and int(num) < 145:
                class_dict["104"] += 1
            elif int(num) > 167 and int(num) < 189:
                class_dict["106"] += 1
            elif int(num) > 207 and int(num) < 237:
                class_dict["108"] += 1

        for class_label, count in class_dict.items():
            if (count / len(matched_names)) > 0.3:
                destination_path = os.path.join(directory, class_label)
                os.makedirs(destination_path, exist_ok=True)
                shutil.copy(image_path, destination_path)

def run_ml_processing(directory):
    results = {}
    for filename in os.listdir(directory):
        if not is_image_file(filename):  # ✅ Skip non-image files
            print(f"⚠️ Skipping non-image file: {filename}")
            continue
        
        image_path = os.path.join(directory, filename)
        matched_names = face_recognizer(image_path)
        print(matched_names)
        results[image_path] = matched_names
    return results

if __name__ == '__main__':
    app.run(debug=True)
