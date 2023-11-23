import json
import logging
import os


def load_bookmarks(bookmarks_file):
    if not os.path.exists(bookmarks_file):
        logging.info(f"'{bookmarks_file}' not found. Creating a new file.")
        with open(bookmarks_file, "w") as file:
            json.dump({"bookmarks": []}, file, indent=4)

    try:
        with open(bookmarks_file, "r") as file:
            return json.load(file)
    except (IOError, json.JSONDecodeError) as e:
        logging.error(f"Error loading bookmarks: {e}")
        raise


def save_bookmarks(data, bookmarks_file):
    try:
        with open(bookmarks_file, "w") as file:
            json.dump(data, file, indent=4)
    except IOError as e:
        logging.error(f"Error saving bookmarks: {e}")
        raise


def bookmark_is_valid(bookmark):
    return "title" in bookmark and "url" in bookmark
