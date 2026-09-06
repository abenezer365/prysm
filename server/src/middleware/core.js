import { randomUUID } from "node:crypto";
import { ZodError } from "zod";
import { AppError } from "../common/errors.js";
export const requestId = (req, res, next) => {
  const id = /^[a-zA-Z0-9_-]{1,80}$/.test(req.header("x-request-id") || "")
    ? req.header("x-request-id")
    : randomUUID();
  req.requestId = id;
  res.setHeader("x-request-id", id);
  next();
};
export const validate = (schema, source = "body") => {
  const middleware = (req, _res, next) => {
    try {
      req[source] = schema.parse(req[source]);
      next();
    } catch (error) {
      next(error);
    }
  };
  middleware.validationSchema = schema;
  middleware.validationSource = source;
  return middleware;
};
export const notFoundHandler = (_req, _res, next) =>
  next(new AppError(404, "ROUTE_NOT_FOUND", "Route not found"));
export const errorHandler = (error, req, res, _next) => {
  const requestId = req.requestId;
  if (error instanceof ZodError)
    return res.status(400).json({
      error: {
        code: "VALIDATION_ERROR",
        message: "Request validation failed",
        details: error.issues,
        requestId,
      },
    });
  if (error?.type === "entity.too.large")
    return res.status(413).json({
      error: {
        code: "PAYLOAD_TOO_LARGE",
        message: "Request payload exceeds the allowed size",
        requestId,
      },
    });
  if (error?.type === "entity.parse.failed")
    return res.status(400).json({
      error: {
        code: "INVALID_JSON",
        message: "Malformed JSON body",
        requestId,
      },
    });
  if (["P1001", "P1002", "P2024"].includes(error?.code))
    return res.status(503).json({
      error: {
        code: "DATABASE_UNAVAILABLE",
        message: "Database is unavailable",
        requestId,
      },
    });
  if (error?.code === "P2002")
    return res.status(409).json({
      error: {
        code: "RESOURCE_CONFLICT",
        message: "Resource already exists",
        requestId,
      },
    });
  const known = error instanceof AppError;
  const status = known ? error.status : 500;
  return res.status(status).json({
    error: {
      code: known ? error.code : "INTERNAL_ERROR",
      message: known ? error.message : "Internal server error",
      ...(known && error.details ? { details: error.details } : {}),
      requestId,
    },
  });
};
