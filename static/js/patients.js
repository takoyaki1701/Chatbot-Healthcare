$(document).ready(function () {
  let editingPatientId = null;

  // Mở modal thêm bệnh nhân
  $("#btnAddPatient").click(function () {
    editingPatientId = null;
    $("#patientModalLabel").text("Thêm bệnh nhân");
    $("#patientForm")[0].reset();
    $("#patientId").val("");
    const modal = new bootstrap.Modal(document.getElementById('patientModal'));
    modal.show();
  });

  // Mở modal sửa khi click vào tên bệnh nhân hoặc nút Sửa
  $(document).on("click", ".patient-name, .btnEdit", function () {
    editingPatientId = $(this).closest("tr").data("id");
    $("#patientModalLabel").text("Chỉnh sửa bệnh nhân");
    const row = $(this).closest("tr");
    $("#patientId").val(editingPatientId);
    $("#patientName").val(row.find("td:eq(1)").text());
    $("#patientGender").val(row.find("td:eq(2)").text());
    $("#patientAddress").val(row.find("td:eq(3)").text());
    $("#patientEmail").val(row.find("td:eq(4)").text());
    $("#patientPhone").val(row.find("td:eq(5)").text());
    const modal = new bootstrap.Modal(document.getElementById('patientModal'));
    modal.show();
  });

  // Xóa bệnh nhân
  $(document).on("click", ".btnDelete", function () {
    if (!confirm("Bạn có chắc muốn xóa bệnh nhân này không?")) return;
    const patientId = $(this).closest("tr").data("id");
    $.ajax({
      url: `/api/patients/${patientId}`,
      type: "DELETE",
      success: function (res) {
        alert(res.message);
        if (res.success) location.reload();
      },
      error: function () {
        alert("Lỗi khi xóa bệnh nhân");
      },
    });
  });

  // Xử lý submit form thêm/sửa bệnh nhân
  $("#patientForm").submit(function (e) {
    e.preventDefault();

    const patientData = {
      name: $("#patientName").val(),
      gender: $("#patientGender").val(),
      address: $("#patientAddress").val(),
      email: $("#patientEmail").val(),
      phone: $("#patientPhone").val(),
    };

    const patientId = $("#patientId").val();
    let ajaxOptions = {
      url: "/api/patients",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(patientData),
      success: function (res) {
        alert(res.message);
        if (res.success) {
          const modal = bootstrap.Modal.getInstance(document.getElementById('patientModal'));
          modal.hide();
          location.reload();
        }
      },
      error: function () {
        alert("Lỗi khi lưu bệnh nhân");
      },
    };

    if (patientId) {
      ajaxOptions.url = `/api/patients/${patientId}`;
      ajaxOptions.type = "PUT";
    }

    $.ajax(ajaxOptions);
  });
});
