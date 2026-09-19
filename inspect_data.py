import pandas as pd
import json
import sys

file_path = r'c:\Proyectos IA Antigravity\4.- sitios-webs\maestro-valencia\dashboard-power-bi\info-ejemplo1\Estadísticas PIRMCT 2025.xlsx'

try:
    xl = pd.ExcelFile(file_path)
    output = {"sheet_names": xl.sheet_names, "sheets": {}}
    for sheet in xl.sheet_names[:3]: # limit to 3 sheets for summary
        df = xl.parse(sheet, nrows=0)
        output["sheets"][sheet] = {
            "columns": list(map(str, df.columns))
        }
    print(json.dumps(output, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
