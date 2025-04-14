# import csv
from math import sin

from datasim import Plot, Resource, simtime, World, XYPlotData
# from .patient import Patient


class ICU(World):
    overview: XYPlotData
    beds: Resource

    def __init__(self):
        super().__init__("ICU world")
        self.overview = XYPlotData(title="ICU bezetting")

        self.beds = Resource(self, "icu_beds", "bed", 4)

        self.add_plot(Plot("overview", self.overview))

        # for row in csv.reader(open("simulatiedata.csv")):
        #     if(not (row[0]).isnumeric()):
        #         continue
        #     self.add(Patient(row[0], ))

    def post_entities_tick(self):
        self.overview.append(simtime.seconds(), sin(simtime.seconds() * 5.0))
