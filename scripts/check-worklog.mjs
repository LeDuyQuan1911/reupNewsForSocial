#!/usr/bin/env node
import { readFile, readdir } from "node:fs/promises";
import { basename, dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const worklogDir = join(root, "docs", "worklog");
const required = [
  "Yêu cầu và phạm vi",
  "Thực hiện",
  "Quyết định",
  "Kiểm chứng",
  "Còn lại",
];

async function check(path) {
  const name = basename(path);
  if (!/^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$/.test(name)) {
    throw new Error(`Tên file không hợp lệ: ${name}`);
  }
  const content = (await readFile(join(worklogDir, name), "utf8")).replace(/\r\n?/g, "\n");
  const date = name.slice(0, 10);
  if (!content.includes(`- Ngày: ${date}`)) throw new Error(`${name}: thiếu ngày khớp tên file`);
  if (!/^- Agent: .+$/m.test(content)) throw new Error(`${name}: thiếu agent`);
  if (!/^- Trạng thái: (hoàn tất|bị chặn)$/m.test(content)) {
    throw new Error(`${name}: trạng thái chưa hoàn tất`);
  }
  for (const heading of required) {
    const marker = `## ${heading}\n`;
    const start = content.indexOf(marker);
    const end = start < 0 ? -1 : content.indexOf("\n## ", start + marker.length);
    const body = start < 0
      ? ""
      : content.slice(start + marker.length, end < 0 ? undefined : end).trim();
    if (!body || /^(Đang kiểm tra\.|TODO|TBD)$/i.test(body)) {
      throw new Error(`${name}: mục "${heading}" chưa có nội dung`);
    }
  }
  console.log(`OK ${name}`);
}

const arg = process.argv[2];
if (!arg || process.argv.length !== 3) {
  console.error("Dùng: node scripts/check-worklog.mjs <tên-file.md | --all>");
  process.exitCode = 1;
} else {
  try {
    const names = arg === "--all"
      ? (await readdir(worklogDir)).filter((name) => name !== "README.md" && name.endsWith(".md"))
      : [arg];
    for (const name of names) await check(name);
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
