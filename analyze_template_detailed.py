import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from docx import Document

doc = Document('docs/docx-templates/Приложение Ж (этикетки).docx')

table = doc.tables[0]
print("=== DETAILED TABLE CONTENT ===\n")

for row_idx, row in enumerate(table.rows):
    print(f"=== ROW {row_idx} ===")
    for cell_idx, cell in enumerate(row.cells):
        text = cell.text.strip()
        if text and len(text) > 5:  # Only non-empty cells
            print(f"  Cell [{row_idx},{cell_idx}]:")
            print(f"    {text[:200]}")
            print()
