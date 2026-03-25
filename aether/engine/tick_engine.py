"""Tick engine: main simulation loop with action collection and execution."""

from __future__ import annotations

import logging
from typing import Any

from aether.actions.action import Action, ActionType
from aether.actions.attack_action import execute_attack
from aether.actions.build_action import execute_build
from aether.actions.collect_action import execute_collect
from aether.actions.hunt_action import execute_hunt
from aether.actions.move_action import execute_move
from aether.actions.reproduce_action import execute_reproduce
from aether.actions.trade_action import execute_trade
from aether.agents.agent import Agent
from aether.agents.decision import decide, observe
from aether.agents.inventory import remove_resource as inv_remove
from aether.engine.rule_engine import RuleEngine
from aether.utils.logger import EventLogger, MetricsWriter
from aether.world.world import World

logger = logging.getLogger("aether.engine")


class TickEngine:
    """Main simulation engine that drives the tick loop.

    Per tick:
        1. Execute all rules in order (via RuleEngine).
        2. Collect agent decisions (observe → decide).
        3. Validate and execute actions.
        4. Post-tick cleanup and logging.

    Attributes:
        world: The simulation world.
        rule_engine: The rule execution engine.
        max_ticks: Maximum number of ticks to run.
        event_logger: JSONL event logger (optional).
        metrics_writer: CSV metrics writer (optional).
    """

    def __init__(
        self,
        world: World,
        rule_engine: RuleEngine,
        max_ticks: int = 1000,
        event_logger: EventLogger | None = None,
        metrics_writer: MetricsWriter | None = None,
    ) -> None:
        self.world = world
        self.rule_engine = rule_engine
        self.max_ticks = max_ticks
        self.event_logger = event_logger
        self.metrics_writer = metrics_writer

        # Per-tick counters for metrics
        self._tick_births: int = 0
        self._tick_deaths: int = 0
        self._tick_trades: int = 0
        self._tick_combats: int = 0

    def collect_actions(self) -> list[Action]:
        """Collect action decisions from all living agents.

        Returns:
            List of Action dicts, one per agent, in agent_id ascending order.
        """
        actions: list[Action] = []
        for agent in self.world.living_agents():
            observation = observe(agent, self.world)
            action = decide(agent, observation, self.world.rng)
            actions.append(action)
        return actions

    def validate_action(self, action: Action) -> bool:
        """Validate that an action is legal.

        Args:
            action: Action to validate.

        Returns:
            True if the action can be executed.
        """
        actor = self.world.agents.get(action["actor_id"])
        if actor is None or not actor.is_alive():
            return False

        if action["type"] == ActionType.ATTACK:
            if "combat" not in [r.name for r in self.rule_engine.rules]:
                return False
            target_id = action.get("target")
            if isinstance(target_id, int) and target_id not in self.world.agents:
                return False

        if action["type"] == ActionType.TRADE:
            target_id = action.get("target")
            if isinstance(target_id, int) and target_id not in self.world.agents:
                return False

        return True

    def execute_action(self, action: Action) -> None:
        """Execute a single validated action and log the result.

        Args:
            action: The action to execute.
        """
        action_type = action["type"]
        actor_id = action["actor_id"]
        target = action.get("target")
        payload = action.get("payload", {})
        result: dict[str, Any] = {}

        if action_type == ActionType.MOVE:
            target_tuple = target if isinstance(target, tuple) else None
            result = execute_move(actor_id, target_tuple, self.world)

        elif action_type == ActionType.COLLECT:
            target_tuple = target if isinstance(target, tuple) else None
            result = execute_collect(actor_id, target_tuple, payload, self.world)

        elif action_type == ActionType.EAT:
            # Eat from inventory: restore energy from food
            agent = self.world.agents.get(actor_id)
            if agent is not None:
                resource = payload.get("resource", "food")
                eaten = inv_remove(agent.inventory, resource, 10.0)
                agent.energy = min(100.0, agent.energy + eaten * 8.0)
                agent.hunger = max(0.0, agent.hunger - eaten * 5.0)
                result = {"agent_id": actor_id, "ate": resource, "amount": eaten}

        elif action_type == ActionType.ATTACK:
            target_id = target if isinstance(target, int) else None
            result = execute_attack(actor_id, target_id, self.world)
            if result.get("success"):
                self._tick_combats += 1

        elif action_type == ActionType.TRADE:
            target_id = target if isinstance(target, int) else None
            result = execute_trade(actor_id, target_id, payload, self.world)
            if result.get("success"):
                self._tick_trades += 1

        elif action_type == ActionType.REPRODUCE:
            result = execute_reproduce(actor_id, self.world)
            if result.get("success"):
                self._tick_births += 1

        elif action_type == ActionType.BUILD:
            target_tuple = target if isinstance(target, tuple) else None
            result = execute_build(actor_id, target_tuple, payload, self.world)

        elif action_type == ActionType.HUNT:
            target_animal_id = target if isinstance(target, int) else None
            result = execute_hunt(actor_id, target_animal_id, self.world)

        elif action_type == ActionType.IDLE:
            result = {"agent_id": actor_id, "action": "idle"}

        # Log event
        if self.event_logger and result:
            self.event_logger.log_event(
                self.world.tick,
                str(action_type),
                result,
            )

        # Q-Learning Feedback Loop
        agent = self.world.agents.get(actor_id)
        if (
            agent is not None
            and getattr(agent, "q_table", None) is not None
            and agent.state_representation is not None
            and agent.last_action is not None
        ):
            reward = self._calculate_reward(action_type, result, agent)
            self._update_q_table(agent, reward)

    def _calculate_reward(
        self,
        action_type: ActionType,
        result: dict[str, Any],
        agent: Agent,
    ) -> float:
        """Calculate intrinsic reward for the action taken."""
        reward = -0.1  # small time penalty for existence
        if action_type == ActionType.EAT:
            reward = 1.0
        elif action_type == ActionType.REPRODUCE and result.get("success"):
            reward = 5.0
        elif action_type == ActionType.COLLECT and result.get("success"):
            reward = 0.5
        elif action_type == ActionType.HUNT and result.get("success"):
            reward = 3.0
        elif action_type == ActionType.ATTACK and result.get("success"):
            reward = 2.0
        elif action_type == ActionType.TRADE and result.get("success"):
            reward = 1.0
        elif not result.get("success", True):
            reward = -1.0  # penalty for blocked / failed abstract action

        # Give big penalty if agent is starving/dying
        if agent.hunger > 80.0:
            reward -= 2.0
        if agent.energy < 20.0:
            reward -= 2.0

        return reward

    def _update_q_table(self, agent: Agent, reward: float) -> None:
        """Perform Bellman update on the Agent's Q-Table."""
        from aether.agents.decision import RL_ACTIONS, _get_discrete_state, observe

        s = agent.state_representation
        a = agent.last_action

        if s is None or a is None or agent.q_table is None:
            return

        obs = observe(agent, self.world)
        next_s = _get_discrete_state(agent, obs)

        if next_s not in agent.q_table:
            agent.q_table[next_s] = {act: 0.0 for act in RL_ACTIONS}

        max_q_next = max(agent.q_table[next_s].values())
        current_q = agent.q_table[s][a]

        new_q = current_q + agent.alpha * (reward + agent.gamma * max_q_next - current_q)
        agent.q_table[s][a] = new_q

    def run_tick(self, tick: int) -> None:
        """Execute a single simulation tick.

        Args:
            tick: Current tick number.
        """
        # Reset per-tick counters
        self._tick_births = 0
        self._tick_deaths = 0
        self._tick_trades = 0
        self._tick_combats = 0

        # 1. Apply all rules in order
        pop_before_rules = self.world.population_size()
        self.rule_engine.apply_all(self.world, tick)
        pop_after_rules = self.world.population_size()
        self._tick_births += max(0, pop_after_rules - pop_before_rules)
        self._tick_deaths += max(0, pop_before_rules - pop_after_rules)

        # 2. Collect agent actions
        actions = self.collect_actions()

        # 3. Validate and execute
        for action in actions:
            if self.validate_action(action):
                self.execute_action(action)

        # 4. Post-tick cleanup
        self.world.post_tick_cleanup(tick)

        # 5. Write metrics
        if self.metrics_writer:
            agents = self.world.living_agents()
            pop = len(agents)
            avg_energy = sum(a.energy for a in agents) / max(pop, 1)
            avg_strength = sum(a.traits.get("strength", 0.0) for a in agents) / max(pop, 1)
            self.metrics_writer.write_tick(
                {
                    "tick": tick,
                    "population": pop,
                    "avg_energy": round(avg_energy, 2),
                    "avg_strength": round(avg_strength, 4),
                    "num_births": self._tick_births,
                    "num_deaths": self._tick_deaths,
                    "num_trades": self._tick_trades,
                    "num_combats": self._tick_combats,
                }
            )

    def run(self, render_callback: Any | None = None, render_interval: int = 10) -> None:
        """Run the full simulation for max_ticks.

        Args:
            render_callback: Optional callable(world, tick) for visualization.
            render_interval: Call render every N ticks.
        """
        logger.info(
            "Starting simulation: %d ticks, %d agents", self.max_ticks, self.world.population_size()
        )

        for tick in range(self.max_ticks):
            self.run_tick(tick)

            if render_callback and tick % render_interval == 0:
                render_callback(self.world, tick)

            # Log population changes
            if tick % 50 == 0:
                logger.info(
                    "Tick %d: population=%d",
                    tick,
                    self.world.population_size(),
                )

        logger.info(
            "Simulation complete: %d ticks, final population=%d",
            self.max_ticks,
            self.world.population_size(),
        )
