// Make sure this file is loaded after DOM is ready

window.addEventListener("DOMContentLoaded", () => {

    // Global audio object
    window.audio = new Audio("/static/sound/notifications.mp3");
    let soundAllowed = false;
    let pendingAudio = false; // Flag to play sound later if not allowed yet

    // Enable sound after first user click
    document.addEventListener("click", () => {
        soundAllowed = true;
        console.log("✅ Sound enabled!");
        // Play pending audio if there was a notification before click
        if (pendingAudio) {
            window.audio.play().catch(err => console.warn("Audio play error:", err));
            pendingAudio = false;
        }
    }, { once: true });

    // DOM elements
    const notifCount = document.getElementById("notif-count");
    const notifDropdown = document.getElementById("notif-dropdown");
    const notifIcon = document.getElementById("notification-icon");

    let unreadCount = 0;

    // WebSocket connection
    const socket = new WebSocket("ws://127.0.0.1:8000/ws/vendor/notifications/");

    socket.onopen = () => console.log("✅ Vendor WebSocket Connected");

    socket.onmessage = (event) => {
        let data;
        try {
            data = JSON.parse(event.data);
        } catch (e) {
            console.warn("Could not parse WebSocket message:", e);
            return;
        }
        if (!data.message) return;

        unreadCount++;
        notifCount.innerText = unreadCount;

        // Add notification to dropdown
        const item = document.createElement("div");
        item.style.padding = "6px 0";
        item.style.borderBottom = "1px solid #ddd";
        item.innerText = data.message;
        notifDropdown.prepend(item);

        // Flash bell
        notifIcon.style.animation = "flashBell 1s infinite";

        // Play sound if allowed, otherwise queue
        if (soundAllowed) {
            window.audio.currentTime = 0;
            window.audio.play().catch(err => console.error("Audio play error:", err));
        } else {
            pendingAudio = true;
        }
    };

    socket.onerror = (err) => console.error("WebSocket Error:", err);
    socket.onclose = () => console.warn("WebSocket disconnected");

    // Bell click: toggle dropdown & reset counter
    notifIcon.addEventListener("click", () => {
        notifDropdown.style.display =
            notifDropdown.style.display === "block" ? "none" : "block";
        notifIcon.style.animation = "none";
        unreadCount = 0;
        notifCount.innerText = "0";

        // Play sound immediately on click if sound is enabled
        if (soundAllowed && window.audio) {
            window.audio.currentTime = 0;
            window.audio.play().catch(err => console.log(err));
        }
    });
});
