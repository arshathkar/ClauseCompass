from typing import List

# Simplified ICS generator
def generate_ics(events: List[dict]) -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//ClauseCompass//EN"
    ]
    
    for ev in events:
        lines.append("BEGIN:VEVENT")
        lines.append(f"SUMMARY:{ev.get('summary', 'Event')}")
        lines.append(f"DTSTART:{ev.get('date', '')}") # Needs proper formatting in real usage
        lines.append("END:VEVENT")
        
    lines.append("END:VCALENDAR")
    return "\n".join(lines)
