# Car Troubleshooting Chatbot Expert System

## Project Description

The **Car Troubleshooting Chatbot Expert System** is an AI-powered solution designed to help users diagnose and resolve common car issues. Leveraging Python, the Experta library (for rule-based reasoning), and Bayesian networks via pgmpy, the chatbot uses user-provided symptoms (e.g., engine issues, noises, or warnings) to offer possible causes and actionable recommendations.

This project demonstrates how artificial intelligence can make technical knowledge accessible, empowering users to manage car troubleshooting confidently.

---

## Features

- **Interactive Chat Interface:** Users can describe their car issues conversationally.
- **Expert System:** Employs rule-based reasoning for accurate problem identification.
- **Bayesian Networks:** Models probabilistic relationships to enhance diagnosis precision.
- **Real-Time Diagnosis:** Provides actionable recommendations for resolving car issues.
- **User-Friendly Design:** A simple, intuitive interface accessible to non-technical users.

---

## How to Run the Project

### Backend: Docker Instructions

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. To run the backend using Docker:
   ```bash
   docker run -p 8000:8000 car-troubleshooting-backend
   ```

3. Alternatively, use `docker-compose` for managing the backend:

   - **Start the backend:**
     ```bash
     docker-compose up
     ```

   - **Stop the backend:**
     ```bash
     docker-compose down
     ```

   - **Rebuild the backend:**
     ```bash
     docker-compose up --build
     ```

---

### Frontend: Running Locally

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies (if not already installed):
   ```bash
   npm install
   ```

3. Start the frontend application:
   ```bash
   npm start
   ```
---

## Deploy:

https://car-chatbot-ashy.vercel.app/

---

## Project Structure

```plaintext
├── backend/
│   ├── Dockerfile       # Backend Docker configuration
│   ├── docker-compose.yml # Backend container orchestration
│   ├── api/             # Backend API logic
│   └── requirements.txt # Backend Python dependencies
├── frontend/
│   ├── public/          # Public assets for the frontend
│   ├── src/             # React components and logic
│   ├── package.json     # Frontend dependencies
│   └── App.css          # Frontend styling
├── docs/
│   ├── design-docs.md   # System design documentation
│   └── user-guide.md    # Instructions for users
└── README.md            # Project overview and instructions
```

---

## Project Objectives

1. **Rule-Based Reasoning:**
   Implement rule-based reasoning using the Experta library to diagnose car issues.

2. **Bayesian Networks:**
   Use pgmpy to model probabilistic relationships, improving decision accuracy.

3. **Real-World Problem Solving:**
   Bridge AI and automotive domains to create a useful tool for non-experts.

---

## Testing and Validation

- **Unit Testing:** Test individual backend modules for accurate diagnosis.
- **Usability Testing:** Conduct tests with users to ensure an intuitive experience.
- **Stress Testing:** Validate system performance under high user traffic.

---

## Future Improvements

- **Expand Knowledge Base:** Include more car issues and advanced diagnostics.
- **Multilingual Support:** Support multiple languages for a broader audience.
- **Voice Interaction:** Add support for voice commands and responses.
- **Integration with IoT:** Connect the chatbot to car diagnostic tools for real-time data.

---

## Contributors

This project was developed as part of the **Integrative Task 2** for the course **Algoritmos y Programación III**.
by 
-David Donneys (full stack)
-gerson

---

---
