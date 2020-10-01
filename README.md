# Spades

OpenAI gym for the card game spades.

For referrence, see [gym-soccer](https://github.com/openai/gym-soccer)

## Development

Agents go in the [agents](./gym_spades/envs/agents) folder. They should inherit from some base class (eg [agent](./gym_spades/envs/agents/agent.py) or [fa_agent](./gym_spades/envs/agents/fa_agent.py)) that contains the logic for state representation.

When playing (training), use the [appropriate environment](./gym_spades/envs/spades_env.py), which will contain a list of all the agents (players) in the game, and simulate play using the base class [spades](./gym_spades/envs/spades/spades.py).

## Installation

### pipenv

Recommended: use [pipenv](https://pipenv.pypa.io/en/latest/).

To use `pipenv`, you must have pyenv or [asdf](https://asdf-vm.com/#/core-manage-asdf) (recommended) installed, or already have python 3.8 as your machine's python version.

If running on Windows, use pyenv.

To install `asdf` and the python plugin (linux or macos only):

For linux:

```bash
sudo apt-get update; sudo apt-get install --no-install-recommends make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
sudo apt install curl git
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.8.0
echo ". $HOME/.asdf/asdf.sh" >> ~/.bashrc
echo ". $HOME/.asdf/completions/asdf.bash" >> ~/.bashrc
asdf plugin-add python
asdf install python 3.8.2
```

To install `pipenv`:

```bash
pip install --user pipenv
```

Read the [documentation](https://pipenv.pypa.io/en/latest/install/#pragmatic-installation-of-pipenv) if you run in to any problems.

Then restart your shell (close and reopen)

If you don't want to, just replace `pipenv` with `pip` everywhere in the below commands.

### the project

```bash
git clone https://github.com/will-jac/rl-spades.git
cd rl-spades
pipenv install
cd gym_spades
pipenv install -e .
```

Press Y on any prompts to install the required libraries. If using `pip`, you may need to install these yourself.

## Usage

```bash
pipenv run python file.py
```
