/** Real PostgreSQL + HTTP AI + local RAG + backend workflow, with disposable records. */
import assert from "node:assert/strict";
import { randomBytes, randomUUID } from "node:crypto";
import { spawn } from "node:child_process";
import { mkdirSync, cpSync } from "node:fs";
import { resolve } from "node:path";
import argon2 from "argon2";
import { WebSocket } from "ws";
import { prisma } from "../src/config/database.js";
import { createApp } from "../src/app.js";
import { loadEnv } from "../src/config/env.js";
import { attachChatWebSocket } from "../src/modules/chat/websocket.js";

const root = resolve(import.meta.dirname, "../..");
const runKey = randomUUID(),
  internalKey = randomBytes(32).toString("hex");
const env = loadEnv({
  ...process.env,
  NODE_ENV: "test",
  AI_ENGINE_BASE_URL: "http://127.0.0.1:18100",
  RAG_BASE_URL: "http://127.0.0.1:18200",
  AI_ENGINE_API_KEY: internalKey,
  RAG_API_KEY: internalKey,
  AI_ENGINE_TIMEOUT_MS: "600000",
  RATE_LIMIT_MAX: "1000",
});
const children = [],
  users = [],
  cases = [],
  subjects = [],
  applications = [],
  conversations = [];
const evidenceBefore = new Set(
  (await prisma.evidenceReference.findMany({ select: { id: true } })).map(
    (x) => x.id,
  ),
);
let server,
  wss,
  base,
  checks = 0;
const cutoffAt = "2025-12-11T10:00:00Z";
function start(args, cwd) {
  const child = spawn("python", args, {
    cwd,
    windowsHide: true,
    stdio: "ignore",
    env: {
      ...process.env,
      PYTHONDONTWRITEBYTECODE: "1",
      AI_ENGINE_API_KEY: internalKey,
      RAG_API_KEY: internalKey,
    },
  });
  children.push(child);
  return child;
}
async function ready(url, child) {
  for (let i = 0; i < 120; i++) {
    if (child.exitCode !== null)
      throw new Error("Test service failed to start");
    try {
      if (
        (
          await fetch(url, {
            headers: { Authorization: "Bearer " + internalKey },
            signal: AbortSignal.timeout(1000),
          })
        ).ok
      )
        return;
    } catch {}
    await new Promise((r) => setTimeout(r, 250));
  }
  throw new Error("Test service readiness timed out");
}
async function call(method, path, body, token, status = 200) {
  const response = await fetch(base + path, {
    method,
    headers: {
      "content-type": "application/json",
      ...(token ? { Authorization: "Bearer " + token } : {}),
    },
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    signal: AbortSignal.timeout(600000),
  });
  const result = response.status === 204 ? null : await response.json();
  assert.equal(
    response.status,
    status,
    method + " " + path + ": " + JSON.stringify(result?.error),
  );
  checks++;
  return result;
}
try {
  const knowledge = resolve(root, ".tmp/phase5-knowledge-" + runKey);
  mkdirSync(knowledge, { recursive: true });
  cpSync(resolve(root, "chatbot/rag/knowledge_base"), knowledge, {
    recursive: true,
  });
  const ai = start(
    [
      "-m",
      "uvicorn",
      "api.intelligence:app",
      "--host",
      "127.0.0.1",
      "--port",
      "18100",
      "--no-access-log",
    ],
    resolve(root, "ai-engine"),
  );
  const rag = start(
    [
      "-c",
      "import main, uvicorn; from pathlib import Path; main.service.key_manager.keys=[]; main.service.store=main.KnowledgeStore(Path(" +
        JSON.stringify(knowledge) +
        ")); uvicorn.run(main.app, host='127.0.0.1', port=18200, access_log=False)",
    ],
    resolve(root, "chatbot"),
  );
  await Promise.all([
    ready(env.AI_ENGINE_BASE_URL + "/ready", ai),
    ready(env.RAG_BASE_URL + "/health", rag),
  ]);
  server = createApp(env).listen(0, "127.0.0.1");
  await new Promise((r) => server.once("listening", r));
  wss = attachChatWebSocket(server, env);
  base = "http://127.0.0.1:" + server.address().port + "/api/v1";
  const role = await prisma.role.findUniqueOrThrow({
    where: { code: "INVESTIGATOR" },
  });
  const adminRole = await prisma.role.findUniqueOrThrow({
    where: { code: "ADMIN" },
  });
  const clearance = await prisma.clearanceLevel.findFirstOrThrow({
    where: { rank: 4 },
  });
  const password = randomBytes(24).toString("base64url");
  for (const code of ["owner", "other", "admin"]) {
    users.push(
      await prisma.user.create({
        data: {
          email: runKey + "-" + code + "@phase5.invalid",
          displayName: "Phase 5 verification",
          passwordHash: await argon2.hash(password),
          status: "ACTIVE",
          roleId: code === "admin" ? adminRole.id : role.id,
          clearanceLevelId: clearance.id,
        },
      }),
    );
  }
  let owner = await call("POST", "/auth/login", {
    email: users[0].email,
    password,
  });
  const other = await call("POST", "/auth/login", {
    email: users[1].email,
    password,
  });
  const admin = await call("POST", "/auth/login", {
    email: users[2].email,
    password,
  });
  await call("GET", "/auth/me", undefined, owner.accessToken);
  const application = await call(
    "POST",
    "/applications",
    {
      email: runKey + "-applicant@phase5.invalid",
      displayName: "Test applicant",
      profession: "Investigator",
      reason: "Authorized synthetic benchmark investigation access.",
      justification:
        "This disposable integration test verifies the existing account application and approval workflow. No real applicant data is involved.",
    },
    undefined,
    202,
  );
  applications.push(application.id);
  const approved = await call(
    "PATCH",
    "/applications/" + application.id,
    { status: "APPROVED", reviewNote: "Integration verification only" },
    admin.accessToken,
  );
  users.push(
    await prisma.user.findUniqueOrThrow({
      where: { email: runKey + "-applicant@phase5.invalid" },
    }),
  );
  await call("POST", "/auth/login", {
    email: users[3].email,
    password: approved.oneTimeCredential.temporaryPassword,
  });
  console.log(
    "Verified sign-in, application approval and provisioned account sign-in",
  );
  const controlSearch = await call(
    "POST",
    "/search",
    { query: "P01710", limit: 5 },
    owner.accessToken,
  );
  assert.equal(controlSearch.data[0].label, "Bekele Yonas");
  assert.equal(controlSearch.datasetVersion, "prysm-benchmark-v1");
  assert.ok(controlSearch.data[0].analysisCutoffAt);
  const controlSubjectId = controlSearch.data[0].id;
  subjects.push(controlSubjectId);
  const controlCase = await call(
    "POST",
    "/investigations",
    {
      subjectId: controlSubjectId,
      cutoffAt: controlSearch.data[0].analysisCutoffAt,
      title: "Non-suspicious control " + runKey,
    },
    owner.accessToken,
    201,
  );
  cases.push(controlCase.id);
  const controlAnalysis = await call(
    "POST",
    "/investigations/" + controlCase.id + "/analyze",
    {},
    owner.accessToken,
  );
  assert.equal(controlAnalysis.result.assessment.risk_level, "low");
  assert.ok(controlAnalysis.result.assessment.strength < 0.35);
  assert.equal(controlAnalysis.result.evidence.length, 0);
  const controlGraph = await call(
    "GET",
    "/graph/subjects/" + controlSubjectId + "/subgraph?cutoffAt=" +
      encodeURIComponent(controlSearch.data[0].analysisCutoffAt),
    undefined,
    owner.accessToken,
  );
  assert.ok(controlGraph.nodes.length > 0);
  assert.ok(controlGraph.edges.length > 0);
  console.log("Verified non-suspicious search, analysis and relationship graph");
  const search = await call(
    "POST",
    "/search",
    { query: "P01870", limit: 5 },
    owner.accessToken,
  );
  assert.equal(search.data[0].label, "Dawit Bekele");
  assert.equal(search.datasetVersion, "prysm-benchmark-v1");
  assert.ok(search.data[0].analysisCutoffAt);
  const subjectId = search.data[0].id;
  subjects.push(subjectId);
  const item = await call(
    "POST",
    "/investigations",
    {
      subjectId,
      cutoffAt: search.data[0].analysisCutoffAt,
      title: "Phase 5 verification " + runKey,
    },
    owner.accessToken,
    201,
  );
  cases.push(item.id);
  await call(
    "POST",
    "/chat/authorized",
    { investigationId: item.id, question: "Explain" },
    owner.accessToken,
    409,
  );
  await call(
    "GET",
    "/investigations/" + item.id,
    undefined,
    other.accessToken,
    403,
  );
  await call(
    "POST",
    "/investigations/" + item.id + "/analyze",
    {},
    other.accessToken,
    403,
  );
  const analyzed = await call(
    "POST",
    "/investigations/" + item.id + "/analyze",
    {},
    owner.accessToken,
  );
  assert.equal(analyzed.result.version, "prysm-intelligence-v2");
  assert.equal(analyzed.result.assessment.risk_level, "moderate");
  assert.ok(analyzed.result.assessment.strength >= 0.35);
  assert.ok(analyzed.result.evidence.length);
  const retrieved = await call(
    "GET",
    "/investigations/" + item.id + "/intelligence",
    undefined,
    owner.accessToken,
  );
  assert.deepEqual(retrieved.result, analyzed.result);
  await call(
    "GET",
    "/investigations/" + item.id + "/analysis-runs/" + analyzed.runId,
    undefined,
    other.accessToken,
    403,
  );
  const graph = await call(
    "GET",
    "/graph/subjects/" + subjectId + "/subgraph?cutoffAt=" +
      encodeURIComponent(search.data[0].analysisCutoffAt),
    undefined,
    owner.accessToken,
  );
  assert.deepEqual(graph, analyzed.result.graph);
  const detail = await call(
    "GET",
    "/investigations/" + item.id,
    undefined,
    owner.accessToken,
  );
  const evidenceId = detail.findings[0].evidence[0].evidence.id;
  await call("GET", "/evidence/" + evidenceId, undefined, owner.accessToken);
  await call(
    "GET",
    "/evidence/" + evidenceId,
    undefined,
    other.accessToken,
    403,
  );
  const explanation = await call(
    "POST",
    "/chat/authorized",
    { investigationId: item.id, question: "Explain the supported evidence" },
    owner.accessToken,
  );
  conversations.push(explanation.conversationId);
  assert.deepEqual(
    explanation.reasoning.detected.evidence,
    analyzed.result.evidence,
  );
  assert.equal(
    explanation.reasoning.provenance.private_context_sent_to_cloud,
    false,
  );
  const history = await call(
    "GET",
    "/investigations/" + item.id + "/conversation",
    undefined,
    owner.accessToken,
  );
  assert.equal(history.data.length, 1);
  console.log(
    "Verified real analysis, immutable result, graph/evidence, IDOR denial and local explanation/history",
  );
  const exported = await call(
    "POST",
    "/investigations/" + item.id + "/exports",
    { format: "JSON" },
    admin.accessToken,
  );
  assert.deepEqual(exported.result, analyzed.result);
  await call(
    "GET",
    "/suspects/top?cutoffAt=invalid",
    undefined,
    owner.accessToken,
    400,
  );
  console.log(
    "Computing full observed-person ranking through the real AI service",
  );
  const top = await call(
    "GET",
    "/suspects/top?cutoffAt=" + cutoffAt + "&limit=3",
    undefined,
    owner.accessToken,
  );
  assert.equal(top.data.length, 3);
  assert.equal(top.population, "all observed people at cutoff");
  assert.ok(top.data.every((x) => x.is_fraud_probability === false));
  console.log("Verified full-population ranking");
  const document = {
    title: "Phase5-" + runKey,
    content: "General review methodology for synthetic investigations.",
    source: "phase5-verification",
    metadata: { cloud_approved: false },
  };
  const ingested = await call(
    "POST",
    "/rag/ingest",
    document,
    admin.accessToken,
    201,
  );
  const reingested = await call(
    "POST",
    "/rag/ingest",
    {
      ...document,
      content:
        "Updated general review methodology for synthetic investigations.",
    },
    admin.accessToken,
    201,
  );
  assert.equal(ingested.documentId, reingested.documentId);
  await call(
    "PATCH",
    "/rag/documents/" + ingested.jobId,
    { enabled: false },
    admin.accessToken,
  );
  console.log("Verified knowledge ingestion, update and disabling");

  const ws = new WebSocket(base.replace("http:", "ws:") + "/ws/chat");
  await new Promise((resolve, reject) => {
    const timer = setTimeout(
      () => reject(new Error("WebSocket timed out")),
      30000,
    );
    ws.on("message", (raw) => {
      const event = JSON.parse(raw.toString());
      if (event.type === "ready")
        ws.send(
          JSON.stringify({
            type: "authenticate",
            accessToken: owner.accessToken,
          }),
        );
      if (event.type === "authenticated")
        ws.send(
          JSON.stringify({
            investigationId: item.id,
            question: "Explain these findings",
          }),
        );
      if (event.type === "error") {
        clearTimeout(timer);
        reject(new Error(event.code));
      }
      if (event.type === "done") {
        conversations.push(event.conversationId);
        assert.deepEqual(event.evidence, analyzed.result.evidence);
        clearTimeout(timer);
        ws.close();
        checks++;
        resolve();
      }
    });
    ws.on("error", reject);
  });
  owner = await call("POST", "/auth/refresh", {
    refreshToken: owner.refreshToken,
  });
  await call("POST", "/auth/logout", {}, owner.accessToken, 204);
  await call("GET", "/auth/me", undefined, owner.accessToken, 401);
  console.log(
    JSON.stringify({
      status: "passed",
      checks,
      services: [
        "PostgreSQL",
        "AI Phase 3",
        "RAG Phase 4 local",
        "HTTP",
        "WebSocket",
      ],
      cloudCalls: 0,
    }),
  );
} finally {
  if (wss) {
    for (const client of wss.clients) client.terminate();
    wss.close();
  }
  if (server) await new Promise((r) => server.close(r));
  for (const child of children) child.kill();
  // Only disposable records created by this verification run are removed.
  await prisma.ragInteraction.deleteMany({
    where: { userId: { in: users.map((x) => x.id) } },
  });
  await prisma.investigation.deleteMany({ where: { id: { in: cases } } });
  await prisma.accountApplication.deleteMany({
    where: { id: { in: applications } },
  });
  await prisma.auditEvent.deleteMany({
    where: { actorUserId: { in: users.map((x) => x.id) } },
  });
  await prisma.ragDocumentRecord.deleteMany({
    where: { createdBy: { in: users.map((x) => x.id) } },
  });
  await prisma.user.deleteMany({
    where: { id: { in: users.map((x) => x.id) } },
  });
  const newEvidence = (
    await prisma.evidenceReference.findMany({
      where: { findings: { none: {} } },
      select: { id: true },
    })
  ).filter((x) => !evidenceBefore.has(x.id));
  await prisma.evidenceReference.deleteMany({
    where: { id: { in: newEvidence.map((x) => x.id) } },
  });
  await prisma.$disconnect();
}
