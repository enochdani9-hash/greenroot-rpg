from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'ashen_path_dark_fantasy_key'

# The Narrative Engine: Your Dark Fantasy Script
STORY_GRAPH = {
    "prologue": {
        "location": "The Cursed Woods of Oakhaven",
        "character": "The Blind Oracle",
        "text": "The twisted branches block out the moonlight. A withered woman sits by a dying fire, her eyes milky white. 'Another soul wanders into the rot,' she croaks, tossing a handful of bone dust into the embers. 'Tell me, wanderer... what do you seek in the cursed lands?'",
        "choices": [
            {"text": "'I seek the beast that slaughtered my kin.' (Vengeance)", "next_scene": "path_of_blood", "stat_change": {"corruption": 10}},
            {"text": "'I seek a cure for the plague.' (Mercy)", "next_scene": "path_of_light", "stat_change": {"hope": 10}},
            {"text": "Draw your silver sword and demand she let you pass.", "next_scene": "hostile_oracle", "stat_change": {"hp": -15, "corruption": 5}}
        ]
    },
    "path_of_blood": {
        "location": "The Cursed Woods of Oakhaven",
        "character": "The Blind Oracle",
        "text": "She cackles, the sound like dry leaves scraping on stone. 'Vengeance is a heavy blade. It cuts the wielder as deeply as the foe.' She points a gnarled finger toward a narrow path choked with thorns. 'The beast lairs in the Sunken Keep. But you will need blood magic to open the gates.'",
        "choices": [
            {"text": "Walk the thorny path.", "next_scene": "the_sunken_keep", "stat_change": {"hp": -10}},
            {"text": "Ask her to teach you blood magic.", "next_scene": "learn_magic", "stat_change": {"corruption": 20}}
        ]
    },
    "path_of_light": {
        "location": "The Cursed Woods of Oakhaven",
        "character": "The Blind Oracle",
        "text": "Her expression softens, though her sightless eyes remain unsettling. 'A noble fool. The plague is not a sickness of the body, but a curse of the soil. To cleanse it, you must find the Heart of the Forest.' She hands you a faintly glowing talisman.",
        "choices": [
            {"text": "Take the talisman and head deeper into the woods.", "next_scene": "heart_of_forest", "stat_change": {"hope": 15}},
            {"text": "Refuse the witch's trinket and trust your own steel.", "next_scene": "reject_magic", "stat_change": {"corruption": 5}}
        ]
    },
    "hostile_oracle": {
        "location": "The Cursed Woods of Oakhaven",
        "character": "The Blind Oracle",
        "text": "Before your sword clears the scabbard, the campfire erupts. Searing ash blinds you, burning your lungs. When the smoke clears, she is gone, leaving only an echoing whisper: 'The woods will claim you.'",
        "choices": [
            {"text": "Stumble blindly down the left path.", "next_scene": "the_sunken_keep", "stat_change": {}},
            {"text": "Stumble blindly down the right path.", "next_scene": "heart_of_forest", "stat_change": {}}
        ]
    },
    # These are placeholders for the next branches you write!
    "the_sunken_keep": {
        "location": "The Sunken Keep",
        "character": "None",
        "text": "The ruins of the keep rise from the stagnant swamp. (To be continued...)",
        "choices": [{"text": "Restart Game", "next_scene": "prologue", "stat_change": {}}]
    },
    "learn_magic": {
        "location": "The Oracle's Camp",
        "character": "The Blind Oracle",
        "text": "You offer your arm. She slices your palm, whispering dark incantations. Power surges through you, cold and ruthless. (To be continued...)",
        "choices": [{"text": "Restart Game", "next_scene": "prologue", "stat_change": {}}]
    },
    "heart_of_forest": {
        "location": "The Deep Woods",
        "character": "None",
        "text": "The trees here are ancient, their roots pulsing with a faint, sickly purple light. (To be continued...)",
        "choices": [{"text": "Restart Game", "next_scene": "prologue", "stat_change": {}}]
    },
    "reject_magic": {
        "location": "The Deep Woods",
        "character": "None",
        "text": "You walk alone. The darkness seems to press in tighter without the talisman's light. (To be continued...)",
        "choices": [{"text": "Restart Game", "next_scene": "prologue", "stat_change": {}}]
    }
}

@app.route('/', methods=['GET'])
def index():
    if 'current_scene' not in session:
        return render_template('start.html')
    
    scene_data = STORY_GRAPH.get(session['current_scene'])
    return render_template('game.html', scene=scene_data, session=session)

@app.route('/start', methods=['POST'])
def start_game():
    session.clear()
    session['name'] = request.form.get('name', 'Wanderer').strip()
    session['hp'] = 100
    session['corruption'] = 0
    session['hope'] = 0
    session['current_scene'] = "prologue"
    return redirect(url_for('index'))

@app.route('/make_choice', methods=['POST'])
def make_choice():
    choice_index = int(request.form.get('choice_index'))
    current_scene_data = STORY_GRAPH.get(session['current_scene'])
    selected_choice = current_scene_data['choices'][choice_index]
    
    if 'stat_change' in selected_choice:
        for stat, value in selected_choice['stat_change'].items():
            session[stat] = session.get(stat, 0) + value
            
    session['current_scene'] = selected_choice['next_scene']
    
    if session.get('hp', 100) <= 0:
        session.clear()
        session['death_message'] = "Your blood waters the cursed earth. You have died."
        return render_template('start.html', message=session['death_message'])
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
