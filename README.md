# چتر و بستنی

One-page Persian simulation of why low correlation matters: someone sells umbrellas on rainy days and ice cream on sunny days, and their month-by-month income over ten years is drawn from the real weather of each day. Four street businesses (ice cream, umbrellas, beetroot «لبو», air coolers) make four pairs, from strongly opposite (ice cream and umbrellas, ice cream and beetroot) to moving together (ice cream and coolers); each pair shows each business alone and both together, the months with less than a quarter of a typical month's income, and the monthly correlation. Six cities: Tehran, Isfahan, Shiraz, Mashhad, Tabriz, Rasht.

- Live: https://pasmod.github.io/chatr-o-bastani/
- The weather is real, the incomes are not. Daily weather from the [Open-Meteo historical archive](https://open-meteo.com/) (ERA5 reanalysis, CC BY 4.0), Tehran time, for the Persian years 1395–1404 (2016-03-20 to 2026-03-20). Each business earns by one rule per day, summed per Persian month and scaled so that its average month is 100:
  - ice cream: on a day with less than 1 mm of rain or snow, max temperature minus 15 °C (0 if below);
  - umbrellas: 1 on every day with at least 1 mm of rain or snow;
  - beetroot: 15 °C minus the day's mean temperature (0 if above);
  - air coolers: max temperature minus 25 °C (0 if below).
- "Both together" is the average of the two scaled series, so its typical month is also 100. A month is "low income" below 25. Bars are drawn up to three typical months; taller ones are cut (a gap near the top), and tapping a month shows its exact numbers.
- `index.html` is the page, `data.js` its data (no build step for the page). `build_data.py` rebuilds `data.js`: `uv run --with jdatetime python build_data.py`. `preview.png` is the X/Open Graph card, rendered from `preview-src.html` with headless Chrome at 1200×630.
