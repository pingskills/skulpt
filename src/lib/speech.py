import csinsc

def say(text, voice = 0):
    csinsc.say(text, voice)
    
def listen(text = ""):
    print(text, end= "")
    csinsc.listen()
    while csinsc.isListening():
        continue
    response = csinsc.getFinalTranscript()
    print(response)
    return response