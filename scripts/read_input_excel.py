import openpyxl
import json
import argparse

SHEET_APIS = "APIs"
SHEET_APPS = "Applications"
SHEET_CONTRACTS = "Contracts"

def read_sheet(ws):
 headers = [cell.value for cell in ws[1]]
 rows = []
 for row in ws.iter_rows(min_row=2, values_only=True):
    record = dict(zip(headers, row))
 if any(record.values()):
    rows.append(record)
 return rows

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--file", required=True)
 parser.add_argument("--output-apis", required=True)
 parser.add_argument("--output-apps", required=True)
 parser.add_argument("--output-contracts", required=True)
 args = parser.parse_args()

 wb = openpyxl.load_workbook(args.file)

 apis = read_sheet(wb[SHEET_APIS])
 apps = read_sheet(wb[SHEET_APPS])
 contracts = read_sheet(wb[SHEET_CONTRACTS])

 with open(args.output_apis, "w") as f:
    json.dump(apis, f, indent=2)
 with open(args.output_apps, "w") as f:
    json.dump(apps, f, indent=2)
 with open(args.output_contracts, "w") as f:
    json.dump(contracts, f, indent=2)

 print(f"✅ APIs: {len(apis)} | Apps: {len(apps)} | Contracts: {len(contracts)}")