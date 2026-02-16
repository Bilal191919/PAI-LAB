from flask import Flask, render_template, request
import requests

app = Flask(__name__)

JOKE_API_URL = "https://official-joke-api.appspot.com/random_joke"

@app.route('/', methods=['GET', 'POST'])
def home():
    joke_data = None
    error = None

    if request.method == 'POST':
        try:
            response = requests.get(JOKE_API_URL)
            
            if response.status_code == 200:
                joke_data = response.json()
            else:
                error = "Failed to retrieve joke. Please try again."
        except Exception as e:
            error = f"An error occurred: {e}"

    return render_template('index.html', joke=joke_data, error=error)

if __name__ == '__main__':
    print("Starting Flask App...")
    print("Go to http://127.0.0.1:5000/ to get a joke!")
    app.run(debug=True)
