import random
random.seed(42)

from ai2thor.controller import Controller
from ai2thor.controller import RECEPTACLE_OBJECTS


controller = Controller()
controller.reset('FloorPlan21')

objects = controller.last_event.metadata['objects']
receptacles= [obj["objectType"] for obj in objects if obj["receptacle"]]
receptacles = set(receptacles)
# receptacles.remove("Drawer")
receptacles.remove("Cabinet")
receptacles.remove("Fridge")
receptacles.remove("Microwave")
receptacles =list(receptacles)
# print(receptacles)
controller.step(
    action="InitialRandomSpawn",
    randomSeed=4342333,
    forceVisible=False,
    numPlacementAttempts=5,
    placeStationary=False,
    numDuplicatesOfType = [
        {
            "objectType": "Fork",
            "count": 2
        },
        {
            "objectType": "Potato",
            "count": 2
        },
                {
            "objectType": "Egg",
            "count": 2
        },
        {
            "objectType": "Tomato",
            "count": 2
        },
        {
            "objectType": "PepperShaker",
            "count": 2
        },
        {
            "objectType": "Apple",
            "count": 2
        },
        {
            "objectType": "Lettuce",
            "count": 2
        },
        {
            "objectType": "Bread",
            "count": 2
        },
        {
            "objectType": "Potato",
            "count": 2
        },
        {
            "objectType": "Mug",
            "count": 2
        },
    {
        "objectType": "Bowl",
        "count": 2
    },
    {
        "objectType": "Plate",
        "count": 2
    },
    {
        "objectType": "Knife",
        "count": 2
    },
                {
        "objectType": "Pot",
        "count": 2
    }
    ],
    excludedReceptacles=receptacles
)
   
objects = controller.last_event.metadata['objects']
print(objects[0].keys())
receptacles_og= [obj["objectType"] for obj in objects if (obj["receptacle"] and obj["openable"]) ]
print(receptacles_og)
      
controller.interact()

#Floor4 =['Drawer', 'Drawer', 'Drawer', 'Cabinet', 'Drawer', 'Drawer', 'Drawer', 'Cabinet', 'Fridge', 'Microwave']
#Floor9= ['Cabinet', 'Cabinet', 'Cabinet', 'Drawer', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Drawer', 'Drawer', 'Drawer', 'Cabinet', 'Drawer', 'Drawer', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Drawer', 'Drawer', 'Cabinet', 'Drawer', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Drawer', 'Drawer', 'Cabinet', 'Fridge', 'Microwave']
#Floor2=['Cabinet', 'Drawer', 'Drawer', 'Drawer', 'Drawer', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Drawer', 'Drawer', 'Cabinet', 'Drawer', 'Drawer', 'Drawer', 'Cabinet', 'Drawer', 'Cabinet', 'Drawer', 'Drawer', 'Drawer', 'Cabinet', 'Microwave', 'Fridge']
#Floor3 =['Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Drawer', 'Drawer', 'Fridge', 'Microwave', 'Drawer', 'Drawer', 'Drawer', 'Drawer', 'Drawer', 'Drawer']
#Floor5 = ['Drawer', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Drawer', 'Cabinet', 'Cabinet', 'Drawer', 'Cabinet', 'Microwave', 'Fridge']
#Floor2 = ['Drawer', 'Drawer', 'Drawer', 'Cabinet', 'Drawer', 'Drawer', 'Cabinet', 'Drawer', 'Cabinet', 'Drawer', 'Cabinet', 'Cabinet', 'Cabinet', 'Cabinet', 'Drawer', 'Cabinet', 'Drawer', 'Cabinet', 'Microwave', 'Fridge']
