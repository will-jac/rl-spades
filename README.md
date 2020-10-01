# Spades

OpenAI gym for the card game spades.

For referrence, see [gym-soccer](https://github.com/openai/gym-soccer)

## Development

Agents go in the [agents](./gym_spades/envs/agents) folder. They should inherit from some base class (eg [agent](./gym_spades/envs/agents/agent.py) or [fa_agent](./gym_spades/envs/agents/fa_agent.py)) that contains the logic for state representation.

When playing (training), use the [appropriate environment](./gym_spades/envs/spades_env.py), which will contain a list of all the agents (players) in the game, and simulate play using the base class [spades](./gym_spades/envs/spades/spades.py).

## Installation

```bash
cd gym-spades
pip install -e .
```

## Usage

Jack:
```bash
pipenv run python file.py
```