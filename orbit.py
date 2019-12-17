#!/usr/bin/env python

import fileinput


def main():
    system = PlanetarySystem()

    for line in fileinput.input():
        center_of_mass, satellite = tuple(line.strip().split(')'))
        orbit = Orbit(center_of_mass, satellite)
        system.add_orbit(orbit)

    print(len(system))
    print(system.move('YOU', 'SAN'))


class PlanetarySystem:
    def __init__(self):
        self.center_of_mass = Orbit(None, 'COM')
        self.orbits = {'COM': self.center_of_mass}
        self.incomplete_orbits = []

    def add_orbit(self, orbit):
        self.orbits[orbit.name] = orbit

        for incomplete_orbit in self.incomplete_orbits.copy():
            if orbit.name == incomplete_orbit.center_of_mass_name:
                orbit.add_satellite(incomplete_orbit)
                self.incomplete_orbits.remove(incomplete_orbit)

        if orbit.center_of_mass_name in self.orbits:
            center_of_mass = self.orbits[orbit.center_of_mass_name]
            center_of_mass.add_satellite(orbit)
        else:
            self.incomplete_orbits.append(orbit)

    def move(self, from_orbit, to_orbit):
        from_orbit = self.center_of_mass.find_descendent(from_orbit)
        return from_orbit.move(to_orbit)

    def __repr__(self):
        return str(self.center_of_mass)

    def __len__(self):
        orbits = [self.center_of_mass]
        length = 0

        while len(orbits) > 0:
            orbit = orbits.pop()
            length += len(orbit)
            if len(orbit.satellites) > 0:
                orbits.extend(orbit.satellites.values())

        return length


class Orbit:
    def __init__(self, center_of_mass_name, name):
        self.center_of_mass = None
        self.center_of_mass_name = center_of_mass_name
        self.name = name
        self.satellites = {}

    def add_satellite(self, satellite):
        satellite.center_of_mass = self
        self.satellites[satellite.name] = satellite

    def move(self, center_of_mass):
        orbit = self
        distance = 0

        while orbit is not None and center_of_mass not in orbit:
            satellite = orbit.find_satellite_with_descendent(center_of_mass)

            if satellite is not None:
                distance += 1
                orbit = satellite
            else:
                distance += 1
                orbit = orbit.center_of_mass

        return distance - 1

    def find_satellite_with_descendent(self, name):
        for satellite in self.satellites.values():
            satellites = [satellite]

            while len(satellites) > 0:
                sat = satellites.pop()
                if name in sat:
                    return satellite
                if len(sat.satellites) > 0:
                    satellites.extend(sat.satellites.values())

        return None

    def find_descendent(self, name):
        satellites = [self]

        while len(satellites) > 0:
            satellite = satellites.pop()
            if name in satellite:
                return satellite.satellites[name]
            if len(satellite.satellites) > 0:
                satellites.extend(satellite.satellites.values())

        return None

    def satellite_names(self):
        return set(satellite.name for satellite in self.satellites)

    def __len__(self):
        orbit = self
        length = 0

        while orbit.center_of_mass is not None:
            length += 1
            orbit = orbit.center_of_mass

        return length

    def __contains__(self, value):
        return value in self.satellites


if __name__ == '__main__':
    main()
