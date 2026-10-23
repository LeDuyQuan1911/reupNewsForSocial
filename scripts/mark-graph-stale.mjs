#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";

function git(...args) {
  const result = spawnSync("git", args, { encoding: "utf8" });
  if (result.status !== 0) throw new Error(result.stderr.trim() || `git ${args[0]} failed`);
  return result.stdout.trim();
}

const root = git("rev-parse", "--show-toplevel");
const head = git("rev-parse", "HEAD");
const parent = spawnSync("git", ["rev-parse", "--verify", "HEAD^"], { encoding: "utf8" });
const changed = parent.status === 0
  ? git("diff", "--name-only", "HEAD^", "HEAD", "--")
  : git("ls-tree", "-r", "--name-only", "HEAD", "--");
const paths = changed.split(/\r?\n/).filter((path) =>
  path && !path.startsWith(".ua/") && !path.startsWith(".understand-anything/"),
);

if (paths.length > 0) {
  const dataDir = join(root, existsSync(join(root, ".understand-anything")) ? ".understand-anything" : ".ua");
  await mkdir(dataDir, { recursive: true });
  await writeFile(join(dataDir, "stale.json"), `${JSON.stringify({ head, changedPaths: paths }, null, 2)}\n`);
  console.log(`[codebase-graph] Graph cần làm mới sau commit ${head.slice(0, 7)}.`);
}
