
# 🎯 StrikeGoal

**Smart Exam Planner for Indian Entrance Exams**

StrikeGoal is an intelligent study planning assistant designed to help students prepare for competitive exams like **JEE (Main/Advanced)**, **NEET**, **BITSAT**, and more. It uses AI to generate personalized study schedules based on exam dates and syllabus weightage.

## ✨ Features
- **Smart Study Planner**: Generates daily schedules prioritizing high-weightage topics.
- **AI Strategy Coach**: (Optional) Get personalized tips using Google Gemini AI.
- **Exam Calendar**: View dates for major entrance exams.
- **Calendar Sync**: Export plans to `.ics` or sync to Google Tasks.
- **Authentication**: Secure login for personalized sessions.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- [Google Gemini API Key](https://aistudio.google.com/) (Optional, for AI Strategy)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/strikegoal.git
   cd strikegoal
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Authentication:**
   The app comes with a default user. **Change this for production!**
   - File: `auth_config.yaml`
   - Default User: `student`
   
   To generate a new password hash:
   ```bash
   python -c "import bcrypt; print(bcrypt.hashpw(b'YOUR_PASSWORD', bcrypt.gensalt()).decode())"
   ```
   Replace the hash in `auth_config.yaml`.

### Running the App

```bash
streamlit run app.py
```
Access the app at `http://localhost:8501`.

## 🧪 Testing

We use `pytest` for unit testing.

```bash
# Run all tests
pytest tests

# Run specific test file
pytest tests/test_study_planner.py
```

## 🔒 Security Note
- **API Keys**: enter your Gemini API key in the UI settings (it is not stored permanently).
- **Credentials**: Passwords are hashed using bcrypt. Do not commit `auth_config.yaml` with real production credentials if the repo is public.

## 📦 Deployment

### Streamlit Cloud
1. Push this code to GitHub.
2. Log in to [Streamlit Cloud](https://streamlit.io/cloud).
3. Connect your repo and select `app.py` as the entry point.
4. **Secrets**: If you use API keys, add them in the Streamlit Cloud secrets management.

---
Made with ❤️ for Indian Students

