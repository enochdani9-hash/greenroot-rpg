import random
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'super_secret_forge_key'

# A tiny sample dictionary for testing. In a real game, we'd use a large text file.
VALID_WORDS = {"CAT", "BAT", "FARM", "CODE", "GAME", "PYTHON", "SWORD", "MAGIC", "FIRE", "ICE", "RUN"}

def generate_letters():
    vowels = "AEIOU"
    consonants = "BCDFGHJKLMNPQRSTVWXYZ"
    # Ensure they always get at least 2 vowels and 5 consonants
    letters = random.choices(vowels, k=2) + random.choices(consonants, k=5)
    random.shuffle(letters)
    return letters

@app.route('/', methods=['GET'])
def index():
    if 'started' not in session:
        return render_template('start.html')
    return render_template('game.html', session=session)

@app.route('/start', methods=['POST'])
def start_game():
    session['name'] = request.form.get('name', 'Hero').strip()
    session['hp'] = 50
    session['max_hp'] = 50
    session['gold'] = 0
    session['level'] = 1
    session['monster_name'] = "Goblin"
    session['monster_hp'] = 15
    session['monster_max_hp'] = 15
    session['current_letters'] = generate_letters()
    session['message'] = "A wild Goblin appears! Form a word to attack!"
    session['started'] = True
    return redirect(url_for('index'))

@app.route('/attack', methods=['POST'])
def attack():
    word = request.form.get('word', '').strip().upper()
    available_letters = list(session['current_letters'])
    
    # 1. Validate the word can be made from the letters
    valid_creation = True
    for char in word:
        if char in available_letters:
            available_letters.remove(char)
        else:
            valid_creation = False
            break
            
    if not valid_creation:
        session['message'] = f"❌ You can't spell '{word}' with your current letters!"
        return redirect(url_for('index'))
        
    # 2. Check if it's a real word (using our tiny dictionary for now)
    if word not in VALID_WORDS:
        session['message'] = f"❌ '{word}' is not a valid word!"
        return redirect(url_for('index'))
        
    # 3. Calculate Damage (Length of word = Damage)
    damage = len(word) * 2 
    session['monster_hp'] -= damage
    
    if session['monster_hp'] <= 0:
        # Monster Defeated!
        gold_earned = random.randint(5, 15)
        session['gold'] += gold_earned
        session['level'] += 1
        
        # Spawn new monster
        session['monster_name'] = random.choice(["Orc", "Troll", "Dragon", "Slime"])
        session['monster_max_hp'] = 10 + (session['level'] * 5)
        session['monster_hp'] = session['monster_max_hp']
        session['current_letters'] = generate_letters()
        
        session['message'] = f"💥 '{word}' dealt {damage} damage! You defeated the monster and found 🪙 {gold_earned} Gold! A new {session['monster_name']} appears!"
    else:
        # Monster hits back
        monster_damage = random.randint(2, 5)
        session['hp'] -= monster_damage
        session['current_letters'] = generate_letters() # New letters each turn
        session['message'] = f"⚔️ '{word}' dealt {damage} damage! The {session['monster_name']} hit you for {monster_damage} damage."
        
        if session['hp'] <= 0:
            session.clear()
            session['message'] = "💀 You have been defeated. Game Over."
            return render_template('start.html', message=session['message'])

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
