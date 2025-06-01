const chatButton = document.getElementById("chat-button");
const chatPopup = document.getElementById("chat-popup");
const chatMessages = document.getElementById("chat-messages");
const chatInput = document.getElementById("chat-input");
const chatSendBtn = document.getElementById("chat-send-btn");
const modeSelect = document.getElementById("mode-select");
const ttsToggle = document.getElementById("tts-toggle");

// Thêm lựa chọn chế độ
function populateModeOptions() {
  const options = [
    {value: "lookup", text: "Tra cứu thông tin"},
    {value: "diagnosis", text: "Chẩn đoán triệu chứng"}
  ];
  for(let opt of options){
    let el = document.createElement("option");
    el.value = opt.value;
    el.textContent = opt.text;
    modeSelect.appendChild(el);
  }
}
populateModeOptions();

chatButton.onclick = () => {
  if (chatPopup.style.display === "flex") chatPopup.style.display = "none";
  else {
    chatPopup.style.display = "flex";
    if (!chatMessages.innerHTML) {
      chatMessages.innerHTML += `<div class="bot-msg message">Chào bạn! Tôi là trợ lý sức khỏe ảo. Bạn có thể chọn chế độ và bắt đầu nhập.</div>`;
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  }
};

async function sendMessage() {
  let msg = chatInput.value.trim();
  if (!msg) return;

  const mode = modeSelect.value;

  chatMessages.innerHTML += `<div class="user-msg message">${msg}</div>`;
  chatInput.value = "";
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    const res = await fetch("/api/chatbot", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message: msg, mode: mode})
    });
    const data = await res.json();

    chatMessages.innerHTML += `<div class="bot-msg message">${data.reply}</div>`;
    chatMessages.scrollTop = chatMessages.scrollHeight;

    if (ttsToggle.checked && 'speechSynthesis' in window) {
      let utterance = new SpeechSynthesisUtterance(data.reply);
      utterance.lang = 'vi-VN';
      window.speechSynthesis.speak(utterance);
    }

    if(mode === "diagnosis"){
      if(data.reply.toLowerCase().includes("kết quả") || data.reply.toLowerCase().includes("dự đoán bệnh")){
        modeSelect.value = "lookup";
        chatMessages.innerHTML += `<div class="bot-msg message"><i>Chẩn đoán hoàn thành. Bạn có thể chọn lại chế độ.</i></div>`;
      }
    }

  } catch (err) {
    chatMessages.innerHTML += `<div class="bot-msg message">Lỗi kết nối máy chủ.</div>`;
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
}

chatSendBtn.onclick = sendMessage;
chatInput.addEventListener("keypress", e => {
  if (e.key === "Enter") sendMessage();
});
