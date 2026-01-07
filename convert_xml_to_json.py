import xml.etree.ElementTree as ET
import json

# Parse the XML file
tree = ET.parse('d:\\OMRGBMK\\DEsktop\\municipalities_sorted.xml')
root = tree.getroot()

# Find the worksheet
worksheet = root.find('.//{urn:schemas-microsoft-com:office:spreadsheet}Worksheet')

# Find the table
table = worksheet.find('.//{urn:schemas-microsoft-com:office:spreadsheet}Table')

# Extract rows
municipalities = []
for row in table.findall('.//{urn:schemas-microsoft-com:office:spreadsheet}Row'):
    cells = row.findall('.//{urn:schemas-microsoft-com:office:spreadsheet}Cell')
    if len(cells) >= 3:
        municipality = cells[0].find('.//{urn:schemas-microsoft-com:office:spreadsheet}Data').text
        district = cells[1].find('.//{urn:schemas-microsoft-com:office:spreadsheet}Data').text
        province = cells[2].find('.//{urn:schemas-microsoft-com:office:spreadsheet}Data').text
        municipalities.append({
            'name': municipality,
            'district': district,
            'province': province
        })

# Write to JSON
with open('d:\\OMRGBMK\\OMRGBMK-NP\\assets\\data\\municipalities.json', 'w', encoding='utf-8') as f:
    json.dump(municipalities, f, ensure_ascii=False, indent=2)

print(f'Converted {len(municipalities)} municipalities to JSON.')