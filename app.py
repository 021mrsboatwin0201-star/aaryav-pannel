import time
import threading
import traceback
from flask import Flask, jsonify, request, send_from_directory
from instagrapi import Client

app = Flask(__name__, static_folder='.')

# Global state for tasks and logs
active_tasks = {}
task_threads = {}
logs = []

def add_log(message):
    timestamp = time.strftime("[%H:%M:%S]")
    log_entry = f"{timestamp} {message}"
    logs.insert(0, log_entry)
    if len(logs) > 100:
        logs.pop()

@app.route('/ping')
def ping():
    """Uptime Robot ping endpoint to keep Render awake 24/7"""
    return jsonify({"status": "alive", "timestamp": time.time()}), 200

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/account/verify', methods=['POST'])
def verify_account():
    data = request.json
    sessionid = data.get('sessionid')
    try:
        cl = Client()
        cl.load_settings({})
        # Inject sessionid cookie into instagrapi client
        cl.set_sessionid(sessionid)
        user_id = cl.user_id_from_username(cl.username)
        username = cl.username
        add_log(f"Successfully bound contract for @{username}")
        return jsonify({"status": "success", "username": username, "sessionid": sessionid})
    except Exception as e:
        add_log(f"Account verification failed: {str(e)}")
        return jsonify({"status": "error", "message": "Invalid Session ID or Challenge Required."}), 400

@app.route('/api/task/start', methods=['POST'])
def start_task():
    data = request.json
    task_type = data.get('type')
    task_id = str(int(time.time() * 1000))
    
    if task_type == 'spam':
        session_id = data.get('session_id')
        username = data.get('username')
        thread_id = data.get('thread_id')
        target = data.get('target', 'target')
        jitter = float(data.get('jitter', 3.5))
        payload = data.get('payload', []) # Receives [spamPayload] single block or array
        
        def run_spam():
            try:
                cl = Client()
                cl.set_sessionid(session_id)
                add_log(f"[@{username}] Started DM Spam task on thread {thread_id}")
                
                while task_id in active_tasks:
                    for msg in payload:
                        if task_id not in active_tasks:
                            break
                        formatted_msg = msg.replace('{target}', f"@{target}" if target else "")
                        cl.direct_send(formatted_msg, thread_ids=[int(thread_id)])
                        add_log(f"[@{username}] Sent payload block to {thread_id}")
                        time.sleep(jitter)
            except Exception as e:
                add_log(f"[@{username}] Spam task crashed: {str(e)}")
            finally:
                if task_id in active_tasks:
                    del active_tasks[task_id]
                if task_id in task_threads:
                    del task_threads[task_id]

        active_tasks[task_id] = {"task_id": task_id, "type": "spam", "username": username, "thread_id": thread_id, "started_at": time.strftime("%H:%M:%S")}
        t = threading.Thread(target=run_spam)
        task_threads[task_id] = t
        t.start()

    elif task_type == 'nclock':
        session_id = data.get('session_id')
        username = data.get('username')
        thread_id = data.get('thread_id')
        nc_text = data.get('nc_text')
        jitter = float(data.get('jitter', 4.0))

        def run_nclock():
            try:
                cl = Client()
                cl.set_sessionid(session_id)
                add_log(f"[@{username}] Started NC Lock on thread {thread_id}")
                counter = 1
                while task_id in active_tasks:
                    title = f"{nc_text} [{counter}]"
                    cl.direct_update_group_title(int(thread_id), title)
                    add_log(f"[@{username}] Updated NC Title to: {title}")
                    counter += 1
                    time.sleep(jitter)
            except Exception as e:
                add_log(f"[@{username}] NC Lock error: {str(e)}")
            finally:
                if task_id in active_tasks:
                    del active_tasks[task_id]
                if task_id in task_threads:
                    del task_threads[task_id]

        active_tasks[task_id] = {"task_id": task_id, "type": "nclock", "username": username, "thread_id": thread_id, "started_at": time.strftime("%H:%M:%S")}
        t = threading.Thread(target=run_nclock)
        task_threads[task_id] = t
        t.start()

    return jsonify({"status": "success", "task_id": task_id})

@app.route('/api/task/stop', methods=['POST'])
def stop_task():
    data = request.json
    task_id = data.get('task_id')
    if task_id in active_tasks:
        del active_tasks[task_id]
        add_log(f"Terminated task ID: {task_id}")
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Task not found"}), 404

@app.route('/api/tasks/active', methods=['GET'])
def get_active_tasks():
    tasks_list = list(active_tasks.values())
    return jsonify({"tasks": tasks_list, "logs": logs})

@app.route('/api/group/create', methods=['POST'])
def create_group():
    data = request.json
    session_id = data.get('session_id')
    title = data.get('title')
    usernames = data.get('usernames', [])
    try:
        cl = Client()
        cl.set_sessionid(session_id)
        user_ids = [cl.user_id_from_username(u.strip()) for u in usernames if u.strip()]
        thread = cl.direct_create_group(user_ids, title)
        add_log(f"Created Group '{title}' with ID: {thread.id}")
        return jsonify({"status": "success", "thread_id": thread.id})
    except Exception as e:
        add_log(f"Group creation failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
