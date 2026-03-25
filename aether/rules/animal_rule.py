"""Animal rule — governs Animal AI per tick (movement, hunting, fleeing, spawning)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aether.agents.animal import Animal
from aether.rules.base_rule import Rule

if TYPE_CHECKING:
    from aether.world.world import World


class AnimalRule(Rule):
    """Per-tick AI for all world Animals.

    Rabbits:
      - Spawn probabilistically each tick up to a soft cap.
      - Flee from agents and wolves within vision radius.
      - Move randomly otherwise.

    Wolves:
      - Spawn rarely.
      - Chase the nearest agent or rabbit.
      - Attack co-located agents for damage.

    Config params:
        rabbit_spawn_prob (float): Chance per tick to spawn a new rabbit. Default 0.03.
        wolf_spawn_prob (float): Chance per tick to spawn a new wolf. Default 0.005.
        rabbit_cap (int): Max rabbit population. Default 30.
        wolf_cap (int): Max wolf population. Default 8.
        wolf_attack_damage (float): HP wolves deal to co-located agents. Default 12.0.
        vision_radius (int): How many cells animals can see. Default 3.
    """

    name = "animal"

    def apply(self, world: World, tick: int) -> None:
        """Run one tick of animal AI.

        Args:
            world: The simulation world.
            tick: Current tick number.
        """
        params = self.params
        rabbit_spawn_prob: float = float(params.get("rabbit_spawn_prob", 0.03))
        wolf_spawn_prob: float = float(params.get("wolf_spawn_prob", 0.005))
        rabbit_cap: int = int(params.get("rabbit_cap", 30))
        wolf_cap: int = int(params.get("wolf_cap", 8))
        wolf_dmg: float = float(params.get("wolf_attack_damage", 12.0))
        vision: int = int(params.get("vision_radius", 3))

        # Count current populations
        rabbits = [a for a in world.living_animals() if a.kind == "rabbit"]
        wolves = [a for a in world.living_animals() if a.kind == "wolf"]

        # --- Spawning ---
        if len(rabbits) < rabbit_cap and world.rng.random() < rabbit_spawn_prob:
            rx = world.rng.randint(0, world.width - 1)
            ry = world.rng.randint(0, world.height - 1)
            rabbit = Animal(id=world.next_animal_id(), kind="rabbit", x=rx, y=ry)
            world.add_animal(rabbit)
            rabbits.append(rabbit)

        if len(wolves) < wolf_cap and world.rng.random() < wolf_spawn_prob:
            wx = world.rng.randint(0, world.width - 1)
            wy = world.rng.randint(0, world.height - 1)
            wolf = Animal(id=world.next_animal_id(), kind="wolf", x=wx, y=wy, health=150.0)
            world.add_animal(wolf)
            wolves.append(wolf)

        # --- Rabbit AI ---
        for rabbit in rabbits:
            if not rabbit.is_alive():
                world.remove_animal(rabbit.id)
                continue
            self._rabbit_tick(rabbit, world, vision)

        # --- Wolf AI ---
        for wolf in wolves:
            if not wolf.is_alive():
                world.remove_animal(wolf.id)
                continue
            self._wolf_tick(wolf, world, vision, wolf_dmg)

    def _rabbit_tick(self, rabbit: Animal, world: World, vision: int) -> None:
        """Move rabbit: flee from nearby threats, otherwise random walk."""
        threats = [
            a
            for a in world.living_agents()
            if abs(a.x - rabbit.x) <= vision and abs(a.y - rabbit.y) <= vision
        ]
        # Also flee wolves
        wolf_threats = [
            w
            for w in world.living_animals()
            if w.kind == "wolf" and abs(w.x - rabbit.x) <= vision and abs(w.y - rabbit.y) <= vision
        ]

        if threats or wolf_threats:
            # Move away from nearest threat
            all_threats: list[Any] = [*threats, *wolf_threats]
            threat = all_threats[0]
            dx = 1 if rabbit.x < threat.x else -1  # noqa: SIM210
            dy = 1 if rabbit.y < threat.y else -1  # noqa: SIM210
            new_x = (rabbit.x - dx) % world.width
            new_y = (rabbit.y - dy) % world.height
        else:
            new_x = (rabbit.x + world.rng.randint(-1, 1)) % world.width
            new_y = (rabbit.y + world.rng.randint(-1, 1)) % world.height

        # Don't move into a wall
        cell = world.get_cell(new_x, new_y)
        if cell.structure is None or cell.structure.kind != "wall":
            rabbit.x = new_x
            rabbit.y = new_y

    def _wolf_tick(self, wolf: Animal, world: World, vision: int, dmg: float) -> None:
        """Wolf AI: chase nearest agent or rabbit, attack on contact."""
        # Find nearest prey (agents first, then rabbits)
        prey_agents = sorted(
            [
                a
                for a in world.living_agents()
                if abs(a.x - wolf.x) <= vision and abs(a.y - wolf.y) <= vision
            ],
            key=lambda a: abs(a.x - wolf.x) + abs(a.y - wolf.y),
        )
        prey_animals = sorted(
            [
                r
                for r in world.living_animals()
                if r.kind == "rabbit"
                and abs(r.x - wolf.x) <= vision
                and abs(r.y - wolf.y) <= vision
            ],
            key=lambda r: abs(r.x - wolf.x) + abs(r.y - wolf.y),
        )

        target_x, target_y = wolf.x, wolf.y
        if prey_agents:
            target_x, target_y = prey_agents[0].x, prey_agents[0].y
        elif prey_animals:
            target_x, target_y = prey_animals[0].x, prey_animals[0].y
        else:
            # Random wander
            target_x = (wolf.x + world.rng.randint(-1, 1)) % world.width
            target_y = (wolf.y + world.rng.randint(-1, 1)) % world.height

        # Step toward target
        dx = 0 if target_x == wolf.x else (1 if target_x > wolf.x else -1)
        dy = 0 if target_y == wolf.y else (1 if target_y > wolf.y else -1)
        new_x = (wolf.x + dx) % world.width
        new_y = (wolf.y + dy) % world.height

        cell = world.get_cell(new_x, new_y)
        if cell.structure is None or cell.structure.kind != "wall":
            wolf.x = new_x
            wolf.y = new_y

        # Attack any agents sharing the cell
        for agent in world.living_agents():
            if agent.x == wolf.x and agent.y == wolf.y:
                agent.health = max(0.0, agent.health - dmg)

        # Kill co-located rabbits
        for rabbit in world.living_animals():
            if rabbit.kind == "rabbit" and rabbit.x == wolf.x and rabbit.y == wolf.y:
                rabbit.health = 0.0
