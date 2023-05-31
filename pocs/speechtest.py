import pyttsx3
# def onStart(name):
#    print('starting', name)
# def onWord(name, location, length):
#    print('word', name, location, length)
# def onEnd(name, completed):
#    print('finishing', name, completed)
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

engine = pyttsx3.init()
engine.say('The quick brown fox jumped over the lazy dog.', 'fox')
engine.startLoop(True)
# engine.iterate() must be called inside externalLoop()
for x in range(200):
    engine.say('The quick brown fox jumped over the lazy dog.', 'fox')
engine.endLoop()