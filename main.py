import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from uuid import uuid4
from utils import load_bookmarks, save_bookmarks, bookmark_is_valid


app = Flask(__name__)
CORS(app)

app.config.from_mapping(
    BOOKMARKS_FILE='./bookmarks.json',
    PORT=5000
)

logging.basicConfig(level=logging.INFO)


@app.route('/bookmarks', methods=['GET'])
def get_bookmarks():
    try:
        data = load_bookmarks(app.config['BOOKMARKS_FILE'])
        if len(data["bookmarks"]) == 0:
            return jsonify({"bookmarks": []}), 200
        return jsonify(data)
    except Exception:
        return jsonify({'error': 'Unable to access bookmarks.'}), 500


@app.route('/bookmarks/<string:id>', methods=['GET'])
def get_bookmark_by_id(id):
    try:
        data = load_bookmarks(app.config['BOOKMARKS_FILE'])
        bookmark = next((b for b in data["bookmarks"] if b["id"] == id), None)
        if bookmark:
            return jsonify(bookmark)
        else:
            jsonify({'error': 'No bookmark with this id exists.'}), 404

    except Exception:
        return jsonify({'error': 'Unable to access bookmarks.'}), 500


@app.route('/bookmarks', methods=['POST'])
def create_bookmark():
    if not request.is_json:
        return jsonify({'error': 'Invalid content type.'}), 415
    bookmark = request.get_json()
    if not bookmark_is_valid(bookmark):
        return jsonify({'error': 'Invalid bookmark data.'}), 400

    try:
        data = load_bookmarks(app.config['BOOKMARKS_FILE'])
        print(data)
        new_bookmark = {
            "title": bookmark["title"],
            "url": bookmark["url"],
            "id": str(uuid4())
        }
        data["bookmarks"].append(new_bookmark)
        save_bookmarks(data, app.config['BOOKMARKS_FILE'])
        return jsonify(new_bookmark), 201
    except Exception:
        return jsonify({'error': 'Could not save bookmark.'}), 500


@app.route('/bookmarks/<string:id>', methods=['PUT'])
def update_bookmark(id):
    if not request.is_json:
        return jsonify({'error': 'Invalid content type.'}), 415
    updated_data = request.get_json()
    if not bookmark_is_valid(updated_data):
        return jsonify({'error': 'Invalid bookmark data.'}), 400

    try:
        data = load_bookmarks(app.config['BOOKMARKS_FILE'])
        bookmark = next((b for b in data["bookmarks"] if b["id"] == id), None)
        if not bookmark:
            return jsonify({'error': 'No bookmark with this id exists.'}), 404
        bookmark.update(updated_data)
        save_bookmarks(data, app.config['BOOKMARKS_FILE'])
        return jsonify(bookmark)
    except Exception:
        return jsonify({'error': 'Unable to update bookmark.'}), 500


@app.route('/bookmarks/<string:id>', methods=['DELETE'])
def delete_bookmark(id):
    try:
        data = load_bookmarks(app.config['BOOKMARKS_FILE'])
        bookmarks = data["bookmarks"]
        if id not in [b["id"] for b in bookmarks]:
            return jsonify({'error': 'No bookmark with this id exists.'}), 404
        data["bookmarks"] = [b for b in bookmarks if b["id"] != id]
        save_bookmarks(data, app.config['BOOKMARKS_FILE'])
        return jsonify({'success': f'Bookmark with id {id} deleted.'})
    except Exception:
        return jsonify({'error': 'Unable to delete bookmark.'}), 500


if __name__ == '__main__':
    app.run(port=app.config['PORT'])
