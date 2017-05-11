myvar = {1:10,2:20}

class myclass():
    def __init__(self):
        myvar[1]=100
        print myvar
        self.printvar()

    def printvar(self):
        print myvar


k = myclass()
