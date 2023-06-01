# # the expexted behaviour of the code is as following:

# acronyms: TTS = text to speech

# There is an array of sentences, and new sentences will be added to the back of the array, independent of the following TTS process that uses and deletes the element at the 0th index of the sentences array.
# The TTS function, independently in a diffrent thread, checks if the array is empty, and if not, execute on the new first sentence, which is the element at the 0th index of the sentences array, conducts text to speech, and importantly is not interrupted while it is not finished saying that sentence, and when the speech process finishes (there might be a process that signals that), delete the said first sentence in the array.
# It then start again, execute on the new first sentence, the element at the 0th index, which used to be the second sentence in the previous loop cycle.
# The starting sentences will each be iterated on in a loop, and will only stop and wait for new sentences when the sentences array is empty.
# The sentence prompt on the other hand is always visible, and adds to the sentences array when the user so pleases.

# The code still does not do text to speech as intended.
# It now goes through the first sentence automatically, and presents the text prompt while executing, as intended
# But it stopped at the first sentence, and no other sentence is voiced out.
# The text prompt is still there but it doesn't do anything; either the add to array doesn't work, or that it does work, but the TTS loop can't do anything with it.
# Just to remind you that this is the entire python file. Make radical changes if need be.
# And add print statements liberally to help the debuging process. MAke the print statements meaningful.

import threading
import time
import queue
from gtts import gTTS
import os

sentences = queue.Queue()
running = True

def text_to_speech():
    global running

    while running:
        if not sentences.empty():
            sentence = sentences.get()
            print(f"<<[]>> Speaking: {sentence}", flush=True)
            tts = gTTS(text=sentence, lang='en')
            tts.save("temp.mp3")
            os.system("mpg321 temp.mp3")
            os.remove("temp.mp3")
        else:
            time.sleep(0.1)

    print("<<[]>> Text-to-speech thread has stopped.", flush=True)

def add_sentence(sentence):
    sentences.put(sentence)
    print(f"<<[]>> Added sentence: {sentence}", flush=True)

def add_sentences_process():
    global running
    while True:
        print("<<[]>> new loop", flush=True)
        sentence = input("Enter a new sentence (type 'exit' to quit): ")

        if sentence.lower() == 'exit':
            running = False
            break
        print("<<[]>> About to add sentence", flush=True)
        add_sentence(sentence)

def main():
    for sentence in [
        "This is the first sentence.",
        "This is the second sentence.",
        "This is the third sentence.",
        "This is the fourth sentence.",
        "This is the fifth sentence.",
    ]:
        add_sentence(sentence)

    speech_thread = threading.Thread(target=text_to_speech)
    speech_thread.start()

    add_sentences_thread = threading.Thread(target=add_sentences_process)
    add_sentences_thread.start()

    speech_thread.join()
    add_sentences_thread.join()

if __name__ == "__main__":
    main()

# AS a side note, and it may or may not be important, the following is from the offical documentation of pyttsx3, use if appropriate:

# Running a driver event loop
# 
# engine = pyttsx3.init()
# def onStart(name):
#    print 'starting', name
# def onWord(name, location, length):
#    print 'word', name, location, length
# def onEnd(name, completed):
#    print 'finishing', name, completed
#    if name == 'fox':
#       engine.say('What a lazy dog!', 'dog')
#    elif name == 'dog':
#       engine.endLoop()
# engine = pyttsx3.init()
# engine.connect('started-utterance', onStart)
# engine.connect('started-word', onWord)
# engine.connect('finished-utterance', onEnd)
# engine.say('The quick brown fox jumped over the lazy dog.', 'fox')
# engine.startLoop()

# Using an external event loop
# 
# engine = pyttsx3.init()
# engine.say('The quick brown fox jumped over the lazy dog.', 'fox')
# engine.startLoop(False)
# # engine.iterate() must be called inside externalLoop()
# externalLoop()
# engine.endLoop()