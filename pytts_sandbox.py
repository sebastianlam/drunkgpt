import pyttsx3
import threading
import queue, os, time

sentences = []
running = True
count = 0

def status_signal(focus):
    if len(focus) == 0:
        return 'pause'
    else: return 'mid'



def text_to_speech():
    # global running
    # engine = pyttsx3.init()
    # global count
    # global sentences
    # def onStart(name):
    #     print('starting', name)
    # def onWord(name, location, length):
    #     print('word', name, location, length)
    # def onEnd(name, completed):
    #     print('finishing', name, completed, count)
    #     if name == 'init':
    #         engine.say(sentences.pop(), 'init')
    #     elif name == 'pause':
    #         engine.endLoop()
    # engine = pyttsx3.init()
    # engine.connect('started-utterance', onStart)
    # engine.connect('started-word', onWord)
    # engine.connect('finished-utterance', onEnd)
    # engine.say('Right lets chop some heads off my mateys.', 'init')
    # engine.startLoop()
    while True:
        if len(sentences) > 0:
            os.system(f"say {sentences.pop()}")
        else:
            time.sleep(0.5)


def add_sentence(sentence):
    sentences.append(sentence)
    print(sentences, flush=True)


def sentences_process():
    global running
    while True:
        sentence = input("Enter a new sentence (type 'exit' to quit): ")

        if sentence.lower() == 'exit':
            running = False
            break
        add_sentence(sentence)
        print(sentences, flush=True)


def main():
    initial_sentences = [
        "This is the first sentence.",
        "This is the second sentence.",
        "This is the third sentence.",
        "This is the fourth sentence.",
        "This is the fifth sentence.",
    ]

    for sentence in initial_sentences:
        add_sentence(sentence)

    sentences_thread = threading.Thread(target=sentences_process)
    sentences_thread.start()
    voice_thread = threading.Thread(target=text_to_speech)
    voice_thread.start()
    sentences_thread.join()
    voice_thread.join()
    


if __name__ == "__main__":
    main()