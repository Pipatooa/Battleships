from flask import Flask
from flask import jsonify
from flask import request

import battleships

app = Flask(__name__)


@app.route('/', methods=["GET"])
def api_root():
    return jsonify({})


@app.route("/battleships", methods=["POST"])
def api_battleships():
    return jsonify(battleships.handle_request(request))


if __name__ == "__main__":
    app.run("0.0.0.0", threaded=True)
