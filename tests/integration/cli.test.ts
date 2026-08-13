import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { runCli } from "../../src/cli.js";

const temporaryDirectories: string[] = [];

afterEach(async () => {
  await Promise.all(
    temporaryDirectories.splice(0).map((directory) =>
      rm(directory, { force: true, recursive: true }),
    ),
  );
});

describe("runCli", () => {
  it("generates from a fixture and prints the output path", async () => {
    const directory = await mkdtemp(join(tmpdir(), "ube-cli-"));
    temporaryDirectories.push(directory);
    const output: string[] = [];
    const errors: string[] = [];
    const outputPath = join(directory, "ube.gif");

    const exitCode = await runCli(
      [
        "generate",
        "--config",
        resolve("ube.config.json"),
        "--fixture",
        resolve("tests/fixtures/calendar.json"),
        "--output",
        outputPath,
      ],
      {
        env: {},
        writeOut: (message) => output.push(message),
        writeError: (message) => errors.push(message),
      },
    );

    expect(exitCode).toBe(0);
    expect(output).toEqual([
      `Generated 120 frames at ${outputPath} (960x320)`,
    ]);
    expect(errors).toEqual([]);
  }, 30_000);

  it("requires a token outside fixture mode", async () => {
    const errors: string[] = [];

    const exitCode = await runCli(
      ["generate", "--config", resolve("ube.config.json")],
      {
        env: { GITHUB_TOKEN: "" },
        writeOut: () => undefined,
        writeError: (message) => errors.push(message),
      },
    );

    expect(exitCode).toBe(1);
    expect(errors).toEqual([
      "GITHUB_TOKEN is required unless --fixture is used",
    ]);
  });
});
