from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'ashen_path_dark_fantasy_key'

# The Narrative Engine: Now with HD Image Support and Expanded Paths
STORY_GRAPH = {
    "prologue": {
        "location": "The Cursed Woods of Oakhaven",
        "character": "The Blind Oracle",
        "image": "https://images.unsplash.com/photo-1541535881962-3bb3ecbb3bbb?auto=format&fit=crop&w=800&q=80",
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
        "image": "https://images.unsplash.com/photo-1541535881962-3bb3ecbb3bbb?auto=format&fit=crop&w=800&q=80",
        "text": "She cackles, the sound like dry leaves scraping on stone. 'Vengeance is a heavy blade. It cuts the wielder as deeply as the foe.' She points a gnarled finger toward a narrow path choked with thorns. 'The beast lairs in the Sunken Keep.'",
        "choices": [
            {"text": "Walk the thorny path to the keep.", "next_scene": "the_sunken_keep", "stat_change": {"hp": -10}},
            {"text": "Demand she give you a weapon of blood magic first.", "next_scene": "learn_magic", "stat_change": {"corruption": 15}}
        ]
    },
    "path_of_light": {
        "location": "The Cursed Woods of Oakhaven",
        "character": "The Blind Oracle",
        "image": "https://images.unsplash.com/photo-1541535881962-3bb3ecbb3bbb?auto=format&fit=crop&w=800&q=80",
        "text": "Her expression softens, though her sightless eyes remain unsettling. 'A noble fool. The plague is a curse of the soil. To cleanse it, you must find the Heart of the Forest.' She hands you a faintly glowing talisman.",
        "choices": [
            {"text": "Take the talisman and head deeper into the woods.", "next_scene": "heart_of_forest", "stat_change": {"hope": 15}},
            {"text": "Refuse the witch's trinket and trust your own steel.", "next_scene": "reject_magic", "stat_change": {"corruption": 5}}
        ]
    },
    "hostile_oracle": {
        "location": "The Cursed Woods of Oakhaven",
        "character": "The Blind Oracle",
        "image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80",
        "text": "Before your sword clears the scabbard, the campfire erupts. Searing ash blinds you. When the smoke clears, she is gone. Only two paths remain.",
        "choices": [
            {"text": "Stumble blindly down the blood-stained path.", "next_scene": "the_sunken_keep", "stat_change": {}},
            {"text": "Follow the faint glow deeper into the trees.", "next_scene": "heart_of_forest", "stat_change": {}}
        ]
    },
    "the_sunken_keep": {
        "location": "The Sunken Keep",
        "character": "Sir Kaelen, the Ashen Knight",
        "image": "https://images.unsplash.com/photo-1605639732731-9a7493a38a7c?auto=format&fit=crop&w=800&q=80",
        "text": "The ruins rise from the stagnant swamp. Blocking the grand archway is a towering knight. His armor is fused to his flesh by dark magic, glowing with a dull, terrifying heat. 'None pass the Ashen Guard,' his voice booms from inside the helm.",
        "choices": [
            {"text": "Draw your weapon. 'I am not asking for permission.'", "next_scene": "fight_kaelen", "stat_change": {"corruption": 5}},
            {"text": "Show him the marks of the plague. Beg for entry.", "next_scene": "plead_kaelen", "stat_change": {"hope": 5}}
        ]
    },
    "heart_of_forest": {
        "location": "The Deep Woods",
        "character": "The Rootbound Spirit",
        "image": "https://images.unsplash.com/photo-1519074069444-1ba4fff66d16?auto=format&fit=crop&w=800&q=80",
        "text": "You enter a clearing where the trees are ancient, their roots pulsing with a sickly purple light. A spirit made of shattered wood and crying moss emerges from the earth. 'The soil screams,' it whispers. 'Will you share its pain?'",
        "choices": [
            {"text": "Use the talisman to purify the spirit.", "next_scene": "purify_spirit", "stat_change": {"hope": 20}},
            {"text": "Strike the abomination down.", "next_scene": "kill_spirit", "stat_change": {"corruption": 20}}
        ]
    },
    "learn_magic": {
        "location": "The Oracle's Camp",
        "character": "The Blind Oracle",
        "image": "https://images.unsplash.com/photo-1541535881962-3bb3ecbb3bbb?auto=format&fit=crop&w=800&q=80",
        "text": "You offer your arm. She slices your palm, whispering dark incantations. Power surges through you, cold and ruthless. You are ready to face the Keep.",
        "choices": [{"text": "March to the Sunken Keep.", "next_scene": "the_sunken_keep", "stat_change": {}}]
    },
    "reject_magic": {
        "location": "The Deep Woods",
        "character": "None",
        "image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80",
        "text": "You walk alone. The darkness seems to press in tighter without the talisman's light. The trees begin to whisper your name.",
        "choices": [{"text": "Keep moving forward.", "next_scene": "heart_of_forest", "stat_change": {}}]
    },
    # Endings for this chapter
    "fight_kaelen": {
        "location": "The Sunken Keep Courtyard",
        "character": "Sir Kaelen",
        "image": "https://images.unsplash.com/photo-1605639732731-9a7493a38a7c?auto=format&fit=crop&w=800&q=80",
        "text": "Blades clash in the muck. You manage to slip your sword between his armor plates, but his fiery counterattack leaves you badly burned. You survive, but the keep is dark and full of terrors. [END OF CHAPTER 1]",
        "choices": [{"text": "Play Again", "next_scene": "prologue", "stat_change": {}}]
    },
    "plead_kaelen": {
        "location": "The Sunken Keep Courtyard",
        "character": "Sir Kaelen",
        "image": "https://images.unsplash.com/photo-1605639732731-9a7493a38a7c?auto=format&fit=crop&w=800&q=80",
        "text": "He looks at your wounds. The fiery glow inside his helmet dims. 'Another victim,' he sighs, stepping aside. 'May the gods have mercy on what you find inside.' [END OF CHAPTER 1]",
        "choices": [{"text": "Play Again", "next_scene": "prologue", "stat_change": {}}]
    },
    "purify_spirit": {
        "location": "The Cleansed Grove",
        "character": "The Rootbound Spirit",
        "image": "https://images.unsplash.com/photo-1519074069444-1ba4fff66d16?auto=format&fit=crop&w=800&q=80",
        "text": "The talisman flares with blinding white light. The purple rot recedes, and the spirit bows to you before turning into a bed of fresh spring flowers. The plague here is broken. [END OF CHAPTER 1]",
        "choices": [{"text": "Play Again", "next_scene": "prologue", "stat_change": {}}]
    },
    "kill_spirit": {
        "location": "The Rotting Grove",
        "character": "The Rootbound Spirit",
        "image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80",
        "text": "You hack the spirit to pieces. Black sap coats your blade. You have survived, but the woods feel even darker now. You feel the corruption taking root in your own heart. [END OF CHAPTER 1]",
        "choices": [{"text": "Play Again", "next_scene": "prologue", "stat_change": {}}]
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
