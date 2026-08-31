import { spawn } from "node:child_process";
import { createInterface } from "node:readline";
import { resolve } from "node:path";
import { Prisma, PrismaClient } from "@prisma/client";

const db = new PrismaClient();
const raw = resolve(process.argv.find(x => x.startsWith("--raw="))?.slice(6) || "../data/raw");
const replace = process.argv.includes("--replace");
const python = process.env.PRYSM_PYTHON || resolve("../.venv/Scripts/python.exe");
const json = (value: unknown) => JSON.parse(JSON.stringify(value)) as Prisma.InputJsonValue;
async function main() {
  if (replace) await db.datasetRecord.deleteMany({});
  const child = spawn(python, [resolve("scripts/export-parquet-jsonl.py"), raw], { stdio: ["ignore", "pipe", "inherit"] });
  const exitPromise = new Promise<number>((ok) => child.once("close", code => ok(code ?? 1)));
  const lines = createInterface({ input: child.stdout }); let batch: any[] = [], count = 0;
  const flush = async () => { if (!batch.length) return; await db.datasetRecord.createMany({ data: batch, skipDuplicates: true }); count += batch.length; batch = []; };
  for await (const line of lines) { const row = JSON.parse(line); batch.push({ ...row, eventAt: row.eventAt ? new Date(row.eventAt) : null, payload: json(row.payload) }); if (batch.length >= 500) await flush(); }
  await flush(); const exit = await exitPromise; if (exit) throw new Error(`Parquet exporter exited ${exit}`);
  console.log(JSON.stringify({ status: "ok", attempted: count, raw, replace }));
}
main().finally(() => db.$disconnect());
