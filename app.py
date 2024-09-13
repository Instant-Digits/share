from flask import Flask, request, jsonify
from flask_cors import CORS

import LabelCreate
from PrintLabel import PrintLabel


app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Hello, Flask with CORS!"

@app.route('/printLotNumber', methods=['POST'])
def print_lot_number():
    try:
        data = request.get_json()
        out=PrintLabel(LabelCreate.generateLotLabel(data))
        return jsonify(out)
    except Exception as e:
        print(f"Error:", e)
        # Return an error response if the request is not JSON
        return jsonify({
            'status': False,
            'message': str(e)
        }), 400



@app.route('/printSkidSticker', methods=['POST'])
def printSkidLabel():
    try:
        data = request.get_json()
        out=PrintLabel(LabelCreate.generateSkidLabel(data))
        return jsonify(out)
    except Exception as e:
        print(f"Error:", e)
        # Return an error response if the request is not JSON
        return jsonify({
            'status': False,
            'message': str(e)
        }), 400


# Run the application
if __name__ == '__main__':
    app.run(debug=True)
