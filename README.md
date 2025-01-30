# OpenMind OS (omOS)

OpenMind OS is an agent runtime system that enables the creation and execution of digital and physical embodied AI agents with modular capabilities like movement, speech, and perception. A key benefit of using omOS is the ease of deploying consistent digital personas across virtual and physical environments.

## Quick Start

1. Install the Rust python package manager `uv`:

```bash
# for linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# for mac
brew install uv
```

If you are on mac, you may need to install `portaudio` and `hidapi` manually:

```bash
brew install portaudio
brew install hidapi # only needed for XBOX game controller support, for robotics
```

2. Set up environment variables:

Edit `.env` with your API keys (e.g. `OPENMIND_API_KEY`). NOTE: an OpenMind key is required.

```bash
cp .env.example .env
```

3. Run an Hello World agent

This very basic agent uses webcam data to estimate your emotion, generates a fake VLM caption, and sends those two inputs to central LLM. The LLM then returns `movement`, `speech`, and `face` commands, which are displayed in a small `pygame` window. This is windows also shows basic timing debug information so you can see how long each step takes.

```bash
uv run src/run.py spot
```

> [!NOTE]
> `uv` does many things in the background, such as setting up a good `venv` and downloading any dependencies if needed. Please add new dependencies to `pyproject.toml`.

> [!NOTE]
> If you are running complex models, or need to download dependencies, there may be a delay before the agent starts.

> [!NOTE]
> The OpenMind LLM endpoint includes a rate limiter. To use LLM services without rate limiting, please set the OPENMIND_API_KEY environment variable.

> [!NOTE]
> There should be a `pygame` window that pops up when you run `uv run src/run.py spot`. Sometimes the `pygame` window is hidden behind all other open windows - use "show all windows" to find it.

> [!NOTE]
> There is a bug on Mac when installing packages with `brew` - some libraries cannot be found by `uv`. If you get errors such as 
`Unable to load any of the following libraries:libhidapi-hidraw.so` and you are on a Mac, try setting `export DYLD_FALLBACK_LIBRARY_PATH="$HOMEBREW_PREFIX/lib"` in your `.zshenv` or equivalent. 

## Agent and Robot Examples

### Example 1 - The Coinbase Wallet

Similar to the `Hello World (Spot)` example, except uses the Coinbase wallet rather than Ethereum Mainnet.

```bash
uv run src/run.py coinbase
```

The agent tracks the balance of ????? in a Coinbase wallet and sends a message when there is a new transaction. The agent can be instructed via the prompt to express appreciation for receiving tokens. Here is how this is done - see `/config/coinbase.json`:

```bash
"system_prompt": "
... 
You like receiving ETH. If you receive an ETH transaction, show your appreciation though actions and speech. 
...
4. If there is a new ETH transaction, you might:\n    Move: 'shake paw'\n    Speak: {{'sentence': 'Thank you I really appreciate the ETH you just sent.'}}\n    Face: 'smile'\n\n
...",
```

The Coinbase wallet currently supports Base Sepolia and Base Mainnet networks. The Coinbase Wallet integration requires the following environment variables:

- `COINBASE_WALLET_ID`: The ID for the Coinbase Wallet.
- `COINBASE_API_KEY`: The API key for the Coinbase Project API.
- `COINBASE_API_SECRET`: The API secret for the Coinbase Project API.


You can get a Wallet ID from ???????. For new uswers, the procedure is_______. The API_KEY comes from __________. The API_SECRET is _________. These key are all strings and should looke like this:

```bash
COINBASE_WALLET_ID=???????????
COINBASE_API_KEY=?????????
COINBASE_API_SECRET=??????????
```

For more details, please see the [Coinbase documentation](https://docs.cdp.coinbase.com/mpc-wallet/docs/wallets).

### Example 2 - Using DeepSeek as the Core LLM

Similar to the `Hello World (Spot)` example, except uses `DeepSeek` rather than `OpenAI 4o`.

```bash
uv run src/run.py deepseek
```

### Example 3 - Using Cloud Endpoints for Voice Inputs

```bash
uv run src/run.py conversation
```

## Robots

### Unitree Go2 Air Quadruped ("dog")

You can control a Unitree Go2 Air. This has been tested for Linux Ubunto 22.04 running on an Nvidia Orin, and a Mac laptop running Seqoia 15.2. To do this: 

* Connect an `XBOX` controller to your computer. 
* Connect your computer to the Ethernet port of the Unitree Go2 Air, and keep track of the Ethernet port you are using. For example, the port could be `en0`.
* Install `CycloneDDS`, if you do not already have it on your computer.
* Set the correct `CYCLONEDDS_HOME` via `export CYCLONEDDS_HOME="your_path_here/cyclonedds/install"`. You should add this path to your environment e.g. via your `.zshrc`. 

```bash
uv run src/run.py unitree
```

OM1 will control a safe and limited subset of motions (such as `stretch` and `sit down`). You can also manually control the dog via the game controller. Press:

* A to stand up
* B to sit down
* X to shake paw
* Y to stretch  

Allowing the dog to `move`, `pounce`, and `run` requires **you** to add this functionality. **Warning: If you add additional movement capabilities, this is at your own risk. Due to the autonomous nature of the system, we recommend to perform such testing in the absence of squirrels, cats, rabbits, or small children (assuming you are providing a `dog` prompt)**. 

#### Installing CycloneDDS

First, build and install `CycloneDDS`. You can read more about CycloneDDS [here](https://index.ros.org/p/cyclonedds/). `CycloneDDS` works on Mac, Linux, and PC.

> [!NOTE]
> On Mac, you will need `cmake`, which you can install via `brew install cmake`.

To build and install `CycloneDDS`, run:
```bash
git clone https://github.com/eclipse-cyclonedds/cyclonedds -b releases/0.10.x 
cd cyclonedds && mkdir build install && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install -DBUILD_EXAMPLES=ON
cmake --build . --target install
```

Once you have done this, as stated above, set the correct `CYCLONEDDS_HOME` via `export CYCLONEDDS_HOME="your_path_here/cyclonedds/install"`. You should add this path to your environment e.g. via your `.zshrc`. 

#### Unitree Go2 Air Ethernet Setup

Connect the Unitree Go2 Air to your development machine with an Ethernet cable. Then, set the network adapter setting. Open the network settings and find the network interface that is connected to the Go2 Air. In IPv4 setting, change the IPv4 mode to `manual`, set the address to `192.168.123.99`, and set the mask to `255.255.255.0`. After completion, click `apply` (or equivalent) and wait for the network to reconnect. Finally provide the name of the network adapter in the `.env`, such as `UNITREE_WIRED_ETHERNET=eno0`.

#### Unitree Go2 Air Common Problems

*channel factory init error*: If you see a `channel factory init error`, then you have not set the correct network interface adapter - the one you want to use is the network interface adapter *on your development machine - the computer you are currently sitting in front of* that is plugged into the Unitree quadruped (which has its own internal RockChip computer and network interface, which is *not* relevant to you right now). The ethernet adapter - such as `eno0` or `en0` - needs to be set in the `.env`, for example, `UNITREE_WIRED_ETHERNET=en0`.

*"nothing is working"* There are dozens of potential reasons "nothing is working". The first step is to test your ability to `ping` the quadruped:
```bash
ping 192.168.123.99
```

Assuming you can `ping` the robot, then text the `cycloneDDS` middleware. From `cycloneDDS/build`:
```bash
# send some pings
./bin/RoundtripPing 0 0 0
```

In another terminal, receive those pings and send them right back:
```bash
./bin/RoundtripPong
``` 

> [!NOTE]
> On Mac, you will need to `allow incoming connections` for the applications (RoundtripPing and RoundtripPong) - just "allow" the functionality in the security popup at first use.

You should see roundtrip timing data. If all of that works, then open an issue in the repo and we will help you to work though the fault tree to get you started.

## CLI Commands

The main entry point is `src/run.py` which provides the following commands:

- `start`: Start an agent with a specified config
  ```bash
  python src/run.py start [config_name] [--debug]
  ```
  - `config_name`: Name of the config file (without .json extension) in the config directory
  - `--debug`: Optional flag to enable debug logging

## Developer Guide

### Project Structure

```
.
├── config/               # Agent configuration files
├── src/
│   ├── actions/          # Agent outputs/actions/capabilities
│   ├── fuser/            # Input fusion logic
│   ├── inputs/           # Input plugins (e.g. VLM, audio)
│   ├── llm/              # LLM integration
│   ├── providers/        # ????
│   ├── runtime/          # Core runtime system
│   ├── simulators/       # Virtual endpoints such as `RacoonSim`
│   └── run.py            # CLI entry point
```

### Adding New Actions

Actions are the core capabilities of an agent. For example, for a robot, these capabilities are actions such as movement and speech. Each action consists of:

1. Interface (`interface.py`): Defines input/output types.
2. Implementation (`implementation/`): Business logic, if any. Otherwise, use passthrough.
3. Connector (`connector/`): Code that connects `omOS` to specific virtual or physical environments, typically through middleware (e.g. custom APIs, `ROS2`, `Zenoh`, or `CycloneDDS`)

Example action structure:

```
actions/
└── move_{unique_hardware_id}/
    ├── interface.py      # Defines MoveInput/Output
    ├── implementation/
    │   └── passthrough.py
    └── connector/
        ├── ros2.py      # Maps data/commands to middleware and ROS2
        ├── zenoh.py
        └── unitree.py
```

In general, each robot will have specific capabilities, and therefore, each action will be hardware specific.

*Example*: if you are adding support for the Unitree G1 Humanoid version 13.2b, which supports a new movement subtype such as `dance_2`, you could name the updated action `move_unitree_g1_13_2b` and select that action in your `unitree_g1.json` configuration file.

### Configuration

Agents are configured via JSON files in the `config/` directory. Key configuration elements:

```json
{
  "hertz": 0.5,
  "name": "agent_name",
  "system_prompt": "...",
  "agent_inputs": [
    {
      "type": "VlmInput"
    }
  ],
  "cortex_llm": {
    "type": "OpenMindLLM",
    "config": {
      "base_url": "...",
      "api_key": "...",
    }
  },
  "simulators": [
    {
      "type": "BasicDog"
    }
  ],
  "agent_actions": [
    {
      "name": "move",
      "implementation": "passthrough",
      "connector": "ros2"
    }
  ]
}
```

* **Hertz** Defines the base tick rate of the agent. This rate can be overridden to allow the agent to respond quickly to changing environments using event-triggered callbacks through real-time middleware.

* **Name** A unique identifier for the agent.

* **System Prompt** Defines the agent’s personality and behavior. This acts as the system prompt for the agent’s operations.

* **Cortex LLM** Configuration for the language model (LLM) used by the agent.

  - **Type**: Specifies the LLM plugin.

  - **Config**: Optional configuration for the LLM, including the API endpoint and API key. If no API key is provided, the LLM operates with a rate limiter with the OpenMind's public endpoint.

OpenMind OpenAI Proxy endpoint is [https://api.openmind.org/api/core/openai](https://api.openmind.org/api/core/openai)
  
OpenMind DeepSeek Proxy endpoint is [https://api.openmind.org/api/core/deepseek](https://api.openmind.org/api/core/deepseek)

```json
"cortex_llm": {
  "type": "OpenMindLLM",
  "config": {
    "base_url": "...", // Optional: URL of the LLM endpoint
    "api_key": "..."   // Optional: API key from OpenMind
  }
}
```

#### Simulators

Lists the simulation modules used by the agent. These define the simulated environment or entities the agent interacts with.

```json
"simulators": [
  {
    "type": "BasicDog"
  }
]
```

#### Agent Actions

Defines the agent’s available capabilities, including action names, their implementation, and the connector used to execute them.

```json
"agent_actions": [
  {
    "name": "move", // Action name
    "implementation": "passthrough", // Implementation to use
    "connector": "ros2" // Connector handler
  }
]
```

### Runtime Flow

1. Input plugins collect data (vision, audio, etc.)
2. The Fuser combines inputs into a prompt
3. The LLM generates commands based on the prompt
4. The ActionOrchestrator executes commands through actions
5. Connectors map OM1 data/commands to external data buses and data distribution systems such as custom APIs, `ROS2`, `Zenoh`, or `CycloneDDS`.

### Development Tips

1. Use `--debug` flag for detailed logging
2. Add new input plugins in `src/input/plugins/`
3. Add new LLM integrations in `src/llm/plugins/`
4. Test actions with the `passthrough` implementation first
5. Use type hints and docstrings for better code maintainability
6. Run `uv run ruff check . --fix` and `uv run black .` check/format your code. 

## Environment Variables

- `OPENMIND_API_KEY`: The API key for OpenMind endpoints. This is mandatory if you want to use OpenMind endpoints without rate limiting.
- `ETH_ADDRESS`: The Ethereum address of agent, prefixed with `Ox`. Example: `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045`. Only relevant if your agent has a wallet.
- `UNITREE_WIRED_ETHERNET`: Your network adapter that is connected to a Unitree robot. Example: `eno0`. Only relevant if your agent has a physical (robot) embodiment. You can set this to "SIM" to debug some limited functionality.

### Core operating principle of the system

The system is based on a loop that runs at a fixed frequency of `self.config.hertz`. This loop looks for the most recent data from various sources, fuses the data into a prompt, sends that prompt to one or more LLMs, and then sends the LLM responses to virtual agents or physical robots.

```python
# cortex.py
    async def _run_cortex_loop(self) -> None:
        while True:
            await asyncio.sleep(1 / self.config.hertz)
            await self._tick()

    async def _tick(self) -> None:
        finished_promises, _ = await self.action_orchestrator.flush_promises()
        prompt = self.fuser.fuse(self.config.agent_inputs, finished_promises)
        if prompt is None:
            logging.warning("No prompt to fuse")
            return
        output = await self.config.cortex_llm.ask(prompt)
        if output is None:
            logging.warning("No output from LLM")
            return

        logging.debug("I'm thinking... ", output)
        await self.action_orchestrator.promise(output.commands)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Add your license information]
