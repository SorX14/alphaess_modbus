import asynciominimalmodbus
import asyncio
import json

class Reader:
    instrument: asynciominimalmodbus
    mapping: list

    def __init__(self, decimalAddress=85, serial='/dev/serial0', debug=False, baud=9600, json_file=None) -> None:
        self.instrument = asynciominimalmodbus.AsyncioInstrument(serial, decimalAddress, debug=debug)
        self.instrument.serial.baudrate = baud
        self.instrument.serial.timeout = 1

        # Load register JSON
        if json is None:
            raise TypeError("No JSON file supplied")

        try:
            f = open(json_file)
            self.mapping = json.load(f)
        except OSError:
            raise TypeError("Could not find alphaess_registers.json")

    async def get_units(self, name):
        register = await self.get_definition(name)
        return register['units']

    async def get_value(self, name):
        register = await self.get_definition(name)
        
        if register['type'] == "long":
            val = await self.instrument.read_long(int(register['address']), 3, register['signed'])
        else:
            val = await self.instrument.read_register(int(register['address']), 0, 3, register['signed'])

        if register['decimals'] > 0:
            divisor = 10 ** register['decimals']
            val = val / float(divisor)
           
        return val
    
    async def get_formatted_value(self, name):
        return f"{self.getValue(name)}{self.getUnits()}"

    async def get_definition(self, name):
        register = next((item for item in self.mapping if item["name"] == name), None)
        if register is None:
            raise TypeError(f"Register name not found: {name!r}")
        return register