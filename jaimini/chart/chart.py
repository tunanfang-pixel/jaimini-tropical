"""Chart data structure — integrates planetary positions, houses, and Jaimini analysis."""

from ..engine.ephemeris import get_all_planets, get_rahu_ketu
from ..engine.houses import calc_houses, calc_ascendant, WHOLE_SIGN, HOUSE_SYSTEMS
from ..engine.time_utils import parse_dms, format_dms, zodiac_position, local_to_utc, parse_timezone, ZODIAC, ZODIAC_FULL
from ..core.karakas import calc_chara_karakas, karaka_report
from ..core.dashas import calc_chara_dasha, format_dasha_table, calc_all_dasha_years
from ..core.padas import calc_all_padas, calc_upapada, pada_report
from ..core.lagnas import calc_all_special_lagnas, lagna_report
from ..core.divisions import calc_all_divisions, division_report
from ..core.argala import calc_all_argalas, argala_report, classify_argala_rajayoga, calc_karakamsa_rajayoga


class Chart:
    """A Jaimini astrological chart with tropical zodiac."""

    def __init__(self, year, month, day, hour, minute, second,
                 lat, lon, tz_offset=0.0, name="", house_system='W'):
        """
        Args:
            year, month, day: Local date
            hour, minute, second: Local time
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees (East positive)
            tz_offset: Timezone offset from UTC in hours (e.g., +8 for CST)
            name: Optional chart name/label
            house_system: 'W' = Whole Sign, 'P' = Placidus, 'E' = Equal
        """
        self.name = name
        self.house_system = house_system

        # Convert to UTC
        utc_dt = local_to_utc(year, month, day, hour, minute, second, tz_offset)

        self.utc_year = utc_dt.year
        self.utc_month = utc_dt.month
        self.utc_day = utc_dt.day
        self.utc_hour = utc_dt.hour
        self.utc_minute = utc_dt.minute
        self.utc_second = utc_dt.second + (utc_dt.microsecond / 1_000_000)

        self.lat = lat
        self.lon = lon
        self.tz_offset = tz_offset

        # Compute positions
        self.planets = get_all_planets(
            self.utc_year, self.utc_month, self.utc_day,
            self.utc_hour, self.utc_minute, self.utc_second
        )

        self.ascendant = calc_ascendant(
            self.utc_year, self.utc_month, self.utc_day,
            self.utc_hour, self.utc_minute, self.utc_second,
            lat, lon
        )

        self.houses = calc_houses(
            self.utc_year, self.utc_month, self.utc_day,
            self.utc_hour, self.utc_minute, self.utc_second,
            lat, lon, system=house_system
        )

        # Jaimini analysis
        self.karakas_7 = calc_chara_karakas(self.planets, include_rahu=False)
        self.karakas_8 = calc_chara_karakas(self.planets, include_rahu=True)

        self.dasha_years = calc_all_dasha_years(self.planets)
        self.chara_dasha = calc_chara_dasha(
            0,  # Will be computed by the engine
            self.houses, self.planets, chakra='prakriti'
        )

        # Compute birth Julian Day for dasha
        from ..engine.ephemeris import julian_day
        self.birth_jd = julian_day(
            self.utc_year, self.utc_month, self.utc_day,
            self.utc_hour, self.utc_minute, self.utc_second
        )

        # Recompute dasha with correct birth_jd
        self.chara_dasha = calc_chara_dasha(
            self.birth_jd, self.houses, self.planets, chakra='prakriti'
        )

        # Layer 2: Arudha Padas
        self.asc_sign_idx = int(self.ascendant // 30)
        self.padas = calc_all_padas(self.asc_sign_idx, self.planets)
        self.upapada = calc_upapada(self.asc_sign_idx, self.planets)

        # Layer 3: Special Lagnas (HL, GL, VL)
        self.special_lagnas = calc_all_special_lagnas(
            year, month, day, hour, minute, second,
            lat, lon, self.asc_sign_idx, tz_offset
        )

        # Layer 4: Divisional charts (D-3, D-9, D-12)
        self.divisions = calc_all_divisions(self.planets, self.ascendant)

        # Argala analysis (Jaimini judgment system)
        self.argalas = calc_all_argalas(self.houses, self.planets)

        # Argala Rajayoga for Ascendant (most important reference point)
        self.lagna_rajayoga = classify_argala_rajayoga(
            self.argalas[1]  # House 1 = Ascendant
        )

        # Karakamsa Rajayoga
        ak = self.karakas_7[0]  # Atmakaraka is always first
        self.karakamsa_rajayoga = calc_karakamsa_rajayoga(
            ak['planet'], ak['lon'],
            self.divisions, self.planets
        )

    @classmethod
    def from_iso(cls, dt_str, tz_str, lat, lon, name="", house_system='W'):
        """Create chart from ISO datetime string and timezone string.

        Example:
            Chart.from_iso('1949-10-01 15:00:00', '+8', '39°54′25″', '116°23′50″')
        """
        from datetime import datetime
        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        lat_deg = parse_dms(lat)
        lon_deg = parse_dms(lon)
        tz = parse_timezone(tz_str)
        return cls(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second,
                   lat_deg, lon_deg, tz, name=name, house_system=house_system)

    def asc_sign(self):
        """Return the ascendant sign index (0-11) and name."""
        idx = int(self.ascendant // 30)
        return idx, ZODIAC[idx]

    def planets_in_house(self, house_num):
        """Return list of planets in a given house (1-12)."""
        h = self.houses[house_num - 1]
        result = []
        for name, pos in self.planets.items():
            lon = pos['lon']
            sign_idx = int(lon // 30)
            if sign_idx == h['sign_idx']:
                result.append(name)
        return result

    def planet_house(self, planet_name):
        """Return the house number (1-12) where a planet is located."""
        if planet_name not in self.planets:
            return None
        lon = self.planets[planet_name]['lon']
        sign_idx = int(lon // 30)
        for h in self.houses:
            if h['sign_idx'] == sign_idx:
                return h['house']
        return 1

    def summary(self):
        """Generate a comprehensive text summary of the chart."""
        lines = []

        # Header
        asc_sign_idx, asc_name = self.asc_sign()
        asc_str = zodiac_position(self.ascendant)[2]
        lines.append("=" * 70)
        lines.append(f"JAIMINI ASTROLOGY CHART (Tropical Zodiac)")
        lines.append(f"{self.name}" if self.name else "Chart Summary")
        lines.append("=" * 70)
        lines.append(f"Ascendant: {asc_str}  |  House System: {HOUSE_SYSTEMS.get(self.house_system, self.house_system)}")
        lines.append("")

        # Planetary Positions
        lines.append("-" * 70)
        lines.append(f"{'Planet':<12}{'Longitude':<24}{'Sign':<8}{'House':<8}{'Speed(°/d)':<12}{'Retro'}")
        lines.append("-" * 70)

        planet_order = ['Su', 'Mo', 'Ma', 'Me', 'Ju', 'Ve', 'Sa', 'Ra', 'Ke', 'Ur', 'Ne', 'Pl']
        for p in planet_order:
            if p not in self.planets:
                continue
            pos = self.planets[p]
            house = self.planet_house(p)
            speed_str = f"{pos['speed']:.4f}"
            retro = 'R' if pos.get('retrograde') else ''
            lines.append(
                f"{p:<12}"
                f"{pos['sign_str']:<24}"
                f"{pos['sign']:<8}"
                f"{house:<8}"
                f"{speed_str:<12}"
                f"{retro}"
            )

        # Houses (Whole Sign cusps)
        lines.append("")
        lines.append("-" * 70)
        lines.append("HOUSE CUSPS (Whole Sign)")
        lines.append("-" * 70)
        for h in self.houses:
            planets = self.planets_in_house(h['house'])
            planets_str = ', '.join(planets) if planets else '—'
            lines.append(f"House {h['house']:2d}: {h['sign']:<5} | Planets: {planets_str}")

        # Karakas
        lines.append("")
        lines.append(karaka_report(self.karakas_7))

        # Arudha Padas
        lines.append("")
        lines.append(pada_report(self.padas))
        if self.upapada:
            lines.append(f"\n  Upapada (UL): {self.upapada['sign_full']} "
                         f"(lord: {self.upapada['lord']})")
            lines.append(f"  {self.upapada['description']}")

        # Special Lagnas
        lines.append("")
        lines.append(lagna_report(self.special_lagnas))

        # Divisional Charts
        lines.append("")
        lines.append(division_report(self.divisions, 'D9'))
        lines.append("")
        lines.append(division_report(self.divisions, 'D3'))

        # Argala Analysis
        lines.append("")
        lines.append(argala_report(self.argalas))

        # Rajayoga Summary
        lines.append("")
        lines.append("=" * 60)
        lines.append("RAJAYOGA SUMMARY")
        lines.append("=" * 60)
        lines.append(f"  Lagna Argala Rajayoga: {self.lagna_rajayoga['type']} — {self.lagna_rajayoga['desc']}")
        kr = self.karakamsa_rajayoga
        lines.append(f"  Karakamsa Rajayoga: {'YES' if kr['is_rajayoga'] else 'No'} (level {kr['yoga_level']})")
        lines.append(f"    Karakamsa Sign: {kr['karakamsa_sign']} | AK ({kr['ak_planet']}) own Navamsa: {kr['ak_in_own_navamsa']}")
        lines.append(f"    {kr['description']}")

        # Dasha Years Summary
        lines.append("")
        lines.append("-" * 70)
        lines.append("DASHA YEARS (All Signs)")
        lines.append("-" * 70)
        for d in self.dasha_years:
            lines.append(f"  {d['sign_name']:<8} ({d['lord']}): {d['years']} years")

        # Chara Dasha Timeline
        lines.append("")
        lines.append(format_dasha_table(self.chara_dasha, include_antar=True))

        return "\n".join(lines)
