from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Lista en memoria para almacenar tareas
tasks = []
task_id_counter = 1

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task)

@app.route('/tasks', methods=['POST'])
def create_task():
    global task_id_counter
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    task = {
        'id': task_id_counter,
        'title': data['title'],
        'description': data.get('description', ''),
        'done': data.get('done', False)
    }
    tasks.append(task)
    task_id_counter += 1
    return jsonify(task), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    if 'title' in data:
        task['title'] = data['title']
    if 'description' in data:
        task['description'] = data['description']
    if 'done' in data:
        task['done'] = data['done']
    return jsonify(task)

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    task = next((t for t in tasks if t['id'] == task_id), None)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    tasks = [t for t in tasks if t['id'] != task_id]
    return jsonify({'message': 'Task deleted'})


if __name__ == '__main__':
    app.run(debug=True)