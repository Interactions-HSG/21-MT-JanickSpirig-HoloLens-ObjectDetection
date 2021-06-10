from main import Run
from flask import Flask

app = Flask(__name__)

@app.route('/RunRecognition')
def RunRecognition():
    Run()

app.run()