// filepath: LegalLink/static/js/document-upload.js
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const uploadInput = document.getElementById('document-upload');
    const uploadButton = document.getElementById('upload-button');
    const responseContainer = document.getElementById('response-container');

    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const formData = new FormData();
        formData.append('pdf_file', uploadInput.files[0]);

        fetch('/upload-document/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken') // Get CSRF token for security
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                responseContainer.innerHTML = `<p class="error">${data.error}</p>`;
            } else {
                responseContainer.innerHTML = `<p>Document uploaded successfully!</p>`;
                // Optionally display analysis results or further instructions
            }
        })
        .catch(error => {
            responseContainer.innerHTML = `<p class="error">An error occurred: ${error.message}</p>`;
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Check if this cookie string begins with the desired name
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});