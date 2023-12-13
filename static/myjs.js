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
