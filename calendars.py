import calendar, datetime, os, json, time, threading
from dateutil.relativedelta import relativedelta
from playsound import playsound

# --- SETTINGS ---
calendar.setfirstweekday(calendar.SUNDAY)
DATA_FILE = ".cal_events.json"
SOUND_FILE = "alert.mp3" 

# Control flag
is_paused = False

def get_chaos_stamp():
    n = datetime.datetime.now()
    return n.strftime(f"%S:%M:%H:%d:{n.isocalendar()[1]}:%m:%y")

def load_events():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def check_alarms():
    events = load_events()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated = False
    for t, desc in list(events.items()):
        if now_str >= t:
            if os.path.exists(SOUND_FILE):
                try: threading.Thread(target=playsound, args=(SOUND_FILE,), daemon=True).start()
                except: pass 
            print(f"\n[!!!] ALERT: {desc.upper()} [!!!]")
            del events[t]; updated = True
    if updated:
        with open(DATA_FILE, "w") as f: json.dump(events, f, indent=4)

def parse_at(cmd):
    try:
        p = cmd.lower().split()
        val, unit = int(p[1]), p[2]
        desc = " ".join(p[3:])
        for fluff in ["will be", "is", "it is", "going to"]:
            desc = desc.replace(fluff, "").strip()
        
        # Relativedelta mapping
        mapping = {unit if unit.endswith('s') else unit+'s': val}
        target = (datetime.datetime.now() + relativedelta(**mapping)).strftime("%Y-%m-%d %H:%M:%S")
        
        events = load_events()
        events[target] = desc
        with open(DATA_FILE, "w") as f: json.dump(events, f, indent=4)
        return f"Locked: '{desc}' for {target}"
    except: return "Usage: at [n] [unit] [event]"

def user_input_handler():
    global is_paused
    while True:
        input() # Wait for user to hit Enter to interrupt
        is_paused = True
        print("\n--- CLOCK PAUSED ---")
        cmd = input("COMMAND (or 'exit'): ").strip()
        
        if cmd.lower() == 'exit':
            os._exit(0)
        elif cmd.lower().startswith('at '):
            print(parse_at(cmd))
            time.sleep(1.5)
        
        is_paused = False

if __name__ == "__main__":
    # Start the input thread
    threading.Thread(target=user_input_handler, daemon=True).start()
    
    while True:
        if not is_paused:
            os.system('cls' if os.name == 'nt' else 'clear')
            now = datetime.datetime.now()
            print(f"CHAOS_INDEX | {get_chaos_stamp()}\n" + "="*35)
            print(calendar.month(now.year, now.month)) 
            check_alarms()
            print("\n[PRESS ENTER TO TYPE A COMMAND]")
        
        time.sleep(1)
