import machine

interruptCounter=0
totalInterruptsCounter=0

timer=machine.Timer(0)

def handlerInterrupt(Timer):
        global interruptCounter
        interruptCounter = interruptCounter + 1
        print("oi")
        
timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=handlerInterrupt) #period=1000, ou seja, a interrupção acontece uma vez por segundo; mode=machine.Timer.PERIODIC pois acontece em loop, a cada 1000 ms; callback=handlerInterrupt ou seja, a função que vai acontecer quando a interrupção for chamada

while True:
    if interruptCounter > 0:
        state = machine.disable_irq()
        interruptCounter = interruptCounter - 1
        machine.enable_irq(state)
        
        totalInterruptsCounter = totalInterruptsCounter + 1
        print("interrupt has occurred: "+ str(totalInterruptsCounter))