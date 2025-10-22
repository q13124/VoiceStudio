# VoiceStudio SLOs

## API SLO
- **Availability**: 99.9% monthly (error rate < 0.1%)
- **Latency**: p95 < 500 ms over rolling 1h

## Audio Quality SLO
- **Clip hit rate**: < 2% 7-day avg
- **WR baseline (golden-set vs. reference)**: >= 60% 7-day avg

## Error Budget
- Availability budget per 30 days at 99.9%: 43m 12s of errors/downtime.
- Burn alerts:
  - **Fast burn**: >5% of monthly budget consumed in 1h
  - **Slow burn**: >50% consumed in 24h
