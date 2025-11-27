# server.py — Mesa 2.x compatible
from mesa.visualization import ModularServer
from mesa.visualization.modules import ChartModule
from model import BuildingModel

# Chart definition
chart = ChartModule(
    [
        {"Label": "Avg_Wait_Time", "Color": "#FF0000"},
        {"Label": "Avg_Satisfaction", "Color": "#00FF00"},
        {"Label": "Crowding", "Color": "#0000FF"},
    ],
    data_collector_name="datacollector",
)

# IMPORTANT: Mesa 2.x uses:
# ModularServer(model_cls, visualization_elements, name=None, model_params=None)

server = ModularServer(
    BuildingModel,                     # model class
    [chart],                           # visualization modules
    "VTS Hybrid Simulation - Rowland PhD",   # name of the visualisation
    {
        "N_floors": 6,
        "N_elevators": 2,
        "peak_hour": True,
        "backup_power": True,
        "door_time": 10.6,
        "capacity": 16,
        "vibration": 1.01,
        "noise": 55.9,
        "speed": 3.0,
    },
)

server.port = 8521
server.launch()
