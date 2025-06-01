from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import os
import uuid
from selftesting import HealthcareChatbot

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

USERS_FILE = "users.json"
PATIENTS_FILE = "patients.jsonpytho"
DOCTORS_FILE = "doctors.json"
APPOINTMENTS_FILE = "appointments.json"

kb_path = r"D:\btap SAD\Chatbot Healthcare\knowledge_base"
chatbot = HealthcareChatbot(kb_path)

# --- Hàm load/save người dùng ---
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

# --- Hàm load/save bệnh nhân ---
def load_patients():
    if not os.path.exists(PATIENTS_FILE):
        return []
    with open(PATIENTS_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return []
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return []

def save_patients(patients):
    with open(PATIENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(patients, f, indent=2, ensure_ascii=False)

# --- Hàm load/save bác sĩ ---
def load_doctors():
    if not os.path.exists(DOCTORS_FILE):
        return []
    with open(DOCTORS_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return []
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return []

def save_doctors(doctors):
    with open(DOCTORS_FILE, "w", encoding="utf-8") as f:
        json.dump(doctors, f, indent=2, ensure_ascii=False)

# --- Hàm load/save lịch hẹn ---
def load_appointments():
    if not os.path.exists(APPOINTMENTS_FILE):
        return []
    with open(APPOINTMENTS_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return []
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return []

def save_appointments(appointments):
    with open(APPOINTMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(appointments, f, indent=2, ensure_ascii=False)

# --- Decorator kiểm tra đăng nhập ---
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            flash("Bạn cần đăng nhập để truy cập trang này.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes đăng nhập/đăng ký/đăng xuất ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        users = load_users()
        user = users.get(email)

        if user and user["password"] == password:
            session["user"] = email
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Email hoặc mật khẩu không đúng.", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        password_confirm = request.form.get("password_confirm", "").strip()

        if not email or not password or not password_confirm:
            flash("Vui lòng điền đủ thông tin.", "warning")
        elif password != password_confirm:
            flash("Mật khẩu xác nhận không khớp.", "warning")
        else:
            users = load_users()
            if email in users:
                flash("Email đã được đăng ký.", "warning")
            else:
                users[email] = {"password": password}
                save_users(users)
                flash("Đăng ký thành công! Bạn có thể đăng nhập.", "success")
                return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Bạn đã đăng xuất.", "info")
    return redirect(url_for("login"))

# --- Trang dashboard ---
@app.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session.get("user"))

# --- Trang quản lý bệnh nhân ---
@app.route("/patients")
@login_required
def patients():
    patients = load_patients()
    return render_template("patients.html", patients=patients, username=session.get("user"))

# --- API lấy danh sách bệnh nhân ---
@app.route("/api/patients", methods=["GET"])
@login_required
def api_get_patients():
    return jsonify(load_patients())

# --- API thêm bệnh nhân ---
@app.route("/api/patients", methods=["POST"])
@login_required
def api_add_patient():
    data = request.json
    patients = load_patients()
    new_id = max([p.get("id", 0) for p in patients], default=0) + 1
    new_patient = {
        "id": new_id,
        "name": data.get("name", ""),
        "gender": data.get("gender", ""),
        "address": data.get("address", ""),
        "email": data.get("email", ""),
        "phone": data.get("phone", "")
    }
    patients.append(new_patient)
    save_patients(patients)
    return jsonify({"success": True, "message": "Thêm bệnh nhân thành công!", "patient": new_patient})

# --- API sửa bệnh nhân ---
@app.route("/api/patients/<int:patient_id>", methods=["PUT"])
@login_required
def api_edit_patient(patient_id):
    data = request.json
    patients = load_patients()
    for p in patients:
        if p.get("id") == patient_id:
            p["name"] = data.get("name", p["name"])
            p["gender"] = data.get("gender", p["gender"])
            p["address"] = data.get("address", p["address"])
            p["email"] = data.get("email", p["email"])
            p["phone"] = data.get("phone", p["phone"])
            save_patients(patients)
            return jsonify({"success": True, "message": "Cập nhật bệnh nhân thành công!", "patient": p})
    return jsonify({"success": False, "message": "Không tìm thấy bệnh nhân"}), 404

# --- API xóa bệnh nhân ---
@app.route("/api/patients/<int:patient_id>", methods=["DELETE"])
@login_required
def api_delete_patient(patient_id):
    patients = load_patients()
    new_patients = [p for p in patients if p.get("id") != patient_id]
    if len(new_patients) == len(patients):
        return jsonify({"success": False, "message": "Không tìm thấy bệnh nhân"}), 404
    save_patients(new_patients)
    return jsonify({"success": True, "message": "Xóa bệnh nhân thành công!"})

# --- Trang quản lý bác sĩ ---
@app.route("/doctors")
@login_required
def doctors():
    doctors = load_doctors()
    return render_template("doctors.html", doctors=doctors, username=session.get("user"))

# --- API lấy danh sách bác sĩ ---
@app.route("/api/doctors", methods=["GET"])
@login_required
def api_get_doctors():
    return jsonify(load_doctors())

# --- API thêm bác sĩ ---
@app.route("/api/doctors", methods=["POST"])
@login_required
def api_add_doctor():
    data = request.json
    doctors = load_doctors()
    new_id = max([d.get("id", 0) for d in doctors], default=0) + 1
    new_doctor = {
        "id": new_id,
        "name": data.get("name", ""),
        "specialty": data.get("specialty", ""),
        "phone": data.get("phone", ""),
        "email": data.get("email", ""),
        "patients": data.get("patients", [])
    }
    doctors.append(new_doctor)
    save_doctors(doctors)
    return jsonify({"success": True, "message": "Thêm bác sĩ thành công!", "doctor": new_doctor})

# --- API sửa bác sĩ ---
@app.route("/api/doctors/<int:doctor_id>", methods=["PUT"])
@login_required
def api_edit_doctor(doctor_id):
    data = request.json
    doctors = load_doctors()
    for d in doctors:
        if d.get("id") == doctor_id:
            d["name"] = data.get("name", d["name"])
            d["specialty"] = data.get("specialty", d["specialty"])
            d["phone"] = data.get("phone", d["phone"])
            d["email"] = data.get("email", d["email"])
            d["patients"] = data.get("patients", d.get("patients", []))
            save_doctors(doctors)
            return jsonify({"success": True, "message": "Cập nhật bác sĩ thành công!", "doctor": d})
    return jsonify({"success": False, "message": "Không tìm thấy bác sĩ"}), 404

# --- API xóa bác sĩ ---
@app.route("/api/doctors/<int:doctor_id>", methods=["DELETE"])
@login_required
def api_delete_doctor(doctor_id):
    doctors = load_doctors()
    new_doctors = [d for d in doctors if d.get("id") != doctor_id]
    if len(new_doctors) == len(doctors):
        return jsonify({"success": False, "message": "Không tìm thấy bác sĩ"}), 404
    save_doctors(new_doctors)
    return jsonify({"success": True, "message": "Xóa bác sĩ thành công!"})

# --- Trang quản lý lịch hẹn ---
@app.route("/appointments")
@login_required
def appointments():
    appointments = load_appointments()
    patients = load_patients()
    doctors = load_doctors()
    return render_template("appointments.html", appointments=appointments, patients=patients, doctors=doctors, username=session.get("user"))

# --- API lấy danh sách lịch hẹn ---
@app.route("/api/appointments", methods=["GET"])
@login_required
def api_get_appointments():
    return jsonify(load_appointments())

# --- API thêm lịch hẹn ---
@app.route("/api/appointments", methods=["POST"])
@login_required
def api_add_appointment():
    data = request.json
    appointments = load_appointments()
    new_id = max([a.get("id", 0) for a in appointments], default=0) + 1
    new_appointment = {
        "id": new_id,
        "patient": data.get("patient", ""),
        "doctor": data.get("doctor", ""),
        "date": data.get("date", ""),
        "symptoms": data.get("symptoms", ""),
        "status": data.get("status", "Chưa xác nhận"),
        "notes": data.get("notes", "")
    }
    appointments.append(new_appointment)
    save_appointments(appointments)
    return jsonify({"success": True, "message": "Thêm lịch hẹn thành công!", "appointment": new_appointment})

# --- API sửa lịch hẹn ---
@app.route("/api/appointments/<int:appointment_id>", methods=["PUT"])
@login_required
def api_edit_appointment(appointment_id):
    data = request.json
    appointments = load_appointments()
    for a in appointments:
        if a.get("id") == appointment_id:
            a["patient"] = data.get("patient", a["patient"])
            a["doctor"] = data.get("doctor", a["doctor"])
            a["date"] = data.get("date", a["date"])
            a["symptoms"] = data.get("symptoms", a["symptoms"])
            a["status"] = data.get("status", a["status"])
            a["notes"] = data.get("notes", a["notes"])
            save_appointments(appointments)
            return jsonify({"success": True, "message": "Cập nhật lịch hẹn thành công!", "appointment": a})
    return jsonify({"success": False, "message": "Không tìm thấy lịch hẹn"}), 404

# --- API xóa lịch hẹn ---
@app.route("/api/appointments/<int:appointment_id>", methods=["DELETE"])
@login_required
def api_delete_appointment(appointment_id):
    appointments = load_appointments()
    new_appointments = [a for a in appointments if a.get("id") != appointment_id]
    if len(new_appointments) == len(appointments):
        return jsonify({"success": False, "message": "Không tìm thấy lịch hẹn"}), 404
    save_appointments(new_appointments)
    return jsonify({"success": True, "message": "Xóa lịch hẹn thành công!"})

# --- API Chatbot cho selftesting và đặt lịch ---
@app.route("/api/chatbot", methods=["POST"])
def api_chatbot():
    data = request.json
    mode = data.get("mode", "lookup")
    user_message = data.get("message", "").strip().lower()

    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    if not user_message:
        return jsonify({"reply": "Bạn chưa nhập câu hỏi."})

    # Chatbot lookup thông thường
    if mode == "lookup":
        matched_entry, score = chatbot.find_best_match(user_message)
        if matched_entry:
            answer = matched_entry.get("answer", "Xin lỗi, tôi chưa có câu trả lời phù hợp.")
        else:
            answer = "Rất tiếc, tôi chưa hiểu câu hỏi của bạn."
        return jsonify({"reply": answer})

    # Chatbot chẩn đoán
    elif mode == "diagnosis":
        if "diagnosis_state" not in session:
            session["diagnosis_state"] = {
                "current_index": 0,
                "symptoms_answered": []
            }
            first_symptom = chatbot.symptoms_list[0]
            return jsonify({"reply": f"Bạn có bị {first_symptom} không? (y/n)"})

        else:
            state = session["diagnosis_state"]
            ans = user_message
            if ans not in ["y", "n"]:
                return jsonify({"reply": "Vui lòng trả lời 'y' hoặc 'n'."})

            idx = state["current_index"]
            symptom = chatbot.symptoms_list[idx]
            state["symptoms_answered"].append((symptom, ans))

            idx += 1
            if idx >= len(chatbot.symptoms_list):
                symptoms_positive = [s for s, a in state["symptoms_answered"] if a == "y"]
                diagnosis_entry = chatbot.diagnose(symptoms_positive)
                result_text = chatbot.get_full_diagnosis_info(diagnosis_entry)
                session.pop("diagnosis_state", None)
                return jsonify({"reply": result_text})
            else:
                state["current_index"] = idx
                session["diagnosis_state"] = state
                next_symptom = chatbot.symptoms_list[idx]
                return jsonify({"reply": f"Bạn có bị {next_symptom} không? (y/n)"})

    # Chatbot đặt lịch
    elif mode == "appointment":
        if "appointment_state" not in session:
            session["appointment_state"] = {
                "step": 0,
                "appointment_data": {}
            }
            return jsonify({"reply": "Xin chào! Tôi là trợ lý đặt lịch. Bạn vui lòng cho biết tên bệnh nhân."})

        else:
            state = session["appointment_state"]
            step = state["step"]
            user_input = user_message.strip()

            if step == 0:
                state["appointment_data"]["patient"] = user_input
                state["step"] = 1
                session["appointment_state"] = state
                return jsonify({"reply": "Vui lòng cho biết tên bác sĩ bạn muốn đặt lịch."})

            elif step == 1:
                state["appointment_data"]["doctor"] = user_input
                state["step"] = 2
                session["appointment_state"] = state
                return jsonify({"reply": "Vui lòng cho biết ngày hẹn (YYYY-MM-DD)."})

            elif step == 2:
                state["appointment_data"]["date"] = user_input
                state["step"] = 3
                session["appointment_state"] = state
                return jsonify({"reply": "Vui lòng mô tả triệu chứng."})

            elif step == 3:
                state["appointment_data"]["symptoms"] = user_input
                state["step"] = 4
                session["appointment_state"] = state
                return jsonify({"reply": "Bạn có muốn ghi chú gì thêm không?"})

            elif step == 4:
                state["appointment_data"]["notes"] = user_input
                # Lưu lịch hẹn
                appointments = load_appointments()
                new_id = max([a.get("id", 0) for a in appointments], default=0) + 1
                new_appointment = {
                    "id": new_id,
                    "patient": state["appointment_data"].get("patient", ""),
                    "doctor": state["appointment_data"].get("doctor", ""),
                    "date": state["appointment_data"].get("date", ""),
                    "symptoms": state["appointment_data"].get("symptoms", ""),
                    "status": "Chưa xác nhận",
                    "notes": state["appointment_data"].get("notes", "")
                }
                appointments.append(new_appointment)
                save_appointments(appointments)
                session.pop("appointment_state", None)
                return jsonify({"reply": "Lịch hẹn đã được lưu thành công! Cảm ơn bạn."})

            else:
                session.pop("appointment_state", None)
                return jsonify({"reply": "Đã xảy ra lỗi. Vui lòng thử lại."})

    else:
        return jsonify({"reply": "Chế độ không hợp lệ."})

if __name__ == "__main__":
    app.run(debug=True)
