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
                        alert('User Login Berhasil');
                        document.cookie = "mytoken=" + response.token;
                        redirectToCorrectPage();
                    } else {
                        alert(response["msg"]);
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
                alert('User registration berhasil!');
                window.location.href = '/login';
            } else {
                alert(response['msg']);
            }
        }
    });
}
function daftar(){
    // let nama = $('#inputName').val();
    let tanggal = $('#inputDate').val();
    let sesi = $('#inputSession').val();
    let mcu = $('#inputMCU').val();

    $.ajax({
        url: '/pendaftaranonline',
        method: 'POST',
        data: {
            // nama: nama,
            tanggal: tanggal,
            sesi: sesi,
            mcu: mcu
        },
        success: function(response) {
            if (response["result"] === 'success') {
                alert('Pendaftaran berhasil! Nomor antrian Anda: ' + response.nomor_antrian);
                // Redirect ke halaman yang sesuai atau lakukan sesuatu setelah pendaftaran berhasil
                // window.location.href = '/halaman-sukses';
            } else {
                alert(response['msg']);
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
                alert('User Login Berhasil');
                document.cookie = "mytoken=" + response.token;
                redirectToCorrectPage();
            } else {
                alert(response["msg"]);
            }
        }
        
    });
}
