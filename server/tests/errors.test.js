import request from "supertest";
import { it, expect } from "vitest";
import { createApp } from "../src/app.js";
const env = {
  JWT_ACCESS_SECRET: "x".repeat(32),
  CORS_ORIGIN: "http://localhost",
  RATE_LIMIT_WINDOW_MS: 60000,
  RATE_LIMIT_MAX: 100,
  AI_ENGINE_BASE_URL: "http://localhost:8100",
  RAG_BASE_URL: "http://localhost:8200",
};
it("returns JSON for malformed JSON input", async () => {
  const r = await request(createApp(env))
    .post("/api/v1/auth/login")
    .set("content-type", "application/json")
    .send("{broken");
  expect(r.status).toBe(400);
  expect(r.body.error.code).toBe("INVALID_JSON");
});
it("returns the same error envelope for rate limits", async () => {
  const app = createApp({ ...env, RATE_LIMIT_MAX: 1 });
  await request(app).get("/api/v1/health");
  const r = await request(app).get("/api/v1/health");
  expect(r.status).toBe(429);
  expect(r.body.error.code).toBe("RATE_LIMITED");
  expect(r.body.error.requestId).toBeTruthy();
});
it("rejects malformed pagination instead of querying PostgreSQL", async () => {
  const r = await request(createApp(env)).get("/api/v1/news?limit=NaN");
  expect(r.status).toBe(400);
  expect(r.body.error.code).toBe("VALIDATION_ERROR");
});
