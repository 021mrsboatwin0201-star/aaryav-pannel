import os
import time
import threading
import urllib.request
from flask import Flask, request, jsonify
from flask_cors import CORS
from instagrapi import Client

app = Flask(__name__)
CORS(app)

ACTIVE_TASKS = {}
LOGS = []
INSTA_CLIENTS = {}  # Stores authenticated client instances per session_id

def add_log(msg):
    timestamp = time.strftime("%H:%M:%S")
    LOGS.insert(0, f"[{timestamp}] {msg}")
    if len(LOGS) > 100:
        LOGS.pop()

# Background Worker with Real Instagrapi Integration
def background_worker(task_id, task_data):
    add_log(f"[WORKER] Task {task_id} launched.")
    task_type = task_data.get('type')
    session_id = task_data.get('session_id')
    username = task_data.get('username')
    thread_id = task_data.get('thread_id')
    jitter = float(task_data.get('jitter', 3.5))
    payload = task_data.get('payload', [])
    nc_text = task_data.get('nc_text', '')

    emojis = ['💕', '🔥', '✨', '👑', '⚡', '😈']
    idx = 0

    # Get or initialize client
    client = INSTA_CLIENTS.get(session_id)
    if not client:
        add_log(f"[ERROR] Session client not found for @{username}")
        return

    while ACTIVE_TASKS.get(task_id, {}).get('running', False):
        try:
            if task_type == 'spam':
                msg = payload[idx % len(payload)]
                # Real Instagram Direct Message Thread Send Call
                client.direct_send(msg, thread_ids=[int(thread_id)])
                add_log(f"[SPAM SENT] @{username} -> Thread {thread_id}: {msg}")
                idx += 1
            elif task_type == 'nclock':
                current_emoji = emojis[idx % len(emojis)]
                new_title = f"{nc_text} {current_emoji}"
                # Real Instagram Group Thread Title Change Call
                client.direct_thread_update_title(int(thread_id), new_title)
                add_log(f"[NC LOCK] @{username} changed thread title to: {new_title}")
                idx += 1
            
            time.sleep(jitter)
        except Exception as e:
            add_log(f"[ERROR] Task failed for @{username}: {str(e)}")
            time.sleep(5)

    add_log(f"[WORKER] Task {task_id} stopped.")

# Self-ping heartbeat to keep Render alive
def self_ping_worker():
    app_url = os.environ.get('RENDER_EXTERNAL_URL')
    if not app_url:
        return
    while True:
        try:
            time.sleep(300)
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

# Verify Session ID & Auto-fetch Username via Instagrapi
@app.route('/api/account/verify', methods=['POST'])
def verify_account():
    data = request.json
    sessionid = data.get('sessionid', '').strip()
    
    if not sessionid:
        return jsonify({'status': 'error', 'message': 'Session ID is required'}), 400

    try:
        cl = Client()
        cl.login_by_sessionid(sessionid)
        account_info = cl.account_info()
        username = account_info.username
        
        # Save authenticated client instance
        INSTA_CLIENTS[sessionid] = cl
        
        add_log(f"[AUTH SUCCESS] Account verified: @{username}")
        return jsonify({
            'status': 'success',
            'username': username,
            'sessionid': sessionid
        })
    except Exception as e:
        add_log(f"[AUTH FAILED] Invalid Session ID: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Invalid Session ID or checkpoint required by Instagram.'}), 400

@app.route('/api/task/start', methods=['POST'])
def start_task():
    data = request.json
    task_id = data.get('task_id', 'default_task')
    
    if task_id in ACTIVE_TASKS and ACTIVE_TASKS[task_id]['running']:
        return jsonify({'status': 'error', 'message': 'Task already running'}), 400

    ACTIVE_TASKS[task_id] = {'running': True, 'data': data}
    thread = threading.Thread(target=background_worker, args=(task_id, data), daemon=True)
    thread.start()
    
    return jsonify({'status': 'success', 'message': f'Task {task_id} launched'})

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
    threading.Thread(target=self_ping_worker, daemon=True).start()
    app.run(host='0.0.0.0', port=port)
