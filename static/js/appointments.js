$(document).ready(function () {
  const appointmentModal = new bootstrap.Modal(document.getElementById('appointmentModal'));

  // Hiển thị modal Thêm
  $('#btnAddAppointment').click(() => {
    clearAppointmentForm();
    $('#appointmentModalLabel').text('Thêm lịch hẹn');
    appointmentModal.show();
  });

  // Load dữ liệu lịch hẹn ra bảng
  function loadAppointments() {
    $.get('/api/appointments', (data) => {
      const tbody = $('#appointmentTableBody');
      tbody.empty();
      data.forEach(a => {
        tbody.append(`
          <tr data-id="${a.id}">
            <td>${a.id}</td>
            <td>${a.patient}</td>
            <td>${a.doctor}</td>
            <td>${a.date}</td>
            <td>${a.symptoms}</td>
            <td>${a.status}</td>
            <td>${a.notes}</td>
            <td>
              <button class="btn btn-sm btn-warning btnEdit me-1" title="Sửa lịch hẹn"><i class="fas fa-edit"></i></button>
              <button class="btn btn-sm btn-danger btnDelete" title="Xóa lịch hẹn"><i class="fas fa-trash-alt"></i></button>
            </td>
          </tr>
        `);
      });
    });
  }

  loadAppointments();

  // Clear form
  function clearAppointmentForm() {
    $('#appointmentId').val('');
    $('#appointmentPatient').val('');
    $('#appointmentDoctor').val('');
    $('#appointmentDate').val('');
    $('#appointmentSymptoms').val('');
    $('#appointmentStatus').val('Đang chờ');
    $('#appointmentNotes').val('');
    $('#appointmentForm')[0].classList.remove('was-validated');
  }

  // Submit form
  $('#appointmentForm').submit(function (e) {
    e.preventDefault();
    const form = this;
    if (!form.checkValidity()) {
      form.classList.add('was-validated');
      return;
    }
    const id = $('#appointmentId').val();
    const payload = {
      patient: $('#appointmentPatient').val(),
      doctor: $('#appointmentDoctor').val(),
      date: $('#appointmentDate').val(),
      symptoms: $('#appointmentSymptoms').val(),
      status: $('#appointmentStatus').val(),
      notes: $('#appointmentNotes').val()
    };
    if (id) {
      // Update
      $.ajax({
        url: `/api/appointments/${id}`,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(payload),
        success: () => {
          appointmentModal.hide();
          loadAppointments();
        }
      });
    } else {
      // Add new
      $.ajax({
        url: '/api/appointments',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(payload),
        success: () => {
          appointmentModal.hide();
          loadAppointments();
        }
      });
    }
  });

  // Edit button click
  $('#appointmentTableBody').on('click', '.btnEdit', function () {
    const tr = $(this).closest('tr');
    const id = tr.data('id');
    $.get('/api/appointments', (data) => {
      const appt = data.find(a => a.id === id);
      if (appt) {
        $('#appointmentId').val(appt.id);
        $('#appointmentPatient').val(appt.patient);
        $('#appointmentDoctor').val(appt.doctor);
        $('#appointmentDate').val(appt.date);
        $('#appointmentSymptoms').val(appt.symptoms);
        $('#appointmentStatus').val(appt.status);
        $('#appointmentNotes').val(appt.notes);
        $('#appointmentModalLabel').text('Chỉnh sửa lịch hẹn');
        appointmentModal.show();
      }
    });
  });

  // Delete button click
  $('#appointmentTableBody').on('click', '.btnDelete', function () {
    if (!confirm('Bạn có chắc muốn xóa lịch hẹn này?')) return;
    const tr = $(this).closest('tr');
    const id = tr.data('id');
    $.ajax({
      url: `/api/appointments/${id}`,
      method: 'DELETE',
      success: () => {
        loadAppointments();
      }
    });
  });

  // --- Chatbot Đặt lịch ---
  const chatButton = $('#appointment-chat-button');
  const chatPopup = $('#appointment-chat-popup');
  const chatMessages = $('#appointment-chat-messages');
  const chatInput = $('#appointment-chat-input');
  const chatSendBtn = $('#appointment-chat-send-btn');
  const ttsToggle = $('#appointment-tts-toggle');

  function scrollToBottom() {
    chatMessages.scrollTop(chatMessages[0].scrollHeight);
  }

  chatButton.click(() => {
    chatPopup.toggle();
    if (chatPopup.is(':visible') && chatMessages.children().length === 0) {
      chatMessages.append('<div class="app-bot-msg app-message">Xin chào! Tôi là trợ lý đặt lịch khám bệnh. Vui lòng nhập thông tin để bắt đầu.</div>');
      scrollToBottom();
    }
  });

  async function sendMessage() {
    const msg = chatInput.val().trim();
    if (!msg) return;

    chatMessages.append(`<div class="app-user-msg app-message">${msg}</div>`);
    chatInput.val('');
    scrollToBottom();

    try {
      const res = await fetch('/api/chatbot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, mode: 'appointment' }),
      });
      const data = await res.json();

      chatMessages.append(`<div class="app-bot-msg app-message">${data.reply}</div>`);
      scrollToBottom();

      if (ttsToggle.prop('checked') && 'speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(data.reply);
        utterance.lang = 'vi-VN';
        window.speechSynthesis.speak(utterance);
      }
    } catch (error) {
      chatMessages.append(`<div class="app-bot-msg app-message">Lỗi kết nối máy chủ.</div>`);
      scrollToBottom();
    }
  }

  chatSendBtn.click(sendMessage);
  chatInput.keypress((e) => {
    if (e.key === 'Enter') sendMessage();
  });
});
