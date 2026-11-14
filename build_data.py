"""Build data.js: monthly incomes of four weather-bound street businesses from real daily weather.

Weather: Open-Meteo's historical archive (ERA5 reanalysis), daily, Tehran time, for the ten
Persian years 1395-1404 (2016-03-20 to 2026-03-20). The incomes are not real: each business
earns by one simple rule from the day's weather (RULES below), summed per Persian month and
scaled so that its average month is 100.

    uv run --with jdatetime python build_data.py            # fetch and build
    uv run --with jdatetime python build_data.py --cache raw  # use saved JSON files in raw/
"""
import json, sys, time, urllib.request
from pathlib import Path

import jdatetime

START, END = "2016-03-20", "2026-03-20"   # 1395-01-01 .. 1404-12-29
CITIES = {  # id: (Persian name, latitude, longitude)
    "tehran": ("تهران", 35.69, 51.39),
    "shiraz": ("شیراز", 29.61, 52.54),
    "tabriz": ("تبریز", 38.08, 46.29),
    "mashhad": ("مشهد", 36.30, 59.60),
    "rasht": ("رشت", 37.28, 49.58),
    "isfahan": ("اصفهان", 32.65, 51.67),
}
WET = 1.0  # mm of rain or snow (as water) that make a day rainy
RULES = {  # id: rule on (max temperature, mean temperature, precipitation) of one day
    "ice": lambda tmax, tmean, p: max(0.0, tmax - 15) if p < WET else 0.0,   # dry and warm: the warmer, the more
    "umbrella": lambda tmax, tmean, p: 1.0 if p >= WET else 0.0,           # every rainy day the same
    "beet": lambda tmax, tmean, p: max(0.0, 15 - tmean),                   # cool and cold days: the colder, the more
    "cooler": lambda tmax, tmean, p: max(0.0, tmax - 25),                  # hot days: the hotter, the more
}


def fetch(city, lat, lon, cache):
    if cache and (cache / f"{city}.json").exists():
        return json.loads((cache / f"{city}.json").read_text())
    url = ("https://archive-api.open-meteo.com/v1/archive?"
           f"latitude={lat}&longitude={lon}&start_date={START}&end_date={END}"
           "&daily=temperature_2m_max,temperature_2m_mean,precipitation_sum&timezone=Asia%2FTehran")
    data = json.load(urllib.request.urlopen(url, timeout=120))
    time.sleep(2)
    return data


def monthly(data):
    d = data["daily"]
    months = {}
    for day, tmax, tmean, p in zip(d["time"], d["temperature_2m_max"], d["temperature_2m_mean"], d["precipitation_sum"]):
        y, m, dd = map(int, day.split("-"))
        j = jdatetime.date.fromgregorian(year=y, month=m, day=dd)
        row = months.setdefault((j.year, j.month), {k: 0.0 for k in RULES})
        for k, rule in RULES.items():
            row[k] += rule(tmax, tmean, p or 0.0)
    keys = sorted(months)
    assert len(keys) == 120 and keys[0] == (1395, 1) and keys[-1] == (1404, 12), keys[:2] + keys[-2:]
    out = {}
    for k in RULES:
        v = [months[x][k] for x in keys]
        mean = sum(v) / len(v)
        out[k] = [round(100 * x / mean, 1) for x in v]
    return keys, out


def main():
    cache = Path(sys.argv[sys.argv.index("--cache") + 1]) if "--cache" in sys.argv else None
    here = Path(__file__).parent
    cities, keys = {}, None
    for city, (name, lat, lon) in CITIES.items():
        keys, series = monthly(fetch(city, lat, lon, cache))
        cities[city] = {"name": name, **series}
        print(city, {k: max(v) for k, v in series.items()})
    data = {"start": list(keys[0]), "months": len(keys), "cities": cities}
    js = "// Built by build_data.py from Open-Meteo (ERA5) daily weather, 1395-1404. Do not edit.\n"
    js += "window.DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (here / "data.js").write_text(js)
    print("wrote data.js", len(js), "bytes")


if __name__ == "__main__":
    main()
