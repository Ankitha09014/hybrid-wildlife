# Wildlife Detection System - Implementation Plan

## Task: Add Email Notifications and Detection History

### Backend Changes:
- [x] 1. Create backend/email_service.py - Email notification service
- [x] 2. Create backend/database.py - MongoDB connection and operations
- [x] 3. Update backend/app.py - Integrate email and database, add history endpoints

### Frontend Changes:
- [x] 4. Update frontend/src/App.js - Add System Status menu item with history view
- [x] 5. Add history API calls to fetch from backend

### Configuration:
- [x] 6. Update requirements.txt with needed dependencies

## Details:
- Sender Email: nnm22ad011@nmamit.in
- Recipient Emails: dasankitha2004@gmail.com, veenasundardas@gmail.com
- Database: MongoDB (local mongodb://localhost:27017/)
- History: Last 5 detections to be shown in System Status
