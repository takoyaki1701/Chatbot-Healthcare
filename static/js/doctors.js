$(document).ready(function () {
  let editingDoctorId = null;

  // Mở modal thêm bác sĩ
  $("#btnAddDoctor").click(function () {
    editingDoctorId = null;
    $("#doctorModalLabel").text("Thêm bác sĩ");
    $("#doctorForm")[0].reset();
    $("#doctorId").val("");
    $("#doctorForm").removeClass("was-validated");
    $("#doctorModal").modal("show");
  });

  // Mở modal sửa khi click vào tên bác sĩ
  $(document).on("click", ".doctor-name", function () {
    editingDoctorId = $(this).closest("tr").data("id");
    $("#doctorModalLabel").text("Chỉnh sửa bác sĩ");
    const row = $(this).closest("tr");
    $("#doctorId").val(editingDoctorId);
    $("#doctorName").val(row.find("td:eq(1)").text());
    $("#doctorSpecialty").val(row.find("td:eq(2)").text());
    $("#doctorPhone").val(row.find("td:eq(3)").text());
    $("#doctorEmail").val(row.find("td:eq(4)").text());
    $("#doctorPatients").val(row.find("td:eq(5)").text());
    $("#doctorForm").removeClass("was-validated");
    $("#doctorModal").modal("show");
  });

  // Xóa bác sĩ
  $(document).on("click", ".btnDelete", function () {
    if (!confirm("Bạn có chắc muốn xóa bác sĩ này không?")) return;
    const doctorId = $(this).closest("tr").data("id");
    $.ajax({
      url: `/api/doctors/${doctorId}`,
      type: "DELETE",
      success: function (res) {
        alert(res.message);
        if (res.success) location.reload();
      },
      error: function () {
        alert("Lỗi khi xóa bác sĩ");
      },
    });
  });

  // Xử lý submit form thêm/sửa bác sĩ
  $("#doctorForm").submit(function (e) {
    e.preventDefault();

    // Kiểm tra hợp lệ form Bootstrap
    if (!this.checkValidity()) {
      e.stopPropagation();
      $(this).addClass("was-validated");
      return;
    }

    const doctorData = {
      name: $("#doctorName").val().trim(),
      specialty: $("#doctorSpecialty").val().trim(),
      phone: $("#doctorPhone").val().trim(),
      email: $("#doctorEmail").val().trim(),
      patients: $("#doctorPatients").val()
        .split(",")
        .map((p) => p.trim())
        .filter((p) => p.length > 0),
    };

    const doctorId = $("#doctorId").val();
    let ajaxOptions = {
      url: "/api/doctors",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(doctorData),
      success: function (res) {
        alert(res.message);
        if (res.success) {
          $("#doctorModal").modal("hide");
          location.reload();
        }
      },
      error: function () {
        alert("Lỗi khi lưu bác sĩ");
      },
    };

    if (doctorId) {
      ajaxOptions.url = `/api/doctors/${doctorId}`;
      ajaxOptions.type = "PUT";
    }

    $.ajax(ajaxOptions);
  });
});
