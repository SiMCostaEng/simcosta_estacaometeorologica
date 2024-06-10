from time import sleep


class State0:
    def __init__(self):
        self.name = '0'

    def transition(self, input_var):
        if input_var == 0:
            return State0()
        elif input_var == 1:
            return StateWait.wait()
        else:
            print('erro')
            return State0()
        
class StateWait:
    def __init__(self):
        self.name = 'Wait'
        
        
    def transition(self, input_var):
        if input_var == 1:
            return StateWait.wait()
        elif input_var == 2:
            return StateRead.read()
        else:
            print('erro')
            return State0()
        
    def wait():
        print('going to sleep')
        sleep(5)
        print('waking up')
        input_var=2
        return StateWait().transition(input_var)     

class StateRead:
    def __init__(self):
        self.name = 'Read'

    def transition(self, input_var):
        if input_var == 2:
            return StateRead.read()
        elif input_var == 3:
            return StateSend.send()
        else:
            print('erro')
            return State0()
        
    def read():
        print('leu')
        sleep(1)
        input_var=3
        return StateRead().transition(input_var)
    
class StateSend:
    def __init__(self):
        self.name = 'Send'

    def transition(self, input_var):
        if input_var == 3:
            return StateSend.send()
        elif input_var == 4:
            return StateErase.erase()
        else:
            print('erro')
            return State0()
        
    def send():
        print('enviou')
        sleep(1)
        input_var=4
        return StateSend().transition(input_var)
    
class StateErase:
    def __init__(self):
        self.name = 'Erase'

    def transition(self, input_var):
        if input_var == 4:
            return StateErase()
        elif input_var == 0:
            return State0()
        else:
            print('erro')
            return State0()
        
    def erase():
        print('apagou')
        sleep(1)
        input_var=0
        return StateErase().transition(input_var)
    
# Função principal do programa
def main():
    # Inicializando a máquina de estados com o estado A
    current_state = State0()

    while True:
        global input_var
        input_var = int(input("Digite um número de 0 a 4 (-1 para sair): "))
        if input_var == -1:
            break

        # Fazendo a transição de estado com base no input_var
        current_state = current_state.transition(input_var)
        print("Estado atual:", current_state.name)


# Executando a função principal
if __name__ == "__main__":
    main()

