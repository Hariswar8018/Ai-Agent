/**
 * LifeSync — Chat Frontend Logic
 * Handles sending messages to the Flask /chat endpoint,
 * rendering responses, and managing the chat UI state.
 */

(function () {
    "use strict";

    // --- DOM Elements ---
    const chatArea = document.getElementById("chat-area");
    const messagesContainer = document.getElementById("messages-container");
    const messageInput = document.getElementById("message-input");
    const sendBtn = document.getElementById("send-btn");
    const typingIndicator = document.getElementById("typing-indicator");
    const welcomeCard = document.getElementById("welcome-card");

    // --- State ---
    // Unique client ID so the server can maintain session per browser tab
    const clientId = "client_" + Math.random().toString(36).substring(2, 10);
    let isSending = false;

    // --- Initialization ---
    function init() {
        sendBtn.addEventListener("click", handleSend);
        messageInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
            }
        });

        // Capability chip quick-actions
        document.querySelectorAll(".capability-chip").forEach(function (chip) {
            chip.addEventListener("click", function () {
                messageInput.value = chip.dataset.message;
                handleSend();
            });
        });

        messageInput.focus();
    }

    // --- Send Message ---
    async function handleSend() {
        const text = messageInput.value.trim();
        if (!text || isSending) return;

        // Hide welcome card on first message
        if (welcomeCard) {
            welcomeCard.style.display = "none";
        }

        // Add user message to chat
        appendMessage("user", text);
        messageInput.value = "";
        isSending = true;
        sendBtn.disabled = true;

        // Show typing indicator
        showTyping(true);
        scrollToBottom();

        try {
            const res = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text, client_id: clientId }),
            });

            const data = await res.json();

            showTyping(false);

            if (res.ok && data.reply) {
                appendMessage("agent", data.reply);
            } else {
                appendMessage("error", data.error || "Something went wrong.");
            }
        } catch (err) {
            showTyping(false);
            appendMessage("error", "Could not connect to the server. Please try again.");
        } finally {
            isSending = false;
            sendBtn.disabled = false;
            messageInput.focus();
            scrollToBottom();
        }
    }

    // --- Render Message Bubble ---
    function appendMessage(type, text) {
        var div = document.createElement("div");
        div.className = "message " + type;

        var avatar = document.createElement("div");
        avatar.className = "message-avatar";
        avatar.textContent = type === "user" ? "👤" : type === "agent" ? "✨" : "⚠️";

        var bubble = document.createElement("div");
        bubble.className = "message-bubble";
        bubble.innerHTML = formatMessage(text);

        div.appendChild(avatar);
        div.appendChild(bubble);
        messagesContainer.appendChild(div);
        scrollToBottom();
    }

    // --- Simple Markdown Formatter ---
    function formatMessage(text) {
        // Escape HTML first
        var s = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        // Bold: **text**
        s = s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
        // Italic: *text*
        s = s.replace(/\*(.+?)\*/g, "<em>$1</em>");
        // Inline code: `code`
        s = s.replace(/`(.+?)`/g, "<code>$1</code>");
        // Unordered list items: - item  or * item
        s = s.replace(/^[\-\*]\s+(.+)$/gm, "<li>$1</li>");
        // Wrap consecutive <li> in <ul>
        s = s.replace(/((?:<li>.*<\/li>\n?)+)/g, "<ul>$1</ul>");
        // Line breaks → paragraphs
        s = s
            .split(/\n\n+/)
            .map(function (p) { return "<p>" + p.replace(/\n/g, "<br>") + "</p>"; })
            .join("");

        return s;
    }

    // --- Typing Indicator ---
    function showTyping(visible) {
        if (visible) {
            typingIndicator.classList.add("visible");
        } else {
            typingIndicator.classList.remove("visible");
        }
    }

    // --- Auto-scroll ---
    function scrollToBottom() {
        requestAnimationFrame(function () {
            chatArea.scrollTop = chatArea.scrollHeight;
        });
    }

    // --- Boot ---
    init();
})();
