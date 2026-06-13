# LinguaKlang

LinguaKlang is a Telegram bot that generates themed vocabulary lists and creates pronunciation audio to help language learning.

## Features

- Generate vocabulary by topic
- Translate words between languages
- Create pronunciation audio files
- Repeat target language words for memorization
- Cache generated audio files

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/jero98772/LinguaKlang
cd LinguaKlang
uv sync
````

## Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and **set your Telegram bot token** and other settings.

## Running

Start the bot with:

```bash
docker compose up -d

uv run main.py
```

## Usage

Send a message to the bot in the following format:

```text
<theme>,<native language>,<target language>,[number of words]
```

Example:

```text
animals,English,Spanish,10
```

This generates 10 vocabulary pairs about animals and produces an audio file with pronunciations.

## Requirements

* Python 3.11+
* Ollama running locally
* Telegram Bot Token

