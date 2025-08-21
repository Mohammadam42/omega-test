from flask import Flask, request, jsonify, render_template
from threading import Lock

app = Flask(__name__)

# ---- Shared Data ----
robot_status = {"state": "OFF", "value": 0}  # حالة الروبوت و القيمة القادمة من ESP32
data_lock = Lock()  # لتجنب مشاكل الوصول المتزامن

# ---- Main Web Page ----
@app.route("/")
def index():
    with data_lock:
        status = robot_status["state"]
        value = robot_status["value"]
    return render_template("index.html", status=status, value=value)

# ---- API for ESP32 to send data ----
# ---- API for ESP32 to send data ----
@app.route("/api/update", methods=["GET", "POST"])
def update_from_esp32():
    if request.method == "POST":
        data = request.json
        if not data or "value" not in data:
            return jsonify({"status": "error", "message": "Missing 'value'"}), 400
        with data_lock:
            robot_status["value"] = data["value"]
        return jsonify({"status": "ok", "message": "Value updated"}), 200
    else:  # GET
        with data_lock:
            return jsonify({"value": robot_status["value"], "state": robot_status["state"]})

# ---- API for Web to send commands to ESP32 ----
@app.route("/api/command", methods=["POST"])
def send_command():
    data = request.json
    if not data or "command" not in data:
        return jsonify({"status": "error", "message": "Missing 'command'"}), 400

    command = data["command"].upper()
    if command not in ["ON", "OFF"]:
        return jsonify({"status": "error", "message": "Invalid command"}), 400

    # تحديث الحالة المشتركة
    with data_lock:
        robot_status["state"] = command
    # هنا يمكنك إضافة أي كود لإرسال الأمر فعليًا للـ ESP32 عبر HTTP
    return jsonify({"status": "ok", "message": f"Command '{command}' sent"}), 200

if __name__ == "__main__":
    # Port 5000 -> واجهة الويب
    app.run(host="0.0.0.0", port=5000, debug=True)

