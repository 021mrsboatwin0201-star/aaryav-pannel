import os
import time
import threading
import urllib.request
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ACTIVE_TASKS = {}
LOGS = []

def add_log(msg):
    timestamp = time.strftime("%H:%M:%S")
    LOGS.insert(0, f"[{timestamp}] {msg}")
    if len(LOGS) > 100:
        LOGS.pop()

# Background Worker for Spam / NC Lock
def background_worker(task_id, task_data):
    add_log(f"[WORKER] Task {task_id} started in background loop.")
    task_type = task_data.get('type')
    sessions = task_data.get('sessions', [])
    thread_id = task_data.get('thread_id')
    jitter = float(task_data.get('jitter', 3.5))
    payload = task_data.get('payload', [])
    nc_text = task_data.get('nc_text', '')

    emojis = ['💕', '🔥', '✨', '👑', '⚡', '😈']
    idx = 0

    while ACTIVE_TASKS.get(task_id, {}).get('running', False):
        try:
            if task_type == 'spam':
                msg = payload[idx % len(payload)]
                for session in sessions:
                    add_log(f"[SPAM DISPATCH] Node @{session['username']} -> Thread {thread_id}: {msg}")
                idx += 1
            elif task_type == 'nclock':
                current_emoji = emojis[idx % len(emojis)]
                new_title = f"{nc_text} {current_emoji}"
                for session in sessions:
                    add_log(f"[NC LOCK] Node @{session['username']} changed group title to: {new_title}")
                idx += 1
            
            time.sleep(jitter)
        except Exception as e:
            add_log(f"[ERROR] Worker task {task_id} failed: {str(e)}")
            time.sleep(5)

    add_log(f"[WORKER] Task {task_id} stopped.")

# Self-Ping Heartbeat to prevent Render Free Tier from sleeping
def self_ping_worker():
    # Render automatically sets RENDER_EXTERNAL_URL environment variable
    app_url = os.environ.get('RENDER_EXTERNAL_URL')
    if not app_url:
        return
    
    add_log(f"[HEARTBEAT] Self-ping active for URL: {app_url}")
    while True:
        try:
            time.sleep(300) # Har 5 minute me ping karega
            urllib.request.urlopen(app_url)
        except Exception:
            pass

@app.route('/')
def home():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error loading interface: {str(e)}"

@app.route('/api/task/start', methods=['POST'])
def start_task():
    data = request.json
    task_id = data.get('task_id', 'default_task')
    
    if task_id in ACTIVE_TASKS and ACTIVE_TASKS[task_id]['running']:
        return jsonify({'status': 'error', 'message': 'Task already running'}), 400

    ACTIVE_TASKS[task_id] = {'running': True, 'data': data}
    thread = threading.Thread(target=background_worker, args=(task_id, data), daemon=True)
    thread.start()
    
    return jsonify({'status': 'success', 'message': f'Task {task_id} launched in background'})

@app.route('/api/task/stop', methods=['POST'])
def stop_task():
    data = request.json
    task_id = data.get('task_id', 'default_task')
    if task_id in ACTIVE_TASKS:
        ACTIVE_TASKS[task_id]['running'] = False
    return jsonify({'status': 'success', 'message': f'Task {task_id} stopped'})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify({'logs': LOGS, 'active_tasks': {k: v['running'] for k, v in ACTIVE_TASKS.items()}})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    # Start heartbeat thread in background
    heartbeat_thread = threading.Thread(target=self_ping_worker, daemon=True)
    heartbeat_thread.start()
    
    app.run(host='0.0.0.0', port=port)
