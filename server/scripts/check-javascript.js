import { readdirSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
let checked = 0;
function check(dir) {
  for (const item of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, item.name);
    if (item.isDirectory()) check(path);
    else if (/\.(?:js|mjs)$/.test(path)) {
      const result = spawnSync(process.execPath, ["--check", path], {
        stdio: "inherit",
      });
      if (result.status !== 0) process.exit(result.status || 1);
      checked++;
    } else if (path.endsWith(".ts"))
      throw new Error("TypeScript source remains: " + path);
  }
}
for (const dir of ["src", "scripts", "tests", "prisma"]) check(dir);
console.log("JavaScript syntax verified: " + checked + " files");
