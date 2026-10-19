import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
    include: ["tests/whitebox/**/*.test.ts"],
    coverage: {
      provider: "v8",
      include: ["lib/hskData.ts", "lib/dateKey.ts"],
      reporter: ["text", "html", "json-summary"],
      reportsDirectory: "./coverage-whitebox",
    },
  },
});
