#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const [baseRef, headRef, taskId, option] = process.argv.slice(2);
const usage = "Dùng: node scripts/review-brief.mjs <base-ref> <head-ref> <task-id> [--dry-run]";

function git(args) {
  return execFileSync("git", args, { cwd: root, encoding: "utf8" }).trim();
}

if (!baseRef || !headRef || !taskId || (option && option !== "--dry-run") || process.argv.length > 6) {
  console.error(usage);
  process.exitCode = 1;
} else if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(taskId)) {
  console.error("task-id chỉ dùng chữ thường, số và dấu gạch ngang");
  process.exitCode = 1;
} else {
  try {
    const base = git(["rev-parse", "--verify", "--end-of-options", `${baseRef}^{commit}`]);
    const head = git(["rev-parse", "--verify", "--end-of-options", `${headRef}^{commit}`]);
    const paths = execFileSync("git", ["diff", "--name-only", "-z", "--no-ext-diff", `${base}...${head}`], {
      cwd: root,
      encoding: "utf8",
    }).split("\0").filter(Boolean);
    if (!paths.length && option !== "--dry-run") {
      throw new Error("Không có file thay đổi giữa base và head; hãy chọn hai commit khác nhau.");
    }
    const template = await readFile(join(root, "reviews", "templates", "REQUEST.md"), "utf8");
    const scope = paths.length ? paths.map((path) => `\n  - ${path}`).join("") : " <không có file khác biệt>";
    const request = template
      .replace("# Yêu cầu review: <task-id>", `# Yêu cầu review: ${taskId}`)
      .replace("- Base commit: <SHA>", `- Base commit: ${base}`)
      .replace("- Head commit hoặc PR: <SHA hoặc URL>", `- Head commit hoặc PR: ${head}`)
      .replace("- Phạm vi file: <đường dẫn liên quan>", `- Phạm vi file:${scope}`);

    if (option === "--dry-run") {
      console.log(request);
    } else {
      const dir = join(root, "reviews", "requests");
      await mkdir(dir, { recursive: true });
      const output = join(dir, `${taskId}.md`);
      await writeFile(output, request, { encoding: "utf8", flag: "wx" });
      console.log(`Đã tạo reviews/requests/${taskId}.md; điền tiêu chí chấp nhận trước khi giao reviewer.`);
    }
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
