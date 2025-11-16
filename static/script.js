// Conteneurs principaux
const chatContainer = document.querySelector(".chat-container");
const chatBox = document.getElementById("chat-box"); // Zone de messages
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

// Fonction pour créer un message
const createChatBubble = (text, type = "outgoing") => {
    const chatDiv = document.createElement("div");
    chatDiv.classList.add("chat", type);

    const chatContent = document.createElement("div");
    chatContent.classList.add("chat-content");

    const img = document.createElement("img");
    img.src = type === "outgoing" ? "/static/profil.jpg" : "/static/bot.jpg";
    img.alt = type === "outgoing" ? "User Image" : "AI Image";

    const chatDetails = document.createElement("div");
    chatDetails.classList.add("chat-details");
    chatDetails.textContent = text;

    chatContent.appendChild(img);
    chatContent.appendChild(chatDetails);
    chatDiv.appendChild(chatContent);
    return chatDiv;
};

// Fonction pour envoyer un message
const handleOutgoingChat = () => {
    const userText = userInput.value.trim();
    if (!userText) return; // Ignore si aucun texte saisi

    const outgoingChat = createChatBubble(userText, "outgoing");
    chatBox.appendChild(outgoingChat);
    scrollToBottom();

    userInput.value = ""; // Vide le champ d'entrée

    // Placeholder pour la réponse du bot
    const incomingChatDiv = createChatBubble("...", "incoming");
    chatBox.appendChild(incomingChatDiv);
    scrollToBottom();

    // Récupération de la réponse du bot
    getChatResponse(incomingChatDiv, userText);
};

// Défilement automatique vers le bas
const scrollToBottom = () => {
    chatBox.scrollTop = chatBox.scrollHeight;
};

// Fonction pour récupérer la réponse du bot
const getChatResponse = async (incomingChatDiv, userText) => {
    const API_URL = "http://127.0.0.1:8005/search_and_reformulate";

    try {
        const formData = new FormData();
        formData.append("query", userText);

        const response = await fetch(API_URL, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            incomingChatDiv.querySelector(".chat-details").textContent =
                "Sorry, I couldn't process your request.";
            return;
        }

        const data = await response.json();
        if (data && data.response) {
            incomingChatDiv.querySelector(".chat-details").textContent = data.response;
        } else {
            incomingChatDiv.querySelector(".chat-details").textContent =
                "Sorry, I couldn't understand.";
        }
    } catch (error) {
        incomingChatDiv.querySelector(".chat-details").textContent =
            "An error occurred. Please try again.";
    }

    scrollToBottom();
};

// Gestion des événements
sendBtn.addEventListener("click", handleOutgoingChat);
userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleOutgoingChat();
    }
});
