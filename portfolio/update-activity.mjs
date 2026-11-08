const fields = (block, label) =>
  block.match(new RegExp("^- " + label + ": (.*)$", "m"))?.[1];

function setField(block, label, value) {
  const field = new RegExp("^- " + label + ": .*\\n?", "m");
  if (field.test(block)) {
    return block.replace(field, (line) => "- " + label + ": " + value + (line.endsWith("\n") ? "\n" : ""));
  }
  return block.trimEnd() + "\n- " + label + ": " + value + "\n\n";
}

function updateRecord(markdown, label, id, edit) {
  const parts = markdown.split(/(?=^## )/m);
  const matches = parts.map((block, i) => fields(block, label) === id ? i : -1).filter(i => i >= 0);
  if (matches.length > 1) throw new Error("Duplicate ID: " + id);
  if (matches.length) {
    const i = matches[0];
    const tail = parts[i].match(/\n*$/)[0];
    parts[i] = edit(parts[i].trimEnd()).trimEnd() + tail;
  } else {
    parts.splice(1, 0, edit(null).trimEnd() + "\n\n");
  }
  return { markdown: parts.join(""), added: !matches.length };
}

function singleLine(value, name) {
  if (typeof value !== "string" || !value.trim() || /[\r\n]/.test(value)) {
    throw new Error("A nonempty single-line " + name + " is required");
  }
  return value.trim();
}

function validateDate(value) {
  const date = new Date(value);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value) || !Number.isFinite(date.valueOf()) ||
      date.toISOString().slice(0, 10) !== value) throw new Error("Use a valid YYYY-MM-DD date");
}

function recordActivity(markdown, data, today) {
  const { id, date, title, kind, status, subject } = data;
  if (!/^event-[a-z0-9-]+$/.test(id ?? "")) throw new Error("Use an event- ID");
  validateDate(date);
  if (!["予定", "実施未確認", "実施済み", "中止"].includes(status)) throw new Error("Invalid activity status");
  if (status === "実施済み" && date > today) throw new Error("The event date is in the future");
  if (data.approved && status !== "実施済み") throw new Error("Publication requires completion");
  const result = updateRecord(markdown, "ID", id, (old) => {
    let block = (old ?? "## New\n\n- ID: " + id).replace(/^## .*/, () => "## " + singleLine(title, "title"));
    for (const [label, value] of [["日付", date], ["種別", kind], ["状況", status],
      ["掲載判定", data.approved ? "掲載可" : "要確認"], ["演題", subject]]) {
      if (value !== undefined) block = setField(block, label, singleLine(value, label));
    }
    return block;
  });
  return result.markdown
    .replace(/^更新日: \d{4}-\d{2}-\d{2}/m, "更新日: " + today)
    .replace(/^\d+(?=レコード。)/m, String(result.markdown.split(/^## /m).length - 1));
}

function projectActivity(privateMarkdown, publicMarkdown, id, today, options = {}) {
  if (!/^event-[a-z0-9-]+$/.test(id ?? "")) throw new Error("Use an event- ID");
  const matches = privateMarkdown.split(/(?=^## )/m).filter(block => fields(block, "ID") === id);
  if (matches.length !== 1) throw new Error("Expected exactly one private record for " + id);
  const block = matches[0];
  const date = fields(block, "日付");
  validateDate(date);
  if (date > today || fields(block, "状況") !== "実施済み" || fields(block, "掲載判定") !== "掲載可") {
    throw new Error("Only completed, approved activities on or before today can be published");
  }
  const title = singleLine(block.match(/^## (.*)$/m)?.[1], "title");
  const kind = singleLine(fields(block, "種別"), "kind");
  const subject = options.includeSubject ? singleLine(fields(block, "演題"), "subject") : null;
  return updateRecord(publicMarkdown, "id", id, (old) => {
    let next = "## " + title + "\n\n- id: " + id + "\n- date: " + date + "\n- kind: " + kind;
    const subtitle = subject ?? (old ? fields(old, "subtitle") : null);
    if (subtitle) next += "\n- subtitle: " + subtitle;
    const note = old ? fields(old, "note") : null;
    if (note) next += "\n- note: " + note;
    if (!options.news) next += "\n- omit_news: true";
    return next;
  }).markdown;
}

import { readFileSync, writeFileSync } from "node:fs";

const [command, ...args] = process.argv.slice(2);
const parts = new Intl.DateTimeFormat("en-CA", {
  timeZone: "Asia/Tokyo", year: "numeric", month: "2-digit", day: "2-digit"
}).formatToParts(new Date());
const part = (type) => parts.find(p => p.type === type).value;
const today = [part("year"), part("month"), part("day")].join("-");

try {
  if (command === "record" && args.length === 2) {
    const [privateFile, inputFile] = args;
    const data = JSON.parse(readFileSync(inputFile, "utf8"));
    const original = readFileSync(privateFile, "utf8");
    const updated = recordActivity(original, data, today);
    if (updated !== original) writeFileSync(privateFile, updated, "utf8");
  } else if (command === "project" && args.length >= 3 &&
      args.slice(3).every(arg => ["--news", "--include-subject"].includes(arg))) {
    const [privateFile, publicFile, id, ...flags] = args;
    const original = readFileSync(publicFile, "utf8");
    const updated = projectActivity(readFileSync(privateFile, "utf8"), original, id, today, {
      news: flags.includes("--news"),
      includeSubject: flags.includes("--include-subject")
    });
    if (updated !== original) writeFileSync(publicFile, updated, "utf8");
  } else {
    throw new Error(
      "Usage:\n  node portfolio/update-activity.mjs record PRIVATE.md INPUT.json\n" +
      "  node portfolio/update-activity.mjs project PRIVATE.md portfolio/content/activities.md EVENT_ID [--news] [--include-subject]"
    );
  }
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
