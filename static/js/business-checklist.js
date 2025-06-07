// filepath: LegalLink/static/js/business-checklist.js

document.addEventListener('DOMContentLoaded', function() {
    const checklistForm = document.getElementById('checklist-form');
    const checklistOutput = document.getElementById('checklist-output');

    checklistForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const businessInfo = {
            name: document.getElementById('business-name').value,
            description: document.getElementById('business-description').value,
            targetMarket: document.getElementById('target-market').value,
            businessModel: document.getElementById('business-model').value,
            location: document.getElementById('business-location').value,
            businessType: document.getElementById('business-type').value,
            fundingNeeds: document.getElementById('funding-needs').value,
            team: document.getElementById('team').value.split(','),
            productType: document.getElementById('product-type').value,
            marketingPlan: document.getElementById('marketing-plan').value
        };

        fetch('/generate-business-checklist/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ business_info: businessInfo })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                checklistOutput.innerHTML = `<p class="error">${data.error}</p>`;
            } else {
                displayChecklist(data.checklist);
            }
        })
        .catch(error => {
            checklistOutput.innerHTML = `<p class="error">Terjadi kesalahan: ${error.message}</p>`;
        });
    });

    function displayChecklist(checklist) {
        checklistOutput.innerHTML = '<h3>Checklist Bisnis Anda:</h3><ul>';
        checklist.forEach(item => {
            checklistOutput.innerHTML += `<li>${item}</li>`;
        });
        checklistOutput.innerHTML += '</ul>';
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});