from flask import Flask, jsonify, send_from_directory, request
from ultralytics import YOLO
import cv2
import os
import tempfile
import subprocess
import time
import wave
import numpy as np
import sounddevice as sd
import librosa
import urllib.request
import json
import torch
import torch.nn as nn
from flask_cors import CORS
from datetime import datetime

# Import our custom modules
from email_service import send_danger_alert_email
from database import store_detection, get_detection_history, get_all_detections

app = Flask(__name__, static_folder="static")
CORS(app)

# Load YOLOv8 model
model = YOLO(os.path.join("yolov8", "best.pt"))

# IP camera stream (update if your camera uses a different path)
ip_camera_url = "http://192.168.133.6:8080/video"

# IP camera audio stream (set to your camera's audio/rtsp stream if different)
ip_camera_audio_url = "http://192.168.133.6:8080/audio.wav"

# PANNs assets
PANNS_DATA_DIR = os.path.join(os.path.expanduser("~"), "panns_data")
PANNS_LABELS_PATH = os.path.join(PANNS_DATA_DIR, "class_labels_indices.csv")
# Use a separate filename to avoid conflicts with partially locked downloads
PANNS_CHECKPOINT_PATH = os.path.join(PANNS_DATA_DIR, "Cnn14_mAP=0.431.pth.bin")
PANNS_LABELS_URL = "https://raw.githubusercontent.com/qiuqiangkong/audioset_tagging_cnn/master/metadata/class_labels_indices.csv"
PANNS_CHECKPOINT_URL = "https://zenodo.org/record/3987831/files/Cnn14_mAP%3D0.431.pth?download=1"
PANNS_MIN_BYTES = 300_000_000  # Cnn14 checkpoint is large; re-download if smaller than 300MB

def download_file(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    urllib.request.urlretrieve(url, path)

def get_remote_size(url):
    try:
        with urllib.request.urlopen(url) as response:
            length = response.headers.get("Content-Length")
            return int(length) if length else None
    except Exception:
        return None

def ensure_panns_assets():
    os.makedirs(PANNS_DATA_DIR, exist_ok=True)
    if not os.path.exists(PANNS_LABELS_PATH):
        download_file(PANNS_LABELS_URL, PANNS_LABELS_PATH)
    expected_size = get_remote_size(PANNS_CHECKPOINT_URL)
    if os.path.exists(PANNS_CHECKPOINT_PATH):
        local_size = os.path.getsize(PANNS_CHECKPOINT_PATH)
        min_size = expected_size if expected_size else PANNS_MIN_BYTES
        if local_size < min_size:
            try:
                os.remove(PANNS_CHECKPOINT_PATH)
            except OSError:
                pass
    if not os.path.exists(PANNS_CHECKPOINT_PATH):
        download_file(PANNS_CHECKPOINT_URL, PANNS_CHECKPOINT_PATH)

ensure_panns_assets()

# Load PANNs audio tagging model (AudioSet pretrained)
from panns_inference import AudioTagging, labels as panns_labels
audio_tagger = AudioTagging(checkpoint_path=PANNS_CHECKPOINT_PATH, device="cpu")

MODEL_PATH = r"C:\models\audio_classifier.pth"
LABELS_PATH = r"C:\models\labels.json"

class MLP(nn.Module):
    def __init__(self, in_dim, num_classes):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes),
        )

    def forward(self, x):
        return self.net(x)

USE_FINETUNED_AUDIO = True
audio_classifier = None
audio_labels = None

def load_audio_classifier():
    global audio_classifier, audio_labels
    if not (os.path.exists(MODEL_PATH) and os.path.exists(LABELS_PATH)):
        return
    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        audio_labels = json.load(f)
    # Infer embedding size from a dummy 10s input
    dummy = np.zeros((1, 32000 * 10), dtype=np.float32)
    _, embedding = audio_tagger.inference(dummy)
    emb = embedding[0]
    if emb.ndim > 1:
        emb = emb.mean(axis=0)
    audio_classifier = MLP(emb.shape[0], len(audio_labels))
    audio_classifier.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    audio_classifier.eval()

load_audio_classifier()

TARGET_KEYWORDS = {
    "lion": ["roar", "roaring", "growl", "big cat", "animal"],
    "tiger": ["roar", "roaring", "growl", "big cat", "animal"],
    "cheetah": ["cat", "growl", "animal"],
    "cat": ["cat", "meow", "purr"],
    "dog": ["dog", "bark", "growl"],
    "human": ["speech", "human", "scream", "shout"],
    "cow": ["cattle", "cow", "moo"],
    "deer": ["deer", "animal"],
}

def build_target_indices():
    indices = {}
    for target, keywords in TARGET_KEYWORDS.items():
        idxs = []
        for i, name in enumerate(panns_labels):
            lname = name.lower()
            if any(k in lname for k in keywords):
                idxs.append(i)
        indices[target] = idxs
    return indices

target_indices = build_target_indices()

def capture_audio_wav(url, seconds=6, sample_rate=32000):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.close()
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        url,
        "-t",
        str(seconds),
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        "-f",
        "wav",
        tmp.name,
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=12)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="ignore")[-400:])
    return tmp.name

def capture_audio_mic(seconds=6, sample_rate=32000):
    audio = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.close()
    with wave.open(tmp.name, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())
    return tmp.name

def load_waveform(wav_path):
    with wave.open(wav_path, "rb") as wf:
        sample_rate = wf.getframerate()
        n_frames = wf.getnframes()
        audio = wf.readframes(n_frames)
        waveform = np.frombuffer(audio, dtype=np.int16).astype(np.float32) / 32768.0
    return sample_rate, waveform

def infer_audio(waveform):
    # If fine-tuned classifier is available, use it
    if USE_FINETUNED_AUDIO and audio_classifier is not None and audio_labels is not None:
        if waveform.ndim == 1:
            waveform = waveform[None, :]
        _, embedding = audio_tagger.inference(waveform)
        emb = embedding[0]
        if emb.ndim > 1:
            emb = emb.mean(axis=0)
        with torch.no_grad():
            logits = audio_classifier(torch.from_numpy(emb).unsqueeze(0))
            probs = torch.softmax(logits, dim=1).squeeze(0).numpy()
        return {audio_labels[str(i)]: float(probs[i]) for i in range(len(probs))}

    # Fallback to generic AudioSet scores
    if waveform.ndim == 1:
        waveform = waveform[None, :]
    (clipwise_output, embedding) = audio_tagger.inference(waveform)
    scores_np = clipwise_output[0]
    target_scores = {}
    for target, idxs in target_indices.items():
        if idxs:
            target_scores[target] = float(np.max(scores_np[idxs]))
        else:
            target_scores[target] = 0.0
    return target_scores

# Local fallback video (kept for testing if IP cam is down)
video_filename = "LionM.mp4"
video_path = os.path.join("static", video_filename)

# Dangerous animals list (matching frontend)
DANGEROUS_ANIMALS = [
    "tiger", "leopard", "lion", "bear", "elephant",
    "wild boar", "boar", "wolf", "panther", "crocodile",
    "rhino", "hippo", "snake"
]

# Track last alert time to prevent spam (in-memory)
last_alert_time = {}
ALERT_COOLDOWN_SECONDS = 60  # Minimum time between alerts for same animal

def is_dangerous_animal(animal_name):
    """Check if an animal is in the dangerous list"""
    return any(dangerous in str(animal_name).lower() for dangerous in DANGEROUS_ANIMALS)

def should_send_alert(animal_name):
    """Check if we should send an alert (cooldown check)"""
    current_time = time.time()
    animal_key = animal_name.lower()
    
    if animal_key not in last_alert_time:
        return True
    
    if current_time - last_alert_time[animal_key] > ALERT_COOLDOWN_SECONDS:
        return True
    
    return False

def update_alert_time(animal_name):
    """Update the last alert time for an animal"""
    last_alert_time[animal_name.lower()] = time.time()

@app.route("/detect", methods=["GET"])
def detect_from_video():
    # Read directly from the IP camera stream with timeouts
    cap = cv2.VideoCapture()
    try:
        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 3000)
        cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 3000)
    except Exception:
        pass
    cap.open(ip_camera_url, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(ip_camera_url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    detected_classes = set()
    class_counts = {}
    class_max_conf = {}
    min_conf = float(request.args.get("min_conf", 0.5))
    min_count = int(request.args.get("min_count", 2))

    if not cap.isOpened():
        return jsonify({
            "status": "error",
            "message": "Could not open IP camera stream. Check the URL: " + ip_camera_url
        }), 500

    frame_count = 0
    max_wait_seconds = 6
    start_time = time.time()
    while frame_count < 5:  # Process only 5 frames for speed
        if time.time() - start_time > max_wait_seconds:
            break
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)[0]
        for box in results.boxes:
            conf = float(box.conf[0]) if hasattr(box, "conf") else 1.0
            if conf < min_conf:
                continue
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            detected_classes.add(label)
            class_counts[label] = class_counts.get(label, 0) + 1
            class_max_conf[label] = max(class_max_conf.get(label, 0.0), conf)

        frame_count += 1

    cap.release()
    if frame_count == 0:
        return jsonify({
            "status": "error",
            "message": "No frames received from IP camera stream: " + ip_camera_url
        }), 500

    # Filter out single-frame flickers/false positives
    filtered_counts = {k: v for k, v in class_counts.items() if v >= min_count}
    filtered_counts = {k: v for k, v in filtered_counts.items() if class_max_conf.get(k, 0.0) >= min_conf}
    video_scores = {label: count / frame_count for label, count in filtered_counts.items()}

    # Store detections and send email alerts for dangerous animals
    for animal, score in video_scores.items():
        is_dangerous = is_dangerous_animal(animal)
        
        # Store in MongoDB
        store_detection(animal, "video", score, is_dangerous)
        
        # Send email if dangerous and within cooldown
        if is_dangerous and should_send_alert(animal):
            send_danger_alert_email(animal, "video", score)
            update_alert_time(animal)

    return jsonify({
        "status": "success",
        "detected": list(filtered_counts.keys()),
        "counts": filtered_counts,
        "scores": video_scores,
        "frames": frame_count
    })

@app.route("/audio_detect", methods=["GET"])
def detect_from_audio():
    seconds = int(request.args.get("seconds", 8))
    threshold = float(request.args.get("threshold", 0.06))
    silence_rms = float(request.args.get("silence_rms", 0.03))
    min_top_score = float(request.args.get("min_top_score", 0.15))
    try:
        # Use laptop mic if no IP camera audio URL is set
        if not ip_camera_audio_url:
            wav_path = capture_audio_mic(seconds=seconds, sample_rate=32000)
        else:
            wav_path = capture_audio_wav(ip_camera_audio_url, seconds=seconds, sample_rate=32000)
        sample_rate, waveform = load_waveform(wav_path)
        os.unlink(wav_path)
        if sample_rate != 32000:
            waveform = librosa.resample(waveform, orig_sr=sample_rate, target_sr=32000)
        # Pad/crop to 10 seconds for PANNs
        target_len = 32000 * 10
        if len(waveform) < target_len:
            waveform = np.pad(waveform, (0, target_len - len(waveform)))
        elif len(waveform) > target_len:
            waveform = waveform[:target_len]

        # Silence gate: when near-silent, return zero scores
        rms = float(np.sqrt(np.mean(np.square(waveform))))
        if rms < silence_rms:
            # Return explicit zeros for all labels when silent
            if audio_labels is not None:
                zero_scores = {audio_labels[str(i)]: 0.0 for i in range(len(audio_labels))}
            else:
                zero_scores = {}
            return jsonify({
                "status": "success",
                "detected": [],
                "scores": zero_scores
            })

        scores = infer_audio(waveform)
        # Disable human completely from audio results
        if "human" in scores:
            scores.pop("human", None)

        # If nothing is confidently animal-like, zero everything
        max_score = max(scores.values(), default=0.0)
        if max_score < min_top_score:
            if audio_labels is not None:
                zero_scores = {audio_labels[str(i)]: 0.0 for i in range(len(audio_labels))}
            else:
                zero_scores = {k: 0.0 for k in scores.keys()}
            return jsonify({
                "status": "success",
                "detected": [],
                "scores": zero_scores
            })

        detected = [k for k, v in scores.items() if v >= threshold]
        detected_sorted = sorted(detected, key=lambda k: scores[k], reverse=True)
        
        # Store detections and send email alerts for dangerous animals
        for animal in detected_sorted:
            score = scores.get(animal, 0)
            is_dangerous = is_dangerous_animal(animal)
            
            # Store in MongoDB
            store_detection(animal, "audio", score, is_dangerous)
            
            # Send email if dangerous and within cooldown
            if is_dangerous and should_send_alert(animal):
                send_danger_alert_email(animal, "audio", score)
                update_alert_time(animal)
        
        return jsonify({
            "status": "success",
            "detected": detected_sorted,
            "scores": scores
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Route to get detection history (last 5 detections)
@app.route("/history", methods=["GET"])
def get_history():
    """Get the last 5 detection records from the database"""
    try:
        limit = int(request.args.get("limit", 5))
        history = get_detection_history(limit)
        return jsonify({
            "status": "success",
            "history": history
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Route to serve local video file (optional fallback)
@app.route("/video")
def serve_video():
    return send_from_directory("static", video_filename)

if __name__ == "__main__":
    # Disable reloader to avoid Windows watchdog/socket issues with large ML deps
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)