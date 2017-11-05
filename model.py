import json
import math
import logging

import matplotlib.pyplot as plt


class Agent:

    def __init__(self, position, **agent_attributes):
        self.position = position
        for attr_name, attr_value in agent_attributes.items():
            setattr(self, attr_name, attr_value)


class Position:

    def __init__(self, longitude_degrees, latitude_degrees):
        self.longitude_degrees = longitude_degrees
        self.latitude_degrees = latitude_degrees

    @property
    def longitude(self):
        return self.longitude_degrees * math.pi / 180

    @property
    def latitude(self):
        return self.latitude_degrees * math.pi / 180


class Zone:

    EARTH_RADIUS_KILOMETERS = 6371
    MIN_LONGITUDE_DEGREES = -180
    MAX_LONGITUDE_DEGREES = 180
    MIN_LATITUDE_DEGREES = -90
    MAX_LATITUDE_DEGREES = 90
    WIDTH_DEGREE = 1
    HEIGHT_DEGREE = 1
    ZONES = []

    def __init__(self, corner1, corner2):
        self.corner1 = corner1
        self.corner2 = corner2
        self.inhabitants = []
        self.logger = logging.getLogger(__name__)

    def contains(self, position):
        return max(self.corner1.longitude_degrees, self.corner2.longitude_degrees) > position.longitude_degrees >= \
               min(self.corner1.longitude_degrees, self.corner2.longitude_degrees) and \
               max(self.corner1.latitude_degrees, self.corner2.latitude_degrees) > position.latitude_degrees >= \
               min(self.corner1.latitude_degrees, self.corner2.latitude_degrees)

    def add_inhabitant(self, inhabitant):
        self.inhabitants.append(inhabitant)

    def population_density(self):
        try:
            return self.population / self.area
        except ZeroDivisionError:
            self.logger.error('Division by zero', exc_info=True)

    def average_agreeableness(self):
        if not self.inhabitants:
            return 0
        # list comprehension
        return sum([inhabitant.agreeableness for inhabitant in self.inhabitants]) / self.population

    def average_income(self):
        if not self.inhabitants:
            return 0
        return sum([inhabitant.income for inhabitant in self.inhabitants]) / self.population

    @property
    def width(self):
        return abs(self.corner2.longitude - self.corner1.longitude) * self.EARTH_RADIUS_KILOMETERS

    @property
    def height(self):
        return abs(self.corner2.latitude - self.corner1.latitude) * self.EARTH_RADIUS_KILOMETERS

    @property
    def area(self):
        return self.width * self.height

    @property
    def population(self):
        return len(self.inhabitants)

    @classmethod
    def _initialize_zones(cls):
        for latitude in range(cls.MIN_LATITUDE_DEGREES, cls.MAX_LATITUDE_DEGREES, cls.HEIGHT_DEGREE):
            for longitude in range(cls.MIN_LONGITUDE_DEGREES, cls.MAX_LONGITUDE_DEGREES, cls.WIDTH_DEGREE):
                bottom_left_corner = Position(longitude, latitude)
                top_right_corner = Position(longitude + cls.WIDTH_DEGREE, latitude + cls.HEIGHT_DEGREE)
                zone = Zone(bottom_left_corner, top_right_corner)
                cls.ZONES.append(zone)
        print(len(cls.ZONES))

    @classmethod
    def find_zone_that_contains(cls, position):

        # PEP8: "For sequences, (strings, lists, tuples), use the fact that empty sequences are false."
        if not cls.ZONES:
            cls._initialize_zones()

        longitude_index = int((position.longitude_degrees - cls.MIN_LONGITUDE_DEGREES)/cls.WIDTH_DEGREE)
        latitude_index = int((position.latitude_degrees - cls.MIN_LATITUDE_DEGREES)/cls.HEIGHT_DEGREE)
        longitude_bins = int((cls.MAX_LONGITUDE_DEGREES - cls.MIN_LONGITUDE_DEGREES)/cls.WIDTH_DEGREE)
        zone_index = longitude_bins * latitude_index + longitude_index
        zone = cls.ZONES[zone_index]

        assert zone.contains(position)
        return zone


class BaseGraph:

    def __init__(self):
        self.title = 'Your Graph Title'
        self.x_label = 'X-axis label'
        self.y_label = 'Y-axis label'
        self.show_grid = True

    def xy_values(self, zones):
        raise NotImplementedError

    def show(self, zones):
        x_values, y_values = self.xy_values(zones)
        plt.plot(x_values, y_values, '.')
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        plt.title(self.title)
        plt.grid(self.show_grid)
        plt.show()


class AgreeablenessGraph(BaseGraph):

    def __init__(self):
        super().__init__()
        self.title = 'Nice people live in the countryside'
        self.x_label = 'population density'
        self.y_label = 'agreeableness'

    def xy_values(self, zones):
        x_values = [zone.population_density() for zone in zones]
        y_values = [zone.average_agreeableness() for zone in zones]
        return x_values, y_values


class IncomeGraph(BaseGraph):

    def __init__(self):
        super().__init__()
        self.title = 'rich people live in the cities'
        self.x_label = 'population density'
        self.y_label = 'income'

    def xy_values(self, zones):
        x_values = [zone.population_density() for zone in zones]
        y_values = [zone.average_income() for zone in zones]
        return x_values, y_values


def main():
    with open('agents-100k.json', 'rt') as f:
        list_of_agents = json.load(f)
        for my_agent_attributes in list_of_agents:
            longitude = my_agent_attributes.pop('longitude')
            latitude = my_agent_attributes.pop('latitude')
            position = Position(longitude, latitude)
            agent = Agent(position, **my_agent_attributes)
            zone = Zone.find_zone_that_contains(agent.position)
            zone.add_inhabitant(agent)

    agreeableness_graph = AgreeablenessGraph()
    agreeableness_graph.show(Zone.ZONES)

    income_graph = IncomeGraph()
    income_graph.show(Zone.ZONES)

main()

# L'encapsulation est un mot qui illustre deux concepts :
#   le fait que les attributs et les méthodes d'un objet lui sont spécifiquement associés.
#   le champ d'action des attributs et des méthodes est par défaut l'objet lui-même et non tout autre objet.

# Une méthode protégée est accessible à l'intérieur d'une classe mais ne doit pas être aisément accessible
# de l'extérieur. Vous ajoutez pour cela un underscore au début du nom.
# Une méthode privée est accessible à l'intérieur d'une classe mais ne doit pas être accessible
# de l'extérieur. Vous ajoutez pour cela deux underscores au début du nom.
# Pour y accéder: _MaClasse__methode_privee()
