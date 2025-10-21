#!/usr/bin/env python3
"""
VoiceStudio VRAM Chart Generator
Generates PNG charts from VRAM telemetry CSV data
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
import sys

def generate_vram_chart(csv_path, output_path):
    """Generate VRAM usage chart from CSV data"""
    if not os.path.exists(csv_path):
        print(f"VRAM telemetry CSV not found: {csv_path}")
        return False
    
    try:
        # Read CSV data
        df = pd.read_csv(csv_path)
        df['time_utc'] = pd.to_datetime(df['time_utc'])
        
        # Create chart
        plt.figure(figsize=(14, 8))
        
        # Plot VRAM usage
        plt.subplot(2, 1, 1)
        plt.plot(df['time_utc'], df['used_mb'], label='Used VRAM (MB)', linewidth=2, color='blue')
        plt.plot(df['time_utc'], df['total_mb'], label='Total VRAM (MB)', linewidth=2, linestyle='--', color='red')
        
        plt.title('VoiceStudio GPU VRAM Usage Over Time', fontsize=14, fontweight='bold')
        plt.xlabel('Time')
        plt.ylabel('VRAM (MB)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=2))
        plt.xticks(rotation=45)
        
        # Plot usage percentage
        plt.subplot(2, 1, 2)
        df['usage_percent'] = (df['used_mb'] / df['total_mb']) * 100
        plt.plot(df['time_utc'], df['usage_percent'], label='VRAM Usage %', linewidth=2, color='green')
        
        plt.title('VRAM Usage Percentage', fontsize=12)
        plt.xlabel('Time')
        plt.ylabel('Usage (%)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.ylim(0, 100)
        
        # Format x-axis
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=2))
        plt.xticks(rotation=45)
        
        # Save chart
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"VRAM chart generated: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error generating VRAM chart: {e}")
        return False

def main():
    """Main function"""
    csv_path = r"C:\VoiceStudio\logs\vram_telemetry.csv"
    output_path = r"C:\VoiceStudio\logs\vram_usage_chart.png"
    
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    
    success = generate_vram_chart(csv_path, output_path)
    if success:
        print("VRAM chart generation completed successfully!")
    else:
        print("VRAM chart generation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
