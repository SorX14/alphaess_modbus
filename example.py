#!/usr/bin/env python3
import logging
import sys
import asyncio
from alphamodbus.alphamodbus import Reader
import traceback

def configureLogger():
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s', datefmt='%a, %d %b %Y %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

async def main():
    logger.debug("Starting reader...")
    reader: Reader = Reader(json_file="alphaess_registers.json")

    while True:
        pv = await reader.get_value("inverter_power_total")
        grid = await reader.get_value("total_active_power_grid_meter")
        battery = await reader.get_value("battery_power")

        load = pv + grid + battery
        logger.info(f"PV: {pv}W GRID: {grid}W USE: {load}W Battery: {battery}W")
    
        await asyncio.sleep(1)
        
if __name__ == "__main__":
    try:
        logger = configureLogger()
        loop = asyncio.run(main())
    except (ValueError, Exception) as e:
        logger.debug(str(e))
        logger.debug(traceback.format_exc())
    except KeyboardInterrupt:
        pass