import csv
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

# --- Configuration ---
NUM_CLIENTS = 50
NUM_CAMPAIGNS_PER_CLIENT = 5
NUM_LEADS_PER_CAMPAIGN = 100

# --- Data Storage (in-memory) ---
clients = []
campaigns = []
leads = []
opportunities = []
deals = []

# --- Data Generation Functions ---

def create_clients():
    for i in range(1, NUM_CLIENTS + 1):
        clients.append({
            'client_id': i,
            'client_name': fake.company(),
            'industry': 'Life Sciences',
            'created_at': fake.date_time_this_decade()
        })

def create_campaigns():
    for client in clients:
        for i in range(1, NUM_CAMPAIGNS_PER_CLIENT + 1):
            campaigns.append({
                'campaign_id': len(campaigns) + 1,
                'campaign_name': f'{client["client_name"]} Campaign {i}',
                'client_id': client['client_id'],
                'start_date': fake.date_time_this_year(),
                'end_date': fake.date_time_this_year() + timedelta(days=random.randint(30, 90)),
                'budget': random.randint(10000, 100000)
            })

def create_leads_opportunities_deals():
    for campaign in campaigns:
        for i in range(1, NUM_LEADS_PER_CAMPAIGN + 1):
            lead_id = len(leads) + 1
            leads.append({
                'lead_id': lead_id,
                'campaign_id': campaign['campaign_id'],
                'lead_name': fake.name(),
                'lead_email': fake.email(),
                'created_at': fake.date_time_between(start_date=campaign['start_date'], end_date=campaign['end_date'])
            })

            # Create opportunity from lead
            if random.random() < 0.5: # 50% of leads become opportunities
                opportunity_id = len(opportunities) + 1
                opportunities.append({
                    'opportunity_id': opportunity_id,
                    'lead_id': lead_id,
                    'opportunity_name': f'Opportunity for {leads[-1]["lead_name"]}',
                    'status': random.choice(['Open', 'Closed Won', 'Closed Lost']),
                    'created_at': leads[-1]['created_at'] + timedelta(days=random.randint(1, 10))
                })

                # Create deal from opportunity
                if opportunities[-1]['status'] == 'Closed Won':
                    deals.append({
                        'deal_id': len(deals) + 1,
                        'opportunity_id': opportunity_id,
                        'deal_name': f'Deal with {leads[-1]["lead_name"]}',
                        'amount': random.randint(5000, 50000),
                        'closed_at': opportunities[-1]['created_at'] + timedelta(days=random.randint(1, 20))
                    })

def write_to_csv():
    """Writes all generated data to CSV files."""
    data_map = {
        'clients.csv': clients,
        'campaigns.csv': campaigns,
        'leads.csv': leads,
        'opportunities.csv': opportunities,
        'deals.csv': deals
    }

    for filename, data in data_map.items():
        if not data:
            print(f"Warning: No data for {filename}")
            continue
        with open(filename, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=data[0].keys(), quoting=csv.QUOTE_ALL)
            dict_writer.writeheader()
            dict_writer.writerows(data)
    print("CSV files generated successfully.")


if __name__ == '__main__':
    print("Starting synthetic data generation for Klick Health...")
    create_clients()
    create_campaigns()
    create_leads_opportunities_deals()
    write_to_csv()
    print("Synthetic data generation complete.")