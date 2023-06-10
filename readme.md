# CHAT SCRIPT BIOLERPLATE

## GLOBAL DEPENDENCIES

```sh
brew install portaudio gh
```

## DEV SETUP

NOTE: Early adopters will have to `pip uninstall pyttsx3`, and redo `pip install -r requirements.txt` to replace a broken package with its functional fork.

Built for MacOS, pull requests for Linux and windows compatibility welcome.

### INITIAL INSTALLATION

```sh
brew install portaudio gh pyenv 
# install poetry, see: https://python-poetry.org/docs/#installing-with-the-official-installer
gh repo clone sebastianlam/drunkgpt
cd drunkgpt
poetry install  #create environment
poetry shell
export OPENAI_API_KEY=<YOUR_KEY>    #REPLACE <YOUR_KEY> WITH YOUR OPENAI_API_KEY FROM https://platform.openai.com/account/api-keys
poetry run python main.py
```

### SUBSEQUENT DEVELOPMENT

```sh
git pull
export OPENAI_API_KEY=<YOUR_KEY>            #set YOUR OPENAI_API_KEY
poetry shell
poetry run python main.py
make git m="commit message"                 #one line commit
```

## FEATURES

### Persona/bot selector

### Speech recognition with **`Wisper`**

### Text to speech with `py3-tts` ~~**`pyttsx3`**~~

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

### in the works

#### Async TTS

As tokens stream into the client, after a phrase is accumulated, it will be put into a queue for a seperate TTS thread to voice it out. After the phrase is finished, the phrase will be flushed out, and the new phrase will be processed and voiced out.

#### start and end tone for voice input

#### multi agent chat

#### api access for audited access

```python
    import io, sys
    # master context
    master = {
        "parties": {
            "host": "Brian"
            "guest": "Goop"}
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
