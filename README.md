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

If you are on mac, you may need to install `pyaudio` manually:

```bash
brew install portaudio
```

2. Set up environment variables:

Edit `.env` with your API keys (e.g. OPENAI_API_KEY). NOTE: an OpenAI api key is required.

```bash
cp .env.example .env
```

3. Run an Hello World agent

This very basic agent uses webcam data to estimate your emotion, generates a fake VLM caption, and sends those two inputs to central LLM. The LLM then returns `movement`, `speech`, and `face` commands, which are displayed in a small `pygame` window. This is windows also shows basic timing debug information so you can see how long each step takes.


```bash
uv run src/run.py spot
```

NOTE: `uv` does many things in the background, such as setting up a good `venv` and downloading any dependencies if needed. Please add new dependencies to `pyproject.toml`.

NOTE: If you are running complex models, or need to download dependencies, there may be a delay before the agent starts.

NOTE: There should be a `pygame` window that pops up when you run `uv run src/run.py spot`. Sometimes the `pygame` window is hidden behind all other open windows - use "show all windows" to find it.

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
├── config/                 # Agent configuration files
├── src/
│   ├── fuser/            # Input fusion logic
│   ├── input/            # Input plugins (e.g. VLM, audio)
│   ├── llm/              # LLM integration
│   ├── actions/          # Agent outputs/actions/capabilities
│   ├── runtime/          # Core runtime system
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
        ├── ros2.py      # Maps omOS data/commands to other ROS2
        ├── zenoh.py
        └── unitree_LL.py
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
    "type": "OpenAILLM",
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

#### Hertz

Defines the base tick rate of the agent. This rate can be overridden to allow the agent to respond quickly to changing environments using event-triggered callbacks through real-time middleware.

```json
"hertz": 0.5
```

#### Name

A unique identifier for the agent.

```json
"name": "agent_name"
```

#### System Prompt

Defines the agent’s personality and behavior. This acts as the system prompt for the agent’s operations.

```json
"system_prompt": "..."
```

#### Cortex LLM

Configuration for the language model (LLM) used by the agent.

- **Type**: Specifies the LLM plugin.

- **Config**: Optional configuration for the LLM, including the API endpoint and API key. If no API key is provided, the LLM operates with a rate limiter with the Openmind's public endpoint.


  > [!NOTE]
  >
  > Openmind OpenAI Proxy endpoint is [https://api.openmind.org/api/core/openai](https://api.openmind.org/api/core/openai)

```json
"cortex_llm": {
  "type": "OpenAILLM",
  "config": {
    "base_url": "...", // Optional: URL of the LLM endpoint
    "api_key": "..."   // Optional: API key can be obtained from Openmind
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

Defines the agent’s available capabilities, including action names, their implementation, and the connector handler used to execute them.

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
5. Connectors map omOS data/commands to external data buses and data distribution systems such as custom APIs, `ROS2`, `Zenoh`, or `CycloneDDS`.

### Core operating principle of the system

The system is not event or callback driven, but is based on a loop that runs at a fixed frequency of `self.config.hertz`. This loop looks for the most recent data from various sources, fuses the data into a prompt, sends that prompt to one or more LLMs, and then sends the LLM responses to virtual or physical robots.


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

### Development Tips

1. Use `--debug` flag for detailed logging
2. Add new input plugins in `src/input/plugins/`
3. Add new LLM integrations in `src/llm/plugins/`
4. Test actions with the `passthrough` implementation first
5. Use type hints and docstrings for better code maintainability

## Environment Variables

Required environment variables:

- `OPENAI_API_KEY`: The API key for OpenAI integration. This is mandatory if you want to use OpenAI’s LLM services without rate limiting.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Add your license information here]
