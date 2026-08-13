import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import {
  ConfigError,
  type ResolvedConfig,
  validateConfig,
} from "./schema.js";

export async function loadConfig(path: string): Promise<ResolvedConfig> {
  const configPath = resolve(path);
  const raw = await readFile(configPath, "utf8");
  const config = validateConfig(parseJson(raw, configPath));
  const configDirectory = dirname(configPath);

  return {
    ...config,
    configPath,
    characterPath: resolve(configDirectory, config.character),
    outputPath: resolve(configDirectory, config.output.path),
  };
}

function parseJson(raw: string, path: string): unknown {
  try {
    return JSON.parse(raw) as unknown;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new ConfigError(`${path}: invalid JSON: ${message}`);
  }
}
