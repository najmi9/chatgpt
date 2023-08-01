const chatForm = document.getElementById('chat-form');
const chatContainer = document.querySelector('#chat-container');

chatForm.addEventListener('submit', function(event) {
    const submitButton = this.querySelector('button');
    submitButton.disabled = true;

    event.preventDefault();
    const messageInput = this.querySelector('input');
    const message = messageInput.value;
    messageInput.value = '';
    chatContainer.innerHTML += '<div class="chat-message"><div class="message-text user">' + message + '</div></div>';
    fetch('/chatbot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    }).then(r => r.json())
    .then((data) => {
        chatContainer.innerHTML += '<div class="chat-message bot-anwser"><div class="message-text bot">' + data.message + '</div></div>';
        chatContainer.scrollTop = chatContainer.scrollHeight;
        submitButton.disabled = false;
    }
    ).catch(function(error) {
        console.error(error);
        submitButton.disabled = false;
    });

});
