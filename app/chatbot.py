def get_chat_response(user_text, ai_data=None):
    """
    PulseAI General Assistant: Updated for TikTok demo.
    Removes personal names and adds flexible response logic.
    """
    msg = user_text.lower().strip()
    
    # Safely extract the AI results
    risk_score = ai_data.get('probability', 0) if ai_data else 0
    risk_level = ai_data.get('risk_level', "Unknown") if ai_data else "Unknown"

    # --- 1. GREETINGS (Name Removed) ---
    greetings = ["hi", "hello", "hey", "hy", "how are you", "good morning"]
    if any(word in msg for word in greetings):
        return "Hello! I'm your PulseAI Assistant. I'm here to support your heart health journey. How can I help you today?"

    # --- 2. THE AI RESULTS & EXPLANATIONS ---
    # Added 'xplain' and 'explain' to keywords
    result_keywords = ["score", "result", "risk", "percentage", "analysis", "test", "explain", "xplain"]
    if any(word in msg for word in result_keywords):
        if ai_data:
            return (f"Your latest fused analysis (Clinical + ECG + X-ray) shows a {round(risk_score * 100, 2)}% probability. "
                    f"This is categorized as '{risk_level}'. This model uses deep learning to identify patterns in your cardiac data.")
        return "I don't see any recent heart health scans in your profile. Please go to the 'Predictor' page to run an analysis!"

    # --- 3. MEDICAL & LIFESTYLE ADVICE ---
    lifestyle = ["diet", "food", "eat", "exercise", "workout", "improve", "advice", "suggest", "doctor", "hospital"]
    if any(word in msg for word in lifestyle):
        return ("To support your heart health, I recommend the DASH diet (low sodium, high fiber) and at least 150 minutes of moderate exercise per week. "
                "Always consult with a cardiologist regarding your specific results.")

    # --- 4. APPRECIATION (Name Removed) ---
    thanks = ["thanks", "thank you", "bye", "ok", "great", "helpful"]
    if any(word in msg for word in thanks):
        return "You're very welcome! I'm always here if you have more questions. Stay healthy!"

    # --- 5. THE "REPLY TO ANYTHING" ENGINE ---
    # If no keywords match, the bot provides a context-aware helpful response
    return (f"I understand you're asking about '{user_text}'. While I am specialized in heart health tracking, "
            "I can certainly help you navigate your risk scores, explain your ECG analysis, or provide cardiac wellness tips. "
            "What would you like to explore first?")