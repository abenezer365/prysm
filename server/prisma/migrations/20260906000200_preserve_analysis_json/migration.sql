-- Preserve the engine's JSON numeric representation through Prisma round trips.
-- Existing payloads are retained; the API continues returning parsed JSON objects.
ALTER TABLE "analysis_runs" ALTER COLUMN "response_payload" TYPE TEXT
  USING "response_payload"::text;
