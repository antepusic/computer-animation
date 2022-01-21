from SCFG import SCFG
from examples import *

BuildingSCFG = SCFG()
BuildingSCFG.parse_least_general_conforming(tall_building, wide_building, wing_building)
BuildingSCFG.mix_up_tops()

for _ in range(3):
    BuildingSCFG.draw_random_production()
