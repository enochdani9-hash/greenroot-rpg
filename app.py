from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'immersive_rpg_key'

# This is your Narrative Engine. You write the story here.
STORY_GRAPH = {
    "prologue": {
        "location": "The Smoldering Ruins",
        "character": "Mysterious Stranger",
        "text": "The smoke clears. A figure in a ragged cloak steps over the debris, extending a gloved hand toward you. 'You're late,' they say, their voice laced with static.",
        "choices": [
            {"text": "Take their hand.", "next_scene": "take_hand", "stat_change": {"trust": 10}},
            {"text": "Draw your weapon.", "next_scene": "draw_weapon", "stat_change": {"hp": -10, "trust": -20}},
            {"text": "Ask who they are.", "next_scene": "ask_identity", "stat_change": {}}
        ]
    },
    "take_hand": {
        "location": "Hidden Safehouse",
        "character": "Elara (The Stranger)",
        "text": "She pulls you up effortlessly. 'I'm Elara. We don't have much time before the sector goes into lockdown. Grab your gear.'",
        "choices": [
            {"text": "Follow her inside.", "next_scene": "inside_safehouse", "stat_change": {}},
            {"text": "Refuse to move until she explains.", "next_scene": "demand_answers", "stat_change": {"trust": -5}}
        ]
    },
    "draw_weapon": {
        "location": "The Smoldering Ruins",
        "character": "Mysterious Stranger",
        "text": "Before your blade even clears its sheath, they disarm you with a brutal kick to your ribs. You lose 10 HP. 'Foolish,' they spit. 'I'm trying to save your life.'",
        "choices": [
            {"text": "Yield and listen.", "next_scene": "take_hand", "stat_change": {}},
            {"text": "Fight back barehanded.", "next_scene": "game_over_death", "stat_change": {"hp": -100}}
        ]
    },
    # You can add hundreds of scenes here!
}

@app.route('/', methods=['GET'])
def index():
    if 'current_scene' not in session:
        return render_template('start.html')
    
    scene_data = STORY_GRAPH.get(session['current_scene'])
    return render_template('game.html', scene=scene_data, session=session)

@app.route('/start', methods=['POST'])
def start_game():
    session['name'] = request.form.get('name', 'Wanderer').strip()
    session['hp'] = 100
    session['trust'] = 50 # Relationship meter with companions
    session['current_scene'] = "prologue"
    return redirect(url_for('index'))

@app.route('/make_choice', methods=['POST'])
def make_choice():
    choice_index = int(request.form.get('choice_index'))
    current_scene_data = STORY_GRAPH.get(session['current_scene'])
    selected_choice = current_scene_data['choices'][choice_index]
    
    # Apply any stat changes from the choice
    if 'stat_change' in selected_choice:
        for stat, value in selected_choice['stat_change'].items():
            session[stat] = session.get(stat, 0) + value
            
    # Move to the next scene
    session['current_scene'] = selected_choice['next_scene']
    
    # Check for death
    if session.get('hp', 100) <= 0:
        session.clear()
        return "You died. <a href='/'>Restart</a>" # We can make a proper death screen later
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
