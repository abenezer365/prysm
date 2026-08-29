import { randomUUID } from "node:crypto";
import type { ErrorRequestHandler, RequestHandler } from "express";
import { ZodError, type ZodType } from "zod";
import { AppError } from "../common/errors.js";
import type { AuthRequest } from "../common/types.js";

export const requestId: RequestHandler = (req, res, next) => {
  const id = String(req.header("x-request-id") || randomUUID());
  (req as AuthRequest).requestId = id; res.setHeader("x-request-id", id); next();
};
export const validate = (schema: ZodType, source: "body" | "query" | "params" = "body"): RequestHandler =>
  (req, _res, next) => { try { (req as any)[source] = schema.parse((req as any)[source]); next(); } catch (error) { next(error); } };
export const notFoundHandler: RequestHandler = (_req, _res, next) => next(new AppError(404, "ROUTE_NOT_FOUND", "Route not found"));
export const errorHandler: ErrorRequestHandler = (error, req, res, _next) => {
  const requestId = (req as AuthRequest).requestId;
  if (error instanceof ZodError) return res.status(400).json({ error: { code: "VALIDATION_ERROR", message: "Request validation failed", details: error.issues, requestId } });
  const known = error instanceof AppError;
  const status = known ? error.status : 500;
  return res.status(status).json({ error: { code: known ? error.code : "INTERNAL_ERROR", message: known ? error.message : "Internal server error", ...(known && error.details ? { details: error.details } : {}), requestId } });
};
