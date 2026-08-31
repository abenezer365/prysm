import request from "supertest";
import { describe, expect, it } from "vitest";
import { createApp } from "../src/app.js";
const env = {
  NODE_ENV: "test",
  PORT: 4000,
  DATABASE_URL: "postgresql://unused",
  JWT_ACCESS_SECRET: "a".repeat(32),
  JWT_REFRESH_SECRET: "b".repeat(32),
  ACCESS_TOKEN_TTL: "15m",
  REFRESH_TOKEN_TTL: "7d",
  AI_ENGINE_BASE_URL: "http://127.0.0.1:8100",
  AI_ENGINE_API_KEY: "",
  AI_ENGINE_TIMEOUT_MS: 120000,
  RAG_BASE_URL: "http://127.0.0.1:8200",
  RAG_API_KEY: "",
  RAG_TIMEOUT_MS: 30000,
  CORS_ORIGIN: "http://localhost:3000",
  RATE_LIMIT_WINDOW_MS: 60000,
  RATE_LIMIT_MAX: 100,
  MODEL_ARTIFACT_BASE_URL: "",
} as const;
describe("API boundary", () => {
  const app = createApp(env);
  it("serves liveness without dependencies", async () => {
    const response = await request(app).get("/api/v1/health");
    expect(response.status).toBe(200);
    expect(response.body.status).toBe("ok");
    expect(response.headers["x-request-id"]).toBeTruthy();
  });
  it("uses the stable error contract", async () => {
    const response = await request(app).get("/api/v1/missing");
    expect(response.status).toBe(404);
    expect(response.body.error.code).toBe("ROUTE_NOT_FOUND");
    expect(response.body.error.requestId).toBeTruthy();
  });
  it("requires auth for protected resources", async () => {
    const response = await request(app).get("/api/v1/investigations");
    expect(response.status).toBe(401);
    expect(response.body.error.code).toBe("AUTHENTICATION_REQUIRED");
  });
  it("rejects public chat attempts to inject authorized context", async () => {
    const response = await request(app)
      .post("/api/v1/chat/public")
      .send({
        question: "secret",
        subjectId: "00000000-0000-4000-8000-000000000000",
      });
    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe("VALIDATION_ERROR");
  });
  it("rejects oversized JSON payloads", async () => {
    const response = await request(app)
      .post("/api/v1/applications")
      .set("content-type", "application/json")
      .send(JSON.stringify({ data: "x".repeat(1_100_000) }));
    expect(response.status).toBe(413);
  });
  it("requires a substantive access application", async () => {
    const response = await request(app)
      .post("/api/v1/applications")
      .send({
        email: "applicant@example.com",
        displayName: "Applicant",
        profession: "Analyst",
        reason: "too short",
        justification: "brief",
      });
    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe("VALIDATION_ERROR");
  });
  it("validates contact submissions before persistence", async () => {
    const response = await request(app)
      .post("/api/v1/contact")
      .send({ name: "A", email: "invalid", message: "short" });
    expect(response.status).toBe(400);
  });
  it("validates bug diagnostics and severity", async () => {
    const response = await request(app)
      .post("/api/v1/bug-reports")
      .send({
        description: "A sufficiently detailed report of a failure.",
        severity: "IMPOSSIBLE",
      });
    expect(response.status).toBe(400);
  });
  it("protects administrative completion APIs", async () => {
    for (const path of [
      "/api/v1/dashboard/summary",
      "/api/v1/users",
      "/api/v1/activity",
      "/api/v1/rag/conversations",
    ]) {
      const response = await request(app).get(path);
      expect(response.status).toBe(401);
    }
  });
  it("protects refresh tokens against malformed input", async () => {
    const response = await request(app)
      .post("/api/v1/auth/refresh")
      .send({ refreshToken: "invalid" });
    expect(response.status).toBe(400);
  });
  it("validates contributor applications before persistence", async () => {
    const response = await request(app)
      .post("/api/v1/contributors/applications")
      .send({ email: "invalid", displayName: "A", expertise: "x", motivation: "short" });
    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe("VALIDATION_ERROR");
  });
  it("protects settings and contributor moderation", async () => {
    const settings = await request(app).patch("/api/v1/me/settings").send({ preferences: { compactMode: true } });
    const contributors = await request(app).get("/api/v1/contributors/applications");
    expect(settings.status).toBe(401);
    expect(contributors.status).toBe(401);
  });
});
