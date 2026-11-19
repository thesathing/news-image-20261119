// THE DAYBOOK — Thursday 19 November 2026: Three Powers, One Table.
// Entry program for make.fun bounty news-image-20261119.
//
// The front page itself (entry.png, next to this file) is the entry:
// 44 stories, 13 cards, drawn for Thursday 19 November 2026. This
// program does one job and does it carefully: it checks that the image
// is a whole, well-formed PNG of the right size, then writes it to the
// output folder the grader reads. It never touches the network and it
// never changes a byte, so running it twice writes identical bytes.
//
// Run it outside the grader's container with:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const PNG_MAGIC = Buffer.from([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
]);
const IEND_TAIL = Buffer.from([
  0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82,
]);
const MAX_BYTES = 1024 * 1024;
const WANT_WIDTH = 1024;
const WANT_HEIGHT = 1024;

function die(message) {
  throw new Error(`THE DAYBOOK entry: ${message}`);
}

function checkMagic(bytes) {
  if (bytes.length < 8 || !bytes.subarray(0, 8).equals(PNG_MAGIC)) {
    die("entry.png does not start with the PNG signature");
  }
}

function readSize(bytes) {
  // The IHDR chunk must follow the signature: 4-byte length at 8..12,
  // the letters "IHDR" at 12..16, then width and height as big-endian
  // 32-bit integers at 16..20 and 20..24.
  if (bytes.length < 33) {
    die("entry.png is too short to hold an IHDR chunk");
  }
  if (bytes.readUInt32BE(8) !== 13) {
    die("entry.png has an IHDR chunk of the wrong length");
  }
  if (bytes.toString("ascii", 12, 16) !== "IHDR") {
    die("entry.png has no IHDR chunk where one belongs");
  }
  return {
    width: bytes.readUInt32BE(16),
    height: bytes.readUInt32BE(20),
    bitDepth: bytes[24],
    colorType: bytes[25],
  };
}

function checkTail(bytes) {
  // A PNG is only whole when it ends with its IEND trailer. Without
  // this check a file cut short mid-write would still pass the header
  // checks above and hand the judge a broken image.
  if (
    bytes.length < IEND_TAIL.length ||
    !bytes.subarray(bytes.length - IEND_TAIL.length).equals(IEND_TAIL)
  ) {
    die("entry.png is truncated: its IEND trailer is missing");
  }
}

function sha256Hex(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

const here = fileURLToPath(new URL(".", import.meta.url));
const sourcePath = join(here, "entry.png");
const source = readFileSync(sourcePath);
const sizeOnDisk = statSync(sourcePath).size;

if (sizeOnDisk > MAX_BYTES) {
  die(`entry.png is ${sizeOnDisk} bytes, over the 1 MiB limit`);
}
if (source.length !== sizeOnDisk) {
  die("entry.png changed size while being read");
}

checkMagic(source);
const dims = readSize(source);
if (dims.width !== WANT_WIDTH || dims.height !== WANT_HEIGHT) {
  die(
    `entry.png is ${dims.width}x${dims.height}, ` +
      `expected ${WANT_WIDTH}x${WANT_HEIGHT}`,
  );
}
if (dims.bitDepth !== 8) {
  die(`entry.png has bit depth ${dims.bitDepth}, expected 8`);
}
if (dims.colorType !== 2) {
  die(`entry.png has color type ${dims.colorType}, expected 2 (truecolor)`);
}
checkTail(source);

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });
const outPath = join(outDir, "entry.png");
writeFileSync(outPath, source);

// The grader runs this program twice and both runs must write the same
// bytes, so read the copy back and compare it with the source byte
// for byte before declaring success.
const written = readFileSync(outPath);
if (!written.equals(source)) {
  die("the written entry.png differs from the source");
}

console.log(
  `wrote ${outPath} (${source.length} bytes, sha256 ${sha256Hex(source)})`,
);
