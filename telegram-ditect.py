from flask import Flask, Response
from picamera2 import Picamera2
import cv2
import time
import telebot

# =========================
# TELEGRAM CONFIG
# =========================

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

bot = telebot.TeleBot(BOT_TOKEN)

# =========================
# FLASK
# =========================

app = Flask(__name__)

# =========================
# CAMERA SETUP
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
# HUMAN DETECTOR
# =========================

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# =========================
# VARIABLES
# =========================

prev_time = 0
previous_gray = None
frame_count = 0
last_alert_time = 0

# =========================
# SEND TELEGRAM ALERT
# =========================

def send_telegram_alert(image_path):

    global last_alert_time

    # Prevent spam
    if time.time() - last_alert_time < 15:
        return

    try:

        with open(image_path, 'rb') as photo:

            bot.send_photo(
                CHAT_ID,
                photo,
                caption="🚨 HUMAN DETECTED!"
            )

        print("Telegram Alert Sent")

        last_alert_time = time.time()

    except Exception as e:

        print("Telegram Error:", e)

# =========================
# FRAME GENERATOR
# =========================

def generate_frames():

    global prev_time
    global previous_gray
    global frame_count

    while True:

        frame_count += 1

        # Capture frame
        frame = picam2.capture_array()

        # FIX COLORS
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Resize
        frame = cv2.resize(frame, (320, 240))

        # =========================
        # MOTION DETECTION
        # =========================

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        motion_detected = False

        if previous_gray is not None:

            diff = cv2.absdiff(previous_gray, gray)

            _, thresh = cv2.threshold(
                diff,
                25,
                255,
                cv2.THRESH_BINARY
            )

            motion_pixels = cv2.countNonZero(thresh)

            if motion_pixels > 5000:

                motion_detected = True

                # Red border
                cv2.rectangle(
                    frame,
                    (0, 0),
                    (320, 240),
                    (0, 0, 255),
                    3
                )

        previous_gray = gray

        # =========================
        # HUMAN DETECTION
        # =========================

        if motion_detected and frame_count % 5 == 0:

            boxes, weights = hog.detectMultiScale(
                frame,
                winStride=(8, 8),
                padding=(8, 8),
                scale=1.05
            )

            for (x, y, w, h) in boxes:

                # Rectangle
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    3
                )

                # Label
                cv2.putText(
                    frame,
                    "HUMAN DETECTED",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

                # Save snapshot
                image_path = "alert.jpg"

                cv2.imwrite(image_path, frame)

                # Send Telegram alert
                send_telegram_alert(image_path)

        # =========================
        # FPS COUNTER
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
        # STATUS
        # =========================

        status = (
            "MOTION DETECTED"
            if motion_detected
            else "NO MOTION"
        )

        color = (
            (0, 0, 255)
            if motion_detected
            else (255, 255, 255)
        )

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
        # TIMESTAMP
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
        # ENCODE FRAME
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
# HOME PAGE
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
                max-width:900px;
            }

            h1{
                color:lime;
            }

        </style>

    </head>

    <body>

        <h1>Pi Zero 2W AI Surveillance</h1>

        <img src="/video_feed">

    </body>

    </html>
    """

# =========================
# VIDEO FEED
# =========================

@app.route('/video_feed')

def video_feed():

    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

# =========================
# MAIN
# =========================

if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
