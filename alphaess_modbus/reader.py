import asynciominimalmodbus
import asyncio
import json
from .formatter import Formatter
from pathlib import Path

class Reader:
    instrument: asynciominimalmodbus
    mapping: list
    custom_formatter = None
    debug: bool

    def __init__(self, decimalAddress=85, serial='/dev/serial0', debug=False, baud=9600, json_file=None, formatter=None) -> None:
        self.instrument = asynciominimalmodbus.AsyncioInstrument(serial, decimalAddress, debug=debug)
        self.instrument.serial.baudrate = baud
        self.instrument.serial.timeout = 1

        self.debug = debug

        if formatter is not None:
            self.custom_formatter = formatter

        # Load register JSON
        if json_file is None:
            p = Path(__file__)
            json_file = p.absolute().with_name('registers.json')

        try:
            f = open(json_file)
            self.mapping = json.load(f)
        except OSError:
            raise RuntimeError(f"Could not find JSON file {json_file!r}")
    
    def conform_name(self, name) -> str:
        """ Conform a register name if copied from PDF """
        return name.lower().strip().replace("  ", " ").translate({ord(ch): "_" for ch in ' (-:'}).translate({ord(ch): None for ch in ')'}).replace("___", "_").replace("__", "_")

    async def get_units(self, name) -> str:
        """ Get the units (e.g. 'KWh') for a register if available """
        name = self.conform_name(name)
        register = await self.get_definition(name)
        return register['units']

    async def get_value(self, name) -> int:
        """ Ask inverter for a specific register """
        name = self.conform_name(name)
        register = await self.get_definition(name)
        if self.debug:
            print(f"{name} -> {register['hex']}")
        
        if register['type'] == "long":
            val = await self.instrument.read_long(int(register['address']), 3, register['signed'])
        else:
            val = await self.instrument.read_register(int(register['address']), 0, 3, register['signed'])

        if register['decimals'] > 0:
            divisor = 10 ** register['decimals']
            val = val / float(divisor)
           
        return val
    
    async def get_formatted_value(self, name, use_formatter=True):
        """ 
        Ask inverter for a specific register and add units (if available). 
        Normally returns a str but can be overridden with formatters
        """
        name = self.conform_name(name)
        val = await self.get_value(name)

        if use_formatter is True:
            # Use custom formatter first
            if self.custom_formatter is not None:
                if callable(getattr(self.custom_formatter, name, None)):
                    func = getattr(self.custom_formatter, name)
                    return func(self.custom_formatter, val)

            # Now try internal formatter
            if callable(getattr(Formatter, name, None)):
                func = getattr(Formatter, name)
                return func(Formatter, val)

        units = await self.get_units(name)
        return f"{val}{units}"

    async def get_definition(self, name) -> dict:
        """ Look up name in JSON registers """
        name = self.conform_name(name)
        register = next((item for item in self.mapping if item["name"] == name), None)
        if register is None:
            raise RuntimeError(f"Register name not found: {name!r}")

        # Sanity check the result
        try:
            assert "name" in register
            assert "type" in register
            assert "decimals" in register
            assert "units" in register
        except AssertionError as e:
            raise RuntimeError(f"JSON file has a malformed entry for {name}")

        return register