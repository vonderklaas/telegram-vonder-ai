py-bookmarks

## Quick Start

```bash

python main.py

```

## API Endpoints

```python
@app.route('/bookmarks', methods=['GET'])
@app.route('/bookmarks/<string:id>', methods=['GET'])
@app.route('/bookmarks', methods=['POST'])
@app.route('/bookmarks/<string:id>', methods=['PUT'])
@app.route('/bookmarks/<string:id>', methods=['DELETE'])
```
