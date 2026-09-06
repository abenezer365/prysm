import { spawnSync } from "node:child_process";
import { mkdirSync } from "node:fs";
import { resolve } from "node:path";
// Credentials are inherited only through child environment, never printed.
const url = new URL(process.env.DATABASE_URL);
const directory = resolve("../.tmp/database-backups");
mkdirSync(directory, { recursive: true });
const output = resolve(
  directory,
  "phase5-" + new Date().toISOString().replaceAll(":", "-") + ".dump",
);
const executable =
  process.env.PG_DUMP || "C:/Program Files/PostgreSQL/18/bin/pg_dump.exe";
const args = [
  "--host",
  url.hostname,
  "--port",
  url.port || "5432",
  "--username",
  decodeURIComponent(url.username),
  "--dbname",
  url.pathname.slice(1),
  "--format=custom",
  "--file",
  output,
];
const result = spawnSync(executable, args, {
  env: { ...process.env, PGPASSWORD: decodeURIComponent(url.password) },
  stdio: ["ignore", "pipe", "pipe"],
});
if (result.status !== 0)
  throw new Error("Database backup failed; migration must not proceed");
console.log("Database backup saved: " + output);
