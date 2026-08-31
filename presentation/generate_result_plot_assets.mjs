import fs from "node:fs/promises";
import { createRequire } from "node:module";
const require = createRequire(import.meta.url);
const sharp = require("C:/Users/acer/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp");

const ROOT = "E:/Research/Thesis/thesis/presentation/images";
const data = [
  ["Static few-shot", .1451, .1001, .1897], ["RAG only", .1182, .0753, .1618],
  ["Neural loop", .2354, .1934, .2772], ["Symbolic loop", .1091, .0649, .1524],
  ["Neural + symbolic feedback", .2570, .2151, .2987], ["Intrinsic self-critique", .2147, .1711, .2584],
  ["External-role self-critique", .1804, .1381, .2231], ["Hosted judge loop", .1715, .1282, .2149],
  ["Blind resampling", .2087, .1664, .2510],
];

const esc = (s) => s.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");

function svgFigure(withLabels) {
  const width = withLabels ? 2600 : 1500;
  const height = 1040;
  const left = withLabels ? 610 : 120;
  const right = withLabels ? 1980 : width - 90;
  const plotW = right - left;
  const top = 100;
  const rowH = 88;
  const axisY = top + data.length * rowH + 18;
  const min = -.02, max = .32;
  const x = (v) => left + ((v - min) / (max - min)) * plotW;
  const ticks = [0, .05, .10, .15, .20, .25, .30];
  const parts = [`<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">`,
    `<style>text{font-family:Aptos,Arial,sans-serif}.label{font-size:36px;fill:#263A52}.value{font-size:32px;fill:#263A52}.tick{font-size:28px;fill:#64748B}.zero{font-size:25px;font-weight:700;fill:#4B5563}.head{font-family:Arial,sans-serif;font-size:34px;font-weight:900;fill:#243B57;stroke:#243B57;stroke-width:.45px;letter-spacing:.35px}</style>`];

  if (withLabels) {
    parts.push(`<text class="head" x="38" y="50">CONDITION</text>`);
    parts.push(`<text class="head" x="${(left + right) / 2}" y="50" text-anchor="middle">PAIRED EFFECT WITH 95% CI</text>`);
    parts.push(`<text class="head" x="2280" y="50" text-anchor="middle">Δ (95% CI)</text>`);
  }

  for (const t of ticks) {
    const tx = x(t), zero = t === 0;
    parts.push(`<line x1="${tx}" y1="72" x2="${tx}" y2="${axisY}" stroke="${zero ? "#667085" : "#DCE5ED"}" stroke-width="${zero ? 4 : 2}"/>`);
    parts.push(`<text class="tick" x="${tx}" y="${axisY + 48}" text-anchor="middle">${t.toFixed(2)}</text>`);
  }
  parts.push(`<text class="zero" x="${x(0)}" y="50" text-anchor="middle">Δ = 0</text>`);

  data.forEach(([label, estimate, low, high], i) => {
    const cy = top + i * rowH + 30;
    const highlight = label === "Neural + symbolic feedback";
    const color = highlight ? "#0B6AA8" : "#55768E";
    if (highlight) parts.push(`<rect x="${withLabels ? 18 : left - 24}" y="${cy - 34}" width="${withLabels ? width - 36 : plotW + 48}" height="68" rx="16" fill="#DCECF7" fill-opacity="0.72"/>`);
    if (withLabels) {
      parts.push(`<text class="label" x="38" y="${cy + 10}" font-weight="${highlight ? 700 : 400}">${esc(label)}</text>`);
      parts.push(`<text class="value" x="2280" y="${cy + 10}" text-anchor="middle" font-weight="${highlight ? 700 : 400}">${estimate.toFixed(3)} [${low.toFixed(3)}, ${high.toFixed(3)}]</text>`);
    }
    parts.push(`<line x1="${x(low)}" y1="${cy}" x2="${x(high)}" y2="${cy}" stroke="${color}" stroke-width="6"/>`);
    parts.push(`<line x1="${x(low)}" y1="${cy - 17}" x2="${x(low)}" y2="${cy + 17}" stroke="${color}" stroke-width="5"/>`);
    parts.push(`<line x1="${x(high)}" y1="${cy - 17}" x2="${x(high)}" y2="${cy + 17}" stroke="${color}" stroke-width="5"/>`);
    parts.push(`<circle cx="${x(estimate)}" cy="${cy}" r="12" fill="${color}" stroke="#FFFFFF" stroke-width="3"/>`);
  });
  parts.push(`<line x1="${left}" y1="${axisY}" x2="${right}" y2="${axisY}" stroke="#667085" stroke-width="3"/>`);
  parts.push(`<text x="${(left + right) / 2}" y="${height - 20}" text-anchor="middle" font-family="Aptos,Arial,sans-serif" font-size="32" fill="#263A52">Paired change in Verifier-B target probability relative to zero-shot</text>`);
  parts.push(`</svg>`);
  return parts.join("");
}

async function save(stem, withLabels) {
  const svg = svgFigure(withLabels);
  const svgPath = `${ROOT}/${stem}.svg`;
  const pngPath = `${ROOT}/${stem}.png`;
  await fs.writeFile(svgPath, svg, "utf8");
  await sharp(Buffer.from(svg)).resize({ width: withLabels ? 5200 : 3000 }).png().toFile(pngPath);
}

await fs.mkdir(ROOT, { recursive: true });
await save("experimental_results_plot_only_transparent", false);
await save("experimental_results_plot_with_labels_transparent", true);
