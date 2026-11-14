import os
import time
import threading
import random
import string
import json
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, jsonify, request, send_from_directory
from instagrapi import Client

app = Flask(__name__, static_folder='.')

SERVER_START_TIME = time.time()

active_tasks = {}
task_threads = {}
logs = []

TASKS_STORE_FILE = "active_tasks_store.json"
TEMPLATES_STORE_FILE = "templates_store.json"

executor = ThreadPoolExecutor(max_workers=None)
cooldown_tracker = {}

saved_nc_templates = []
saved_spam_templates = []
EMOJIS_LIST = ["🔥", "⚡", "🔴", "💀", "👑", "☣️", "💥", "⚠️", "🟢", "🔵", "🌪️", "🔱"]

def add_log(message):
    timestamp = time.strftime("[%H:%M:%S]")
    log_entry = f"{timestamp} {message}"
    logs.insert(0, log_entry)
    if len(logs) > 100:
        logs.pop()

# Proxy configuration from Render Environment Variable
PROXY_URL = os.environ.get("INSTA_PROXY", "") 

def get_instagrapi_client(sessionid):
    cl = Client()
    
    # Device fingerprinting set to avoid detection
    cl.set_device({
        "app_version": "269.0.0.18.75",
        "android_version": 31,
        "android_release": "12.0",
        "dpi": "480dpi",
        "resolution": "1080x2280",
        "manufacturer": "Xiaomi",
        "device": "mojito",
        "model": "Redmi Note 10",
        "cpu": "qcom"
    })
    
    # Apply Webshare / Custom Proxy if configured
    if PROXY_URL:
        cl.set_proxy(PROXY_URL)
        print(f"[PROXY ACTIVE] Connected via proxy.")

    cl.login_by_sessionid(sessionid)
    return cl

def save_tasks_to_disk():
    try:
        with open(TASKS_STORE_FILE, 'w') as f:
            json.dump(active_tasks, f, indent=4)
    except Exception as e:
        add_log(f"[STORAGE ERROR]: Failed to save tasks -> {str(e)}")

def load_saved_templates():
    global saved_nc_templates, saved_spam_templates
    if os.path.exists(TEMPLATES_STORE_FILE):
        try:
            with open(TEMPLATES_STORE_FILE, 'r') as f:
                data = json.load(f)
                saved_nc_templates = data.get('nc', [])
                saved_spam_templates = data.get('spam', [])
        except Exception as e:
            add_log(f"[TEMPLATE ERROR]: Failed to load templates -> {str(e)}")

def spawn_task_worker(task_data):
    task_id = task_data['task_id']
    task_type = task_data['type']
    
    if task_type == 'spam':
        u = task_data['username']
        s = task_data['session_id']
        tid = task_data['thread_id']
        target = task_data.get('target', '')
        jitter = float(task_data.get('jitter', 3.5))
        payload = task_data.get('payload', [])

        def run_spam():
            try:
                cl = get_instagrapi_client(s)
                add_log(f"[@{u}] Resumed Single DM Spam on thread {tid}")
                while task_id in active_tasks:
                    for msg in payload:
                        if task_id not in active_tasks:
                            break
                        formatted_msg = msg.replace('{target}', f"#{target}" if target else "")
                        cl.direct_send(formatted_msg, thread_ids=[int(tid)])
                        add_log(f"[@{u}] Sent payload block to {tid}")
                        time.sleep(jitter)
            except Exception as e:
                add_log(f"[@{u}] Spam task crashed: {str(e)}")
            finally:
                if task_id in active_tasks:
                    del active_tasks[task_id]
                    save_tasks_to_disk()

        t = threading.Thread(target=run_spam)
        task_threads[task_id] = t
        t.start()

    elif task_type == 'swarm':
        u = task_data['username']
        s = task_data['sessionid']
        tid = task_data['thread_id']
        target = task_data.get('target', '')
        jitter = float(task_data.get('jitter', 3.5))
        payload = task_data.get('payload', [])

        def run_swarm():
            try:
                cl = get_instagrapi_client(s)
                add_log(f"[SWARM @{u}] Resumed Swarm attack on {tid}")
                while task_id in active_tasks:
                    for msg in payload:
                        if task_id not in active_tasks:
                            break
                        formatted_msg = msg.replace('{target}', f"@{target}" if target else "")
                        cl.direct_send(formatted_msg, thread_ids=[int(tid)])
                        add_log(f"[SWARM @{u}] Payload delivered to {tid}")
                        time.sleep(jitter)
            except Exception as e:
                add_log(f"[SWARM @{u}] Error: {str(e)}")
            finally:
                if task_id in active_tasks:
                    del active_tasks[task_id]
                    save_tasks_to_disk()

        t = threading.Thread(target=run_swarm)
        task_threads[task_id] = t
        t.start()

    elif task_type == 'nclock':
        u = task_data['username']
        s = task_data['session_id']
        tid = task_data['thread_id']
        nc_text = task_data.get('nc_text', '')
        jitter = float(task_data.get('jitter', 4.0))

        def run_nclock():
            try:
                cl = get_instagrapi_client(s)
                add_log(f"[@{u}] Resumed NC Lock on thread {tid}")
                counter = 1
                while task_id in active_tasks:
                    title = f"{nc_text} [{counter}]"
                    try:
                        cl.direct_thread_update_title(int(tid), title)
                    except AttributeError:
                        th_obj = cl.direct_thread(int(tid))
                        th_obj.update_title(title)
                    add_log(f"[@{u}] Updated NC Title to: {title}")
                    counter += 1
                    time.sleep(jitter)
            except Exception as e:
                add_log(f"[@{u}] NC Lock error: {str(e)}")
            finally:
                if task_id in active_tasks:
                    del active_tasks[task_id]
                    save_tasks_to_disk()

        t = threading.Thread(target=run_nclock)
        task_threads[task_id] = t
        t.start()

def auto_resume_all_tasks():
    load_saved_templates()
    if os.path.exists(TASKS_STORE_FILE):
        try:
            with open(TASKS_STORE_FILE, 'r') as f:
                saved_data = json.load(f)
                add_log(f"[AUTO-RESUME ENGINE] Recovered {len(saved_data)} tasks from disk!")
                for task_id, tinfo in saved_data.items():
                    active_tasks[task_id] = tinfo
                    spawn_task_worker(tinfo)
        except Exception as e:
            add_log(f"[AUTO-RESUME ERROR]: Failed to resume tasks -> {str(e)}")

auto_resume_all_tasks()

@app.route('/ping')
def ping():
    return jsonify({"status": "alive", "timestamp": time.time()}), 200

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/account/verify', methods=['POST'])
def verify_account():
    data = request.json or {}
    sessionid = data.get('sessionid', '').strip()
    if not sessionid:
        return jsonify({"status": "error", "message": "Session ID is required."}), 400

    try:
        cl = get_instagrapi_client(sessionid)
        account_info = cl.account_info()
        username = account_info.username
        add_log(f"Successfully bound contract for @{username}")
        return jsonify({"status": "success", "username": username, "sessionid": sessionid})
    except Exception as e:
        error_msg = str(e)
        add_log(f"Account verification failed: {error_msg}")
        return jsonify({"status": "error", "message": f"Session Login Failed: {error_msg}"}), 400

@app.route('/api/task/start', methods=['POST'])
def start_task():
    data = request.json or {}
    task_type = data.get('type')
    task_id_base = str(int(time.time() * 1000))

    if task_type == 'spam':
        u = data.get('username')
        task_id = f"{task_id_base}_{u}"
        task_info = {
            "task_id": task_id, "type": "spam", "username": u, 
            "session_id": data.get('session_id'), "thread_id": data.get('thread_id'),
            "target": data.get('target', ''), "jitter": data.get('jitter', 3.5),
            "payload": data.get('payload', []), "started_at": time.strftime("%H:%M:%S")
        }
        active_tasks[task_id] = task_info
        save_tasks_to_disk()
        spawn_task_worker(task_info)

    elif task_type == 'swarm_spam':
        accounts = data.get('accounts', [])
        for acc in accounts:
            u = acc['username']
            task_id = f"{task_id_base}_{u}"
            task_info = {
                "task_id": task_id, "type": "swarm", "username": u,
                "sessionid": acc['sessionid'], "thread_id": data.get('thread_id'),
                "target": data.get('target', ''), "jitter": data.get('jitter', 3.5),
                "payload": data.get('payload', []), "started_at": time.strftime("%H:%M:%S")
            }
            active_tasks[task_id] = task_info
            save_tasks_to_disk()
            spawn_task_worker(task_info)

    elif task_type == 'nclock':
        u = data.get('username')
        task_id = f"{task_id_base}_{u}"
        task_info = {
            "task_id": task_id, "type": "nclock", "username": u,
            "session_id": data.get('session_id'), "thread_id": data.get('thread_id'),
            "nc_text": data.get('nc_text'), "jitter": data.get('jitter', 4.0),
            "started_at": time.strftime("%H:%M:%S")
        }
        active_tasks[task_id] = task_info
        save_tasks_to_disk()
        spawn_task_worker(task_info)

    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
