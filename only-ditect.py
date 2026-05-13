from flask import Flask, Response
from picamera2 import Picamera2
import cv2
import time

app = Flask(__name__)

# =========================
# Camera Setup
# =========================

picam2 = Picamera2()

picam2.configure(
    picam2.create_preview_configuration(
        main={"size": (320, 240)}
    )
)

picam2.start()

time.sleep(2)

# =========================
# Human Detector
# =========================

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# =========================
# FPS Variables
# =========================

prev_time = 0

# =========================
# Motion Detection Variables
# =========================

previous_gray = None

# =========================
# Frame Generator
# =========================

def generate_frames():

    global prev_time
    global previous_gray

    while True:

        # Capture frame
        frame = picam2.capture_array()

        # Convert BGRA -> BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        # Resize for speed
        frame = cv2.resize(frame, (320, 240))

        # =========================
        # Motion Detection
        # =========================

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        motion_detected = False

        if previous_gray is not None:

            diff = cv2.absdiff(previous_gray, gray)

            _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

            motion_pixels = cv2.countNonZero(thresh)

            if motion_pixels > 5000:
                motion_detected = True

        previous_gray = gray

        # =========================
        # Human Detection
        # ONLY when motion exists
        # =========================

        if motion_detected:

            boxes, weights = hog.detectMultiScale(
                frame,
                winStride=(16, 16),
                padding=(4, 4),
                scale=1.1
            )

            for (x, y, w, h) in boxes:

                # Human rectangle
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

                # Human label
                cv2.putText(
                    frame,
                    "HUMAN DETECTED",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

        # =========================
        # FPS Counter
        # =========================

        current_time = time.time()

        fps = 1 / (current_time - prev_time) if prev_time != 0 else 0

        prev_time = current_time

        cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )

        # =========================
        # Motion Status
        # =========================

        status = "MOTION DETECTED" if motion_detected else "NO MOTION"

        color = (0, 0, 255) if motion_detected else (255, 255, 255)

        cv2.putText(
            frame,
            status,
            (10, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

        # =========================
        # Timestamp
        # =========================

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        cv2.putText(
            frame,
            timestamp,
            (10, 230),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255),
            1
        )

        # =========================
        # Encode Frame
        # =========================

        ret, buffer = cv2.imencode('.jpg', frame)

        frame_bytes = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            frame_bytes +
            b'\r\n'
        )

# =========================
# Home Page
# =========================

@app.route('/')

def index():

    return """
    <html>
        <head>
            <title>Pi Zero 2W AI Surveillance</title>

            <style>
                body{
                    background:#111;
                    color:white;
                    text-align:center;
                    font-family:Arial;
                }

                img{
                    border:4px solid lime;
                    margin-top:20px;
                    width:90%;
                    max-width:800px;
                }

                h1{
                    color:lime;
                }
            </style>

        </head>

        <body>

            <h1>Pi Zero 2W AI Human Detection</h1>

            <img src="/video_feed">

        </body>
    </html>
    """

# =========================
# Video Feed Route
# =========================

@app.route('/video_feed')

def video_feed():

    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

# =========================
# Main
# =========================

if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
