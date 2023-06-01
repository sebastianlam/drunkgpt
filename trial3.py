import pyttsx3
import threading
import time

sentences = [
    "This is the first sentence.",
    "This is the second sentence.",
    "This is the third sentence.",
    "This is the fourth sentence.",
    "This is the fifth sentence.",
]

lock = threading.Lock()
new_sentence = threading.Condition(lock)
running = True

def text_to_speech():
    global running
    engine = pyttsx3.init()
    engine.startLoop(False)

    while running:
        with new_sentence:
            if not sentences:
                new_sentence.wait()

            if not running:
                break

            sentence = sentences.pop(0)

        engine.say(sentence)
        while engine.isBusy():
            engine.iterate()
            time.sleep(0.1)

def add_sentence(sentence):
    with new_sentence:
        sentences.append(sentence)
        new_sentence.notify()

def add_sentences_process():
    global running
    while True:
        time.sleep(0.1)
        sentence = input("Enter a new sentence (type 'exit' to quit): ")

        if sentence.lower() == 'exit':
            with new_sentence:
                running = False
                new_sentence.notify()
            break

        add_sentence(sentence)

def main():
    speech_thread = threading.Thread(target=text_to_speech)
    speech_thread.start()

    add_sentences_thread = threading.Thread(target=add_sentences_process)
    add_sentences_thread.start()

    speech_thread.join()
    add_sentences_thread.join()

if __name__ == "__main__":
    main()