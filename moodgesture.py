import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe solutions
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh

# Drawing specifications
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1, color=(0, 255, 0))

# Initialize Face Mesh
face_mesh = mp_face_mesh.FaceMesh(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_faces=1
)

# Initialize webcam
cap = cv2.VideoCapture(0)

def detect_emotion(face_landmarks):
    """Detect between 5 basic emotions with teeth detection for happy"""
    landmarks = face_landmarks.landmark
    
    # Eye openness
    left_eye_top = (landmarks[159].y + landmarks[158].y) / 2
    left_eye_bottom = (landmarks[145].y + landmarks[153].y) / 2
    left_eye_open = abs(left_eye_top - left_eye_bottom)
    
    right_eye_top = (landmarks[386].y + landmarks[385].y) / 2
    right_eye_bottom = (landmarks[374].y + landmarks[380].y) / 2
    right_eye_open = abs(right_eye_top - right_eye_bottom)
    
    avg_eye_open = (left_eye_open + right_eye_open) / 2
    
    # Mouth features
    mouth_top = landmarks[13].y
    mouth_bottom = landmarks[14].y
    mouth_openness = abs(mouth_top - mouth_bottom)
    
    # Smile detection (using mouth width and openness)
    left_lip = landmarks[61]
    right_lip = landmarks[291]
    mouth_width = abs(left_lip.x - right_lip.x)
    
    # Teeth detection (mouth open but corners stretched wide)
    showing_teeth = mouth_openness > 0.04 and mouth_width > 0.18
    
    # Emotion detection
    if avg_eye_open < 0.015:
        return "sleepy"
    elif showing_teeth:  # Showing teeth = happy
        return "happy"
    elif mouth_openness > 0.08:  # Very open mouth without wide smile
        return "surprised"
    elif (left_lip.y + right_lip.y)/2 - (mouth_top + mouth_bottom)/2 > 0.03:
        return "sad"
    elif mouth_width > 0.16:  # Smile without teeth showing
        return "happy"
    else:
        return "neutral"

def draw_avatar(emotion):
    """Draw avatar with clear teeth for happy expression"""
    height, width = 480, 640
    avatar = np.zeros((height, width, 3), dtype=np.uint8)
    center_x, center_y = width//2, height//2
    
    # Face
    cv2.circle(avatar, (center_x, center_y), 150, (255, 220, 180), -1)
    
    # Eyes
    eye_y = center_y - 50
    if emotion == "sleepy":
        # Closed eyes
        cv2.line(avatar, (center_x-65, eye_y), (center_x-35, eye_y), (0,0,0), 2)
        cv2.line(avatar, (center_x+35, eye_y), (center_x+65, eye_y), (0,0,0), 2)
    elif emotion == "happy":
        # Happy squint eyes
        cv2.ellipse(avatar, (center_x-50, eye_y), (20, 10), 0, 0, 180, (0,0,0), 2)
        cv2.ellipse(avatar, (center_x+50, eye_y), (20, 10), 0, 0, 180, (0,0,0), 2)
    elif emotion == "surprised":
        # Wide open eyes
        cv2.circle(avatar, (center_x-50, eye_y), 20, (0,0,0), -1)
        cv2.circle(avatar, (center_x+50, eye_y), 20, (0,0,0), -1)
    elif emotion == "sad":
        # Droopy eyes
        cv2.ellipse(avatar, (center_x-50, eye_y+5), (20, 10), 0, 0, 180, (0,0,0), 2)
        cv2.ellipse(avatar, (center_x+50, eye_y+5), (20, 10), 0, 0, 180, (0,0,0), 2)
    else:  # neutral
        cv2.circle(avatar, (center_x-50, eye_y), 15, (0,0,0), -1)
        cv2.circle(avatar, (center_x+50, eye_y), 15, (0,0,0), -1)
    
    # Mouth with teeth for happy
    mouth_y = center_y + 50
    if emotion == "happy":
        # Big smile with teeth
        cv2.ellipse(avatar, (center_x, mouth_y), (60, 30), 0, 0, 180, (0,0,0), 3)
        # Draw teeth
        for i in range(5):
            x_pos = center_x - 50 + i*25
            cv2.line(avatar, (x_pos, mouth_y), (x_pos, mouth_y-20), (255,255,255), 2)
    elif emotion == "surprised":
        # Open mouth (circle)
        cv2.circle(avatar, (center_x, mouth_y), 30, (0,0,0), 2)
    elif emotion == "sad":
        # Frown
        cv2.ellipse(avatar, (center_x, mouth_y+20), (40, 20), 0, 0, 180, (0,0,0), 3)
    elif emotion == "sleepy":
        # Small line mouth
        cv2.line(avatar, (center_x-20, mouth_y), (center_x+20, mouth_y), (0,0,0), 2)
    else:  # neutral
        cv2.line(avatar, (center_x-30, mouth_y), (center_x+30, mouth_y), (0,0,0), 2)
    
    # Emotion text with color coding
    colors = {
        "happy": (0, 200, 0),
        "surprised": (255, 165, 0),
        "sleepy": (100, 100, 255),
        "sad": (255, 0, 0),
        "neutral": (0, 0, 255)
    }
    cv2.putText(avatar, emotion.upper(), (50, 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, colors[emotion], 2)
    
    return avatar

# Main loop
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        continue
    
    frame = cv2.flip(frame, 1)
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image)
    
    emotion = "neutral"
    if results.multi_face_landmarks:
        emotion = detect_emotion(results.multi_face_landmarks[0])
        
        # Draw face landmarks
        mp_drawing.draw_landmarks(
            image=frame,
            landmark_list=results.multi_face_landmarks[0],
            connections=mp_face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=drawing_spec,
            connection_drawing_spec=drawing_spec
        )
    
    avatar = draw_avatar(emotion)
    combined = np.hstack((frame, avatar))
    
    cv2.imshow('Emotion Detection', combined)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
