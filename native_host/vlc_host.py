import sys
import json
import struct
import subprocess
import os
import logging

# Setup logging to diagnose any runtime issues
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vlc_host.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logging.info("VLC Host started.")

def read_message():
    try:
        raw_length = sys.stdin.buffer.read(4)
        if len(raw_length) == 0:
            logging.info("Stdin EOF reached.")
            return None
        message_length = struct.unpack('@I', raw_length)[0]
        
        message_bytes = sys.stdin.buffer.read(message_length)
        if len(message_bytes) < message_length:
            logging.error("Incomplete message body read.")
            return None
            
        message = message_bytes.decode('utf-8')
        logging.info(f"Received raw message: {message}")
        return json.loads(message)
    except Exception as e:
        logging.exception("Error reading message:")
        return None

def send_message(message_dict):
    try:
        message_bytes = json.dumps(message_dict).encode('utf-8')
        length_bytes = struct.pack('@I', len(message_bytes))
        sys.stdout.buffer.write(length_bytes)
        sys.stdout.buffer.write(message_bytes)
        sys.stdout.buffer.flush()
        logging.info(f"Sent response: {message_dict}")
    except Exception as e:
        logging.exception("Error sending message:")

def find_vlc():
    paths = [
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "VideoLAN", "VLC", "vlc.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "VideoLAN", "VLC", "vlc.exe"),
    ]
    for p in paths:
        if os.path.exists(p):
            logging.info(f"Found VLC at: {p}")
            return p
    logging.warning("VLC not found in standard paths. Attempting to run via command 'vlc'...")
    return "vlc"

def main():
    try:
        msg = read_message()
        if not msg:
            sys.exit(0)

        if msg.get("ping"):
            logging.info("Ping message received.")
            send_message({"status": "ok", "ping": True})
            sys.exit(0)

        url = msg.get("url")
        if not url:
            logging.warning("No URL provided in message.")
            send_message({"status": "error", "error": "No URL provided"})
            sys.exit(0)
        
        vlc_bin = find_vlc()
        logging.info(f"Launching VLC for URL: {url}")
        
        pid = None
        launched = False
        
        if os.name == 'nt':
            try:
                os.startfile(vlc_bin, arguments=f'"{url}"')
                logging.info("VLC successfully launched via os.startfile.")
                launched = True
            except Exception as e:
                logging.warning(f"os.startfile failed: {e}")
                
            if not launched:
                try:
                    cmd = f'start "" "{vlc_bin}" "{url}"'
                    subprocess.Popen(cmd, shell=True)
                    logging.info("VLC successfully launched via cmd start command.")
                    launched = True
                except Exception as e:
                    logging.warning(f"cmd start failed: {e}")
                    
        if not launched:
            proc = subprocess.Popen([vlc_bin, url], close_fds=True)
            pid = proc.pid
            logging.info(f"VLC process spawned via Popen with PID {pid}.")
            
        send_message({"status": "success", "pid": pid})
        sys.exit(0)
        
    except Exception as e:
        logging.exception("Error in main execution:")
        send_message({"status": "error", "error": str(e)})
        sys.exit(1)

if __name__ == '__main__':
    main()
