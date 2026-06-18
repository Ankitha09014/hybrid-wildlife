Hybrid AI for Preventing Wild Animal Intrusions
Overview

Hybrid AI for Preventing Wild Animal Intrusions is an intelligent monitoring system designed to reduce human-wildlife conflict by detecting and predicting animal intrusions in real time. The system combines computer vision and sound-based analysis to identify animals approaching agricultural or residential areas and generate early alerts.

The solution integrates YOLOv8 for image-based animal detection and Support Vector Machine (SVM) models for sound classification. A web-based interface provides live monitoring, intrusion alerts, and system management capabilities.

System Architecture
IP Camera captures live video streams.
YOLOv8 processes video frames and detects animals.
Audio sensors capture environmental sounds.
SVM model classifies animal sounds.
Backend processes detection results.
Web application displays alerts and monitoring information.
Technologies Used
Backend
Python
Flask
Artificial Intelligence
YOLOv8
Support Vector Machine (SVM)
OpenCV
Frontend
React.js
HTML
CSS
JavaScript
Database
MongoDB
Tools
Git
GitHub
VS Code
Backend Implementation

The backend was developed using Flask and performs the following functions:

Receives video streams from IP cameras.
Processes images using YOLOv8.
Integrates sound classification results from SVM.
Generates real-time alerts.
Handles communication between AI models and the web interface.
Stores detection records and monitoring information.

Results
Successfully detected animal intrusions from live camera feeds.
Combined visual and audio analysis for improved reliability.
Enabled real-time monitoring and alert generation.
Reduced dependency on manual surveillance methods.
