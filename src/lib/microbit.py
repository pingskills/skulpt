import microBit

class Microbit:
    def __init__(self, blockUntilConnect = True):
        self.uBit = microBit.Microbit()
        if blockUntilConnect:
            while not self.uBit.isConnected():
                continue        
            self.name = self.uBit.getName()
        
    def setText(self, text):
        self.uBit.setText(text)
        
    def getButtonA(self):
        return self.uBit.getButtonA();
        
    def waitForButtonA(self):
        while self.uBit.getButtonA() == 0:
            continue