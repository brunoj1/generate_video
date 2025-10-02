import runpod
from runpod.serverless.utils import rp_upload
import os
import websocket
import base64
import json
import uuid
import logging
import urllib.request
import urllib.parse
import binascii  # Import for handling Base64 errors
# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server_address = os.getenv('SERVER_ADDRESS', '127.0.0.1')
client_id = str(uuid.uuid4())

def save_data_if_base64(data_input, temp_dir, output_filename):
    """
    Checks if the input data is a Base64 string. If so, saves it as a file and returns the path.
    If it's a regular path string, returns it as is.
    """
    # If the input is not a string, return it as is
    if not isinstance(data_input, str):
        return data_input

    try:
        # Base64 strings will decode successfully
        decoded_data = base64.b64decode(data_input)
        
        # Create the directory if it doesn't exist
        os.makedirs(temp_dir, exist_ok=True)
        
        # If decoding succeeds, save it as a temporary file
        file_path = os.path.abspath(os.path.join(temp_dir, output_filename))
        with open(file_path, 'wb') as f:  # Save in binary write mode ('wb')
            f.write(decoded_data)
        
        # Return the path of the saved file
        print(f"✅ Saved Base64 input as file '{file_path}'.")
        return file_path

    except (binascii.Error, ValueError):
        # If decoding fails, treat it as a regular path and return the original value
        print(f"➡️ Treating '{data_input}' as a file path.")
        return data_input

def queue_prompt(prompt):
    url = f"http://{server_address}:8188/prompt"
    logger.info(f"Queueing prompt to: {url}")
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(url, data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    url = f"http://{server_address}:8188/view"
    logger.info(f"Getting image from: {url}")
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"{url}?{url_values}") as response:
        return response.read()

def get_history(prompt_id):
    url = f"http://{server_address}:8188/history/{prompt_id}"
    logger.info(f"Getting history from: {url}")
    with urllib.request.urlopen(url) as response:
        return json.loads(response.read())

def get_videos(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_videos = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break
        else:
            continue

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        videos_output = []
        if 'gifs' in node_output:
            for video in node_output['gifs']:
                # Read the file directly using fullpath and encode it to base64
                with open(video['fullpath'], 'rb') as f:
                    video_data = base64.b64encode(f.read()).decode('utf-8')
                videos_output.append(video_data)
        output_videos[node_id] = videos_output

    return output_videos

def load_workflow(workflow_path):
    with open(workflow_path, 'r') as file:
        return json.load(file)

def handler(job):
    job_input = job.get("input", {})

    logger.info(f"Received job input: {job_input}")
    task_id = f"task_{uuid.uuid4()}"
    last_task_id = f"task_{uuid.uuid4()}"

    first_image_base64_input = job_input.get("first_image_base64")
    last_image_base64_input = job_input.get("last_image_base64")

    # Use helper function to determine image file path (Base64 or Path)
    # Since the image extension is unknown, assume .jpg or get it from input  
    first_image_path = save_data_if_base64(first_image_base64_input, task_id, "first_input_image.jpg")
    last_image_path = save_data_if_base64(last_image_base64_input, last_task_id, "last_input_image.jpg")

    # Choose appropriate workflow file
    workflow_file = "/wan22.json"

    prompt = load_workflow(workflow_file)
    
    length = job_input.get("length", 81)
    steps = job_input.get("steps", 10)

    prompt["260"]["inputs"]["image"] = first_image_path
    prompt["261"]["inputs"]["image"] = last_image_path
    prompt["846"]["inputs"]["value"] = length
    prompt["246"]["inputs"]["value"] = job_input["prompt"]
    prompt["835"]["inputs"]["noise_seed"] = job_input["seed"]
    prompt["830"]["inputs"]["cfg"] = job_input["cfg"]
    prompt["849"]["inputs"]["value"] = job_input["width"]
    prompt["848"]["inputs"]["value"] = job_input["height"]
    
    # Apply step configuration
    if "834" in prompt:
        prompt["834"]["inputs"]["steps"] = steps
        logger.info(f"Steps set to: {steps}")
        lowsteps = int(steps * 0.6)
        prompt["829"]["inputs"]["step"] = lowsteps
        logger.info(f"LowSteps set to: {lowsteps}")      
                        
    ws_url = f"ws://{server_address}:8188/ws?clientId={client_id}"
    logger.info(f"Connecting to WebSocket: {ws_url}")
    
    # First check if HTTP connection is possible
    http_url = f"http://{server_address}:8188/"
    logger.info(f"Checking HTTP connection to: {http_url}")
    
    # Check HTTP connection (up to 1 minute)
    max_http_attempts = 180
    for http_attempt in range(max_http_attempts):
        try:
            import urllib.request
            response = urllib.request.urlopen(http_url, timeout=5)
            logger.info(f"HTTP connection successful (attempt {http_attempt+1})")
            break
        except Exception as e:
            logger.warning(f"HTTP connection failed (attempt {http_attempt+1}/{max_http_attempts}): {e}")
            if http_attempt == max_http_attempts - 1:
                raise Exception("Cannot connect to ComfyUI server. Please check if the server is running.")
            time.sleep(1)
    
    ws = websocket.WebSocket()
    # Attempt WebSocket connection (up to 3 minutes)
    max_attempts = int(180 / 5)  # 3 minutes (try every 5 seconds)
    for attempt in range(max_attempts):
        import time
        try:
            ws.connect(ws_url)
            logger.info(f"WebSocket connection successful (attempt {attempt+1})")
            break
        except Exception as e:
            logger.warning(f"WebSocket connection failed (attempt {attempt+1}/{max_attempts}): {e}")
            if attempt == max_attempts - 1:
                raise Exception("WebSocket connection timed out (3 minutes)")
            time.sleep(5)

    videos = get_videos(ws, prompt)
    ws.close()

    # Handle case when no video is found
    for node_id in videos:
        if videos[node_id]:
            return {"video": videos[node_id][0]}
    
    return {"error": "Unable to find video."}

runpod.serverless.start({"handler": handler})