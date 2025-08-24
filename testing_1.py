import csv

# Define the filename
filename = 'spiders.csv'

# Define the column headers
headers = [
    'spider_id',
    'spider_name',
    'spider_type',
    'weight',
    'major_dimension_mm',
    'secondary_dimension_mm',
    'width_mm',
    'height_mm',
    'attachment_sites_each_side',
    'attachment_distance',
    'central_square_length_mm',
    'central_square_height_mm'
]

# Define the data row
row = [
    '001',
    'SPIDER FOR BIG M/C',
    '4-way',
    20,
    3100,
    650,
    250,
    100,
    14,
    100,
    350,
    100
]

# Write the CSV file
with open(filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(headers)
    writer.writerow(row)

print(f"CSV file '{filename}' created successfully.")
