#!/usr/bin/env node
import { readFile, readdir, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const catalogDir = join(root, "plugins");
const manifestPath = join(root, "project.plugins.json");
const validId = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/;

function fail(message) {
  throw new Error(message);
}

async function readJson(path) {
  try {
    return JSON.parse(await readFile(path, "utf8"));
  } catch (error) {
    if (error instanceof SyntaxError) fail(`JSON không hợp lệ: ${path}`);
    throw error;
  }
}

async function loadCatalog() {
  const entries = await readdir(catalogDir, { withFileTypes: true });
  const catalog = new Map();
  for (const entry of entries.filter((item) => item.isDirectory())) {
    const id = entry.name;
    if (!validId.test(id)) fail(`Tên thư mục plugin không hợp lệ: ${id}`);
    const metadata = await readJson(join(catalogDir, id, "plugin.json"));
    if (
      metadata.id !== id ||
      typeof metadata.name !== "string" ||
      !metadata.name.trim() ||
      typeof metadata.description !== "string" ||
      !metadata.description.trim()
    ) {
      fail(`Metadata plugin không hợp lệ: ${id}`);
    }
    const instructions = await readFile(join(catalogDir, id, "INSTRUCTIONS.md"), "utf8");
    if (!instructions.trim()) fail(`INSTRUCTIONS.md trống: ${id}`);
    catalog.set(id, metadata);
  }
  return catalog;
}

async function loadManifest(catalog) {
  const manifest = await readJson(manifestPath);
  if (
    manifest.schemaVersion !== 1 ||
    !Array.isArray(manifest.enabled) ||
    manifest.enabled.some((id) => typeof id !== "string" || !catalog.has(id)) ||
    new Set(manifest.enabled).size !== manifest.enabled.length
  ) {
    fail("project.plugins.json không hợp lệ hoặc chứa plugin không có trong catalog");
  }
  return manifest;
}

function usage() {
  return "Dùng: node scripts/plugins.mjs list | check | enable <id> | disable <id>";
}

async function main() {
  const [command, id, ...extra] = process.argv.slice(2);
  if (!command || command === "help" || extra.length) {
    console.log(usage());
    if (!command || command === "help") return;
    fail("Tham số không hợp lệ");
  }

  const catalog = await loadCatalog();
  const manifest = await loadManifest(catalog);

  if (command === "check") {
    if (id) fail(usage());
    console.log(`Hợp lệ: ${catalog.size} plugin, ${manifest.enabled.length} đang bật`);
    return;
  }
  if (command === "list") {
    if (id) fail(usage());
    for (const [pluginId, metadata] of catalog) {
      console.log(`[${manifest.enabled.includes(pluginId) ? "x" : " "}] ${pluginId} — ${metadata.description}`);
    }
    return;
  }
  if (command !== "enable" && command !== "disable") fail(usage());
  if (!id || !catalog.has(id)) fail(`Plugin không tồn tại: ${id ?? "(thiếu id)"}`);

  const enabled = new Set(manifest.enabled);
  if (command === "enable") enabled.add(id);
  else enabled.delete(id);
  const next = [...enabled].sort();
  if (next.join("\0") !== manifest.enabled.join("\0")) {
    manifest.enabled = next;
    await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
  }
  console.log(`${id}: ${command === "enable" ? "đã bật" : "đã tắt"}`);
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
