import asyncio
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
import json
from .formatter import Formatter
from .reader import Reader
from pathlib import Path

class ReaderTCP(Reader):
    instrument: AsyncModbusTcpClient
    mapping: list
    custom_formatter = None
    debug: bool
    slave_id: int

    def __init__(self, ip=None, port=502, slave_id=int(0x55), debug=False, json_file=None, formatter=None) -> None:
        self.instrument = AsyncModbusTcpClient(ip, port=port)
        self.debug = debug
        self.slave_id = slave_id

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
        return name.lower().strip().replace("  ", " ").translate({ord(ch): "_" for ch in ' (-:'}).translate(
            {ord(ch): None for ch in ')'}).replace("___", "_").replace("__", "_")

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

        if self.instrument.connected is False:
            await self.instrument.connect()

        if register['type'] == "long":
            val = await self.instrument.read_holding_registers(int(register['address']), 2, slave=self.slave_id)
            decoder = BinaryPayloadDecoder.fromRegisters(val.registers, byteorder='>', wordorder='>')
            if register['signed'] is True:
                val = decoder.decode_32bit_int()
            else:
                val = decoder.decode_32bit_uint()
        else:
            val = await self.instrument.read_holding_registers(int(register['address']), 1, slave=self.slave_id)
            decoder = BinaryPayloadDecoder.fromRegisters(val.registers, byteorder='>', wordorder='>')
            if register['signed'] is True:
                val = decoder.decode_16bit_int()
            else:
                val = decoder.decode_16bit_uint()

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