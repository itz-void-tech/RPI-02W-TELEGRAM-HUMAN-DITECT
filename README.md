# 🛡️ Pi Zero 2W AI Surveillance System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Hardware](https://img.shields.io/badge/Hardware-Raspberry%20Pi%20Zero%202W-red)](https://www.raspberrypi.com/)

A lightweight, high-efficiency AI surveillance solution designed specifically for the resource-constrained Raspberry Pi Zero 2W. This system combines motion detection, human detection via OpenCV, and instant Telegram alerts with a live Flask-based web dashboard.

---

## ✨ Features

*   **Live Streaming:** Real-time camera feed accessible via any web browser.
*   **Dual-Stage Detection:** 
    1.  **Motion Detection:** Filters out static frames to save CPU cycles.
    2.  **Human Detection:** Uses OpenCV HOG (Histogram of Oriented Gradients) descriptors.
*   **Instant Alerts:** Sends snapshots directly to your Telegram bot when a human is detected.
*   **Performance Overlays:** Real-time FPS counter and timestamp watermarks.
*   **Edge Optimized:** Built for Raspberry Pi OS Lite to ensure minimal RAM overhead.

---

## 🛠️ Hardware Requirements

| Component | Recommendation |
| :--- | :--- |
| **SBC** | Raspberry Pi Zero 2W |
| **Camera** | RPi Camera Module (v2 or v3) |
| **Storage** | 16GB+ MicroSD (Class 10) |
| **Connectivity** | Stable 2.4GHz WiFi |

---

## 💻 Software Stack

*   **Backend:** Python 3
*   **Vision:** OpenCV, Imutils, Picamera2
*   **Web Server:** Flask
*   **Messaging:** Telegram Bot API (pyTelegramBotAPI)

---

## 🚀 Installation & Setup

### 1. System Preparation
Update your system and install the necessary native dependencies:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-full python3-venv python3-pip python3-opencv python3-picamera2 python3-numpy
