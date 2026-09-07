import cors from "cors";
import express from "express";
import rateLimit from "express-rate-limit";
import helmet from "helmet";
import { pinoHttp } from "pino-http";
import { errorHandler, notFoundHandler, requestId } from "./middleware/core.js";
import { apiRoutes } from "./routes/index.js";
export function createApp(env) {
  const app = express();
  app.disable("x-powered-by");
  app.use(
    requestId,
    pinoHttp({
      autoLogging: false,
      redact: [
        "req.headers.authorization",
        "req.body.password",
        "req.body.refreshToken",
      ],
    }),
    helmet(),
    cors({ origin: env.CORS_ORIGIN.split(","), credentials: true }),
    express.json({ limit: "1mb" }),
    rateLimit({
      windowMs: env.RATE_LIMIT_WINDOW_MS,
      limit: env.RATE_LIMIT_MAX,
      standardHeaders: "draft-8",
      legacyHeaders: false,
      handler: (req, res) =>
        res.status(429).json({
          error: {
            code: "RATE_LIMITED",
            message: "Too many requests",
            requestId: req.requestId,
          },
        }),
    }),
  );
  app.use("/api/v1", apiRoutes(env));
  app.use(notFoundHandler, errorHandler);
  return app;
}
