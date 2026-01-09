from ...schema import Reference
from .base import BaseMermaidConverter


class ReferenceConverter(BaseMermaidConverter[Reference]):
    def convert(self, node: Reference) -> str:
        # Mermaid syntax: Entity1 }|..|| Entity2 : label

        # Determine cardinality
        # DBML:
        # < : one-to-many (Left is one, Right is many) -> ||--o{
        # > : many-to-one (Left is many, Right is one) -> }o--||
        # - : one-to-one -> ||--||
        # <> : many-to-many -> }o--o{

        # Note: Mermaid has identifying and non-identifying relationships (solid vs dotted).
        # DBML doesn't explicitly distinguish. Let's use non-identifying (..) as default or solid (--).
        # DBML references are usually FKs, which implies dependency?
        # Let's use -- (solid) for now as it looks cleaner.

        relation_map = {
            "<": "||--o{",
            ">": "}o--||",
            "-": "||--||",
            "<>": "}o--o{",
        }

        # Default to one-to-many if unknown? Or just use --
        symbol = relation_map.get(node.relationship, "--")

        # Left side
        table1 = node.from_table.name
        if node.from_table.db_schema:
            table1 = f'"{node.from_table.db_schema}.{node.from_table.name}"'

        # Right side
        table2 = node.to_table.name
        if node.to_table.db_schema:
            table2 = f'"{node.to_table.db_schema}.{node.to_table.name}"'

        # Build string
        # table1 symbol table2 : label

        parts = [table1, symbol, table2]

        # Optional label (using column names)
        # DBML references are on columns. Mermaid references are between tables.
        # We can add the column names as the label.

        from_cols = node.from_columns
        to_cols = node.to_columns

        col1 = from_cols[0] if isinstance(from_cols, list) else from_cols
        col2 = to_cols[0] if isinstance(to_cols, list) else to_cols

        # If composite key, join with comma
        if isinstance(from_cols, list) and len(from_cols) > 1:
            col1 = ",".join(from_cols)
        if isinstance(to_cols, list) and len(to_cols) > 1:
            col2 = ",".join(to_cols)

        label = f'"{col1} - {col2}"'
        parts.append(":")
        parts.append(label)

        return " ".join(parts)
