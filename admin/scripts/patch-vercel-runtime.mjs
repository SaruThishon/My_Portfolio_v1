/**
 * Postbuild script: patches the Vercel function runtime to nodejs22.x
 *
 * @astrojs/vercel v7 only knows about Node 18/20 in its SUPPORTED_NODE_VERSIONS
 * map. When the build machine runs Node 26 it falls back to nodejs18.x, which
 * Vercel now rejects as discontinued. This script overwrites that value after
 * the adapter writes the config.
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';

const CONFIG_PATH = '.vercel/output/functions/_render.func/.vc-config.json';

if (!existsSync(CONFIG_PATH)) {
  console.error(`✗ vc-config not found at: ${CONFIG_PATH}`);
  process.exit(1);
}

const config = JSON.parse(readFileSync(CONFIG_PATH, 'utf8'));
const before = config.runtime;
config.runtime = 'nodejs22.x';
writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
console.log(`✓ Patched Vercel function runtime: ${before} → nodejs22.x`);
