"""Weather rule: dynamically shifts global weather and temperature."""

from __future__ import annotations

from aether.rules.base_rule import Rule
from aether.world.world import World


class WeatherRule(Rule):
    """Shifts the weather state over time.

    Config params:
        season_length (int): Ticks per season. Default 100.
    """

    name = "weather"

    def apply(self, world: World, tick: int) -> None:
        """Cycle the weather based on the current tick.

        Args:
            world: The simulation world.
            tick: Current tick number.
        """
        season_length = self.params.get("season_length", 100)
        seasons = ["Spring", "Summer", "Autumn", "Winter"]

        cycle_idx = (tick // season_length) % 4
        world.weather_state = seasons[cycle_idx]

        # Adjust global temperature roughly based on season
        if world.weather_state == "Spring":
            world.global_temperature = 15.0
        elif world.weather_state == "Summer":
            world.global_temperature = 30.0
        elif world.weather_state == "Autumn":
            world.global_temperature = 10.0
        elif world.weather_state == "Winter":
            world.global_temperature = -5.0
