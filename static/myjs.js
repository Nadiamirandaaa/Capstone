function redirectToCorrectPage() {
    if (document.referrer.includes("/login")) {
        window.location.href = "/akun";
    } else {
        window.location.href = "/pendaftaranonline";
    }
}

function login() {
            let nama = $('#inputName').val();
            let nik = $('#inputNIK').val();
    
            $.ajax({
                url: '/login',
                method: 'POST',
                data: {
                    nama: nama,
                    nik: nik
                },
                success: function(response) {
                    if (response.result === "success") {
                        Swal.fire({
                            title: "Berhasil melakukan login!",
                            text: response.message,
                            icon: "success"
                          }).then((result) => {
                            redirectToCorrectPage();
                        });
                        document.cookie = "mytoken=" + response.token;
                    } else {
                        Swal.fire({
                            title: "Gagal melakukan login!",
                            text: response.message,
                            icon: "error"
                          });
                    }
                },
                error : function(response){
                    if (response['result'] === 'error') {
                        Swal.fire({
                            title: "Gagal melakukan login!",
                            text: response.message,
                            icon: "error"
                          }).then((result) => {
                                location.reload();
                        });
                }
            }
                
            });
}

function register() {
    let nama = $('#inputName').val();
    let nik = $('#inputNIK').val();
    let gender = $('#inputGender').val();
    let alamat = $('#inputAddress').val();


    $.ajax({
        type: 'POST',
        url: '/register',
        data: {
            nama: nama,
            nik: nik,
            gender: gender,
            alamat: alamat
        },
        success: function (response) {
            if (response['result'] === 'success') {
                Swal.fire({
                    title: "Berhasil melakukan registrasi!",
                    text: response.message,
                    icon: "success"
                  }).then((result) => {
                        window.location.href = '/login';
                });
                // window.location.href = '/login';
            } else {
                Swal.fire({
                    title: "Gagal melakukan registrasi!",
                    text: response.message,
                    icon: "error"
                  }).then((result) => {
                    location.reload();
            });
            }
        },
        error : function(response){
            if (response['result'] === 'error') {
                Swal.fire({
                    title: "Gagal melakukan registrasi!",
                    text: response.message,
                    icon: "error"
                  }).then((result) => {
                        location.reload();
                });
        }
    }
    });
}
function daftar(){
    // let nama = $('#inputName').val();
    let tanggal = $('#inputDate').val();
    let sesi = $('#inputSession').val();
    let mcu = $('#inputMCU').val();
    let nama = $('#inputNama').val();

    
    $.ajax({
        url: '/pendaftaranonline',
        method: 'POST',
        data: {
            // nama: nama,
            tanggal: tanggal,
            sesi: sesi,
            mcu: mcu,
            nama: nama
        },
        success: function(response) {
            if (response["result"] === 'success') {
                $('#nomorAntrian').text(response.nomor_antrian);
                $('#tanggal').text(response.tanggal);
                $('#hari').text(response.hari);
                $('#sesi').text(response.sesi);
                $('#jam').text(response.jam);
                $('#resultModal').modal('show');
            } else {
                Swal.fire({
                    title: "Gagal melakukan pendaftaran!",
                    text: response.message,
                    icon: "error"
                  }).then((result) => {
                    location.reload();
            });
            }
        },
        error : function(response){
            if (response['result'] === 'error') {
                Swal.fire({
                    title: "Gagal melakukan pendaftaran!",
                    text: response.message,
                    icon: "error"
                  }).then((result) => {
                        location.reload();
                });
        }
    }
    });
}

function logAdmin() {
    let nama = $('#inputName').val();
    let pass = $('#inputPass').val();

    $.ajax({
        url: '/admin/login',
        method: 'POST',
        data: {
            nama: nama,
            pass: pass
        },
        success: function(response) {
            if (response.result === "success") {
                alert('Admin Login Berhasil');
                document.cookie = "mytoken=" + response.token;
                window.location.href = "/admin";
            } else {
                alert(response["msg"]);
            }
        }
        
    });
}

$(document).ready(function(){
    // Menampilkan modal alur pendaftaran pasien ketika gambar di klik
    $('[data-target="#modalPendaftaran"]').click(function(){
        $('#modalPendaftaran').modal('show');
    });

    // Menampilkan modal alur cek hasil pemeriksaan ketika gambar di klik
    $('[data-target="#modalPemeriksaan"]').click(function(){
        $('#modalPemeriksaan').modal('show');
    });
});

function refreshPage() {
    location.reload();
}

function sign_out() {
    $.removeCookie("mytoken", { path: "/" });
    alert("Signed out!");
    window.location.href = "/";
  }

function signout() {
    $.removeCookie("mytoken", { path: "/" });
    alert("Signed out!");
    window.location.href = "/admin";
  }


function deleteuser() {
    

    $.ajax({
        url: '/delete_user/' + id,
        method: 'POST',
        success: function(response) {
            if (response.result === "success") {
                Swal.fire({
                    title: "Are you sure?",
                    text: "You won't be able to revert this!",
                    icon: "warning",
                    showCancelButton: true,
                    confirmButtonColor: "#3085d6",
                    cancelButtonColor: "#d33",
                    confirmButtonText: "Yes, delete it!"
                  }).then((result) => {
                    if (result.isConfirmed) {
                      Swal.fire({
                        title: "Deleted!",
                        text: "Your file has been deleted.",
                        icon: "success"
                      });
                    }
                  });
            } else {
                alert(response.message);
            }
        }
        
    });
}