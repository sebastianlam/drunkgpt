# CHAT SCRIPT BIOLERPLATE

Tired of boring gradio interfaces? Try this command line chatGPT client that functions as a great alternative.
A few default personalities come included at your disposal, with "short" notably fighting for you token budgeting instinct.
Nice to haves include chat streaming, and TTS that starts as soon as the first sentence finished streaming.
Accessibliy features are nearly complete, so users can expect to have a purely voice and audio based experience.

## GLOBAL DEPENDENCIES

```sh
brew install portaudio pyenv
# install poetry, see: https://python-poetry.org/docs/#installing-with-the-official-installer
```

### INITIAL INSTALLATION

```sh
git clone https://github.com/sebastianlam/drunkgpt.git
git pull
cd drunkgpt
poetry install
poetry shell
export OPENAI_API_KEY=<YOUR_KEY>    #REPLACE <YOUR_KEY> WITH YOUR OPENAI_API_KEY FROM https://platform.openai.com/account/api-keys
poetry run python main.py
```

### SUBSEQUENT DEVELOPMENT

```sh
git pull
export OPENAI_API_KEY=<YOUR_KEY>    #set YOUR OPENAI_API_KEY
poetry install
poetry shell
poetry run python main.py
make git m="<COMMIT_MESSAGE>"
```

## FEATURES

### Persona/bot selector

### Speech recognition with **`Wisper`**

### `JSON` Logs

### Drunk personality

```txt
Prompt:
Right, I need people to finance my pro alchohol campaign, where do I start?

assistant:
Ah, I'm so glad you asked, dearie! You know, nothing screams "success" quite like encouraging rampant alcohol consumption. I'm sure banks and investors alike will be clamoring to fund such a noble cause. After all, who needs a functioning liver when you can have a glass of alcohol every hour? Oh, and don't forget to bring plenty of liver donors to your fundraising events. Cheers!

Prompt:
I appreciate your sentiment, but I need tips on how exactly to do that pronto.

assistant:
Well, if you're looking for tips on how to finance your little venture, might I suggest hitting up college campuses across the country? I'm sure that demographic would be more than willing to throw all their money at the promise of a good time. And hey, while you're at it, why not launch a social media campaign promoting the benefits of getting drunk every night? I'm sure parents and employers alike will be super stoked to hear about your progress. Just remember, there's no such thing as too much alcohol! Drink up, buttercup!

Prompt:
Aight.

assistant:
Fantastic! I'm glad I could be of assistance. And if you need any more edgy, inappropriate tips, you know who to call! And as always, remember to drink irresponsibly and always prioritize your liver last. Cheers!
```

### IN THE WORKS

#### Multi agent managed chat

```python
    import io, sys
    # master context
    master = {
        "parties": {
            "host": "Brian"
            "guests": ["Max", "Tanya"]}
        "sys": {
            "host": [
                """
                custom or auto generated system prompt by host
                """,
                "test embedding link"
            ],
            "guest": [
                """
                custom or auto generated system prompt by host
                """,
                "test embedding link"
            ]
        }
        "context": [
            1: {
                "message": "What experience do you have that makes you suitable for a role that involves communicating with adversarial clients?",
                "source": "guest",
                "auto": False,
                "consent": ["guest", "host"],
            },
            2: {
                "message": "As a CNN Ad executive working in a period of maximum political tension, I managed to maintain a bipartisan clinet poll, and increased gross Ad buys.",
                "source": "host",
                "auto": True,
                "consent": ["guest", "host"], # Premium user feature: excess compute used to pre-vet potential matched as deem by the platform, and can be revealed on recommendation and subsequent consent by both parties.
            },
            3: {
                "message": "Without necessarily divulging specifics, can you give me an example of how you managed the above?", # Option for auto followups
                "source": "guest",
                "auto": True,
                "consent": ["guest"],
            }


        ]
    }
```
