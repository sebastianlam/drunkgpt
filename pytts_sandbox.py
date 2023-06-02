import pyttsx3
import threading
import queue

sentences = queue.Queue()
running = True


def text_to_speech():
    global running
    engine = pyttsx3.init()

    def onEnd(name, completed):
        if not sentences.empty():
            sentence = sentences.get()
            engine.say(sentence, name)
            print('1', flush=True)
        print('2', flush=True)

    engine.connect('finished-utterance', onEnd)

    while running or not sentences.empty():
        if not sentences.empty():
            sentence = sentences.get()
            engine.say(sentence, sentence)
            engine.runAndWait()
            print('3', flush=True)
        print('4', flush=True)


def add_sentence(sentence):
    sentences.put(sentence)


def add_sentences_process():
    global running
    while True:
        sentence = input("Enter a new sentence (type 'exit' to quit): ")

        if sentence.lower() == 'exit':
            running = False
            break
        add_sentence(sentence)


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

    speech_thread = threading.Thread(target=text_to_speech)
    speech_thread.start()

    add_sentences_thread = threading.Thread(target=add_sentences_process)
    add_sentences_thread.start()

    add_sentences_thread.join()
    speech_thread.join()


if __name__ == "__main__":
    main()