<!-- insertion marker -->
## [v0.7.0](https://github.com/daihuynh/lark-dbml/releases/tag/v0.7.0) - 2026-01-09

<small>[Compare with v0.6.0](https://github.com/daihuynh/lark-dbml/compare/v0.6.0...v0.7.0)</small>

### Features

- **Mermaid Converter**: Added support for converting DBML to Mermaid diagrams.
- **SQL Parsing**: Added support for parsing SQL DDL statements into DBML models (`from_sql`). This allows for round-trip conversion (SQL -> DBML -> SQL).
- **Check Constraints**: Added support for Check constraints.

### Improvements

- **Test Coverage**: Significantly improved test coverage for SQL converter.

## [v0.6.0](https://github.com/daihuynh/lark-dbml/releases/tag/v0.6.0) - 2025-08-08

<small>[Compare with v0.5.1](https://github.com/daihuynh/lark-dbml/compare/v0.5.1...v0.6.0)</small>

### Features

- LALR(1) algorithm is available.
- Standalone is supported.

## [v0.5.1](https://github.com/daihuynh/lark-dbml/releases/tag/v0.5.1) - 2025-08-01

<small>[Compare with v0.5.0](https://github.com/daihuynh/lark-dbml/compare/v0.5.0...v0.5.1)</small>

### Code Refactoring
- relax validation rules for index types by in [#14](https://github.com/daihuynh/lark-dbml/pull/14)

### New Contributors
- [@skarndev](https://github.com/skarndev) made their first contribution in [#14](https://github.com/daihuynh/lark-dbml/pull/14)


## [v0.5.0](https://github.com/daihuynh/lark-dbml/releases/tag/v0.5.0) - 2025-07-29

<small>[Compare with v0.4.0](https://github.com/daihuynh/lark-dbml/compare/v0.4.0...v0.5.0)</small>

### Features

- Data Contract conversion.
- EBNF Grammar update. DBML keywords are now case insensitive. Right recursions are changed to left recursions as recommended by Lark ([1640651](https://github.com/daihuynh/lark-dbml/commit/164065113175b809b22a09ad1aa9ba52fc12ea0f) by Austin Huynh).

### Bug Fixes

- true and false literals are assigned to true and false aliases. The orders of true and false literals are rearranged ([a4cf5ac](https://github.com/daihuynh/lark-dbml/commit/a4cf5ac26787e8ef608130b5522ff99e65069af8) by Austin Huynh).

### Code Refactoring

- remove lark-dbml version ([56cd1ae](https://github.com/daihuynh/lark-dbml/commit/56cd1aeaec13a0a08c74fea3c8cfe74e189b5e78) by Austin Huynh).
- dynamic package version ([92390a7](https://github.com/daihuynh/lark-dbml/commit/92390a71daa9b1899d23f4eebcb54819499a70bf) by Austin Huynh).

## [v0.4.0](https://github.com/daihuynh/lark-dbml/releases/tag/v0.4.0) - 2025-07-18

<small>[Compare with v0.3.0](https://github.com/daihuynh/lark-dbml/compare/v0.3.0...v0.4.0)</small>

### Features

- add dump and dumps function for lark_dbml ([1bd5480](https://github.com/daihuynh/lark-dbml/commit/1bd54808daeb91b2d84f8d454c194d1590ce465a) by Austin Huynh).
- table_partial_orders for Table model. This property helps to preserve the order of table partials in the table definition. Without it, the result will see the table partials either in front of columns or behind of columns ([b95a7fb](https://github.com/daihuynh/lark-dbml/commit/b95a7fb450548df46d30379efaa3923a94c6a45c) by Austin Huynh).
- Pydantic to DBML converter ([b5a3028](https://github.com/daihuynh/lark-dbml/commit/b5a3028882fc3d3521ec4e7a56573c4896f78bc4) by Austin Huynh).

### Bug Fixes

- column type was not fully implemented ([70142f7](https://github.com/daihuynh/lark-dbml/commit/70142f70cd5d4f9dfc013e49b51d57f0c2441a06) by Austin Huynh).

### Code Refactoring

- DBMLConverterSettings ([8b36256](https://github.com/daihuynh/lark-dbml/commit/8b36256943e1171364d7049cd925ea2141c59fa6) by Austin Huynh).
- add __all__ ([b650a3e](https://github.com/daihuynh/lark-dbml/commit/b650a3e85ef3a0860fe9491320db6cdd7bdd0b6f) by Austin Huynh).

## [v0.3.0](https://github.com/daihuynh/lark-dbml/releases/tag/v0.3.0) - 2025-07-12

<small>[Compare with v0.2.0](https://github.com/daihuynh/lark-dbml/compare/v0.2.0...v0.3.0)</small>

### Features

- v0.3.0 ([7563265](https://github.com/daihuynh/lark-dbml/commit/75632650100ce454e93ab78327aff46ec77ff17b) by Austin Huynh).
- Add sqlglot for SQL converter as an optional dependency ([59c0070](https://github.com/daihuynh/lark-dbml/commit/59c0070d9a4fa9d5d1a939c2748953c7828320b7) by Austin Huynh).
- SQL Converter ([3496a82](https://github.com/daihuynh/lark-dbml/commit/3496a826ceca8eeafaee77aae03703f51832c8a0) by Austin Huynh).
- add unit testing pipeline ([85d0da5](https://github.com/daihuynh/lark-dbml/commit/85d0da593c2ba28cc04fe9edbed38992fe1aad31) by Austin Huynh).

### Bug Fixes

- Referenced column allow quoted string values ([f2af26d](https://github.com/daihuynh/lark-dbml/commit/f2af26d0f8c17fd21e1161de71b627b0ac688510) by Austin Huynh).
- multiple column ref supports string type too ([2d76da9](https://github.com/daihuynh/lark-dbml/commit/2d76da936c1bd30992be60795a0663a178c0714f) by Austin Huynh).

### Code Refactoring

- pre-commit should not fix end of file for SQL files in expectation folder ([30c92f2](https://github.com/daihuynh/lark-dbml/commit/30c92f28482abbab9332f9abcc4b10c325274a5f) by Austin Huynh).
- move dbml files from mock to examples folder in the project root ([ea08dea](https://github.com/daihuynh/lark-dbml/commit/ea08deaa35c094398faf3053cc890c84cf5cde08) by Austin Huynh).



<a name="v0.2.0"></a>

## [v0.2.0](https://github.com/daihuynh/lark-dbml/compare/v0.1.1...v0.2.0) (2025-07-01)

### Added
-  ([133880e](https://github.com/daihuynh/lark-dbml/commit/133880e05b56600b8cac6063f6b7be21f71fcac1))

### Fixed

-  ([9510b9e](https://github.com/daihuynh/lark-dbml/commit/9510b9e29a97e1f6d8b71ccfd0ce10712c626d9f))
-  ([0c9d3ac](https://github.com/daihuynh/lark-dbml/commit/0c9d3ac5ee99cf499ef1e491ac7a1d951af10469))

<a name="v0.1.1"></a>

## [v0.1.1](https://github.com/daihuynh/lark-dbml/compare/v0.1.0...v0.1.1) (2025-06-30)

<a name="v0.1.0"></a>

## [v0.1.0](https://github.com/daihuynh/lark-dbml/compare/7551b9fc12e2fc49cc7eaf613bb083655d52347a...v0.1.0) (2025-06-30)
