from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'custom_engine_key'

@app.route('/')
def game_engine():
    # Serves the custom game engine to the browser
    return render_template('engine.html')

if __name__ == '__main__':
    app.run(debug=True)
