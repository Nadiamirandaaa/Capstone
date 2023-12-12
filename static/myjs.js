
function login() {
    $(document).ready(function () {
        $('#login-form').submit(function (event) {
            event.preventDefault();
            var nama = $('#inputName').val();
            var nik = $('#inputNIK').val();
    
            $.ajax({
                url: '/login',
                method: 'POST',
                data: {
                    nama: nama,
                    nik: nik
                },
                success: function (response) {
                    // Menyimpan token ke local storage atau session storage
                    localStorage.setItem('token', response.token);
                    // Redirect ke halaman lain atau lakukan aksi setelah login berhasil
                    window.location.href = '/akun'; // Ganti dengan halaman setelah login berhasil
                },
                error: function (xhr, status, error) {
                    var errorMessage = xhr.responseJSON.error;
                    $('#error-message').text(errorMessage);
                }
            });
        });
    });
}

function register() {
    $(document).ready(function() {
        $('#registrationForm').submit(function(event) {
            event.preventDefault();
            var formData = $(this).serialize();
            $.ajax({
                type: 'POST',
                url: '/register',
                data: formData,
                success: function(response) {
                    if (response.status === 'error') {
                        // Handle error message
                        alert('Error: ' + response.message);
                    } else if (response.status === 'success') {
                        // Handle success message
                        alert('Success: ' + response.message);
                        if (response.redirect_url) {
                            // Redirect to the provided URL
                            window.location.href = response.redirect_url;
                        }
                    }
                },
                error: function(xhr, status, error) {
                    // Handle errors with the request
                    alert('Request Error: ' + error);
                }
            });
        });
    });
    
}
