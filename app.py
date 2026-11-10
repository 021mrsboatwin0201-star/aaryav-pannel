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

def get_instagrapi_client(sessionid):
    cl = Client()
    cl.set_user_agent("Instagram 269.0.0.18.75 Android (31/12; 480dpi; 1080x2280; Xiaomi; Redmi Note 10; mojito; qcom; en_US; 314663841)")
    cl.login_by_sessionid(sessionid)
    return cl

def format_template(template_str, target_name):
    formatted = template_str.replace("{target}", target_name)
    if "{emoji}" in formatted:
        rand_emojis = "".join(random.choices(EMOJIS_LIST, k=3))
        formatted = formatted.replace("{emoji}", rand_emojis)
    return formatted

def generate_random_username():
    letters = string.ascii_lowercase
    name_part = "".join(random.choices(letters, k=random.randint(4, 7)))
    num_part = str(random.randint(10, 999))
    suffixes = ["_offical", "_king", "_vip", "", "07", "786"]
    return f"{name_part}{num_part}{random.choice(suffixes)}"

def save_tasks_to_disk():
    try:
        data_to_save = {}
        for tid, tinfo in active_tasks.items():
            data_to_save[tid] = {k: v for k, v in tinfo.items() if k != 'thread_obj'}
        with open(TASKS_STORE_FILE, 'w') as f:
            json.dump(data_to_save, f, indent=2)
    except Exception as e:
        print(f"[DISK SAVE ERROR]: {e}")

def load_saved_templates():
    global saved_nc_templates, saved_spam_templates
    if os.path.exists(TEMPLATES_STORE_FILE):
        try:
            with open(TEMPLATES_STORE_FILE, 'r') as f:
                data = json.load(f)
                saved_nc_templates = data.get('nc', [])
                saved_spam_templates = data.get('spam', [])
        except Exception as e:
            print(f"[TEMPLATE LOAD ERROR]: {e}")

def save_templates_to_disk():
    try:
        with open(TEMPLATES_STORE_FILE, 'w') as f:
            json.dump({'nc': saved_nc_templates, 'spam': saved_spam_templates}, f, indent=2)
    except Exception as e:
        print(f"[TEMPLATE SAVE ERROR]: {e}")

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

    elif task_type == 'multi_fight':
        u = task_data['username']
        s = task_data['sessionid']
        target_name = task_data.get('target_name', 'MONARCH')
        interval_seconds = int(task_data.get('interval', 300))

        def run_multi_worker():
            try:
                cl = get_instagrapi_client(s)
                add_log(f"[@{u}] Multi-GC Auto-Resumed. Fetching GCs for this account...")
                
                # Fetch GCs specific to THIS account automatically
                threads = cl.direct_threads(amount=100, selected_filter="group")
                assigned_gcs = [str(t.id) for t in threads if t.is_group]
                add_log(f"[@{u}] Found {len(assigned_gcs)} GCs for attack.")

                while task_id in active_tasks:
                    if not assigned_gcs:
                        time.sleep(60)
                        try:
                            threads = cl.direct_threads(amount=100, selected_filter="group")
                            assigned_gcs = [str(t.id) for t in threads if t.is_group]
                        except:
                            pass
                        continue

                    for thread_id in assigned_gcs:
                        if task_id not in active_tasks:
                            break
                        
                        cooldown_key = f"{s}_{thread_id}"
                        if cooldown_key in cooldown_tracker:
                            if time.time() < cooldown_tracker[cooldown_key]:
                                continue
                            else:
                                del cooldown_tracker[cooldown_key]

                        try:
                            action_type = random.choice(["nc", "spam"])

                            if action_type == "nc":
                                if saved_nc_templates:
                                    raw_nc = random.choice(saved_nc_templates)
                                    final_title = format_template(raw_nc, target_name)
                                    try:
                                        cl.direct_thread_update_title(int(thread_id), final_title)
                                    except AttributeError:
                                        th_obj = cl.direct_thread(int(thread_id))
                                        th_obj.update_title(final_title)
                                    add_log(f"[@{u} | NC] GC {thread_id} -> {final_title}")
                            else:
                                if saved_spam_templates:
                                    raw_spam = random.choice(saved_spam_templates)
                                    final_msg = format_template(raw_spam, target_name)
                                    cl.direct_send(final_msg, thread_ids=[int(thread_id)])
                                    add_log(f"[@{u} | SPAM] GC {thread_id} -> {final_msg}")

                        except Exception as e:
                            err_str = str(e)
                            if "403" in err_str or "1545001" in err_str or "block" in err_str.lower():
                                add_log(f"[@{u}] 403 Hit on GC {thread_id}! Isolating single GC for 30 mins.")
                                cooldown_tracker[cooldown_key] = time.time() + 1800
                            else:
                                add_log(f"[@{u}] Error on GC {thread_id}: {err_str}")

                        time.sleep(4)

                    time.sleep(interval_seconds)
            except Exception as ex:
                add_log(f"[@{u}] Worker crashed: {str(ex)}")
            finally:
                if task_id in active_tasks:
                    del active_tasks[task_id]
                    save_tasks_to_disk()

        t = threading.Thread(target=run_multi_worker)
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
    data = request.json
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

@app.route('/api/gcs/fetch', methods=['POST'])
def fetch_main_gcs():
    data = request.json
    session_id = data.get('session_id')
    try:
        cl = get_instagrapi_client(session_id)
        threads = cl.direct_threads(amount=100, selected_filter="group")
        gc_list = []
        for thread in threads:
            if thread.is_group:
                gc_list.append({
                    "thread_id": str(thread.id),
                    "title": thread.title if thread.title else "Unnamed GC"
                })
        add_log(f"Successfully fetched {len(gc_list)} GCs from main account.")
        return jsonify({"status": "success", "count": len(gc_list), "gcs": gc_list})
    except Exception as e:
        add_log(f"Failed to fetch GCs: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

# ================= FIXED MASS GC CREATOR WITH SAFE DELAY =================
@app.route('/api/gcs/create_mass', methods=['POST'])
def create_mass_gcs():
    data = request.json
    session_ids = data.get('accounts', [])
    base_usernames = data.get('usernames', [])
    target_prefix = data.get('target_prefix', 'MONARCH')
    total_to_create = int(data.get('amount', 20))

    if not session_ids:
        return jsonify({"status": "error", "message": "No sessions selected!"}), 400

    def background_mass_creator():
        created_count = 0
        session_idx = 0
        while created_count < total_to_create:
            current_sess = session_ids[session_idx % len(session_ids)]
            try:
                cl = get_instagrapi_client(current_sess)
                user_ids = []

                if base_usernames:
                    for target_uname in base_usernames:
                        try:
                            uid = cl.user_id_from_username(target_uname.strip().replace('@', ''))
                            if uid not in user_ids:
                                user_ids.append(uid)
                        except:
                            pass

                while len(user_ids) < 2:
                    rand_uname = generate_random_username()
                    try:
                        uid = cl.user_id_from_username(rand_uname)
                        if uid not in user_ids:
                            user_ids.append(uid)
                    except:
                        continue

                group_title = f"{target_prefix} GC #{created_count + 1} ⚡"
                thread = cl.direct_thread_create(user_ids, group_title)
                created_count += 1
                add_log(f"[GC CREATED] #{created_count} -> Title: {group_title} (Members: {len(user_ids)})")
                
                # SAFE DELAY FIX: 15 to 25 seconds random gap to prevent "Exceeded 30 redirects" / logout
                safe_delay = random.uniform(15.0, 25.0)
                time.sleep(safe_delay)
            except Exception as e:
                add_log(f"[GC CREATION ERROR]: {str(e)}")
                time.sleep(20) # Error aane par lamba cool-down
            session_idx += 1
        add_log(f"Mass GC Creation Completed! Total {total_to_create} GCs created.")

    executor.submit(background_mass_creator)
    return jsonify({"status": "success", "message": f"Started creating {total_to_create} GCs safely in background."})

@app.route('/api/templates/save_nc', methods=['POST'])
def save_nc_text():
    global saved_nc_templates
    data = request.json
    text_content = data.get('nc_text', '')
    saved_nc_templates = [line.strip() for line in text_content.split('\n') if line.strip()]
    save_templates_to_disk()
    add_log(f"Saved {len(saved_nc_templates)} NC templates.")
    return jsonify({"status": "success", "message": f"Saved {len(saved_nc_templates)} NC templates!"})

@app.route('/api/templates/save_spam', methods=['POST'])
def save_spam_text():
    global saved_spam_templates
    data = request.json
    text_content = data.get('spam_text', '')
    saved_spam_templates = [line.strip() for line in text_content.split('\n') if line.strip()]
    save_templates_to_disk()
    add_log(f"Saved {len(saved_spam_templates)} Spam templates.")
    return jsonify({"status": "success", "message": f"Saved {len(saved_spam_templates)} Spam templates!"})

@app.route('/api/task/start', methods=['POST'])
def start_task():
    data = request.json
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

# ================= MULTI-FIGHT: AUTO FETCHES GCs PER ACCOUNT =================
@app.route('/api/task/start_multi_fight', methods=['POST'])
def start_multi_fight():
    data = request.json
    accounts = data.get('accounts', [])
    target_name = data.get('target_name', 'MONARCH')
    interval_seconds = int(data.get('interval', 300))
    task_id_base = str(int(time.time() * 1000))

    if not accounts:
        return jsonify({"status": "error", "message": "No accounts selected!"}), 400

    save_nc_text_internal = data.get('save_nc')
    save_spam_text_internal = data.get('save_spam')

    for acc in accounts:
        acc_user = acc['username']
        acc_sess = acc['sessionid']
        task_id = f"{task_id_base}_{acc_user}"
        
        task_info = {
            "task_id": task_id, "type": "multi_fight", "username": acc_user,
            "sessionid": acc_sess, "target_name": target_name, "interval": interval_seconds,
            "started_at": time.strftime("%H:%M:%S")
        }

        active_tasks[task_id] = task_info
        save_tasks_to_disk()
        spawn_task_worker(task_info)

    return jsonify({"status": "success", "message": f"Multi-GC Mega Fight started across {len(accounts)} accounts (Auto-targeting their GCs)!"})

@app.route('/api/task/stop', methods=['POST'])
def stop_task():
    data = request.json
    task_id = data.get('task_id')
    if task_id in active_tasks:
        del active_tasks[task_id]
        save_tasks_to_disk()
        add_log(f"Terminated task ID: {task_id}")
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Task not found"}), 404

@app.route('/api/tasks/active', methods=['GET'])
def get_active_tasks():
    tasks_list = list(active_tasks.values())
    uptime_seconds = int(time.time() - SERVER_START_TIME)
    return jsonify({
        "tasks": tasks_list, 
        "logs": logs,
        "uptime_seconds": uptime_seconds
    })

@app.route('/api/group/create', methods=['POST'])
def create_group():
    data = request.json
    session_id = data.get('session_id')
    title = data.get('title')
    usernames = data.get('usernames', [])
    try:
        cl = get_instagrapi_client(session_id)
        user_ids = [cl.user_id_from_username(u.strip().replace('@', '')) for u in usernames if u.strip()]
        
        while len(user_ids) < 2:
            rand_uname = generate_random_username()
            try:
                uid = cl.user_id_from_username(rand_uname)
                if uid not in user_ids:
                    user_ids.append(uid)
            except:
                continue

        thread = cl.direct_thread_create(user_ids, title)
        add_log(f"Created Group '{title}' with ID: {thread.id}")
        return jsonify({"status": "success", "thread_id": thread.id})
    except Exception as e:
        add_log(f"Group creation failed: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
