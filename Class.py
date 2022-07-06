from abc import ABC, abstractmethod


class Vehicle(ABC):
    @abstractmethod
    def __init__(self, maxVel, acc) -> None:
        self.maxVel = maxVel
        self.acc = acc

    def timeTo100(self):
        return round(100/self.acc, 2)


class Car(Vehicle):
    def __init__(self, maxVel, acc, color) -> None:
        super().__init__(maxVel, acc)
        self.color = color

    @property
    def color(self):
        return self.__color

    @color.setter # hermetisation
    def color(self, color):
        if color == "" or type(color) != str:
            self.__color = "black"
        else:
            self.__color = color

    def __str__(self) -> str:
        return str(f'max vel: {self.maxVel} max acceleration: {self.acc}')



c = Car(3, 4, 'c')
c.color = 2
v = Vehicle
print(c.color)
print(isinstance(c,v))