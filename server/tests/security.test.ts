import { describe, expect, it, vi } from "vitest";
import type { NextFunction, Response } from "express";
import { authorize, enforceOwnership } from "../src/middleware/security.js";
import { AppError } from "../src/common/errors.js";

const req = (permissions: string[], clearanceRank = 2) => ({ principal: { userId: "user-a", sessionId: "s", status: "ACTIVE", role: "ANALYST", permissions, clearanceRank } } as any);
describe("central authorization", () => {
  it("denies a missing permission", () => { const next = vi.fn(); authorize("audit:read")(req([]), {} as Response, next as NextFunction); expect((next.mock.calls[0]![0] as AppError).code).toBe("PERMISSION_DENIED"); });
  it("denies insufficient clearance", () => { const next = vi.fn(); authorize("graph:read", 3)(req(["graph:read"], 2), {} as Response, next as NextFunction); expect((next.mock.calls[0]![0] as AppError).code).toBe("INSUFFICIENT_CLEARANCE"); });
  it("permits permission plus clearance", () => { const next = vi.fn(); authorize("graph:read", 2)(req(["graph:read"], 2), {} as Response, next as NextFunction); expect(next).toHaveBeenCalledWith(); });
  it("blocks IDOR against another owner's private investigation", () => { expect(() => enforceOwnership("user-b", req([]).principal, false)).toThrowError(/Resource access denied/); });
  it("allows explicit cross-resource permission", () => { expect(() => enforceOwnership("user-b", req(["investigation:read:any"]).principal, false)).not.toThrow(); });
});
