import random
import re
from datetime import datetime

def health_chatbot(user_message):
    """Rule-based health chatbot that provides basic health information"""
    
    user_message = user_message.lower().strip()
    
    # Define response patterns and corresponding replies
    responses = {
        # Greetings
        'greeting': {
            'patterns': ['hi', 'hello', 'hey', 'good morning', 'good evening', 'how are you'],
            'responses': [
                "Hello! I'm your health assistant. How can I help you today?",
                "Hi there! I'm here to help with your health questions. What would you like to know?",
                "Hello! Feel free to ask me about symptoms, health tips, or general wellness advice."
            ]
        },
        
        # Common symptoms
        'fever': {
            'patterns': ['fever', 'high temperature', 'hot', 'burning up', 'temperature'],
            'responses': [
                "For fever: Rest, drink plenty of fluids, and monitor your temperature. If fever persists above 101°F (38.3°C) for more than 3 days or reaches 103°F (39.4°C), consult a doctor immediately.",
                "Fever is often your body's way of fighting infection. Stay hydrated, rest, and use fever reducers like acetaminophen if needed. Seek medical attention if symptoms worsen.",
                "For fever management: Take rest, drink water, use cool compresses, and monitor temperature regularly. Contact healthcare provider if concerned."
            ]
        },
        
        'headache': {
            'patterns': ['headache', 'head pain', 'migraine', 'head hurts', 'skull pain'],
            'responses': [
                "For headaches: Try resting in a quiet, dark room, apply cold/warm compress, stay hydrated, and consider over-the-counter pain relievers. If severe or persistent, consult a doctor.",
                "Headache relief: Ensure adequate sleep, manage stress, stay hydrated, and avoid triggers like bright lights. Seek medical help for severe or unusual headaches.",
                "Common headache remedies include rest, hydration, gentle neck stretches, and pain medication if needed. See a doctor for frequent or severe headaches."
            ]
        },
        
        'cough': {
            'patterns': ['cough', 'coughing', 'throat irritation', 'dry cough', 'wet cough'],
            'responses': [
                "For cough: Stay hydrated, use honey for throat soothing, try warm salt water gargles, and consider a humidifier. See a doctor if cough persists over 2 weeks or has blood.",
                "Cough management: Drink warm fluids, avoid irritants like smoke, use throat lozenges, and get adequate rest. Consult healthcare provider if symptoms worsen.",
                "To ease cough: Try herbal teas, honey, steam inhalation, and avoid dry air. Seek medical attention for persistent or productive cough with fever."
            ]
        },
        
        'cold': {
            'patterns': ['cold', 'runny nose', 'stuffy nose', 'sneezing', 'congestion', 'blocked nose'],
            'responses': [
                "For cold symptoms: Rest, drink plenty of fluids, use saline nasal drops, and try steam inhalation. Most colds resolve in 7-10 days. See a doctor if symptoms persist longer.",
                "Cold care: Get adequate sleep, stay hydrated, use a humidifier, and consider over-the-counter decongestants. Consult doctor if symptoms worsen or last over 10 days.",
                "Common cold remedies: Rest, fluids, warm salt water gargles, and avoiding others to prevent spread. Seek medical care if you develop high fever or difficulty breathing."
            ]
        },
        
        'stomach': {
            'patterns': ['stomach pain', 'stomach ache', 'belly pain', 'abdominal pain', 'nausea', 'vomiting', 'diarrhea'],
            'responses': [
                "For stomach issues: Try clear fluids, BRAT diet (bananas, rice, applesauce, toast), avoid dairy and fatty foods. See a doctor for severe pain, persistent vomiting, or blood in stool.",
                "Stomach pain relief: Rest, stay hydrated, eat bland foods, and avoid spicy/fatty meals. Seek immediate medical attention for severe abdominal pain or signs of dehydration.",
                "For digestive issues: Drink clear fluids, eat small frequent meals, avoid irritating foods. Contact healthcare provider if symptoms are severe or persistent."
            ]
        },
        
        # General health topics
        'exercise': {
            'patterns': ['exercise', 'workout', 'fitness', 'physical activity', 'gym'],
            'responses': [
                "Regular exercise is great for health! Aim for 150 minutes of moderate exercise weekly. Start slowly and gradually increase intensity. Always consult your doctor before starting a new exercise program.",
                "Exercise benefits include improved cardiovascular health, stronger bones, and better mental health. Choose activities you enjoy and make them part of your routine.",
                "For fitness: Combine cardio, strength training, and flexibility exercises. Stay hydrated, warm up before exercising, and listen to your body's signals."
            ]
        },
        
        'diet': {
            'patterns': ['diet', 'nutrition', 'food', 'eating', 'healthy eating', 'meal'],
            'responses': [
                "Healthy eating includes plenty of fruits, vegetables, whole grains, lean proteins, and limited processed foods. Stay hydrated and maintain regular meal times.",
                "Nutrition tips: Eat a variety of colorful foods, control portion sizes, limit sugar and sodium, and include healthy fats. Consult a nutritionist for personalized advice.",
                "Balanced diet essentials: 5-9 servings of fruits/vegetables daily, whole grains, lean proteins, and adequate water intake. Avoid excessive processed foods."
            ]
        },
        
        'sleep': {
            'patterns': ['sleep', 'insomnia', 'cant sleep', 'tired', 'fatigue', 'rest'],
            'responses': [
                "Good sleep hygiene: Maintain regular sleep schedule, create comfortable environment, avoid screens before bed, and limit caffeine. Adults need 7-9 hours of sleep nightly.",
                "For better sleep: Keep bedroom cool and dark, establish bedtime routine, avoid large meals before sleep, and exercise regularly (but not close to bedtime).",
                "Sleep improvement tips: Consistent sleep schedule, relaxing bedtime routine, comfortable mattress, and avoiding alcohol/caffeine before bed. See a doctor for persistent sleep issues."
            ]
        },
        
        'water': {
            'patterns': ['water', 'hydration', 'dehydration', 'thirsty', 'drink'],
            'responses': [
                "Stay hydrated by drinking 8-10 glasses of water daily. Increase intake during hot weather or exercise. Signs of dehydration include dark urine, dizziness, and dry mouth.",
                "Hydration is crucial for health. Drink water throughout the day, eat water-rich foods, and monitor urine color as hydration indicator.",
                "Water intake recommendations: About 8 cups daily for most adults, more if active or in hot climate. Include water-rich foods like fruits and vegetables."
            ]
        },
        
        # Emergency situations
        'emergency': {
            'patterns': ['emergency', 'urgent', 'serious', 'hospital', 'ambulance', 'help', 'chest pain', 'cant breathe', 'bleeding'],
            'responses': [
                "🚨 This sounds like an emergency! Please call emergency services immediately (911 in US, 102 in India) or go to the nearest emergency room. Don't delay seeking immediate medical attention.",
                "⚠️ For medical emergencies, call emergency services right away! For chest pain, difficulty breathing, severe bleeding, or loss of consciousness, seek immediate medical help.",
                "🚨 EMERGENCY: Call emergency services now! Don't wait - get immediate medical help for serious symptoms. Your safety is the priority."
            ]
        },
        
        # Medicine related
        'medicine': {
            'patterns': ['medicine', 'medication', 'pills', 'tablets', 'prescription', 'drug'],
            'responses': [
                "Always take medications as prescribed by your doctor. Don't skip doses, complete the full course, and inform your doctor about any side effects or other medications you're taking.",
                "Medicine safety: Take as directed, don't share prescriptions, store properly, check expiration dates, and ask your pharmacist about interactions.",
                "Medication tips: Set reminders for doses, keep an updated list of all medications, report adverse reactions to your doctor, and never stop prescribed medications without consulting your healthcare provider."
            ]
        },
        
        # Mental health
        'stress': {
            'patterns': ['stress', 'anxiety', 'worried', 'mental health', 'depression', 'sad'],
            'responses': [
                "Managing stress: Try deep breathing, regular exercise, adequate sleep, and talking to someone you trust. Consider professional help if stress affects daily life.",
                "For mental wellbeing: Practice relaxation techniques, maintain social connections, engage in hobbies, and don't hesitate to seek professional support when needed.",
                "Stress management: Regular exercise, healthy diet, sufficient sleep, mindfulness, and setting realistic goals. Reach out to mental health professionals if overwhelmed."
            ]
        },
        
        # Default responses
        'default': {
            'patterns': [],
            'responses': [
                "I understand you're asking about health. While I can provide general information, please consult a healthcare professional for personalized medical advice.",
                "That's a good health question! For specific medical concerns, I recommend speaking with a doctor or healthcare provider who can give you personalized guidance.",
                "I'm here to help with general health information. For specific symptoms or conditions, please consult with a qualified healthcare professional.",
                "Thanks for your question! Remember that I provide general health information only. For medical diagnosis or treatment, please see a healthcare provider."
            ]
        }
    }
    
    # Check for emergency keywords first
    emergency_keywords = ['emergency', 'urgent', 'chest pain', 'cant breathe', 'bleeding heavily', 'unconscious', 'stroke', 'heart attack']
    if any(keyword in user_message for keyword in emergency_keywords):
        return random.choice(responses['emergency']['responses'])
    
    # Find matching response category
    for category, data in responses.items():
        if category == 'default':
            continue
        
        for pattern in data['patterns']:
            if pattern in user_message:
                return random.choice(data['responses'])
    
    # If no specific pattern matches, return default response
    return random.choice(responses['default']['responses'])

def get_health_tips():
    """Return random health tips"""
    tips = [
        "💡 Drink at least 8 glasses of water daily to stay hydrated!",
        "💡 Aim for 7-9 hours of sleep each night for optimal health.",
        "💡 Include colorful fruits and vegetables in your daily meals.",
        "💡 Take regular breaks from screen time to rest your eyes.",
        "💡 Practice deep breathing exercises to reduce stress.",
        "💡 Wash your hands frequently to prevent infections.",
        "💡 Take the stairs instead of elevators when possible for extra exercise.",
        "💡 Keep a positive mindset - it's good for your mental and physical health!",
        "💡 Schedule regular check-ups with your healthcare provider.",
        "💡 Limit processed foods and choose whole, natural foods instead."
    ]
    
    return random.choice(tips)

def get_symptom_checker_response(symptoms):
    """Basic symptom checker with recommendations"""
    symptoms = symptoms.lower()
    
    # High priority symptoms requiring immediate attention
    urgent_symptoms = ['chest pain', 'difficulty breathing', 'severe bleeding', 'loss of consciousness', 
                      'severe headache', 'high fever', 'stroke symptoms', 'heart attack']
    
    if any(symptom in symptoms for symptom in urgent_symptoms):
        return "🚨 These symptoms require immediate medical attention! Please call emergency services or go to the nearest emergency room immediately."
    
    # Common symptom combinations
    if 'fever' in symptoms and 'cough' in symptoms:
        return "Fever and cough together may indicate an infection. Rest, stay hydrated, and consult a healthcare provider if symptoms persist or worsen."
    
    if 'headache' in symptoms and 'nausea' in symptoms:
        return "Headache with nausea can have various causes. Rest in a dark, quiet room and stay hydrated. See a doctor if symptoms are severe or persistent."
    
    if 'stomach pain' in symptoms and 'diarrhea' in symptoms:
        return "Stomach pain with diarrhea may indicate gastroenteritis. Stay hydrated with clear fluids and follow a bland diet. Consult a doctor if symptoms persist."
    
    return "I recommend consulting with a healthcare professional for proper evaluation of your symptoms. They can provide accurate diagnosis and appropriate treatment."
