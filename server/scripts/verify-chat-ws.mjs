import WebSocket from "ws";

const token = process.env.PRYSMS_TEST_ACCESS_TOKEN;
const investigationId = process.env.PRYSMS_TEST_INVESTIGATION_ID;
if (!token || !investigationId) {
  throw new Error("PRYSMS_TEST_ACCESS_TOKEN and PRYSMS_TEST_INVESTIGATION_ID are required");
}

const socket = new WebSocket(process.env.PRYSMS_WS_URL || "ws://127.0.0.1:4000/api/v1/ws/chat");
const timer = setTimeout(() => {
  socket.terminate();
  process.exitCode = 1;
}, 30_000);
const messages = [];

socket.on("open", () => socket.send(JSON.stringify({ type: "authenticate", accessToken: token })));
socket.on("message", (raw) => {
  const message = JSON.parse(raw.toString());
  messages.push(message);
  if (message.type === "authenticated") {
    socket.send(JSON.stringify({ question: "Summarize the authorized investigation evidence.", investigationId }));
  }
  if (message.type === "done" || message.type === "error") {
    clearTimeout(timer);
    console.log(JSON.stringify({ terminalType: message.type, requestId: message.requestId, conversationId: message.conversationId, sourceCount: message.sources?.length || 0, eventTypes: messages.map((item) => item.type) }));
    socket.close();
    if (message.type === "error") process.exitCode = 1;
  }
});
socket.on("error", (error) => {
  clearTimeout(timer);
  console.error(error.message);
  process.exitCode = 1;
});
