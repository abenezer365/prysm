import type { Request } from "express";
export type Principal = { userId: string; status: string; role: string; clearanceRank: number; permissions: string[]; sessionId: string };
export type AuthRequest = Request & { principal?: Principal; requestId?: string };
export type Page<T> = { data: T[]; page: { nextCursor: string | null; limit: number } };
