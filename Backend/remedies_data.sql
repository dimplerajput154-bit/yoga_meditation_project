
USE ai_wellness_db;

INSERT INTO health_remedies
(topic, symptoms, self_care_info, precautions, when_to_consult_doctor)
VALUES

(
'Common Cold',
'Runny nose, sneezing, mild cough, sore throat and tiredness.',
'Drink warm fluids, take adequate rest and consider a gentle saline nasal rinse for comfort.',
'Maintain good hand hygiene and avoid sharing personal items.',
'Consult a doctor if symptoms become severe, persist unusually long, or breathing difficulty develops.'
),

(
'Mild Cough',
'Occasional coughing, throat irritation or mucus.',
'Drink warm water or other warm fluids. Honey may soothe a cough in adults and children over 1 year of age.',
'Never give honey to a child below 1 year of age.',
'Seek medical advice for breathing difficulty, chest pain, coughing blood, or a persistent or worsening cough.'
),

(
'Mild Sore Throat',
'Throat pain, dryness, irritation or discomfort while swallowing.',
'Drink warm fluids and gargle with warm salt water if comfortable.',
'Do not swallow the salt-water gargle.',
'Consult a doctor if swallowing or breathing becomes difficult or symptoms are severe.'
),

(
'Headache',
'Mild head pain or pressure.',
'Rest in a quiet environment, drink enough water and take a break from screens.',
'Avoid ignoring headaches that are sudden, severe or unusual.',
'Seek urgent medical care for a sudden severe headache, confusion, weakness or vision problems.'
),

(
'Indigestion',
'Feeling of fullness, mild bloating or stomach discomfort.',
'Eat smaller meals, eat slowly and drink enough water.',
'Avoid foods that repeatedly trigger your symptoms.',
'Consult a doctor if indigestion is frequent, severe or associated with chest pain, vomiting or unexplained weight loss.'
),

(
'Mild Gas',
'Bloating, burping or passing gas.',
'Drink water and take a gentle walk to support comfortable digestion.',
'Eat slowly and avoid foods that consistently cause discomfort.',
'Seek medical advice if gas is severe, persistent or accompanied by significant abdominal pain.'
),

(
'Bloating',
'Feeling of fullness or swelling in the abdomen.',
'Eat smaller meals, drink water and take a gentle walk.',
'Avoid overeating and foods that repeatedly cause bloating.',
'Consult a doctor if bloating is persistent, painful or associated with vomiting.'
),

(
'Mild Constipation',
'Hard stools, difficulty passing stool or feeling of incomplete emptying.',
'Drink adequate water and include fiber-rich foods such as fruits, vegetables and whole grains.',
'Increase dietary fiber gradually and drink enough fluids.',
'Consult a doctor if constipation is persistent or accompanied by severe pain, vomiting or blood in stool.'
),

(
'Mild Acidity',
'Heartburn or burning discomfort after meals.',
'Try smaller meals and avoid lying down immediately after eating.',
'Avoid foods and drinks that repeatedly trigger symptoms.',
'Seek medical advice if symptoms are frequent, severe or associated with chest pain or difficulty swallowing.'
),

(
'Nausea',
'Feeling like you may vomit or reduced appetite.',
'Take small sips of water and try small portions of bland foods if tolerated.',
'Avoid large meals when feeling nauseated.',
'Consult a doctor if vomiting is persistent, severe dehydration occurs or there is severe abdominal pain.'
),

(
'Mild Fatigue',
'Low energy, tiredness or reduced concentration.',
'Get adequate sleep, drink water and eat balanced meals.',
'Avoid overexertion when feeling unusually tired.',
'Consult a doctor if unexplained fatigue persists or significantly affects daily activities.'
),

(
'Muscle Soreness',
'Muscle tenderness, stiffness or mild discomfort.',
'Rest the affected area and use gentle stretching or a warm compress if comfortable.',
'Avoid strenuous exercise if pain is significant.',
'Seek medical advice for severe pain, major swelling, weakness or injury.'
),

(
'Neck Stiffness',
'Tightness or reduced comfortable neck movement.',
'Use gentle neck movements and a warm compress if comfortable.',
'Do not forcefully stretch or twist the neck.',
'Seek medical attention if stiffness follows an injury or occurs with severe headache, fever or neurological symptoms.'
),

(
'Mild Back Discomfort',
'Mild aching, stiffness or discomfort.',
'Avoid staying in one position for too long and perform gentle stretching.',
'Avoid movements that increase pain.',
'Seek medical care for severe pain, weakness, numbness or bladder or bowel changes.'
),

(
'Minor Stress',
'Feeling tense, worried, restless or mentally tired.',
'Try slow deep breathing, relaxation exercises and take a short break.',
'Do not rely only on self-care if stress becomes overwhelming.',
'Seek professional support if stress is persistent or seriously affects daily functioning.'
),

(
'Sleep Difficulty',
'Difficulty falling asleep or staying asleep.',
'Maintain a relaxing bedtime routine and reduce screen use before bed.',
'Avoid using unprescribed sleep medicines.',
'Consult a healthcare professional if sleep problems continue regularly.'
),

(
'Mild Anxiety Feelings',
'Worry, restlessness, tension or difficulty relaxing.',
'Try slow breathing, grounding exercises and spend some time in a quiet environment.',
'Self-care should not replace professional mental-health support.',
'Seek professional help if anxiety is persistent, severe or affects daily life.'
),

(
'Eye Strain',
'Tired eyes, temporary blurred vision or eye discomfort.',
'Follow the 20-20-20 approach: every 20 minutes, look at something about 20 feet away for around 20 seconds.',
'Take regular screen breaks and use comfortable lighting.',
'Consult an eye-care professional if pain or vision changes persist.'
),

(
'Dry Eyes',
'Dryness, burning, irritation or a gritty feeling.',
'Take screen breaks, blink regularly and avoid direct exposure to strong airflow.',
'Avoid rubbing the eyes.',
'Seek professional advice if symptoms are persistent or vision is affected.'
),

(
'Mild Sunburn',
'Redness, warmth and mild skin discomfort.',
'Use a cool damp cloth for comfort, stay out of direct sun and keep skin moisturized.',
'Avoid further sun exposure while the skin is healing.',
'Seek medical care for severe burns, extensive blistering, confusion or other serious symptoms.'
),

(
'Dry Skin',
'Tightness, flaking or rough skin.',
'Use moisturizer regularly and prefer lukewarm rather than very hot baths or showers.',
'Avoid harsh products that irritate the skin.',
'Consult a doctor if skin becomes severely cracked, painful or infected.'
),

(
'Minor Itching',
'Itchy or irritated skin.',
'Apply a cool compress and avoid scratching the area.',
'Avoid products that appear to trigger irritation.',
'Seek medical care if itching is severe, widespread or associated with swelling or breathing difficulty.'
),

(
'Minor Insect Bite',
'Small area of redness, itching or swelling.',
'Wash the area gently and use a cool compress for comfort.',
'Avoid scratching the affected area.',
'Seek urgent help if swelling of the face or throat or breathing difficulty occurs.'
),

(
'Mild Muscle Cramp',
'Sudden painful muscle tightening.',
'Gently stretch the affected muscle and drink water.',
'Do not forcefully stretch a painful muscle.',
'Consult a doctor if cramps are frequent, severe or unexplained.'
),

(
'Mild Dehydration',
'Thirst, dry mouth, tiredness or darker urine.',
'Drink water gradually and replace fluids after normal activity or sweating.',
'Do not ignore worsening dehydration symptoms.',
'Seek medical care for severe weakness, confusion, fainting or inability to keep fluids down.'
),

(
'Mild Fever',
'Increased body temperature, tiredness or sweating.',
'Rest, drink adequate fluids and monitor temperature.',
'Do not use home remedies as a substitute for medical evaluation when needed.',
'Seek medical advice for very high or persistent fever, breathing difficulty, confusion or severe weakness.'
),

(
'Nasal Congestion',
'Blocked nose, difficulty breathing through the nose or mucus.',
'Drink warm fluids and consider a gentle saline nasal rinse.',
'Use saline products according to their instructions.',
'Consult a doctor if congestion is severe, persistent or associated with breathing difficulty.'
),

(
'Sneezing and Mild Allergy Symptoms',
'Sneezing, runny nose or itchy eyes.',
'Avoid known triggers and keep the surrounding environment clean.',
'Do not use medicines without appropriate guidance.',
'Seek urgent help if there is facial or throat swelling or breathing difficulty.'
),

(
'Mild Hoarseness',
'Raspy, weak or altered voice.',
'Rest your voice and drink warm fluids.',
'Avoid shouting or prolonged voice use.',
'Consult a doctor if hoarseness persists, worsens or is associated with breathing difficulty.'
),

(
'Mild Menstrual Cramps',
'Cramping or aching in the lower abdomen.',
'A warm compress and gentle physical activity may provide comfort.',
'Avoid anything that increases pain or discomfort.',
'Consult a doctor if pain is severe, unusual, suddenly worse or significantly interferes with daily activities.'
);