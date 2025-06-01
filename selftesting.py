import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class HealthcareChatbot:
    def __init__(self, kb_folder_path):
        self.kb_folder_path = kb_folder_path
        self.kb_data = []
        self.treatment_kb = []
        self.warning_kb = []
        self.vectorizer = None
        self.question_vectors = None
        self.questions = []
        self.load_all_kb()
        self.load_treatment_kb()
        self.load_warning_kb()
        self.prepare_vectorizer()

        self.symptoms_list = self.build_symptoms_list()

    def load_all_kb(self):
        for filename in os.listdir(self.kb_folder_path):
            if filename.endswith(".json") and filename not in ["kb_treatment.json", "kb_warning.json"]:
                filepath = os.path.join(self.kb_folder_path, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        filtered = [entry for entry in data if "question" in entry]
                        self.kb_data.extend(filtered)
                    except Exception as e:
                        print(f"Lỗi khi đọc file {filename}: {e}")

    def load_treatment_kb(self):
        try:
            path = os.path.join(self.kb_folder_path, "kb_treatment.json")
            with open(path, "r", encoding="utf-8") as f:
                self.treatment_kb = json.load(f)
        except Exception as e:
            print(f"Lỗi tải dữ liệu điều trị: {e}")

    def load_warning_kb(self):
        try:
            path = os.path.join(self.kb_folder_path, "kb_warning.json")
            with open(path, "r", encoding="utf-8") as f:
                self.warning_kb = json.load(f)
        except Exception as e:
            print(f"Lỗi tải dữ liệu cảnh báo: {e}")

    def prepare_vectorizer(self):
        self.questions = [entry["question"] for entry in self.kb_data]
        self.vectorizer = TfidfVectorizer()
        self.question_vectors = self.vectorizer.fit_transform(self.questions)

    def find_best_match(self, user_question):
        user_vec = self.vectorizer.transform([user_question])
        similarities = cosine_similarity(user_vec, self.question_vectors)
        best_idx = similarities.argmax()
        best_score = similarities[0, best_idx]
        if best_score > 0.4:
            return self.kb_data[best_idx], best_score
        else:
            return None, best_score

    def find_treatment(self, disease_name):
        for entry in self.treatment_kb:
            if entry.get("disease", "").lower() == disease_name.lower():
                return entry
        return None

    def find_warning(self, disease_name):
        for entry in self.warning_kb:
            if entry.get("disease", "").lower() == disease_name.lower():
                return entry
        return None

    def build_symptoms_list(self):
        return [
            "sốt", "ho", "hắt hơi", "mệt mỏi", "mất vị giác", "ngứa mắt",
            "đau họng", "đau đầu", "khó thở", "đau ngực"
        ]

    def diagnose(self, user_symptoms):
        max_match = 0
        best_entry = None
        for entry in self.kb_data:
            question = entry.get("question", "").lower()
            count = sum(1 for symp in user_symptoms if symp in question)
            if count > max_match:
                max_match = count
                best_entry = entry
        return best_entry

    def get_full_diagnosis_info(self, diagnosis_entry):
        if not diagnosis_entry:
            return "Không tìm thấy kết quả chẩn đoán phù hợp."
        disease = diagnosis_entry.get("tags", ["Bệnh không xác định"])[0]
        answer = diagnosis_entry.get("answer", "")
        treatment = self.find_treatment(disease)
        warning = self.find_warning(disease)

        res = f"Dự đoán bệnh: {disease}\n{answer}\n"
        if treatment:
            res += f"\nLời khuyên điều trị: {treatment.get('treatment', '')}"
            meds = treatment.get("recommended_medications", [])
            if meds:
                res += "\nThuốc được khuyến nghị: " + ", ".join(meds)
        if warning:
            res += "\n\nCảnh báo: " + "; ".join(warning.get("warnings", []))
            advice = warning.get("advice", "")
            if advice:
                res += f"\nLời khuyên quan trọng: {advice}"
        return res
