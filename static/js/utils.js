// filepath: LegalLink/static/js/utils.js
function showError(message) {
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
        errorContainer.innerText = message;
        errorContainer.style.display = 'block';
    }
}

function hideError() {
    const errorContainer = document.getElementById('error-container');
    if (errorContainer) {
        errorContainer.style.display = 'none';
    }
}

function clearInputField(inputFieldId) {
    const inputField = document.getElementById(inputFieldId);
    if (inputField) {
        inputField.value = '';
    }
}

function toggleLoadingIndicator(isLoading) {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = isLoading ? 'block' : 'none';
    }
}

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}