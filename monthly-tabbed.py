#!/usr/bin/env python3

import sys
import json
from datetime import datetime, timedelta
from collections import defaultdict

def merge_intervals(intervals):
    if not intervals:
        return []
    
    merged = []
    current_start, current_end = intervals[0]
    
    for start, end in intervals[1:]:
        # If intervals are consecutive or overlapping, merge them
        if start <= current_end:
            current_end = max(current_end, end)
        else:
            # Gap found, save current and start new group
            merged.append((current_start, current_end))
            current_start, current_end = start, end
    
    merged.append((current_start, current_end))
    return merged

def main():
    # Read input from Timewarrior
    input_data = sys.stdin.read()
    
    # Split into configuration and JSON data
    lines = input_data.strip().split('\n')
    
    # Find where JSON starts (after blank line)
    json_start = 0
    for i, line in enumerate(lines):
        if line == '':
            json_start = i + 1
            break
    
    # Parse JSON data
    json_data = '\n'.join(lines[json_start:])
    if not json_data:
        data = []
    else:
        data = json.loads(json_data)
    
    # Get configuration (month and tag from the lines before JSON)
    config = {}
    for line in lines[:json_start]:
        if ':' in line:
            key, value = line.split(':', 1)
            config[key.strip()] = value.strip()
    
    # Check for temp.report.start and temp.report.end in config
    if 'temp.report.start' not in config or 'temp.report.end' not in config:
        print("Error: No date range specified", file=sys.stderr)
        print("Usage: timew monthly TAG :month", file=sys.stderr)
        sys.exit(1)
    
    start_date = datetime.fromisoformat(config['temp.report.start'].replace('Z', '+00:00')).date()
    end_date = datetime.fromisoformat(config['temp.report.end'].replace('Z', '+00:00')).date()
    
    # Parse and group by date
    intervals_by_date = defaultdict(list)
    
    for item in data:
        start_str = item.get('start', '')
        end_str = item.get('end', '')
        
        if not start_str or not end_str:
            continue
        
        start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
        
        # Convert to local time
        start_local = start.astimezone()
        end_local = end.astimezone()
        
        date_key = start_local.date()
        intervals_by_date[date_key].append((start_local, end_local))
    
    # Sort intervals within each day
    for date_key in intervals_by_date:
        intervals_by_date[date_key].sort()
    
    # Generate all days in the date range
    current_date = start_date
    while current_date < end_date:
        if current_date in intervals_by_date:
            merged = merge_intervals(intervals_by_date[current_date])
            row = []
            for start, end in merged:
                row.append(start.strftime('%H:%M'))
                row.append(end.strftime('%H:%M'))
            print('\t'.join(row))
        else:
            print('')  # Empty line for days with no tasks
        
        current_date += timedelta(days=1)

if __name__ == '__main__':
    main()
