#!/usr/bin/env python3
"""Render assets/skyline.svg from the current time and weather in Jakarta."""

import json
import urllib.request
from datetime import datetime, timedelta, timezone

LAT, LON = -6.2088, 106.8456
WIB = timezone(timedelta(hours=7))
OUT_PATH = "assets/skyline.svg"

WEATHER_LABELS = {
    "clear": "clear sky",
    "partly_cloudy": "partly cloudy",
    "overcast": "overcast",
    "fog": "foggy",
    "rain": "rain",
    "storm": "thunderstorm",
}


def fetch_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        "&current=temperature_2m,weather_code"
        "&timezone=Asia%2FJakarta"
    )
    with urllib.request.urlopen(url, timeout=15) as r:
        return json.load(r)


def time_bucket(hour):
    return "day" if 6 <= hour < 18 else "night"


def weather_bucket(code):
    if code == 0:
        return "clear"
    if code in (1, 2):
        return "partly_cloudy"
    if code == 3:
        return "overcast"
    if code in (45, 48):
        return "fog"
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82):
        return "rain"
    if code in (95, 96, 99):
        return "storm"
    return "clear"


SKY = {
    "night": {"top": "#0a0a1f", "bot": "#1b1840", "star_op": 1.0},
    "day":   {"top": "#3d6fd6", "bot": "#a9d4ff", "star_op": 0.0},
}


def build_svg(hour, minute, temp, tbucket, wbucket, label):
    sky = SKY[tbucket]
    is_night = tbucket == "night"
    stormy = wbucket == "storm"
    sleepy = is_night and not stormy
    show_moon = is_night
    show_sun = tbucket == "day"
    cloudy = wbucket in ("partly_cloudy", "overcast", "rain", "storm", "fog")
    heavy_cloud = wbucket in ("overcast", "rain", "storm", "fog")
    raining = wbucket in ("rain", "storm")
    foggy = wbucket == "fog"

    stars = ""
    if sky["star_op"] > 0:
        pts = [(60,26),(140,46),(230,22),(320,52),(460,24),(560,44),
               (650,30),(740,50),(110,62),(690,64)]
        for i,(x,y) in enumerate(pts):
            stars += (f'<rect class="star" x="{x}" y="{y}" width="3" height="3" '
                      f'fill="#c9bcff" style="opacity:{sky["star_op"]};animation-delay:{i*0.31:.2f}s"/>')

    moon = ""
    if show_moon:
        moon = ('<g transform="translate(700,40)"><circle cx="0" cy="0" r="16" fill="#f2eecb"/>'
                '<circle cx="6" cy="-4" r="14" fill="#0a0a1f"/></g>')

    sun = ""
    if show_sun:
        sun = '<circle cx="410" cy="34" r="17" fill="#ffd95c"/>'

    def cloud(x, y, scale=1.0, dim=False):
        fill = "#241c46" if dim else "#3a2f66"
        return (f'<g transform="translate({x},{y})">'
                f'<g class="cloud" style="animation-delay:{(x % 5) * 0.5:.1f}s">'
                f'<g transform="scale({scale})" fill="{fill}">'
                '<rect x="6" y="6" width="42" height="8"/><rect x="0" y="14" width="54" height="8"/>'
                '<rect x="14" y="0" width="24" height="6"/></g></g></g>')

    clouds = ""
    if cloudy:
        clouds += cloud(560, 50, dim=heavy_cloud)
        clouds += cloud(230, 78, 0.8, dim=heavy_cloud)
    if heavy_cloud:
        clouds += cloud(300, 30, 0.9, dim=True)
        clouds += cloud(700, 26, 0.7, dim=True)

    rain = ""
    if raining:
        drops = ""
        for i in range(24):
            x = 20 + (i * 33) % 800
            delay = (i * 0.13) % 1.1
            drops += (f'<rect class="drop" x="{x}" y="0" width="2" height="10" fill="#8fb8ff" '
                      f'style="animation-delay:{delay:.2f}s"/>')
        rain = f'<g opacity="0.75">{drops}</g>'

    flash = ""
    if stormy:
        flash = '<rect class="flash" width="820" height="170" fill="#e8e6ff"/>'

    fog_overlay = ""
    if foggy:
        fog_overlay = '<rect y="90" width="820" height="60" fill="#cfd0e6" opacity="0.18"/>'

    # creature mood
    if stormy:
        mouth = '<rect x="21" y="34" width="18" height="8" fill="#14103a"/>'  # surprised open mouth
    elif sleepy:
        mouth = '<rect x="24" y="36" width="12" height="3" fill="#ffffff"/>'
    else:
        mouth = '<rect x="24" y="36" width="12" height="5" fill="#ffffff"/>'

    eyes = ""
    if sleepy:
        eyes = ('<g fill="#14103a"><rect x="15" y="24" width="6" height="3"/>'
                '<rect x="39" y="24" width="6" height="3"/></g>')
    elif stormy:
        eyes = ('<g fill="#14103a"><rect x="14" y="16" width="8" height="14"/>'
                '<rect x="38" y="16" width="8" height="14"/>'
                '<rect x="14" y="16" width="3" height="3" fill="#c9bcff"/>'
                '<rect x="38" y="16" width="3" height="3" fill="#c9bcff"/></g>')
    else:
        eyes = ('<g class="blink"><g class="eyesO" fill="#14103a"><rect x="15" y="18" width="6" height="12"/>'
                '<rect x="39" y="18" width="6" height="12"/><rect x="15" y="18" width="3" height="3" fill="#c9bcff"/>'
                '<rect x="39" y="18" width="3" height="3" fill="#c9bcff"/></g>'
                '<g class="eyesC" fill="#14103a"><rect x="15" y="24" width="6" height="3"/>'
                '<rect x="39" y="24" width="6" height="3"/></g></g>')

    umbrella = ""
    if raining:
        umbrella = ('<g transform="translate(4,-18)">'
                    '<rect x="0" y="8" width="60" height="6" fill="#c9bcff"/>'
                    '<rect x="6" y="2" width="12" height="6" fill="#c9bcff"/>'
                    '<rect x="24" y="0" width="12" height="6" fill="#c9bcff"/>'
                    '<rect x="42" y="2" width="12" height="6" fill="#c9bcff"/>'
                    '<rect x="27" y="12" width="6" height="10" fill="#a9a3d6"/></g>')

    zzz = ""
    if sleepy:
        zzz = ('<text x="66" y="6" font-family="Courier New, monospace" font-weight="700" '
               'font-size="12" fill="#8b7fd6">z z z</text>')

    creature = f'''
  <g transform="translate(366,92) scale(1.4)">
   <g class="idle">
    <ellipse cx="30" cy="58" rx="27" ry="5" fill="#0a0a1f" opacity="0.35"/>
    {umbrella}
    <g class="ears">
      <rect x="9"  y="-12" width="6"  height="6" fill="#5f3fc0"/>
      <rect x="6"  y="-6"  width="12" height="6" fill="#5f3fc0"/>
      <rect x="45" y="-12" width="6"  height="6" fill="#5f3fc0"/>
      <rect x="42" y="-6"  width="12" height="6" fill="#5f3fc0"/>
    </g>
    <g fill="#8a63e8">
      <rect x="15" y="0"  width="30" height="6"/>
      <rect x="9"  y="6"  width="42" height="6"/>
      <rect x="3"  y="12" width="54" height="6"/>
      <rect x="0"  y="18" width="60" height="6"/>
      <rect x="0"  y="24" width="60" height="6"/>
      <rect x="0"  y="30" width="60" height="6"/>
      <rect x="3"  y="36" width="54" height="6"/>
      <rect x="9"  y="42" width="42" height="6"/>
    </g>
    <g fill="#7551d6">
      <rect x="9"  y="42" width="42" height="6"/>
      <rect x="3"  y="36" width="6"  height="6"/>
      <rect x="51" y="36" width="6"  height="6"/>
    </g>
    <rect x="9" y="6" width="12" height="6" fill="#a888f2"/>
    <rect x="12" y="48" width="12" height="6" fill="#5f3fc0"/>
    <rect x="36" y="48" width="12" height="6" fill="#5f3fc0"/>
    {eyes}
    {mouth}
    {zzz}
   </g>
  </g>'''

    time_str = f"{hour:02d}:{minute:02d}"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="820" height="200" viewBox="0 0 820 200" role="img" aria-label="jakarta sky, {tbucket}, {label}">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{sky['top']}"/>
      <stop offset="1" stop-color="{sky['bot']}"/>
    </linearGradient>
    <style>
      @keyframes twinkle {{ 0%,100% {{ opacity: .2; }} 50% {{ opacity: 1; }} }}
      @keyframes drift   {{ 0%,100% {{ transform: translateX(0); }} 50% {{ transform: translateX(14px); }} }}
      @keyframes idle    {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-4px); }} }}
      @keyframes wiggle  {{ 0%,100% {{ transform: rotate(-8deg); }} 50% {{ transform: rotate(8deg); }} }}
      @keyframes eyesO   {{ 0%,92% {{ opacity: 1; }} 93%,100% {{ opacity: 0; }} }}
      @keyframes eyesC   {{ 0%,92% {{ opacity: 0; }} 93%,100% {{ opacity: 1; }} }}
      @keyframes fall    {{ 0% {{ transform: translateY(-10px); opacity: 0; }} 10% {{ opacity: 1; }}
                            100% {{ transform: translateY(180px); opacity: 0; }} }}
      @keyframes flash   {{ 0%,94%,100% {{ opacity: 0; }} 95%,97% {{ opacity: .5; }} }}
      .star  {{ animation: twinkle 2.6s ease-in-out infinite; }}
      .cloud {{ animation: drift 9s ease-in-out infinite; }}
      .idle  {{ animation: idle 1s ease-in-out infinite; }}
      .ears  {{ animation: wiggle 1.3s ease-in-out infinite; transform-box: fill-box; transform-origin: 50% 100%; }}
      .eyesO {{ animation: eyesO 4.2s steps(1) infinite; }}
      .eyesC {{ animation: eyesC 4.2s steps(1) infinite; }}
      .drop  {{ animation: fall 0.9s linear infinite; }}
      .flash {{ animation: flash 4s linear infinite; }}
      .mono  {{ font-family: 'Courier New', monospace; font-weight: 700; }}
    </style>
  </defs>

  <rect width="820" height="200" fill="url(#sky)"/>
  <g>{stars}</g>
  {moon}
  {sun}
  {clouds}
  {fog_overlay}

  <rect x="0" y="170" width="820" height="30" fill="#241c46"/>
  <rect x="0" y="170" width="820" height="4"  fill="#3d3270"/>

  <text class="mono" x="22" y="32" font-size="13" fill="#8b7fd6">jakarta &#183; {time_str} wib</text>
  <text class="mono" x="22" y="50" font-size="11" fill="#5a4f8a">{temp:.0f}&#176;c &#183; {label}</text>
  {creature}
  {rain}
  {flash}
</svg>
'''
    return svg


def main():
    try:
        data = fetch_weather()
        cur = data["current"]
        temp = cur["temperature_2m"]
        code = cur["weather_code"]
    except Exception as e:
        print(f"weather fetch failed, skipping render: {e}")
        return

    now = datetime.now(WIB)
    tbucket = time_bucket(now.hour)
    wbucket = weather_bucket(code)
    label = WEATHER_LABELS[wbucket]

    svg = build_svg(now.hour, now.minute, temp, tbucket, wbucket, label)

    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"rendered {OUT_PATH}: {tbucket}/{wbucket}, {temp}C, {now.hour:02d}:{now.minute:02d} WIB")


if __name__ == "__main__":
    main()
