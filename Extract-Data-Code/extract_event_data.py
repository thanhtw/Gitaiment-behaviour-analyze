import json
import pandas as pd
from datetime import datetime
from collections import Counter

# Load the JSON data
def load_event_data(filepath):
    """Load event data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# Extract and flatten the data
def extract_events(data):
    """Extract relevant fields from event data"""
    events = []
    for record in data:
        event = {
            'id': record.get('_id', {}).get('$oid', ''),
            'player': record.get('player', ''),
            'eventName': record.get('eventName', ''),
            'eventDetail': record.get('eventDetail', ''),
            'gameScene': record.get('gameScene', ''),
            'eventTime': record.get('eventTime', {}).get('$date'),
            'version': record.get('__v', 0)
        }
        events.append(event)
    return events

# Convert to DataFrame
def events_to_dataframe(events):
    """Convert events list to pandas DataFrame"""
    df = pd.DataFrame(events)
    # Convert eventTime to datetime
    df['eventTime'] = pd.to_datetime(df['eventTime'])
    return df

# Analysis functions
def get_summary_statistics(df):
    """Get summary statistics of the event data"""
    print("=" * 50)
    print("EVENT DATA SUMMARY")
    print("=" * 50)
    print(f"\nTotal number of events: {len(df)}")
    print(f"Unique players: {df['player'].nunique()}")
    print(f"Unique event types: {df['eventName'].nunique()}")
    print(f"Unique game scenes: {df['gameScene'].nunique()}")
    print(f"\nDate range: {df['eventTime'].min()} to {df['eventTime'].max()}")
    
    print("\n" + "-" * 50)
    print("EVENT TYPES DISTRIBUTION:")
    print("-" * 50)
    event_counts = df['eventName'].value_counts()
    print(event_counts)
    
    print("\n" + "-" * 50)
    print("TOP 10 PLAYERS BY EVENT COUNT:")
    print("-" * 50)
    player_counts = df['player'].value_counts().head(10)
    print(player_counts)
    
    print("\n" + "-" * 50)
    print("GAME SCENES DISTRIBUTION:")
    print("-" * 50)
    scene_counts = df['gameScene'].value_counts()
    print(scene_counts)
    
    return event_counts, player_counts, scene_counts

def filter_by_player(df, player_name):
    """Filter events by player name"""
    return df[df['player'] == player_name]

def filter_by_event(df, event_name):
    """Filter events by event name"""
    return df[df['eventName'] == event_name]

def filter_by_date_range(df, start_date, end_date):
    """Filter events by date range"""
    mask = (df['eventTime'] >= start_date) & (df['eventTime'] <= end_date)
    return df[mask]

def export_to_csv(df, output_path):
    """Export DataFrame to CSV"""
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Data exported to {output_path}")

# Main execution
if __name__ == "__main__":
    # File path
    filepath = r"d:\02_Submission_Papper\10_GiTaiment\陳子淵\陳子淵\01_EventData\GEG-database.eventdatas.json"
    
    # Load data
    print("Loading data...")
    data = load_event_data(filepath)
    print(f"Loaded {len(data)} records")
    
    # Extract events
    events = extract_events(data)
    
    # Convert to DataFrame
    df = events_to_dataframe(events)
    
    # Display summary statistics
    get_summary_statistics(df)
    
    # Show first few records
    print("\n" + "=" * 50)
    print("SAMPLE DATA (First 10 rows):")
    print("=" * 50)
    print(df.head(10).to_string())
    
    # Export to CSV (optional)
    output_csv = r"d:\02_Submission_Papper\10_GiTaiment\陳子淵\陳子淵\01_EventData\extracted_events.csv"
    export_to_csv(df, output_csv)
    
    # Example: Filter by specific event type
    print("\n" + "=" * 50)
    print("LOGIN EVENTS SUMMARY:")
    print("=" * 50)
    login_events = filter_by_event(df, 'Login')
    print(f"Total login events: {len(login_events)}")
    print(f"Unique users who logged in: {login_events['player'].nunique()}")
