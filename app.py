import os
import time
import threading
import random
import string
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, jsonify, request, send_from_directory
from instagrapi import Client

app = Flask(__name__, static_folder='.')

active_tasks = {}
task_threads = {}
logs = []

# Unlimited / High Workers pool taaki 50+ IDs ek sath parallel makkhan chalein
executor = ThreadPoolExecutor(max_workers=None)

# Cooldown tracking for 403 blocks per individual GC: { "session_threadid": unfreeze_timestamp }
cooldown_tracker = {}

# Saved Templates Storage
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

# ==================== 1. FETCH ALL GCS FROM MAIN ACCOUNT ====================
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

# ==================== 2. MASS GC CREATOR (WITH SMART FALLBACK) ====================
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

                # Try user-provided usernames first
                if base_usernames and random.random() > 0.3:
                    target_uname = random.choice(base_usernames).strip()
                    try:
                        uid = cl.user_id_from_username(target_uname)
                        user_ids.append(uid)
                    except:
                        pass

                # Fallback to random alphanumeric valid users
                if not user_ids:
                    for _ in range(5):
                        rand_uname = generate_random_username()
                        try:
                            uid = cl.user_id_from_username(rand_uname)
                            user_ids.append(uid)
                            break
                        except:
                            continue

                if not user_ids:
                    session_idx += 1
                    time.sleep(2)
                    continue

                group_title = f"{target_prefix} GC #{created_count + 1} ⚡"
                thread = cl.direct_create_group(user_ids, group_title)
                created_count += 1
                add_log(f"[GC CREATED] #{created_count} -> Title: {group_title}")
                time.sleep(random.uniform(6, 12))
            except Exception as e:
                add_log(f"[GC CREATION ERROR]: {str(e)}")
                time.sleep(10)
            session_idx += 1
        add_log(f"Mass GC Creation Completed! Total {total_to_create} GCs created.")

    executor.submit(background_mass_creator)
    return jsonify({"status": "success", "message": f"Started creating {total_to_create} GCs in background."})

# ==================== 3. SAVE TEMPLATES ROUTES ====================
@app.route('/api/templates/save_nc', methods=['POST'])
def save_nc_text():
    global saved_nc_templates
    data = request.json
    text_content = data.get('nc_text', '')
    saved_nc_templates = [line.strip() for line in text_content.split('\n') if line.strip()]
    add_log(f"Saved {len(saved_nc_templates)} NC templates.")
    return jsonify({"status": "success", "message": f"Saved {len(saved_nc_templates)} NC templates!"})

@app.route('/api/templates/save_spam', methods=['POST'])
def save_spam_text():
    global saved_spam_templates
    data = request.json
    text_content = data.get('spam_text', '')
    saved_spam_templates = [line.strip() for line in text_content.split('\n') if line.strip()]
    add_log(f"Saved {len(saved_spam_templates)} Spam templates.")
    return jsonify({"status": "success", "message": f"Saved {len(saved_spam_templates)} Spam templates!"})

# ==================== 4. MULTI-GC MEGA FIGHT (DUAL TASK + SINGLE GC ISOLATION) ====================
@app.route('/api/task/start_multi_fight', methods=['POST'])
def start_multi_fight():
    data = request.json
    accounts = data.get('accounts', []) # List of dicts: [{username, sessionid}, ...]
    all_gcs = data.get('thread_ids', []) # List of GC thread IDs
    target_name = data.get('target_name', 'MONARCH')
    interval_seconds = int(data.get('interval', 300))
    task_id_base = str(int(time.time() * 1000))

    if not accounts or not all_gcs:
        return jsonify({"status": "error", "message": "Accounts or GCs missing!"}), 400

    chunk_size = max(1, len(all_gcs) // len(accounts))

    for i, acc in enumerate(accounts):
        acc_user = acc['username']
        acc_sess = acc['sessionid']
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size if i < len(accounts) - 1 else len(all_gcs)
        assigned_gcs = all_gcs[start_idx:end_idx]

        if not assigned_gcs:
            continue

        task_id = f"{task_id_base}_{acc_user}"

        def run_account_multigc_worker(u, s, tids, tid_key):
            try:
                add_log(f"[@{u}] Multi-GC worker spawned with {len(tids)} GCs.")
                while tid_key in active_tasks:
                    for thread_id in tids:
                        if tid_key not in active_tasks:
                            break
                        
                        cooldown_key = f"{s}_{thread_id}"
                        if cooldown_key in cooldown_tracker:
                            if time.time() < cooldown_tracker[cooldown_key]:
                                continue
                            else:
                                del cooldown_tracker[cooldown_key]

                        try:
                            cl = get_instagrapi_client(s)
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

                        time.sleep(3)

                    time.sleep(interval_seconds)
            except Exception as ex:
                add_log(f"[@{u}] Worker crashed: {str(ex)}")
            finally:
                if tid_key in active_tasks:
                    del active_tasks[tid_key]
                if tid_key in task_threads:
                    del task_threads[tid_key]

        active_tasks[task_id] = {"task_id": task_id, "type": "multi_fight", "username": acc_user, "started_at": time.strftime("%H:%M:%S")}
        t = threading.Thread(target=run_account_multigc_worker, args=(acc_user, acc_sess, assigned_gcs, task_id))
        task_threads[task_id] = t
        t.start()

    return jsonify({"status": "success", "message": f"Multi-GC Mega Fight started across {len(accounts)} accounts!"})

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
