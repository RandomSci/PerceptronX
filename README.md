# PerceptronX

## Overview
PerceptronX is an AI-powered real-time object detection mobile application utilizing YOLOv8. It allows users to detect objects using their device's camera, customize detection filters, and save detected results. Built with Kotlin (Jetpack Compose) for the frontend and FastAPI for the backend, it ensures fast and efficient processing.

## Features
- **Real-Time Object Detection**: Uses YOLOv8 for high-speed, accurate object detection.
- **Custom Object Selection**: Users can choose specific objects to detect.
- **Image Capture**: Allows saving frames during detection.
- **Dark-Themed UI**: A modern and sleek design for an intuitive user experience.
- **Profile & Settings**: Manage user preferences, camera quality, and detection settings.
- **Detection History**: View previously detected objects with timestamps.

## Tech Stack
- **Frontend**: Kotlin (Jetpack Compose)
- **Backend**: FastAPI (Python)
- **Real-time Communication**: WebSockets
- **Database**: Redis (for caching), PostgreSQL (for storing user data)
- **Machine Learning**: YOLOv8 (Ultralytics)
- **Deployment**: Docker (for containerization)

## Installation & Setup
### Prerequisites
- Python 3.9+
- FastAPI
- Kotlin (Android Development)
- Redis & PostgreSQL
- Docker (optional, for deployment)

### Backend Setup
```bash
# Clone the repository
git clone git@github.com:RandomSci/PerceptronX.git
cd perceptronx/backend

# Create and activate a virtual environment
python -m venv ForProjects
source ForProjects/bin/activate  # For Windows: ForProjects\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
1. Open the `frontend` folder in Android Studio.
2. Build and run the project on an emulator or physical device.
3. Ensure the backend is running before testing.

## API Endpoints
- `POST /detect` - Sends an image for object detection.
- `GET /history` - Fetches detection history.
- `WS /live` - WebSocket for real-time detection.

## Roadmap
- [ ] Improve detection accuracy.
- [ ] Optimize real-time streaming.
- [ ] Implement user authentication.
- [ ] Publish to Google Play Store.

## License
MIT License. See [LICENSE](LICENSE) for details.

## Contact
For inquiries or contributions, contact jaymeselwyn@gmail.com.

