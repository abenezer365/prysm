import { PrismaClient } from "@prisma/client";
const db = new PrismaClient();
const rows = await db.datasetRecord.groupBy({ by: ["dataset"], _count: { _all: true }, orderBy: { dataset: "asc" } });
console.log(JSON.stringify({ total: rows.reduce((sum, row) => sum + row._count._all, 0), datasets: rows }, null, 2));
await db.$disconnect();
