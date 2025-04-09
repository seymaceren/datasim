from math import sin

from datasim import simtime
from datasim import World
from datasim import Plot


class ICU(World):
    def __init__(self):
        super().__init__("ICU world")
        self.overview = Plot("overview", "ICU bezetting", ([], [], "line"))

        # self.beds = Bed()
        # self.beds.set_count(4)
        # add_resource(self.beds)

        self.add_plot(self.overview)

    def post_entities_tick(self):
        self.overview.append(0, simtime.seconds(), sin(simtime.seconds() * 5.0))
