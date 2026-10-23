# Data-quality report: farm logbook 2025


## Summary

| item                                                   |   value |
|:-------------------------------------------------------|--------:|
| Rows in raw file (excluding blank lines)               |    1248 |
| Rows kept                                              |    1195 |
| Duplicate rows dropped                                 |      41 |
| Rows with no volume                                    |      12 |
| Decimal slips fixed                                    |       4 |
| Split collections summed (tapper-days with 2+ entries) |      81 |
| Calendar days                                          |     365 |
| Days with no entries                                   |       0 |
| Incomplete days (tapper present, did not tap)          |      12 |

## Decimal slips fixed

Verified against the logbook by the farm owner.

|   source_row | date       | tapper   |   value_raw |   volume_l |
|-------------:|:-----------|:---------|------------:|-----------:|
|           21 | 2025-01-07 | T2       |         262 |       26.2 |
|          120 | 2025-02-03 | T3       |         134 |       13.4 |
|          860 | 2025-09-04 | T2       |         140 |       14   |
|          965 | 2025-10-05 | T4       |         218 |       21.8 |

## Tapper coverage

| tapper   | first_day   | last_day   |   days |   median_l |
|:---------|:------------|:-----------|-------:|-----------:|
| T1       | 2025-03-01  | 2025-10-31 |    241 |      16.8  |
| T2       | 2025-01-01  | 2025-12-31 |    304 |      24    |
| T3       | 2025-01-01  | 2025-12-31 |    299 |      20.9  |
| T4       | 2025-01-01  | 2025-12-31 |    270 |      21.65 |

## Monthly overview

`typical_daily_change_l` is the median day-to-day change in estate total.

| date    |   mean_total_l |   mean_per_tapper_l |   typical_daily_change_l |
|:--------|---------------:|--------------------:|-------------------------:|
| 2025-01 |          64.27 |               21.68 |                     6.15 |
| 2025-02 |          60.8  |               20.27 |                     5.6  |
| 2025-03 |          53.69 |               18.24 |                     7.65 |
| 2025-04 |          53.85 |               18.15 |                     0.6  |
| 2025-05 |          58.12 |               19.37 |                     0.8  |
| 2025-06 |          61.87 |               20.62 |                     1.2  |
| 2025-07 |          64.72 |               21.57 |                     0.6  |
| 2025-08 |          62.22 |               15.81 |                     0.9  |
| 2025-09 |          67.78 |               22.86 |                     1    |
| 2025-10 |          69.64 |               23.47 |                     1.45 |
| 2025-11 |          70.43 |               24.02 |                     0.7  |
| 2025-12 |          72.56 |               24.73 |                     1.1  |
