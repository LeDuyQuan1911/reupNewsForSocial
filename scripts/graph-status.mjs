#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { join } from "node:path";

function git(...args) {
  const result = spawnSync("git", args, { encoding: "utf8" });
  if (result.status !== 0) throw new Error(result.stderr.trim() || `git ${args[0]} failed`);
  return result.stdout.trim();
}

async function jsonOrNull(path) {
  try {
    return JSON.parse(await readFile(path, "utf8"));
  } catch (error) {
    if (error.code === "ENOENT") return null;
    throw error;
  }
}

const root = git("rev-parse", "--show-toplevel");
const head = git("rev-parse", "HEAD");
const dir = join(root, existsSync(join(root, ".understand-anything")) ? ".understand-anything" : ".ua");
const graph = await jsonOrNull(join(dir, "knowledge-graph.json"));
const meta = await jsonOrNull(join(dir, "meta.json"));
const stale = await jsonOrNull(join(dir, "stale.json"));

if (!graph || !meta) {
  console.log("MISSING: chưa có graph; chạy skill understand để tạo baseline.");
} else if (meta.gitCommitHash !== head) {
  console.log(`STALE: graph ở ${meta.gitCommitHash ?? "không rõ"}, HEAD ở ${head}. Chạy skill understand để cập nhật.`);
} else {
  console.log(`CURRENT: graph khớp HEAD ${head.slice(0, 7)}.`);
}
if (stale && stale.head === head && meta?.gitCommitHash !== head) {
  console.log(`Commit mới thay đổi ${stale.changedPaths?.length ?? 0} file.`);
}
