import pandas as pd
import random
from faker import Faker

# Initialize Faker
fake = Faker()

# Define meaningful file titles and locations
file_titles_and_locations = [
    ('Team Meeting Notes', 'team/meetings'),
    ('Product Roadmap', 'product/development'),
    ('Feature Specs', 'product/features'),
    ('Competitor Analysis', 'product/competitors'),
    ('Quarterly Report', 'finance/reports'),
    ('Sprint Planning', 'engineering/sprints'),
    ('Client Feedback', 'customer/feedback'),
    ('Sales Report', 'sales/reports'),
    ('Marketing Strategy', 'marketing/strategies'),
    ('Customer Call Notes', 'customer/calls')
]

# Define available sources
sources = ['google_drive', 'avoma', 'web']

# Generate 500 rows of data
data = []
for _ in range(500):
    # Randomly select a title and corresponding location
    file_title, file_location = random.choice(file_titles_and_locations)
    
    # Generate random file size and type
    file_size = random.randint(500000, 5000000)
    file_type = random.choice(['pdf', 'docx', 'xlsx', 'pptx'])
    
    # Create random file creation and update times
    file_created_at = fake.date_time_this_year()
    file_last_updated_at = file_created_at if random.random() > 0.5 else fake.date_time_this_year()
    
    # Create random file URL
    file_url = f"http://example.com/files/{file_title.replace(' ', '_').lower()}.{file_type}"
    
    # Generate data for each row
    row = {
        'author': fake.name(),
        'source': random.choice(sources),
        'file_title': file_title,
        'file_size': file_size,
        'file_type': file_type,
        'file_location_at_source': file_location,
        'file_created_at': file_created_at,
        'file_last_updated_at': file_last_updated_at,
        'file_url': file_url
    }
    data.append(row)

# Convert to DataFrame
df = pd.DataFrame(data)

# Display the first few rows of the generated DataFrame
print(df.head())
df.to_csv("/Users/arjun-14756/Desktop/Advanced-File-Search/data/file_info.csv", index=False)