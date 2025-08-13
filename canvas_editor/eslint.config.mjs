import { defineConfig } from "eslint/config";
import js from "@eslint/js";
import jsdoc from "eslint-plugin-jsdoc";

export default defineConfig([
  js.configs.recommended,
  jsdoc.configs["flat/recommended"],
  {
    rules: {
      "jsdoc/require-jsdoc": [
        "warn",
        {
          require: {
            FunctionDeclaration: true,
            MethodDefinition: true,
            ClassDeclaration: true,
            ArrowFunctionExpression: true,
            FunctionExpression: true,
          },
        },
      ],
    },
  },
]);
