import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import { defineConfig } from "eslint/config";

export default defineConfig([
  {
    ignores: ["node_modules/**", ".angular/**"],
  },
  {
    files: ["**/*.{js,mjs,cjs,ts,mts,cts}"],
    // files: ["src/**/*.ts"],
    ignores: ["node_modules/**", ".angular/**"],
    plugins: { js },
    extends: ["js/recommended"],
    languageOptions: { globals: globals.browser },
  },
  tseslint.configs.recommended,
]);
