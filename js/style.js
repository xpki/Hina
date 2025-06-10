const textarea = document.getElementById('input');
const sendButton = document.getElementById('send');
const resetButton = document.getElementById('reset');
const chat = document.getElementById('chat');
const lineHeight = parseInt(window.getComputedStyle(textarea).lineHeight, 10);
const sidebar = document.getElementById('sidebar');
const toggleBtn = document.getElementById('toggle-btn');
const maxLines = 8;
const maxHeight = lineHeight * maxLines;
const clientId = localStorage.getItem('hina_client_id') || crypto.randomUUID();
localStorage.setItem('hina_client_id', clientId);

textarea.addEventListener('input', () => {
    textarea.style.height = 'auto';
    textarea.style.overflowY = 'hidden';

    const newHeight = textarea.scrollHeight;
    if (newHeight <= maxHeight) {
    textarea.style.height = newHeight + 'px';
    } else {
    textarea.style.height = maxHeight + 'px';
    textarea.style.overflowY = 'auto';
    }
});

textarea.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendButton.click();
    }
});

sendButton.addEventListener('click', async () => {
    const message = textarea.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    textarea.value = '';
    
    try {
        const response = await fetch('https://hinabackend.onrender.com/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Client-ID': clientId  // Send client ID
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        addMessage(data.choices[0].message.content, 'ai');
        
    } catch (err) {
        console.error('Error:', err);
        addMessage("Hina-sama is unavailable...", 'ai');
    }
});

function addMessage(text, role) {
    const bubble = document.createElement('div');
    bubble.className = role === 'user' ? 'user-message' : 'ai-message';
    bubble.innerHTML = marked.parse(text);
    chat.appendChild(bubble);
    chat.scrollTop = chat.scrollHeight;
}

function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (sidebar) {
    sidebar.classList.toggle('close');
    // Save state to localStorage
    localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('close'));
  }
}

document.addEventListener('DOMContentLoaded', function() {
  const sidebar = document.getElementById('sidebar');
  if (sidebar && localStorage.getItem('sidebarCollapsed') === 'true') {
    sidebar.classList.add('close');
  }
});

window.addEventListener('load', function() {
  document.body.classList.remove('preload');
});

resetButton.addEventListener('click', async () => {
    try {
        await fetch('https://hinabackend.onrender.com/api/reset', {
            method: 'POST',
            headers: { 'X-Client-ID': clientId }
        });
        chat.innerHTML = '';
    } catch (err) {
        console.error('Error resetting chat:', err);
        addMessage("Failed to reset conversation", 'ai');
    }
});

