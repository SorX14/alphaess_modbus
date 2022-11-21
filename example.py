#!/usr/bin/env python3
import logging
import sys
import asyncio
from alphaess_modbus import Reader
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

    # Override default formatter with one of our own
    class formatter:
        def system_time_year_month(self, val) -> str:
            bytes = val.to_bytes(2, byteorder='big')
            # might be a year 3000 bug here :D
            return f"🚨 {int(bytes[0])}-{int(bytes[1])}"

    reader: Reader = Reader(debug=False, formatter=formatter)

    show_system_details = True

    if show_system_details:
        logger.info("Loading system information...")
        # Built-in formatters
        sn = []
        for i in range(1, 16, 2):
            sn.append(await reader.get_formatted_value(f"ems_sn_byte{i}_{i + 1}"))

        logger.info(f"System SN: {''.join(sn)!r}")

        system_mode = await reader.get_formatted_value("system_mode")
        logger.info(f"System mode: {system_mode!r}")

        capacity = await reader.get_formatted_value("PV Capacity Storage")
        logger.info(f"System capacity: {capacity}")

        local_ip = await reader.get_formatted_value("local_ip")
        logger.info(f"Local IP: {local_ip!r}")
        subnet_mask = await reader.get_formatted_value("subnet_mask")
        logger.info(f"Subnet mask: {subnet_mask!r}")
        gateway = await reader.get_formatted_value("gateway")
        logger.info(f"Gateway: {gateway!r}")

        # Show how we're overriding the built-in formatter with our own
        year_month = await reader.get_formatted_value("system_time_year_month")
        day_hour = await reader.get_formatted_value("system_time_day_hour")
        minute_second = await reader.get_formatted_value("system_time_minute_second")

        logger.info(f"System time: {year_month}-{day_hour}:{minute_second}")

    # Showing how you can copy and paste names from the PDF and they'll be conformed
    inverter_total = await reader.get_formatted_value("Inverter Total PV Energy")
    power_factor = await reader.get_definition("Power factor of A phase(Grid)")

    logger.info(f"Inverter total: {inverter_total}")
    logger.info(f"Power factor definition: {power_factor}")

    while True:
        # Show how to get load
        pv = await reader.get_value("inverter_power_total")
        grid = await reader.get_value("total_active_power_grid_meter")
        battery = await reader.get_value("battery_power")

        load = pv + grid + battery
        logger.info(f"PV: {pv}W GRID: {grid}W USE: {load}W Battery: {battery}W")

        voltage = await reader.get_formatted_value("voltage_of_a_phase_grid")
        frequency = await reader.get_formatted_value("frequency_grid")
        logger.info(f"Grid voltage: {voltage} @ {frequency}")

        # total_energy_fed_to_grid = await reader.get_formatted_value("total_energy_feed_to_grid_grid")
        # total_energy_consumed_from_grid = await reader.get_formatted_value("total_energy_consume_from_grid_grid")
        
        # logger.info(f"Total feed in: {total_energy_fed_to_grid} Total grid consumption: {total_energy_consumed_from_grid}")

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