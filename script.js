/**
 * Council of Philosophers - Frontend Logic (Python Backend + Multi-session)
 */

const API_URL = 'http://localhost:5000';

const PHILOSOPHERS = [
    { id: 'socrates', name: 'Socrates', initials: 'SO' },
    { id: 'kafka', name: 'Franz Kafka', initials: 'FK' },
    { id: 'dostoevsky', name: 'Fyodor Dostoevsky', initials: 'FD' },
    { id: 'nietzsche', name: 'Friedrich Nietzsche', initials: 'FN' },
    { id: 'chekhov', name: 'Anton Chekhov', initials: 'AC' }
];

class Council {
    constructor() {
        this.members = new Map();
        this.chatHistory = document.getElementById('chat-history');
        this.container = document.getElementById('council-members');
        this.currentSessionId = null;
    }

    init() {
        this.renderTable();
        this.loadSessions();

        // Event Listeners
        document.getElementById('new-chat-btn').addEventListener('click', () => this.createNewSession());
        /* Settings button removed by user request
        document.getElementById('settings-btn').addEventListener('click', () => this.openSettings());
        document.getElementById('close-settings-btn').addEventListener('click', () => {
            document.getElementById('settings-modal').classList.add('hidden');
        }); 
        */
    }

    renderTable() {
        const radius = 300;
        const total = PHILOSOPHERS.length;
        const angleStep = (2 * Math.PI) / total;

        PHILOSOPHERS.forEach((data, index) => {
            const div = document.createElement('div');
            div.className = 'member-card';
            div.id = `member-${data.id}`;
            const angle = index * angleStep - Math.PI / 2;
            const x = Math.cos(angle) * radius;
            const y = Math.sin(angle) * radius;
            div.style.left = `calc(50% + ${x}px - 70px)`;
            div.style.top = `calc(50% + ${y}px - 90px)`;

            div.innerHTML = `
                <div class="avatar">${data.initials}</div>
                <div class="name">${data.name}</div>
                <div class="status">Listening...</div>
            `;
            this.container.appendChild(div);
            this.members.set(data.name, div);
        });
    }

    // --- Settings / Models ---

    async openSettings() {
        const modal = document.getElementById('settings-modal');
        const list = document.getElementById('model-config-list');
        list.innerHTML = 'Loading...';
        modal.classList.remove('hidden');

        try {
            const res = await fetch(`${API_URL}/philosophers`);
            const data = await res.json(); // returns dict { id: {name, model, prompt} }

            list.innerHTML = '';

            for (const [pid, pdata] of Object.entries(data)) {
                const row = document.createElement('div');
                row.className = 'config-row';

                row.innerHTML = `
                    <span class="config-name">${pdata.name}</span>
                    <input type="text" class="config-model" value="${pdata.model || 'llama3.2:latest'}" placeholder="Model (e.g. mistral)">
                    <button class="config-save" data-pid="${pid}">Save</button>
                `;
                list.appendChild(row);

                // Add save listener
                row.querySelector('.config-save').addEventListener('click', async (e) => {
                    const btn = e.target;
                    const input = row.querySelector('.config-model');
                    const newModel = input.value;

                    btn.textContent = 'Saving...';
                    await this.updateModel(pid, newModel);
                    btn.textContent = 'Saved';
                    setTimeout(() => btn.textContent = 'Save', 2000);
                });
            }

        } catch (e) {
            console.error(e);
            list.textContent = "Error loading settings.";
        }
    }

    async updateModel(pid, modelName) {
        try {
            await fetch(`${API_URL}/philosophers/${pid}/model`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model: modelName })
            });
        } catch (e) {
            console.error(e);
        }
    }


    // --- Session Management ---

    async loadSessions() {
        try {
            const res = await fetch(`${API_URL}/sessions`);
            const sessions = await res.json();

            const listEl = document.getElementById('session-list');
            listEl.innerHTML = ''; // Clear current

            if (sessions.length === 0) {
                this.createNewSession();
            } else {
                sessions.forEach(s => {
                    const el = document.createElement('div');
                    el.className = 'session-item';
                    el.textContent = s.title;
                    el.onclick = () => this.switchSession(s.id);
                    if (s.id === this.currentSessionId) el.classList.add('active');
                    listEl.appendChild(el);
                });

                // If no current session, pick the first one
                if (!this.currentSessionId && sessions.length > 0) {
                    this.switchSession(sessions[0].id);
                }
            }
        } catch (e) {
            console.error("Failed to load sessions", e);
        }
    }

    async createNewSession() {
        try {
            const res = await fetch(`${API_URL}/sessions`, { method: 'POST' });
            const data = await res.json();
            await this.loadSessions(); // Reload list
            this.switchSession(data.id);
        } catch (e) {
            console.error("Error creating session", e);
        }
    }

    async switchSession(sid) {
        this.currentSessionId = sid;

        // Highlight active sidebar item
        document.querySelectorAll('.session-item').forEach(el => el.classList.remove('active'));
        // (Re-render list to easily apply active class, or simpler: just find by text/id if stored)
        // For simplicity, just reloading sessions list usually works or manual DOM update
        await this.loadSessions();

        // Load History
        this.chatHistory.innerHTML = ''; // Clear chat view
        try {
            const res = await fetch(`${API_URL}/sessions/${sid}`);
            const data = await res.json();

            if (data.history.length === 0) {
                this.addSystemMessage("New Session Established.");
            } else {
                data.history.forEach(msg => {
                    this.addMessage(msg.speaker, msg.text, msg.speaker === 'Chairman');
                });
                this.addSystemMessage("History loaded.");
            }

        } catch (e) {
            console.error(e);
        }
    }


    // --- Chat Logic ---

    addSystemMessage(text) {
        const div = document.createElement('div');
        div.className = 'message system';
        div.textContent = text;
        this.chatHistory.appendChild(div);
        this.scrollToBottom();
    }

    addMessage(speaker, text, isUser = false) {
        const div = document.createElement('div');
        div.className = `message ${isUser ? 'user' : ''}`;
        div.innerHTML = `
            <span class="speaker">${speaker}</span>
            <span class="text">${text}</span>
        `;
        this.chatHistory.appendChild(div);
        this.scrollToBottom();
    }

    scrollToBottom() {
        this.chatHistory.scrollTop = this.chatHistory.scrollHeight;
    }

    setMemberStatus(name, status) {
        const member = this.members.get(name);
        if (member) {
            member.querySelector('.status').textContent = status;
            if (status === 'Speaking...') member.classList.add('active');
            else member.classList.remove('active');
        }
    }

    async sendToBackend(input = null) {
        if (!this.currentSessionId) return;

        try {
            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    input: input,
                    session_id: this.currentSessionId
                })
            });

            if (!response.ok) throw new Error("Backend Error");

            const data = await response.json();

            if (data.status === 'received') {
                if (input) this.loadSessions();
                return true;
            }

            this.setMemberStatus(data.speaker, "Speaking...");
            this.addMessage(data.speaker, data.text);

            setTimeout(() => {
                this.setMemberStatus(data.speaker, "Listening...");
            }, 2000);

            // Reload sessions list to update title if changed
            if (input) this.loadSessions();

            return true;
        } catch (e) {
            console.error(e);
            this.addSystemMessage("Error connecting to Council Server.");
            return false;
        }
    }
}

// App Logic
const council = new Council();
council.init();

const input = document.getElementById('chairman-input');
const sendBtn = document.getElementById('send-btn');

async function handleInput() {
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    council.addMessage('Chairman', text, true);

    // 1. Send user input
    await council.sendToBackend(text);

    // 2. Debate flow - Chain multiple responses sequentially
    const turns = 5; // Let all 5 philosophers speak

    for (let i = 0; i < turns; i++) {
        // Wait for the previous turn to complete before starting the next
        const success = await council.sendToBackend(null);
        if (!success) break; // Stop if error

        // Brief pause between turns for readability
        await new Promise(r => setTimeout(r, 2000));
    }
}

sendBtn.addEventListener('click', handleInput);
input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleInput();
});
