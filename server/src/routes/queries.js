import { z } from "zod";
const page = (max = 100) => z.coerce.number().int().min(1).max(max).default(20);
const review = z.enum(["PENDING", "APPROVED", "REJECTED"]).optional();
export const listQueries = {
  "/applications": z.object({ limit: page(), status: review }),
  "/users": z.object({
    limit: page(),
    status: z
      .enum(["PENDING", "ACTIVE", "SUSPENDED", "DISABLED", "REJECTED"])
      .optional(),
    role: z.string().max(80).optional(),
    clearanceRank: z.coerce.number().int().min(1).max(100).optional(),
  }),
  "/activity": z.object({
    limit: page(),
    action: z.string().max(100).optional(),
  }),
  "/news": z.object({ limit: page(50) }),
  "/news/admin": z.object({ limit: page() }),
  "/bug-resolutions": z.object({ limit: page(50) }),
  "/bug-reports": z.object({
    limit: page(),
    status: z
      .enum(["OPEN", "TRIAGED", "IN_PROGRESS", "RESOLVED", "CLOSED"])
      .optional(),
  }),
  "/intelligence-reports": z.object({
    limit: page(),
    status: z.enum(["NEW", "REVIEWED", "FAKE", "SPAM"]).optional(),
  }),
  "/beta/applications": z.object({ limit: page(), status: review }),
  "/contributors/applications": z.object({ limit: page(), status: review }),
  "/datasets": z.object({ limit: page() }),
  "/rag/conversations": z.object({
    limit: page(),
    scope: z.enum(["PUBLIC", "AUTHORIZED"]).optional(),
    conversationId: z.string().uuid().optional(),
  }),
  "/rag/documents": z.object({ limit: page() }),
};
