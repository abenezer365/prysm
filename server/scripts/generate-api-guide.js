import { listQueries } from "../src/routes/queries.js";
import { writeFileSync, readFileSync } from "node:fs";
import { z } from "zod";
import { apiRoutes } from "../src/routes/index.js";
import { contracts } from "../docs/contract-descriptions.js";
const env = {
  JWT_ACCESS_SECRET: "documentation-only",
  AI_ENGINE_BASE_URL: "http://127.0.0.1:8100",
  RAG_BASE_URL: "http://127.0.0.1:8200",
};
const routes = [];
function collect(stack) {
  for (const layer of stack) {
    if (layer.route)
      for (const path of [].concat(layer.route.path))
        for (const method of Object.keys(layer.route.methods))
          routes.push({ path, method, stack: layer.route.stack });
    else if (layer.handle.stack) collect(layer.handle.stack);
  }
}
collect(apiRoutes(env).stack);
const spec = {
  openapi: "3.1.0",
  info: { title: "Prysm Phase 5 API", version: "0.5.0" },
  servers: [{ url: "/api/v1" }],
  components: {
    securitySchemes: {
      bearerAuth: { type: "http", scheme: "bearer", bearerFormat: "JWT" },
    },
  },
  paths: {},
};
const intro = readFileSync(
  new URL("../docs/FRONTEND_FLOW.md", import.meta.url),
  "utf8",
);
let guide =
  intro +
  "\n\n## Complete HTTP endpoint reference\n\nGenerated from the mounted routes and their Zod request validators. `?` means optional. All protected endpoints additionally return 401 for invalid/revoked sessions and 403 for missing permission, clearance or case access. Every endpoint can return the standard 400/413/429/500/502/503 error envelope described above; resource routes can return 404 and conflicting mutations 409. Request field constraints below are enforced; complete machine-readable schemas are in [openapi.json](openapi.json).\n";
function inputSchema(route) {
  const middleware = route.stack.find((x) => x.handle.validationSchema);
  if (middleware)
    return z.toJSONSchema(middleware.handle.validationSchema, {
      io: "input",
      unrepresentable: "any",
    });
  if (route.path === "/search")
    return z.toJSONSchema(
      z.object({
        query: z.string().min(2).max(200),
        limit: z.number().int().min(1).max(50).default(20),
      }),
    );
  return undefined;
}
function fields(schema) {
  return Object.entries(schema?.properties || {})
    .map(([name, field]) => {
      const type =
        field.type ||
        (field.anyOf ? field.anyOf.map((x) => x.type).join("/") : "value");
      const constraints = [
        "format",
        "minLength",
        "maxLength",
        "minimum",
        "maximum",
        "pattern",
        "default",
      ]
        .filter((k) => field[k] !== undefined)
        .map((k) => k + "=" + JSON.stringify(field[k]));
      if (field.enum) constraints.push("one of " + field.enum.join(", "));
      if (field.const !== undefined)
        constraints.push("must equal " + field.const);
      const nested = field.properties ? "; fields: " + fields(field) : "";
      return (
        name +
        (schema.required?.includes(name) ? "" : "?") +
        ": " +
        type +
        (constraints.length ? " (" + constraints.join("; ") + ")" : "") +
        nested
      );
    })
    .join("; ");
}
for (const route of routes) {
  const key = route.method.toUpperCase() + " " + route.path;
  const details = contracts[key];
  if (!details) throw new Error("Missing API documentation: " + key);
  const authenticated = route.stack.some((x) => x.handle.authRequired);
  const grant = route.stack.find((x) => x.handle.permission)?.handle;
  const access = authenticated
    ? grant
      ? grant.permission + ", minimum rank " + grant.minimumClearance
      : "Authenticated"
    : "Public";
  const schema = inputSchema(route);
  const parameters = [...route.path.matchAll(/:([A-Za-z]+)/g)].map((m) => ({
    name: m[1],
    in: "path",
    required: true,
    schema: { type: "string", format: "uuid" },
  }));
  let query = "";
  if (
    [
      "/suspects/top",
      "/dashboard/top-suspects",
      "/graph/subjects/:id/subgraph",
    ].includes(route.path)
  ) {
    parameters.push({
      name: "cutoffAt",
      in: "query",
      required: true,
      schema: { type: "string", format: "date-time" },
    });
    query = "Required query cutoffAt (timezone-aware ISO date-time)";
    if (route.path !== "/graph/subjects/:id/subgraph") {
      parameters.push({
        name: "limit",
        in: "query",
        schema: { type: "integer", minimum: 1, maximum: 50, default: 10 },
      });
      query += "; limit? integer 1–50, default 10";
    }
  } else if (route.method === "get" && details[1].includes("page")) {
    parameters.push({
      name: "limit",
      in: "query",
      schema: {
        type: "integer",
        minimum: 1,
        maximum: 100,
        default:
          route.path === "/investigations" ||
          route.path.endsWith("/conversation")
            ? 50
            : 20,
      },
    });
    query =
      "Optional query limit (bounded integer; default 20, cases/history 50; max 100, public news 50)";
  }
  if (route.method === "get" && listQueries[route.path]) {
    const querySchema = z.toJSONSchema(listQueries[route.path], {
      io: "input",
      unrepresentable: "any",
    });
    for (let i = parameters.length - 1; i >= 0; i--)
      if (parameters[i].in === "query") parameters.splice(i, 1);
    for (const [name, field] of Object.entries(querySchema.properties))
      parameters.push({ name, in: "query", required: false, schema: field });
    query = fields(querySchema);
  }
  const success = /^20[124]/.exec(details[1])?.[0] || "200";
  const operation = {
    summary: details[0],
    description: details[1] + ". Access: " + access,
    security: authenticated ? [{ bearerAuth: [] }] : [],
    parameters,
    responses: {
      [success]: {
        description: details[1],
        ...(success !== "204"
          ? {
              content: {
                "application/json": {
                  schema: { type: "object", description: details[1] },
                },
              },
            }
          : {}),
      },
    },
  };
  for (const status of [400, 401, 403, 404, 409, 413, 429, 500, 502, 503])
    operation.responses[status] = {
      description: "Standard error: {error:{code,message,requestId,details?}}",
    };
  if (schema) {
    delete schema.$schema;
    operation.requestBody = {
      required: true,
      content: { "application/json": { schema } },
    };
  }
  const path = route.path.replace(/:([A-Za-z]+)/g, "{$1}");
  (spec.paths[path] ||= {})[route.method] = operation;
  guide +=
    "\n### " +
    key +
    "\n\n" +
    details[0] +
    ".\n\n- **Auth:** " +
    access +
    ".\n- **Request:** " +
    (parameters.some((p) => p.in === "path") ? "Path IDs are UUIDs. " : "") +
    (query ? query + ". " : "") +
    (schema
      ? fields(schema)
      : route.method === "get"
        ? "No body."
        : "Empty JSON object `{}`.") +
    "\n- **Response:** " +
    details[1] +
    ".\n- **Errors:** Standard envelope and status cases above; case resources enforce ownership/sharing and clearance.\n";
}
const documented = Object.keys(contracts);
if (documented.length !== routes.length)
  throw new Error("Stale or duplicate API descriptions");
writeFileSync(
  new URL("../docs/openapi.json", import.meta.url),
  JSON.stringify(spec, null, 2) + "\n",
);
writeFileSync(new URL("../docs/API.md", import.meta.url), guide);
console.log("Documented " + routes.length + " mounted HTTP endpoints");
