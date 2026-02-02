"""
Quick test script for the updated time parser
"""
import pandas as pd

def parse_time(time_str):
    """
    Parse violation time in HH:mmA or HHmmA format
    Examples: '10:45A' -> '10:45', '1045A' -> '10:45', '02:30P' -> '14:30'
    """
    if pd.isnull(time_str):
        return None
    
    try:
        time_str = str(time_str).strip()
        
        # Extract AM/PM indicator
        if time_str[-1] in ['A', 'P', 'a', 'p']:
            meridiem = time_str[-1].upper()
            time_digits = time_str[:-1]
        else:
            # No AM/PM indicator - assume time is in 24hr format
            meridiem = None
            time_digits = time_str
        
        # Check if format has colon (HH:mm) or not (HHmm)
        if ':' in time_digits:
            # Format: HH:mm
            parts = time_digits.split(':')
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
        else:
            # Format: HHmm - pad with zeros if needed
            time_digits = time_digits.zfill(4)
            hours = int(time_digits[:2])
            minutes = int(time_digits[2:4])
        
        # Convert to 24-hour format if needed
        if meridiem == 'P' and hours != 12:
            hours += 12
        elif meridiem == 'A' and hours == 12:
            hours = 0
        
        return f"{hours:02d}:{minutes:02d}"
        
    except:
        return None

# Test cases
test_times = [
    '09:18A',  # Morning with colon
    '03:38A',  # Early morning with colon
    '11:38A',  # Late morning with colon
    '12:07P',  # Noon with colon
    '09:32A',  # Morning with colon
    '1045A',   # Morning without colon (legacy)
    '0230P',   # Afternoon without colon (legacy)
    '11:59P',  # Just before midnight
    '12:00A',  # Midnight
]

print("Testing time parser:")
print("-" * 40)
for time_str in test_times:
    result = parse_time(time_str)
    hour = int(result.split(':')[0]) if result else None
    print(f"{time_str:10s} -> {result:10s} (hour: {hour})")
