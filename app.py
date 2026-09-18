from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'ashen_path_action_key'

STORY_GRAPH = {
    "prologue": {
        "location": "The Cursed Woods",
        "character": "The Blind Oracle",
        "text": "The twisted branches block out the moonlight. A withered woman sits by a dying fire. 'What do you seek?' she croaks.",
        "choices": [
            {"text": "Ask her for guidance.", "next_scene": "path_of_light", "stat_change": {"hope": 10}},
            # Notice the new "is_action" and "enemy_name" keys below!
            {"text": "Draw your sword and attack!", "next_scene": "hostile_oracle", "stat_change": {"corruption": 5}, "is_action": True, "enemy_name": "The Blind Oracle"}
        ]
    },
    "path_of_light": {
        "location": "The Deep Woods",
        "character": "None",
        "text": "You walk peacefully into the woods.",
        "choices": [{"text": "Restart", "next_scene": "prologue", "stat_change": {}}]
    },
    "hostile_oracle": {
        "location": "The Oracle's Camp",
        "character": "The Blind Oracle",
        "text": "You stand over the defeated Oracle, your blade dripping. The woods grow darker.",
        "choices": [{"text": "Continue deeper.", "next_scene": "prologue", "stat_change": {}}]
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
    session['current_scene'] = "prologue"
    return redirect(url_for('index'))

@app.route('/make_choice', methods=['POST'])
def make_choice():
    choice_index = int(request.form.get('choice_index'))
    current_scene_data = STORY_GRAPH.get(session['current_scene'])
    selected_choice = current_scene_data['choices'][choice_index]
    
    # Apply stats
    if 'stat_change' in selected_choice:
        for stat, value in selected_choice['stat_change'].items():
            session[stat] = session.get(stat, 0) + value

    # Check if this choice triggers a 2D Action Scene
    if selected_choice.get('is_action'):
        session['enemy_name'] = selected_choice.get('enemy_name', 'Enemy')
        session['win_scene'] = selected_choice['next_scene']
        return render_template('action.html', session=session)
            
    # Otherwise, just go to the next text scene
    session['current_scene'] = selected_choice['next_scene']
    return redirect(url_for('index'))

# This route catches the player after they win the 2D mini-game
@app.route('/action_win', methods=['POST'])
def action_win():
    session['current_scene'] = session.get('win_scene', 'prologue')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
