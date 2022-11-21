from fastapi import FastAPI
from alphaess_modbus import Reader
from datetime import datetime

app = FastAPI()

reader: Reader = Reader(debug=False)

@app.get("/GetCustomMenuESSlist")
async def ess_list():
    sn = []
    for i in range(1, 16, 2):
        sn.append(await reader.get_formatted_value(f"ems_sn_byte{i}_{i + 1}"))

    serial = "".join(sn)
    
    battery_type = await reader.get_formatted_value("Battery type")
    mbat = battery_type

    ems_status = ""
    minv = ""

    response = {
        "code": 200,
        "data": [
            {
                "cobat": -1,
                "ems_status": ems_status,
                "mbat": mbat,
                "minv": minv,
                "sys_sn": serial

            }
        ],
        "info": "Success"
    }

    return response


@app.get("/GetLastPowerDataBySN")
async def get_last_power_data_by_sn():
    #pv = await reader.get_value("inverter_power_total")
    #grid = await reader.get_value("total_active_power_grid_meter")
    battery = await reader.get_value("battery_power")

    ppv1 = await reader.get_value("PV1 power")
    ppv2 = await reader.get_value("PV2 power")
    ppv3 = await reader.get_value("PV3 power")
    ppv4 = await reader.get_value("PV4 power")

    pmeter_l1 = await reader.get_value("Active power of A phase(Grid)")
    pmeter_l2 = await reader.get_value("Active power of B phase(Grid)")
    pmeter_l3 = await reader.get_value("Active power of C phase(Grid)")
    soc = await reader.get_value("Battery SOC")

    response = {
        "code": 200,
        "info": "Success",
        "data": {
            "ppv1": ppv1,
            "ppv2": ppv2,
            "ppv3": ppv3,
            "ppv4": ppv4,
            "preal_l1": -1,
            "preal_l2": -1,
            "preal_l3": -1,
            "pmeter_l1": pmeter_l1,
            "pmeter_l2": pmeter_l2,
            "pmeter_l3": pmeter_l3,
            "pmeter_dc": -1,
            "soc": soc,
            "pbat": battery,
            "ev1_power": -1,
            "ev2_power": -1,
            "ev3_power": -1,
            "ev4_power": -1,
            "createtime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ups_model": -1
        }
    }
    return response