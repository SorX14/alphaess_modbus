class Formatter:
    def system_mode(self, val) -> str:
        if val == 1:
            return "AC Mode"
        if val == 2:
            return "DC Mode"
        if val == 3:
            return "Hybrid Mode"
        return "🤷"

    def battery_type(self, val) -> str:
        if val == 2:
            return "M4860"
        if val == 3:
            return "M48100"
        if val == 13:
            return "48112-P"
        if val == 16:
            return "Smile5-BAT"
        if val == 24:
            return "M4856-P"
        if val == 33:
            return "Smile-BAT-5.8P"
        
    def local_ip(self, val) -> str:
        return self.ip_formatter(self, val)

    def subnet_mask(self, val) -> str:
        return self.ip_formatter(self, val)

    def gateway(self, val) -> str:
        return self.ip_formatter(self, val)

    def ip_formatter(self, val) -> str:
        bytes = val.to_bytes(4, byteorder='big')
        return f"{int(bytes[0])}.{int(bytes[1])}.{int(bytes[2])}.{int(bytes[3])}"

    def system_time_year_month(self, val) -> str:
        bytes = val.to_bytes(2, byteorder='big')
        # might be a year 3000 bug here :D
        return f"20{int(bytes[0])}-{int(bytes[1])}"

    def system_time_day_hour(self, val) -> str:
        bytes = val.to_bytes(2, byteorder='big')
        return f"{int(bytes[0])} {int(bytes[1])}"

    def system_time_minute_second(self, val) -> str:
        bytes = val.to_bytes(2, byteorder='big')
        return f"{int(bytes[0])}:{int(bytes[1])}"

    def ems_sn_byte1_2(self, val) -> str:
        return self.ascii(self, val)
    
    def ems_sn_byte3_4(self, val) -> str:
        return self.ascii(self, val)

    def ems_sn_byte5_6(self, val) -> str:
        return self.ascii(self, val)

    def ems_sn_byte7_8(self, val) -> str:
        return self.ascii(self, val)

    def ems_sn_byte9_10(self, val) -> str:
        return self.ascii(self, val)

    def ems_sn_byte11_12(self, val) -> str:
        return self.ascii(self, val)
    
    def ems_sn_byte13_14(self, val) -> str:
        return self.ascii(self, val)

    def ems_sn_byte15_16(self, val) -> str:
        return self.ascii(self, val)

    def ascii(self, val) -> str:
        return val.to_bytes(2, byteorder='big').decode("ascii").rstrip('\x00')