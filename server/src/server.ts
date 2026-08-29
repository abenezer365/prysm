import { createApp } from "./app.js";
import { prisma } from "./config/database.js";
import { loadEnv } from "./config/env.js";
import { attachChatWebSocket } from "./modules/chat/websocket.js";
const env = loadEnv(); const server = createApp(env).listen(env.PORT, () => console.log(JSON.stringify({ level: "info", message: "Prysm backend listening", port: env.PORT }))); const chatWebSocket=attachChatWebSocket(server,env);
async function shutdown() { server.close(async () => { await prisma.$disconnect(); process.exit(0); }); }
process.on("SIGINT", shutdown); process.on("SIGTERM", shutdown);
