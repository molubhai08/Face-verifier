import threading
from deepface import DeepFace
import cv2
import pymongo

# Connect to the MongoDB server
client = pymongo.MongoClient("localhost:27017")

# Access the specific database
db = client['example']

# Access the specific collection within the database
collection = db['ex']

cap = cv2.VideoCapture(0)
img = cv2.imread('')
counter = 0

face_match = False
face_match_lock = threading.Lock()

def check_face(frame):
    global face_match
    try:
        # Perform face verification
        result = DeepFace.verify(frame, img.copy())
        verified = result['verified']
        
        with face_match_lock:
            if verified:
                face_match = True
                # Insert the verification result into MongoDB
                key = {'Name': 'sarthak', 'Status': 'Verified'}
                collection.insert_one(key)
                cap.release()
            else:
                face_match = False
    except Exception as e:
        print(f"Error during face verification: {e}")
        with face_match_lock:
            face_match = False

while True:
    ret, frame = cap.read()
    if ret:
        if counter % 30 == 0:
            try:
                threading.Thread(target=check_face, args=(frame.copy(),)).start()
            except Exception as e:
                print(f"Error creating thread: {e}")
        
        with face_match_lock:
            if face_match:
                cv2.putText(frame, "match", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            else:
                cv2.putText(frame, "no match", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        
        counter += 1
        
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
