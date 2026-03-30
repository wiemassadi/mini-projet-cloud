from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import redis
import os
 
app = Flask(__name__)
 
# Connexion à PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://admin:admin@db:5432/tasks'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
 
# Connexion à Redis
cache = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'redis'),
    port=6379,
    decode_responses=True
)
 
# Modèle de données (table dans PostgreSQL)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)
 
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'done': self.done
        }
 
# Route : lister les tâches
@app.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        cached = cache.get('all_tasks')
        if cached:
            return cached, 200, {'Content-Type': 'application/json'}
    except:
        pass
    tasks = Task.query.all()
    result = [t.to_dict() for t in tasks]
    import json
    try:
        cache.setex('all_tasks', 30, json.dumps(result))
    except:
        pass
    return jsonify(result)
 
# Route : créer une tâche
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'title requis'}), 400
    task = Task(title=data['title'])
    db.session.add(task)
    db.session.commit()
    try:
        cache.delete('all_tasks')
    except:
        pass
    return jsonify(task.to_dict()), 201
 
# Route : supprimer une tâche
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    try:
        cache.delete('all_tasks')
    except:
        pass
    return '', 204
 
# Route : vérification santé
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'flask-todo'})
 
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
