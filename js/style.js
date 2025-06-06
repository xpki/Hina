const textarea = document.getElementById('input');
const sendButton = document.getElementById('send');
const chat = document.getElementById('chat');
const lineHeight = parseInt(window.getComputedStyle(textarea).lineHeight, 10);
const maxLines = 8;
const maxHeight = lineHeight * maxLines;

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
    textarea.style.height = 'auto';

    try {
    const response = await fetch('https://hinabackend.onrender.com/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
    });

    if (!response.ok) throw new Error('Network response was not ok');

    const data = await response.json();
    const reply = data?.choices?.[0]?.message?.content;

    if (reply) {
        addMessage(reply, 'ai');
    } else {
        addMessage("Sorry, no response from AI.", 'ai');
    }
    } catch (err) {
    console.error('Fetch error:', err);
    addMessage("Error contacting Gemini API.", 'ai');
    }
});

function addMessage(text, role) {
    const bubble = document.createElement('div');
    bubble.className = role === 'user' ? 'user-message' : 'ai-message';
    bubble.innerHTML = marked.parse(text);
    chat.appendChild(bubble);
    chat.scrollTop = chat.scrollHeight;
}


const sidebar = document.getElementById('sidebar');
const toggleBtn = document.getElementById('toggle-btn');

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