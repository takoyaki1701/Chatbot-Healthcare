from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from selftesting import HealthcareChatbot
import uuid

app = Flask(__name__)
app.secret_key = "super_secret_key"
CORS(app)

kb_path = r"D:\Chatbot Healthcare\knowledge_base"
chatbot = HealthcareChatbot(kb_path)

@app.route("/")
def index():
    return render_template("chatbot.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    mode = data.get("mode", "lookup")
    user_message = data.get("message", "").strip().lower()

    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

    if not user_message:
        return jsonify({"reply": "Bạn chưa nhập câu hỏi."})

    if mode == "lookup":
        matched_entry, score = chatbot.find_best_match(user_message)
        if matched_entry:
            answer = matched_entry.get("answer", "Xin lỗi, tôi chưa có câu trả lời phù hợp.")
        else:
            answer = "Rất tiếc, tôi chưa hiểu câu hỏi của bạn."
        return jsonify({"reply": answer})

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

    else:
        return jsonify({"reply": "Chế độ không hợp lệ."})

if __name__ == "__main__":
    app.run(debug=True)
