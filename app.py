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
INSTA_CLIENTS = {}

def add_log(msg):
    timestamp = time.strftime("%H:%M:%S")
    LOGS.insert(0, f"[{timestamp}] {msg}")
    if len(LOGS) > 100:
        LOGS.pop()

def background_worker(task_id, task_data):
    add_log(f"[WORKER] Task {task_id} launched.")
    task_type = task_data.get('type')
    session_id = task_data.get('session_id')
    username = task_data.get('username')
    thread_id = task_data.get('thread_id')
    
    # Target name bina '@' ke direct use hoga jaisa user ne input diya hai
    target_name = task_data.get('target', '').strip()
    jitter = float(task_data.get('jitter', 5.0))
    payload = task_data.get('payload', [])

    client = INSTA_CLIENTS.get(session_id)
    if not client:
        add_log(f"[ERROR] Session client missing for @{username}")
        if task_id in ACTIVE_TASKS:
            ACTIVE_TASKS[task_id]['running'] = False
        return

    idx = 0
    while ACTIVE_TASKS.get(task_id, {}).get('running', False):
        try:
            if task_type == 'spam' and payload:
                raw_msg = payload[idx % len(payload)]
                
                if isinstance(raw_msg, str) and raw_msg.strip():
                    # {target} ko plain target name se replace karo (no extra @)
                    formatted_msg = raw_msg.replace("{target}", target_name)
                    
                    client.direct_send(formatted_msg, thread_ids=[int(thread_id)])
                    add_log(f"[SENT] @{username} -> Thread {thread_id}: {formatted_msg[:30]}...")
                
                idx += 1
            elif task_type == 'nclock':
                emojis = ['💕', '🔥', '✨', '👑', '⚡', '😈']
                current_emoji = emojis[idx % len(emojis)]
                nc_text = task_data.get('nc_text', '')
                new_title = f"{nc_text} {current_emoji}"
                
                try:
                    # Latest API Endpoint Payload for Thread Title Update
                    client.private_request(
                        f"direct_v2/threads/{thread_id}/update_title/",
                        data={"title": new_title}
                    )
                    add_log(f"[NC LOCK] @{username} -> Title: {new_title}")
                except Exception as alt_e:
                    try:
                        # Fallback wrapper if endpoint structure varies
                        client.direct_thread_update_title(int(thread_id), new_title)
                        add_log(f"[NC LOCK (Fallback)] @{username} -> Title: {new_title}")
                    except Exception as inner_e:
                        add_log(f"[NC LOCK ERROR] @{username}: {str(alt_e)}")
                
                idx += 1
            
            time.sleep(jitter)
        except Exception as e:
            add_log(f"[ERROR] Task {task_id} (@{username}): {str(e)}")
            time.sleep(8)

    add_log(f"[WORKER] Task {task_id} terminated.")

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

@app.route('/api/account/verify', methods=['POST'])
def verify_account():
    data = request.json
    sessionid = data.get('sessionid', '').strip()
    if not sessionid:
        return jsonify({'status': 'error', 'message': 'Session ID is required'}), 400

    try:
        cl = Client()
        cl.set_user_agent("Instagram 269.0.0.18.75 Android (26/8.0.0; 480dpi; 1080x1920; Samsung; SM-G930F; herolte; samsungexynos8890; en_US; 314665270)")
        cl.login_by_sessionid(sessionid)
        
        account_info = cl.account_info()
        username = account_info.username
        INSTA_CLIENTS[sessionid] = cl
        
        add_log(f"[AUTH SUCCESS] @{username} connected.")
        return jsonify({'status': 'success', 'username': username, 'sessionid': sessionid})
    except Exception as e:
        add_log(f"[AUTH FAILED] {str(e)}")
        return jsonify({'status': 'error', 'message': f'Session error: {str(e)}'}), 400

@app.route('/api/group/create', methods=['POST'])
def create_group():
    data = request.json
    session_id = data.get('session_id')
    group_title = data.get('title')
    usernames = data.get('usernames', [])

    client = INSTA_CLIENTS.get(session_id)
    if not client:
        return jsonify({'status': 'error', 'message': 'Session missing. Verify account first.'}), 400

    try:
        user_pks = [str(client.user_id_from_username(u.strip().replace('@', ''))) for u in usernames if u.strip()]
        thread = client.direct_create_group(user_pks, title=group_title)
        add_log(f"[GROUP CREATED] '{group_title}' with {len(user_pks)} members.")
        return jsonify({'status': 'success', 'thread_id': thread.id})
    except Exception as e:
        add_log(f"[GROUP ERROR] {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/task/start', methods=['POST'])
def start_task():
    data = request.json
    task_id = f"{data.get('type')}_{data.get('username')}_{int(time.time())}"
    
    ACTIVE_TASKS[task_id] = {
        'running': True,
        'type': data.get('type'),
        'username': data.get('username'),
        'thread_id': data.get('thread_id'),
        'started_at': time.strftime("%H:%M:%S")
    }

    thread = threading.Thread(target=background_worker, args=(task_id, data), daemon=True)
    thread.start()
    return jsonify({'status': 'success', 'task_id': task_id})

@app.route('/api/task/stop', methods=['POST'])
def stop_task():
    data = request.json
    task_id = data.get('task_id')
    if task_id in ACTIVE_TASKS:
        ACTIVE_TASKS[task_id]['running'] = False
        return jsonify({'status': 'success', 'message': f'Task {task_id} stopped.'})
    return jsonify({'status': 'error', 'message': 'Task not found'}), 404

@app.route('/api/tasks/active', methods=['GET'])
def get_active_tasks():
    running_list = []
    for tid, info in list(ACTIVE_TASKS.items()):
        if info.get('running'):
            running_list.append({
                'task_id': tid,
                'type': info.get('type'),
                'username': info.get('username'),
                'thread_id': info.get('thread_id'),
                'started_at': info.get('started_at')
            })
    return jsonify({'tasks': running_list, 'logs': LOGS})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    threading.Thread(target=self_ping_worker, daemon=True).start()
    app.run(host='0.0.0.0', port=port)
