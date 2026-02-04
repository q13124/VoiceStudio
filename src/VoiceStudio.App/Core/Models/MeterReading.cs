using System;

namespace VoiceStudio.Core.Models
{
  public class MeterReading
  {
    public double Cpu { get; set; }
    public double Gpu { get; set; }
    public double Ram { get; set; }
    public DateTime Timestamp { get; set; } = DateTime.Now;
  }
}