
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




class Compass:
    def __init__(self, uart_ch):
        self.uart_ch=2
        self.baudrate=4800

    def inicializar():
        uart_ch=2

    def read():
        global uart, a, uart_ch, Compass_info
        if Compass_info != None:
            Compass_info=str(Compass_info)
            Compass_info = get_first_nbr_from_str(Compass_info)
            print(Compass_info)
        return Compass_info
    
    def get_first_nbr_from_str(Compass_info):
        if not input_str and not isinstance(input_str, str):
            return 0
        out_number = ''
        for ele in input_str:
            if (ele == '.' and '.' not in out_number) or ele.isdigit():
                out_number += ele
            elif out_number:
                break
        Compass_data=float(out_number)
        return Compass_data

