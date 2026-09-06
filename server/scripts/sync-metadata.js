import { syncMetadata } from "../src/modules/metadata.js";
import { prisma } from "../src/config/database.js";
try {
  console.log(
    JSON.stringify({ factTables: await syncMetadata(), status: "ok" }),
  );
} finally {
  await prisma.$disconnect();
}
