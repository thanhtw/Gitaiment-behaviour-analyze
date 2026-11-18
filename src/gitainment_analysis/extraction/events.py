"""Source extraction used by the retained analysis pipeline."""
import pandas as pd

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


def events_to_dataframe(events):
    """Convert events list to pandas DataFrame"""
    df = pd.DataFrame(events)
    # Convert eventTime to datetime
    df['eventTime'] = pd.to_datetime(df['eventTime'])
    return df
