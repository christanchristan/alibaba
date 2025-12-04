// Vendor WebSocket
const socket = new WebSocket('ws://127.0.0.1:8000/ws/vendor/notifications/');

socket.onopen = () => {
    console.log("Connected to WebSocket");
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Message received:", data.message); // <- vendor message
};

socket.onclose = () => console.log("Disconnected from WebSocket");
socket.onerror = (err) => console.error("WebSocket error:", err);
