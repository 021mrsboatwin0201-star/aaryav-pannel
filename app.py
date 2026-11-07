import os
import time
import json
import random
import asyncio
import threading
import urllib.request
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from instagrapi import Client
from playwright.async_api import async_playwright

app = Flask(__name__)
CORS(app)

ACTIVE_TASKS = {}
LOGS = []
INSTA_CLIENTS = {}

IST = timezone(timedelta(hours=5, minutes=30))

def ist_now():
    n = datetime.now(IST)
    return f"{n.hour:02d}:{n.minute:02d}:{n.second:02d}:{n.microsecond // 1000:03d}"

def add_log(msg):
    timestamp = time.strftime("%H:%M:%S")
    LOGS.insert(0, f"[{timestamp}] {msg}")
    if len(LOGS) > 100:
        LOGS.pop()

# ==========================================
# EXISTING INSTAGRAPI WORKER (UNTOUCHED)
# ==========================================
def background_worker(thread_task_id, task_data):
    add_log(f"[WORKER] Task {thread_task_id} launched.")
    task_type = task_data.get('type')
    session_id = task_data.get('session_id')
    username = task_data.get('username')
    thread_id = str(task_data.get('thread_id', '')).strip()
    
    target_name = task_data.get('target', '').strip()
    jitter = float(task_data.get('jitter', 5.0))
    payload = task_data.get('payload', [])

    client = INSTA_CLIENTS.get(session_id)
    if not client:
        add_log(f"[ERROR] Session client missing for @{username}")
        if thread_task_id in ACTIVE_TASKS:
            ACTIVE_TASKS[thread_task_id]['running'] = False
        return

    idx = 0
    while ACTIVE_TASKS.get(thread_task_id, {}).get('running', False):
        try:
            if task_type == 'spam' and payload:
                raw_msg = payload[idx % len(payload)]
                if isinstance(raw_msg, str) and raw_msg.strip():
                    formatted_msg = raw_msg.replace("{target}", target_name)
                    client.direct_send(formatted_msg, thread_ids=[thread_id])
                    add_log(f"[SENT] @{username} -> Thread {thread_id}: {formatted_msg[:30]}...")
                idx += 1
            elif task_type == 'nclock':
                emojis = ['💕', '🔥', '✨', '👑', '⚡', '😈']
                current_emoji = emojis[idx % len(emojis)]
                nc_text = task_data.get('nc_text', '')
                new_title = f"{nc_text} {current_emoji}"
                
                try:
                    client.direct_thread_update_title(thread_id, new_title)
                    add_log(f"[NC LOCK] @{username} -> Title: {new_title}")
                except Exception as inner_e:
                    add_log(f"[NC LOCK ERROR] @{username}: {str(inner_e)}")
                idx += 1
            
            time.sleep(jitter)
        except Exception as e:
            add_log(f"[ERROR] Task {thread_task_id} (@{username}): {str(e)}")
            time.sleep(8)

    add_log(f"[WORKER] Task {thread_task_id} terminated.")

# ==========================================
# NEW PLAYWRIGHT WORKER (yashpy.py INTEGRATION)
# ==========================================
PRIMARY_SELECTOR = 'div[role="textbox"]'
MOBILE_UA = "Mozilla/5.0 (Linux; Android 13; vivo V60) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36"
MOBILE_VIEWPORT = {"width": 412, "height": 915}
_SEL = json.dumps(PRIMARY_SELECTOR)

JS_FILL = f"""
(text) => {{
    const el = document.querySelector({_SEL});
    if (!el) return null;
    const wasEmpty = el.innerText.trim() === '';
    el.focus();
    document.execCommand('selectAll', false, null);
    const dt = new DataTransfer();
    dt.setData('text/plain', text);
    el.dispatchEvent(new ClipboardEvent('paste', {{
        clipboardData: dt,
        bubbles: true,
        cancelable: true
    }}));
    return wasEmpty;
}}
"""

async def run_playwright_spammer(task_id, task_data):
    url = task_data.get('url')
    target = task_data.get('target', 'target')
    messages = task_data.get('messages', [
        "[{t}] [{time}] TIME DEKH OR MAA CHUDWA APNI 💙"
    ])
    profile_dir = task_data.get('profile_dir')
    username = task_data.get('username', 'playwright_user')

    add_log(f"[PLAYWRIGHT] Launching browser for @{username}...")

    line_templates = [
        [line.replace("{t}", target) for line in m.split("\n")]
        for m in messages
    ]
    pool_size = len(line_templates)

    def get_next_msg():
        t = ist_now()
        tmpl = line_templates[random.randrange(pool_size)]
        return "\n".join(line.replace("{time}", t) for line in tmpl)

    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=True,
                args=[
                    "--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu",
                    "--disable-setuid-sandbox", "--disable-extensions",
                    "--disable-blink-features=AutomationControlled"
                ],
                user_agent=MOBILE_UA,
                viewport=MOBILE_VIEWPORT,
                is_mobile=True,
                has_touch=True,
                ignore_https_errors=True
            )

            await browser.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """)

            page = browser.pages[0] if browser.pages else await browser.new_page()
            await page.goto(url, timeout=60000, wait_until='domcontentloaded')

            add_log(f"[PLAYWRIGHT] Connected to thread for @{username}")

            while ACTIVE_TASKS.get(task_id, {}).get('running', False):
                try:
                    el = await page.query_selector(PRIMARY_SELECTOR)
                    if el:
                        msg_text = get_next_msg()
                        await page.evaluate(JS_FILL, msg_text)
                        await page.keyboard.press("Enter")
                        add_log(f"[PLAYWRIGHT SENT] @{username} -> Message dispatched")
                    else:
                        add_log(f"[PLAYWRIGHT WARN] Input box not visible for @{username}")
                        await asyncio.sleep(3)
                    await asyncio.sleep(1)
                except Exception as inner_ex:
                    add_log(f"[PLAYWRIGHT ERROR] {str(inner_ex)}")
                    await asyncio.sleep(2)

            await browser.close()
            add_log(f"[PLAYWRIGHT] Session ended for @{username}")

        except Exception as e:
            add_log(f"[PLAYWRIGHT CRASH] @{username}: {str(e)}")

def start_playwright_thread(task_id, task_data):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_playwright_spammer(task_id, task_data))

# ==========================================
# FLASK ROUTES (INSTAGRAPI + PLAYWRIGHT)
# ==========================================
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
    task_type = data.get('type')
    task_id = f"{task_type}_{data.get('username', 'user')}_{int(time.time())}"
    
    ACTIVE_TASKS[task_id] = {
        'running': True,
        'type': task_type,
        'username': data.get('username'),
        'thread_id': data.get('thread_id', 'N/A'),
        'started_at': time.strftime("%H:%M:%S")
    }

    if task_type == 'playwright_spam':
        thread = threading.Thread(target=start_playwright_thread, args=(task_id, data), daemon=True)
    else:
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
    app.run(host='0.0.0.0', port=port)
