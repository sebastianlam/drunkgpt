import pyttsx3
import threading
import time

# Array of sentences
sentences = []

# Condition object for synchronization
condition = threading.Condition()

# Initialize pyttsx3 engine
engine = pyttsx3.init()

def process_sentences():
    while True:
        with condition:
            while len(sentences) == 0:
                # Wait for new sentences to arrive
                condition.wait()
            
            # Get the first sentence from the array
            sentence = sentences[0]
            
            def on_end(event):
                # Delete the first sentence from the array
                with condition:
                    del sentences[0]
                
                # Notify waiting threads that a sentence has been processed
                condition.notify_all()
            
            # Set the event handler for when the speech ends
            engine.connect('end-utterance', on_end)
            
            # Convert the sentence to speech
            engine.iterate(sentence)

def add_sentence(sentence):
    with condition:
        sentences.append(sentence)
        # Notify the text-to-speech process that a new sentence has arrived
        condition.notify_all()

# Example usage
# Start the text-to-speech process in a separate thread
speech_thread = threading.Thread(target=process_sentences)
speech_thread.start()

# Start the process that adds sentences in a separate thread
def add_sentences_process():
    while True:
        # Simulate new sentences being added at irregular intervals
        time.sleep(3)  # Wait for 3 seconds
        sentence = input("Enter a new sentence: ")
        add_sentence(sentence)

add_sentences_thread = threading.Thread(target=add_sentences_process)
add_sentences_thread.start()
