"use client";
import React, { useState, useEffect, useRef } from "react";

export default function ChatPage() {
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState("");
  const socket = useRef<WebSocket | null>(null);

  useEffect(() => {
    socket.current = new WebSocket("ws://127.0.0.1:8000/ws/chat/lobby/"); // Replace with your server
    const ws = socket.current

    ws.onopen = () => console.log("ws opened");
    ws.onclose = () => console.log("ws closed");

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setMessages((prevMessages) => [...prevMessages, `AI: ${data.message}`]);
    };
     return () => {
        if (ws) {
          ws.close()
          console.log("ws closed")
        }
      }
  }, []);

  const sendMessage = () => {
    if (input && socket.current) {
      socket.current.send(JSON.stringify({ message: input }));
      setMessages((prevMessages) => [...prevMessages, `You: ${input}`]);
      setInput("");
    }
  };
  return (
    <div className="flex flex-col h-screen p-4">
      <div className="flex-1 overflow-y-auto">
        {messages.map((msg, index) => (
          <div key={index} className="mb-2 p-2 rounded-md bg-gray-100">
            {msg}
          </div>
        ))}
      </div>
      <div className="flex mt-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 p-2 border rounded-l-md"
        />
        <button onClick={sendMessage} className="p-2 bg-blue-500 text-white rounded-r-md">Send</button>
      </div>
    </div>
  );
}