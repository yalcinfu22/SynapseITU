import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

const here = (p: string) => fileURLToPath(new URL(p, import.meta.url));

// Tests live in the repository's root tests/ folder (BLG411E guide), outside frontend/.
// Packages that the tests import are resolved from frontend/node_modules.
const fromFrontend = ["react", "react-dom", "@testing-library/react", "@testing-library/dom"];

export default defineConfig({
  resolve: {
    alias: [
      { find: "@", replacement: here("./src") },
      ...fromFrontend.map((name) => ({ find: name, replacement: here(`./node_modules/${name}`) })),
    ],
  },
  server: {
    fs: { allow: [here("..")] },
  },
  test: {
    environment: "jsdom",
    include: ["../tests/frontend/**/*.test.{ts,tsx}"],
  },
});
