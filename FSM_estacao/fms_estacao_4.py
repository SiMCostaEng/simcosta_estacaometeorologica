
class CarbonDioxideProbe:
    def __init__(self, uart_ch):
        self.uart_ch = 1
        self.baudrate = 19200
    
    def inicializar():
        uart_ch=1
        uart.write("R\r\n")
    
    def read():
        global uart, a, uart_ch, CarbonDioxideProbe_info
        
        uart_ch=1
        uart.write("R\r\n")
        if a < 20:
            time.sleep(1)
            CarbonDioxideProbe_info=uart.read()
            #print("CarbonDioxideProbe_info: {}".format(CarbonDioxideProbe_info))
            a+=1
        uart.write("S\r\n")
        return CarbonDioxideProbe_info
    
    def separate(CarbonDioxideProbe_info):
        a=[]
        
        if CarbonDioxideProbe_info != None:
            for word in CarbonDioxideProbe_info.split():
                try:
                    a.append(float(word))
                except ValueError:
                    pass
           
        CarbonDioxideProbe_data = a
        return CarbonDioxideProbe_data
