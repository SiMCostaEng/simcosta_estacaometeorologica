class MyDevice:
    def __init__(self):
        self.channels = {}

    def config_channel(self, channel_index: int, ADC: int, PORT: int, param_in_min: float, param_in_max: float, param_out_min: float, param_out_max: float):
        self.channels[channel_index] = {
            "ADC": ADC,
            "PORT": PORT,
            "param_in_min": param_in_min,
            "param_in_max": param_in_max,
            "param_out_min": param_out_min,
            "param_out_max": param_out_max
        }

    def __str__(self):
        return str(self.channels)

# Exemplo de uso
device = MyDevice()
device.config_channel(0, 1, 2, 0.0, 10.0, 0.0, 5.0)
print(device)