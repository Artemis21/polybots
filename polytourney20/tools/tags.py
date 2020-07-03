"""Tags storage/retrieval."""
import json
import os


FILE = 'data/tags.json'

if not os.path.exists(FILE):
    with open(FILE, 'w') as f:
        f.write('{}')


def _get_data():
    """Get all the data."""
    with open(FILE) as f:
        return json.load(f)


def create_tag(name: str, content: str):
    """Create a tag."""
    data = _get_data()
    data[name.lower()] = content
    with open(FILE, 'w') as f:
        json.dump(data, f)


def get_tag(name: str):
    """Get a tag."""
    return _get_data().get(name.lower(), 'Tag not found.')
