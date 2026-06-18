# Hybrid AI for Preventing Wild Animal Intrusions

## Overview

Hybrid AI for Preventing Wild Animal Intrusions is an intelligent monitoring system designed to reduce human-wildlife conflict by detecting and predicting animal intrusions in real time. The system combines computer vision and sound-based analysis to identify animals approaching agricultural or residential areas and generate early alerts.

The solution integrates YOLOv8 for image-based animal detection and Support Vector Machine (SVM) models for sound classification. A web-based interface provides live monitoring, intrusion alerts, and system management capabilities.

---

## Problem Statement

Human-wildlife conflict causes significant crop damage, economic losses, and safety risks in rural communities. Traditional monitoring methods are often manual, inefficient, and unable to provide early warnings.

This project aims to develop an automated system capable of:

* Detecting animals using camera feeds.
* Identifying animal sounds using audio analysis.
* Generating real-time alerts.
* Supporting proactive responses to prevent intrusions.

---

## Features

* Real-time animal detection using YOLOv8.
* Sound-based animal classification using SVM.
* IP camera integration for live monitoring.
* Alert generation for detected intrusions.
* Web-based dashboard for monitoring.
* Historical detection records.
* AI-powered decision support.

---

## System Architecture

1. IP Camera captures live video streams.
2. YOLOv8 processes video frames and detects animals.
3. Audio sensors capture environmental sounds.
4. SVM model classifies animal sounds.
5. Backend processes detection results.
6. Web application displays alerts and monitoring information.

---

## Technologies Used

### Backend

* Python
* Flask

### Artificial Intelligence

* YOLOv8
* Support Vector Machine (SVM)
* OpenCV

### Frontend

* React.js
* HTML
* CSS
* JavaScript

### Database

* MongoDB

### Tools

* Git
* GitHub
* VS Code

---

## Backend Implementation

The backend was developed using Flask and performs the following functions:

* Receives video streams from IP cameras.
* Processes images using YOLOv8.
* Integrates sound classification results from SVM.
* Generates real-time alerts.
* Handles communication between AI models and the web interface.
* Stores detection records and monitoring information.

---

## Project Workflow

1. Capture live video and audio inputs.
2. Detect animals using YOLOv8.
3. Classify sounds using SVM.
4. Process results through Flask backend.
5. Generate alerts if intrusion is detected.
6. Display results on the web dashboard.

---

## Results

* Successfully detected animal intrusions from live camera feeds.
* Combined visual and audio analysis for improved reliability.
* Enabled real-time monitoring and alert generation.
* Reduced dependency on manual surveillance methods.

---

## Future Enhancements

* Deployment on edge devices.
* Mobile application integration.
* Advanced animal movement prediction using LSTM.
* SMS and email notification system.
* Multi-camera monitoring support.



GitHub: https://github.com/Ankitha09014
