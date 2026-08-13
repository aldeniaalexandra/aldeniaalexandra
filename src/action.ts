import { appendFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import { resolve } from "node:path";
import {
  generate,
  type GenerateOptions,
  type GenerateResult,
} from "./generate.js";

export interface ActionRuntime {
  env: NodeJS.ProcessEnv;
  appendOutput(path: string, data: string): Promise<void>;
  generateImpl(options: GenerateOptions): Promise<GenerateResult>;
  writeError(message: string): void;
}

const DEFAULT_RUNTIME: ActionRuntime = {
  env: process.env,
  appendOutput: appendFile,
  generateImpl: generate,
  writeError: (message) => console.error(message),
};

export async function runAction(
  runtime: ActionRuntime = DEFAULT_RUNTIME,
): Promise<number> {
  try {
    const configPath = readInput(runtime.env, "INPUT_CONFIG") || "ube.config.json";
    const token = readInput(runtime.env, "INPUT_TOKEN") || runtime.env.GITHUB_TOKEN;
    const outputPath = readInput(runtime.env, "INPUT_OUTPUT");
    const githubOutput = runtime.env.GITHUB_OUTPUT;
    if (githubOutput === undefined || githubOutput.trim().length === 0) {
      throw new Error("GITHUB_OUTPUT is unavailable");
    }

    const result = await runtime.generateImpl({
      configPath,
      ...(token ? { token } : {}),
      ...(outputPath ? { outputPath } : {}),
    });
    await runtime.appendOutput(
      githubOutput,
      `path=${escapeEnvironmentValue(result.path)}\n`,
    );
    return 0;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    runtime.writeError(`::error::${escapeWorkflowCommand(message)}`);
    return 1;
  }
}

function readInput(env: NodeJS.ProcessEnv, name: string): string {
  return env[name]?.trim() ?? "";
}

function escapeEnvironmentValue(value: string): string {
  return value.replaceAll("%", "%25").replaceAll("\r", "%0D").replaceAll("\n", "%0A");
}

function escapeWorkflowCommand(value: string): string {
  return escapeEnvironmentValue(value).replaceAll(":", "%3A").replaceAll(",", "%2C");
}

const entryPath = process.argv[1];
if (entryPath !== undefined && import.meta.url === pathToFileURL(resolve(entryPath)).href) {
  process.exitCode = await runAction();
}
