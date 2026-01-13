import random
from datetime import datetime, time, timedelta

# --- Data ---

NUTRITION_TIPS = [
    {
        "title": "Walnuts for Wisdom",
        "tip": "Walnuts are rich in DHA, a type of Omega-3 fatty acid that improves cognitive performance. Snacking on a handful can help focus.",
        "category": "Brain Fuel"
    },
    {
        "title": "Hydration Station",
        "tip": "Dehydration leads to fatigue. Keep a water bottle on your desk and sip every 20 minutes.",
        "category": "General Health"
    },
    {
        "title": "The Banana Boost",
        "tip": "Bananas provide a steady release of energy. Great for a pre-study snack to avoid sugar crashes.",
        "category": "Energy"
    },
    {
        "title": "Dark Chocolate Delight",
        "tip": "A small piece of dark chocolate increases blood flow to the brain and can improve memory.",
        "category": "Mood & Focus"
    },
    {
        "title": "Berry Good Memory",
        "tip": "Blueberries are packed with antioxidants that may delay brain aging and improve memory.",
        "category": "Brain Fuel"
    }
]

STRESS_RELIEF_TIPS = [
    {
        "title": "Box Breathing",
        "tip": "Inhale for 4s, Hold for 4s, Exhale for 4s, Hold for 4s. Repeat 4 times to reset your nervous system.",
        "duration": "2 mins"
    },
    {
        "title": "The 20-20-20 Rule",
        "tip": "Every 20 minutes, look at something 20 feet away for 20 seconds to reduce eye strain.",
        "duration": "20 secs"
    },
    {
        "title": "Shoulder Shrugs",
        "tip": "Lift your shoulders to your ears, hold for 5s, and drop them suddenly. Release that tension!",
        "duration": "1 min"
    }
]

# --- Functions ---

def get_daily_tip():
    """Returns a random nutrition or wellness tip."""
    return random.choice(NUTRITION_TIPS)

def get_stress_buster():
    """Returns a random stress relief exercise."""
    return random.choice(STRESS_RELIEF_TIPS)

def calculate_sleep_schedule(wake_time_str):
    """
    Calculates recommended sleep time based on wake time.
    """
    try:
        # Assuming wake_time_str is in "HH:MM" format (24h)
        wake_time = datetime.strptime(wake_time_str, "%H:%M")
        
        # Teenagers/Students need 8-9 hours
        sleep_needed = timedelta(hours=8, minutes=30)
        
        bed_time = wake_time - sleep_needed
        
        return {
            "bed_time": bed_time.strftime("%I:%M %p"),
            "cycles": "5-6 sleep cycles (90 mins each)",
            "hours": "8.5 hours"
        }
    except Exception as e:
        return {"error": str(e)}

def get_exam_day_advice(days_left):
    """Returns specific advice based on proximity to exam."""
    if days_left == 0:
        return "Today is the big day! Eat a light, carb-rich breakfast. Stay hydrated but don't overdrink right before."
    elif days_left == 1:
        return "Relax today. No heavy revision. Sleep early and prepare your exam kit (Admit card, pens) tonight."
    elif days_left <= 7:
        return "Switch to your exam biological clock. Wake up at the time you'd wake up for the exam."
    else:
        return "Consistency is key. Maintain a steady diet and sleep schedule."
