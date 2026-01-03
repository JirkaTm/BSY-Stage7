# Stage 7: The Eagles - MQTT Command & Control

This repository contains a stealthy Python-based Command and Control (C&C) system designed to operate over a public MQTT broker. This project was developed as the final task for Stage 7, simulating a covert communication channel that blends into legitimate IoT traffic.

## 1. Project Overview
The project consists of two main components:
* **The Bot (`bot.py`):** Runs on the "infected" machine, listening for commands and executing them.
* **The Controller (`controller.py`):** Used by the operator to send commands and receive exfiltrated data.

---

## 2. Protocol Description - Middle-earth Smart Pantry (MSP)

The MSP protocol is designed to facilitate communication between a central controller and infected bots over the public MQTT broker `147.32.82.209` using the shared topic `sensors`. The protocol follows a Publish/Subscribe model. Both the controller and the bot subscribe to the `sensors` topic.

* **Commands:** Published by the controller; identified by the presence of the `order_type` key.
* **Responses:** Published by the bot; identified by the presence of the `status` key.
* **Encoding:** All command parameters and execution outputs are encoded in **Base64** before transmission.

The protocol uses kitchen-themed aliases to map to required system functionalities:

| System Function | MSP Alias (`order_type`) | Disguised Parameter Key | Parameter Description |
| :--- | :--- | :--- | :--- |
| **Announce/Ping** | `ping_fridge` | N/A | Requests basic status and bot ID. |
| **List Users (w)** | `kitchen_staff` | N/A | Retrieves current system login sessions. |
| **List Directory (ls)** | `check_pantry` | `shelf_id` | Base64 encoded path of the directory. |
| **User ID (id)** | `head_chef` | N/A | Returns the UID of the process owner. |
| **Copy File (cp)** | `export_recipe` | `recipe_book` | Base64 encoded path of the target file. |
| **Execute Binary** | `start_appliance` | `model_no` | Base64 encoded path to a system binary. |

### Message Structure (JSON)

#### Controller Command Example (List /etc)
The controller hides the path `/etc` as `L2V0Yy8=`.
```json
{
  "appliance_id": "SHIRE-FRIDGE-F0C582",
  "target": "SHIRE-FRIDGE-F0C582",
  "order_type": "check_pantry",
  "shelf_id": "L2V0Yy8="
}
```

#### Bot Response Example
The bot responds with the directory listing wrapped in the `items` key, encoded in Base64.
```json
{
  "appliance_id": "SHIRE-FRIDGE-F0C582",
  "status": "inventory_updated",
  "items": "ZHIteHIteHItIDIgcm9vdCA..."
}
```

### Security Features
* **Contextual Blending:** By using keys like `telemetry`, `temp`, and `inventory`, the traffic mimics legitimate Smart Home traffic commonly found on MQTT sensor topics.
* **No String Pattern Matching:** Traditional Intrusion Detection Systems (IDS) looking for strings like `/bin/sh` or `cat` will fail because the payloads are Base64 encoded.
* **Self-Filtering:** Each bot generates a unique `BOT_ID`. Bots ignore any command not addressed to their specific ID or the `ALL` broadcast, preventing accidental triggering of other devices.

---

## 3. Installation

```bash
# Navigate to the project directory
cd ~/7

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required library or just install requirements.txt
pip install paho-mqtt==1.6.1
```

---

## 4. User Guide: Operating the C&C

### Step 1: Start the Bot
Run the bot on the target machine. It will generate a unique ID upon startup (e.g., `SHIRE-FRIDGE-XXXXXX`).
```bash
python3 bot.py
```

### Step 2: Start the Controller
In a separate terminal (with the `venv` active), launch the controller.
```bash
python3 controller.py
```
When prompted for **Target Appliance ID**, enter the specific ID of your bot or type `ALL` to broadcast to all available bots.

### Step 3: Available Commands
Use the menu options (1-6) to interact with the host:

1. **Ping (Announce):** Verifies the bot is alive and returns fake fridge "telemetry."
2. **Kitchen Staff (w):** Returns the output of the `w` command showing current system users.
3. **Check Pantry (ls):** Lists directory contents. You must provide a path (e.g., `/etc`).
4. **Head Chef (id):** Returns the UID and GID of the user running the bot process.
5. **Export Recipe (cp):** Copies a specified file from the host and displays it in the controller.
6. **Start Appliance (exec):** Executes a system binary specified by the controller (e.g., `/usr/bin/ps`).

---

## 5. Deployment Requirements
* **Broker:** `147.32.82.209`
* **Port:** `1883`
* **Topic:** `sensors`
