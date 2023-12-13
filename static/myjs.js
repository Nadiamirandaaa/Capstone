
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
                        document.cookie = "mytoken=" + response.token + "; path=/pendaftaranonline";
                        window.location.replace("/pendaftaranonline");
                    } else {
                        alert(response["msg"]);
                    }
                }
                
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
