import io
import math
from typing import Optional, Tuple, List

FACE_ENGINE = None

try:  # Prefer face_recognition if available
	import face_recognition  # type: ignore
	FACE_ENGINE = "face_recognition"
except Exception:
	try:
		from deepface import DeepFace  # type: ignore
		import numpy as np  # type: ignore
		FACE_ENGINE = "deepface"
	except Exception:
		FACE_ENGINE = None


def _encoding_fr(image_bytes: bytes) -> Optional[list[float]]:
	try:
		image = face_recognition.load_image_file(io.BytesIO(image_bytes))
		encodings = face_recognition.face_encodings(image)
		if not encodings:
			return None
		return [float(x) for x in encodings[0]]
	except Exception:
		return None


def _encoding_df(image_bytes: bytes) -> Optional[list[float]]:
	try:
		# DeepFace expects path or BGR image; we convert from bytes
		# Use temporary numpy array via cv2.imdecode if available
		import numpy as np  # type: ignore
		import cv2  # type: ignore
		arr = np.frombuffer(image_bytes, dtype=np.uint8)
		bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
		if bgr is None:
			return None
		reps = DeepFace.represent(bgr, model_name="Facenet512", enforce_detection=True)
		if not reps:
			return None
		vec = reps[0].get("embedding")
		if vec is None:
			return None
		return [float(x) for x in vec]
	except Exception:
		return None


def get_face_encoding(image_bytes: bytes) -> Optional[list[float]]:
	if FACE_ENGINE == "face_recognition":
		return _encoding_fr(image_bytes)
	elif FACE_ENGINE == "deepface":
		return _encoding_df(image_bytes)
	return None


def _distance(a: List[float], b: List[float]) -> float:
	# Euclidean distance for face_recognition-compatible encodings
	return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _cosine_similarity(a: List[float], b: List[float]) -> float:
	import numpy as np  # type: ignore
	a_arr = np.array(a)
	b_arr = np.array(b)
	den = (np.linalg.norm(a_arr) * np.linalg.norm(b_arr))
	if den == 0:
		return -1.0
	return float(np.dot(a_arr, b_arr) / den)


def compare_encodings(known: List[float], candidate: List[float], tolerance: float = 0.6) -> Tuple[bool, float]:
	if FACE_ENGINE == "face_recognition":
		dist = _distance(known, candidate)
		return (dist <= tolerance, dist)
	elif FACE_ENGINE == "deepface":
		# Cosine similarity, higher is more similar; map to pseudo-distance
		sim = _cosine_similarity(known, candidate)
		# Convert similarity to a distance-like metric between 0-2
		dist = 1.0 - sim
		# Empirical threshold: sim >= 0.35 ~ 0.65 distance
		return (sim >= (1.0 - tolerance), dist)
	else:
		return (False, float("inf"))