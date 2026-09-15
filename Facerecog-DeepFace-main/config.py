import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import warnings
warnings.filterwarnings("ignore")

import platform
import os
from pathlib import Path
from dotenv import load_dotenv

# Path Konfigurasi
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
CASCADE_PATH = BASE_DIR / "face_ref.xml"
KNOWN_FACES_DIR = BASE_DIR / "known_faces"
EMBEDDINGS_PATH = BASE_DIR / "known_faces_embeddings.json"
MEMBERS_META_PATH = BASE_DIR / "known_faces_meta.json"

# API Endpoints Default
LARAVEL_BASE_URL = os.getenv("LARAVEL_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
LARAVEL_API_KEY = os.getenv("LARAVEL_API_KEY", "")
DEFAULT_API_URL = f"{LARAVEL_BASE_URL}/api/customers/register-face"
DEFAULT_DETECTION_API_URL = f"{LARAVEL_BASE_URL}/api/customers/detect-member"

# Palette Warna UI (BGR Format untuk OpenCV)
COLOR_PRIMARY = (235, 99, 37)       # Vibrant Blue (#2563eb)
COLOR_PRIMARY_SOFT = (250, 240, 230) # Soft Ice Blue
COLOR_ACCENT = (110, 159, 15)       # Emerald Green (#0f9f6e)
COLOR_ACCENT_SOFT = (230, 250, 235)
COLOR_DANGER = (38, 38, 220)        # Crimson Red (#dc2626)
COLOR_DANGER_SOFT = (235, 235, 254)
COLOR_WARNING = (6, 119, 217)       # Amber (#d97706)
COLOR_WARNING_SOFT = (225, 245, 255)
COLOR_TEXT = (51, 32, 23)          # Dark Slate (#172033)
COLOR_MUTED = (140, 119, 107)       # Muted Slate (#6b778c)
COLOR_BORDER = (240, 234, 226)      # Subtle Border (#e2e8f0)
COLOR_BG = (251, 247, 244)          # Light App BG (#f4f7fb)
COLOR_PANEL = (255, 255, 255)       # Card Panel (#ffffff)
COLOR_SURFACE = (244, 238, 232)     # Surface (#e8edf5)
COLOR_BLUE = COLOR_PRIMARY
COLOR_BLUE_SOFT = COLOR_PRIMARY_SOFT

# Model & Parameter AI/ML Inference
FACENET_MODEL_NAME = "Facenet512"
# Referensi Threshold: 0.40 berasal dari rekomendasi default DeepFace untuk Facenet512 dengan Cosine Metric,
# dan telah dikonfirmasi melalui hasil eksperimen empiris (hasil_evaluasi_full.txt) untuk keseimbangan Precision-Recall.
COSINE_DISTANCE_THRESHOLD = 0.40
EMBEDDING_FILE_VERSION = 1

# Parameter Deteksi & Preprocessing Citra Klasik (Non-AI)
LOW_LIGHT_MEAN_LIMIT = 95
LOW_LIGHT_TARGET_MEAN = 125
LOW_LIGHT_BRIGHTNESS_BONUS = 18
FACE_DETECTION_ANGLES = (0, -20, 20, -35, 35)
FACE_DETECTION_IOU_LIMIT = 0.35
REGISTER_SAMPLE_COUNT = 5
REGISTER_SAMPLE_INTERVAL = 0.35
REGISTER_SAMPLE_TIMEOUT = 6.0
