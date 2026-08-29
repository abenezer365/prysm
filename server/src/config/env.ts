import { z } from "zod";

const schema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  PORT: z.coerce.number().int().positive().default(4000),
  DATABASE_URL: z.string().min(1),
  JWT_ACCESS_SECRET: z.string().min(32),
  JWT_REFRESH_SECRET: z.string().min(32),
  ACCESS_TOKEN_TTL: z.string().default("15m"),
  REFRESH_TOKEN_TTL: z.string().default("7d"),
  AI_ENGINE_BASE_URL: z.string().url(), AI_ENGINE_API_KEY: z.string().default(""),
  AI_ENGINE_TIMEOUT_MS: z.coerce.number().int().min(1000).max(600000).default(120_000),
  RAG_BASE_URL: z.string().url(), RAG_API_KEY: z.string().default(""),
  RAG_TIMEOUT_MS: z.coerce.number().int().min(1000).max(120000).default(30_000),
  CORS_ORIGIN: z.string().min(1),
  RATE_LIMIT_WINDOW_MS: z.coerce.number().int().positive().default(60_000),
  RATE_LIMIT_MAX: z.coerce.number().int().positive().default(100),
  MODEL_ARTIFACT_BASE_URL: z.string().default("")
});
export type Env = z.infer<typeof schema>;
export const loadEnv = (source: NodeJS.ProcessEnv = process.env): Env => schema.parse(source);
