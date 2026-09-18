from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'greenroot_secret_key_change_in_production'

@app.route('/', methods=['GET'])
def index():
    if 'started' not in session:
        return render_template('start.html')
    return render_template('game.html', session=session)

@app.route('/start', methods=['POST'])
def start_game():
    name = request.form.get('name', 'Agronaut').strip()
    session['name'] = name if name else "Agronaut"
    session['hp'] = 100
    session['max_hp'] = 100
    session['gold'] = 50
    session['location'] = 'Farm Homestead'
    session['inventory'] = {'tomato_seeds': 3, 'corn_seeds': 2}
    session['crops'] = {'tomatoes': 0, 'corn': 0}
    session['plot_state'] = 'empty'
    session['crop_type'] = None
    session['growth_turns'] = 0
    session['message'] = f"Welcome, {session['name']}! Your agricultural journey begins."
    session['started'] = True
    return redirect(url_for('index'))

@app.route('/action', methods=['POST'])
def handle_action():
    action = request.form.get('action')
    loc = session.get('location')
    msg = ""
    
    # Navigation
    if action == 'travel_north' and loc == 'Farm Homestead':
        session['location'] = 'Wild Fields'
        msg = "🚶 You traveled north to the Wild Fields."
    elif action == 'travel_east':
        if loc == 'Farm Homestead':
            session['location'] = 'Village Market'
            msg = "🚶 You arrived at the Village Market."
        elif loc == 'Wild Fields':
            session['location'] = 'Deep Forest'
            msg = "🚶 You ventured deep into the shadowed forest."
    elif action == 'travel_south' and loc == 'Wild Fields':
        session['location'] = 'Farm Homestead'
        msg = "🚶 You returned to your Farm Homestead."
    elif action == 'travel_west':
        if loc == 'Village Market':
            session['location'] = 'Farm Homestead'
            msg = "🚶 You returned to your Farm Homestead."
        elif loc == 'Deep Forest':
            session['location'] = 'Wild Fields'
            msg = "🚶 You retreated back to the Wild Fields."
            
    # Farming actions
    elif action == 'plant_tomato':
        inv = session['inventory']
        if session['plot_state'] == 'empty' and inv.get('tomato_seeds', 0) > 0:
            inv['tomato_seeds'] -= 1
            session['plot_state'] = 'growing'
            session['crop_type'] = 'tomatoes'
            session['growth_turns'] = 2
            msg = "🌱 You planted tomato seeds in your plot!"
        else:
            msg = "❌ Cannot plant right now or no seeds left."
    elif action == 'tend_plot':
        if session['plot_state'] == 'growing':
            session['growth_turns'] -= 1
            msg = "💧 You watered and weeded the plot."
            if session['growth_turns'] <= 0:
                session['plot_state'] = 'ready'
                msg = "✨ Your tomatoes have fully matured and are ready to harvest!"
        else:
            msg = "❌ Nothing to tend."
    elif action == 'harvest_plot':
        if session['plot_state'] == 'ready':
            c = session['crop_type']
            session['crops'][c] += 3
            session['plot_state'] = 'empty'
            session['crop_type'] = None
            msg = f"🎉 Successful harvest! Collected 3x fresh {c}."
        else:
            msg = "❌ Plot is not ready for harvest."
            
    # Market actions
    elif action == 'buy_tomato_seeds':
        if session['gold'] >= 10:
            session['gold'] -= 10
            session['inventory']['tomato_seeds'] = session['inventory'].get('tomato_seeds', 0) + 1
            msg = "✅ Purchased 1x Tomato Seeds for 🪙 10."
        else:
            msg = "❌ Not enough gold!"
    elif action == 'sell_crops':
        total_earned = 0
        for c, count in session['crops'].items():
            if count > 0:
                total_earned += count * 8
                session['crops'][c] = 0
        if total_earned > 0:
            session['gold'] += total_earned
            msg = f"💰 Sold all crops for 🪙 {total_earned} gold!"
        else:
            msg = "❌ You have no crops to sell."
            
    session['message'] = msg
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)