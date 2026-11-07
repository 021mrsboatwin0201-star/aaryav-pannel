import os
import time
import threading
from flask import Flask, jsonify, request, send_from_directory
from instagrapi import Client

app = Flask(__name__, static_folder='.')

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
    return jsonify({"status": "alive", "timestamp": time.time()}), 200

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/account/verify', methods=['POST'])
def verify_account():
    data = request.json
    sessionid = data.get('sessionid', '').strip()
    
    if not sessionid:
        return jsonify({"status": "error", "message": "Session ID is required."}), 400

    try:
        cl = Client()
        cl.set_user_agent("Instagram 269.0.0.18.75 Android (31/12; 480dpi; 1080x2280; Xiaomi; Redmi Note 10; mojito; qcom; en_US; 314663841)")
        cl.login_by_sessionid(sessionid)
        
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
    data = request.json
    task_type = data.get('type')
    task_id_base = str(int(time.time() * 1000))
    
    # 1. Single Account Spam Campaign
    if task_type == 'spam':
        session_id = data.get('session_id')
        username = data.get('username')
        thread_id = data.get('thread_id')
        target = data.get('target', '')
        jitter = float(data.get('jitter', 3.5))
        payload = data.get('payload', [])
        task_id = f"{task_id_base}_{username}"

        def run_spam():
            try:
                cl = Client()
                cl.set_user_agent("Instagram 269.0.0.18.75 Android (31/12; 480dpi; 1080x2280; Xiaomi; Redmi Note 10; mojito; qcom; en_US; 314663841)")
                cl.login_by_sessionid(session_id)
                add_log(f"[@{username}] Started DM Spam task on thread {thread_id}")
                
                while task_id in active_tasks:
                    for msg in payload:
                        if task_id not in active_tasks:
                            break
                        formatted_msg = msg.replace('{target}', f"#{target}" if target else "")
                        cl.direct_send(formatted_msg, thread_ids=[int(thread_id)])
                        add_log(f"[@{username}] Sent payload block to thread {thread_id}")
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

    # 2. SWARM ATTACK (All linked accounts simultaneous spam raid)
    elif task_type == 'swarm_spam':
        accounts = data.get('accounts', [])
        thread_id = data.get('thread_id')
        target = data.get('target', '')
        jitter = float(data.get('jitter', 3.5))
        payload = data.get('payload', [])

        for acc in accounts:
            acc_user = acc['username']
            acc_sess = acc['sessionid']
            task_id = f"{task_id_base}_{acc_user}"

            def run_swarm_account(u, s, tid):
                try:
                    cl = Client()
                    cl.set_user_agent("Instagram 269.0.0.18.75 Android (31/12; 480dpi; 1080x2280; Xiaomi; Redmi Note 10; mojito; qcom; en_US; 314663841)")
                    cl.login_by_sessionid(s)
                    add_log(f"[SWARM @{u}] Spawned and attacking thread {tid}")
                    
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
                    if task_id in task_threads:
                        del task_threads[task_id]

            active_tasks[task_id] = {"task_id": task_id, "type": "swarm", "username": acc_user, "thread_id": thread_id, "started_at": time.strftime("%H:%M:%S")}
            t = threading.Thread(target=run_swarm_account, args=(acc_user, acc_sess, thread_id))
            task_threads[task_id] = t
            t.start()

    # 3. NC LOCK (Group Title Rotation with Fixed Method)
    elif task_type == 'nclock':
        session_id = data.get('session_id')
        username = data.get('username')
        thread_id = data.get('thread_id')
        nc_text = data.get('nc_text')
        jitter = float(data.get('jitter', 4.0))
        task_id = f"{task_id_base}_{username}"

        def run_nclock():
            try:
                cl = Client()
                cl.set_user_agent("Instagram 269.0.0.18.75 Android (31/12; 480dpi; 1080x2280; Xiaomi; Redmi Note 10; mojito; qcom; en_US; 314663841)")
                cl.login_by_sessionid(session_id)
                add_log(f"[@{username}] Started NC Lock on thread {thread_id}")
                counter = 1
                while task_id in active_tasks:
                    title = f"{nc_text} [{counter}]"
                    
                    try:
                        cl.direct_thread_update_title(int(thread_id), title)
                    except AttributeError:
                        thread = cl.direct_thread(int(thread_id))
                        thread.update_title(title)

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

    return jsonify({"status": "success"})

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
        cl.set_user_agent("Instagram 269.0.0.18.75 Android (31/12; 480dpi; 1080x2280; Xiaomi; Redmi Note 10; mojito; qcom; en_US; 314663841)")
        cl.login_by_sessionid(session_id)
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
