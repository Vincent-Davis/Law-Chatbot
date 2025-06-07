// filepath: LegalLink/static/js/chat.js

document.addEventListener("DOMContentLoaded", function() {
    const chatForm = document.querySelector("form");
    const questionInput = document.getElementById("question");
    const chatBox = document.querySelector(".chat-box");

    chatForm.addEventListener("submit", function(event) {
        event.preventDefault();
        const userMessage = questionInput.value.trim();

        if (userMessage) {
            appendMessage("Anda: " + userMessage, "user");
            questionInput.value = "";

            fetch(chatForm.action, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({ question: userMessage })
            })
            .then(response => response.json())
            .then(data => {
                if (data.answer) {
                    appendMessage("AI: " + data.answer, "ai");
                } else if (data.error) {
                    appendMessage("Error: " + data.error, "ai");
                }
            })
            .catch(error => {
                appendMessage("Error: " + error.message, "ai");
            });
        }
    });

    function appendMessage(message, role) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", role);
        messageDiv.innerHTML = `<strong>${role === "user" ? "Anda:" : "AI:"}</strong> <p>${message}</p>`;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});