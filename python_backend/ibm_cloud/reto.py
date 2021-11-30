from mesa import Agent, Model
from mesa.space import MultiGrid as Grid
from mesa.time import RandomActivation
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid

import random

class Pasto(Agent):
    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.pos = pos

class Semaforo(Agent):
    #0 rojo, 1 amarillo, 2 verde
    def __init__(self, model, pos, turno):
        super().__init__(model.next_id(), model)
        self.model = model
        self.pos = pos
        self.turno = turno
        self.estado = 0
        self.contadorVerde = 0
        self.contadorAmarillo = 0

    def step(self):
        #Esta en rojo y ya es su turno de estar en verde
        if(self.estado == 0 and self.model.turnoSemaforos == self.turno):
            self.estado = 2
            return

        #Esta en verde y aun no alcanza el tiempo
        if(self.estado == 2 and self.contadorVerde < self.model.tiempoVerde):
            self.contadorVerde += 1
            return

        #Esta en verde y ya alcanzo el tiempo
        if(self.estado == 2 and self.contadorVerde == self.model.tiempoVerde):
            self.contadorVerde = 0
            self.estado = 1
            return

        #Esta en amarillo y aun no alcanza el tiempo
        if(self.estado == 1 and self.contadorAmarillo < self.model.tiempoAmarillo):
            self.contadorAmarillo += 1
            return

        #Esta en amarillo y ya alcanzo el tiempo
        if(self.estado == 1 and self.contadorAmarillo == self.model.tiempoAmarillo):
            self.contadorAmarillo = 0
            self.estado = 0
            self.model.siguienteTurnoSemaforo()
            return 

class Calle(Agent):
    def __init__(self, model, pos, tipo):
        super().__init__(model.next_id(), model)
        self.pos = pos
        self.tipo = tipo

indicesMatriz = [15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0]
paseCruceros = [(7, 2), (8, 13), (2, 8), (13, 7)]

class Car(Agent):
    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.pos = pos
        self.model = model
        self.cambioDireccion = 0
        self.orientacion = None  # 1 arriba, 2 abajo, 3 derecha, 4 izquierda
         
    def step(self):
        tipoCasilla = self.model.matrix[indicesMatriz[self.pos[1]]][self.pos[0]]
        next_move = self.getNextStep(tipoCasilla)
        next_move = self.orientationChange(next_move)
        print("Actual:")
        print(self.pos)
        print("Siguiente:")
        print(next_move)
        contenidos_siguiente_casilla = self.model.grid.get_cell_list_contents(next_move)
        if len(contenidos_siguiente_casilla) == 0:
            if(self.pos in paseCruceros):
                if self.checarPaso() == True:
                    self.model.grid.move_agent(self, next_move)
            else:
                self.model.grid.move_agent(self, next_move)
        elif len(contenidos_siguiente_casilla) == 1 and type(contenidos_siguiente_casilla[0]) is Semaforo:
            if(self.pos in self.model.semaforos):
                self.model.grid.move_agent(self, next_move)
            elif contenidos_siguiente_casilla[0].estado == 2:
                self.model.grid.move_agent(self, next_move)
    
    def checarPaso(self):
        tipoCasilla = self.model.matrix[indicesMatriz[self.pos[1]]][self.pos[0]]
        if tipoCasilla == 1:
            for x in range(self.pos[0]-2, self.pos[0] + 3 ):
                for y in range(self.pos[1]+1, self.pos[1] + 3 ):
                    contenidos_siguiente_casilla = self.model.grid.get_cell_list_contents((x, y))
                    if len(contenidos_siguiente_casilla) > 0:
                        return False
            return True
        
        elif tipoCasilla == 2:
            for x in range(self.pos[0]-2, self.pos[0] + 3 ):
                for y in range(self.pos[1]- 2, self.pos[1]):
                    contenidos_siguiente_casilla = self.model.grid.get_cell_list_contents((x, y))
                    if len(contenidos_siguiente_casilla) > 0:
                        return False
            return True
            
        elif tipoCasilla == 3:
            for x in range(self.pos[0] + 1, self.pos[0] + 3 ):
                for y in range(self.pos[1]- 2, self.pos[1] + 3):
                    contenidos_siguiente_casilla = self.model.grid.get_cell_list_contents((x, y))
                    if len(contenidos_siguiente_casilla) > 0:
                        return False
            return True
        
        elif tipoCasilla == 4:
            for x in range(self.pos[0] - 2, self.pos[0] ):
                for y in range(self.pos[1]- 2, self.pos[1] + 3):
                    contenidos_siguiente_casilla = self.model.grid.get_cell_list_contents((x, y))
                    if len(contenidos_siguiente_casilla) > 0:
                        return False
            return True
        
    
    def orientationChange(self, next_move):
        if self.pos[0] != next_move[0]:
            if self.pos[0] > next_move[0]:
                siguienteOrientacion = 4
            else:
                siguienteOrientacion = 3

        elif self.pos[1] != next_move[1]:
            if self.pos[1] > next_move[1]:
                siguienteOrientacion = 2
            else:
                siguienteOrientacion = 1

        if self.orientacion == None:
            self.orientacion = siguienteOrientacion 
            return next_move
            
        #Se corrije next step y se continúa con la misma direccion
        if self.cambioDireccion == 1 and siguienteOrientacion != self.orientacion:
            self.cambioDireccion = 0
            casillaActual = self.model.matrix[indicesMatriz[self.pos[1]]][self.pos[0]]
            if casillaActual == 1 or casillaActual == 2 or casillaActual == 3 or casillaActual == 4:
                return self.getNextStep(casillaActual)
            else:
                return self.getNextStep(self.orientacion)
        
        if not self.cambioDireccion == 1 and siguienteOrientacion != self.orientacion:
            self.cambioDireccion += 1
            self.orientacion = siguienteOrientacion
            return next_move

        if siguienteOrientacion == self.orientacion:
            self.cambioDireccion = 0
            return next_move
            
        
    def getNextStep(self, tipoCasilla):
        if tipoCasilla == 1: #arriba
            return (self.pos[0], self.pos[1] + 1)
        elif tipoCasilla == 2: #abajo
            return (self.pos[0], self.pos[1] - 1)
        elif tipoCasilla == 3: #derehca
            return (self.pos[0] + 1, self.pos[1])
        elif tipoCasilla == 4: #izquierda
            return (self.pos[0] - 1, self.pos[1])
        elif tipoCasilla == 5: #arriba o derehca
            posibles = [(self.pos[0], self.pos[1] + 1),(self.pos[0] + 1, self.pos[1])]
            return posibles[random.randint(0,1)]
        elif tipoCasilla == 6: #arriba o izquierda
            posibles = [(self.pos[0], self.pos[1] + 1),(self.pos[0] - 1, self.pos[1])]
            return posibles[random.randint(0,1)]
        elif tipoCasilla == 7: #abajo o derecha
            posibles = [(self.pos[0], self.pos[1] - 1),(self.pos[0] + 1, self.pos[1])]
            return posibles[random.randint(0,1)]
        elif tipoCasilla == 8: #abajo o izquierda
            posibles = [(self.pos[0], self.pos[1]-1),(self.pos[0] - 1, self.pos[1])]
            return posibles[random.randint(0,1)]

class City(Model):
    def __init__(self, nCoches=15):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.grid = Grid(16, 16, torus=False)
        self.origenes = [(0,0), (1,0),(3,0), (13, 1), (8, 4), (7, 11), (4,14), (8,6), (8,5), (7,9),(7,10), (6,7), (5,7), (9,8), (10,8)]
        self.semaforos = [(7,7),(8,7),(7,8),(8,8)]
        self.turnoSemaforos = 0
        self.tiempoVerde = 6
        self.tiempoAmarillo = 2

        self.numCoches = nCoches
        self.numLights = 4

        # 1 - solo arriba
        # 2 - solo abajo
        # 3 - solo derecha
        # 4 - solo izquierda
        # 5 - arriba o derecha
        # 6 - arriba o izquierda
        # 7 - abajo o derecha
        # 8 - abajo o izquierda

        self.matrix = [
            [2,4,4,4,4,4,4,8,4,4,4,4,4,4,4,4],
            [2,3,3,3,3,3,3,7,5,3,3,3,3,3,2,1],
            [2,1,0,0,0,0,0,2,1,0,0,0,0,0,2,1],
            [2,1,0,0,0,0,0,2,1,0,0,0,0,0,2,1],
            [2,1,0,0,0,0,0,2,1,0,0,0,0,0,2,1],
            [2,1,0,0,0,0,0,2,1,0,0,0,0,0,2,1],
            [2,1,0,0,0,0,0,2,1,0,0,0,0,0,2,1],
            [2,6,4,4,4,4,4,8,6,4,4,4,4,4,8,6],
            [7,5,3,3,3,3,3,7,5,3,3,3,3,3,7,1],
            [2,1,0,0,0,0,0,2,1,0,0,0,0,0,2,1],
            [2,1,0,0,0,0,0,2,1,0,0,0,0,0,2,1],
            [2,1,0,0,0,0,0,2,1,0,0,0,0,0,2,1],
            [2,1,0,0,0,0,0,2,1,0,0,0,0,0,2,1],
            [2,1,0,0,0,0,0,2,1,0,0,0,0,0,2,1],
            [2,1,4,4,4,4,4,8,6,4,4,4,4,4,4,1], 
            [3,3,3,3,3,3,3,3,5,3,3,3,3,3,3,1], 
        ]

        for i in range(nCoches):
            car = Car(self, self.origenes[i])
            self.grid.place_agent(car, car.pos)
            self.schedule.add(car)

        for i in range(len(self.semaforos)):
            semaforo = Semaforo(self, self.semaforos[i], i)
            self.grid.place_agent(semaforo, semaforo.pos)
            self.schedule.add(semaforo)

        for _,x,y in self.grid.coord_iter():
            if self.matrix[y][x] == 0:
                block = Pasto(self, (x, y))
                self.grid.place_agent(block, block.pos)

        
    def siguienteTurnoSemaforo(self):
        if(self.turnoSemaforos < len(self.semaforos) - 1):
            self.turnoSemaforos += 1
        else:
            self.turnoSemaforos = 0
        print("Turno Semaforo: " + str(self.turnoSemaforos))


    def step(self):
        self.schedule.step()


def agent_portrayal(agent):
    if type(agent) is Car:
        portrayal = {"Shape": "circle", "Filled": "true", "Color": "Blue", "r": 0.75, "Layer": 0}
    elif type(agent) is Pasto:
        portrayal = {"Shape": "rect",  "w": 1, "h": 1, "Filled": "true", "Color": "Gray", "Layer": 0}
    elif type(agent) is Semaforo:
        if(agent.estado == 0):
            portrayal = {"Shape": "rect",  "w": 1, "h": 1, "Filled": "true", "Color": "Red", "Layer": 0}
        elif(agent.estado == 1):
            portrayal = {"Shape": "rect",  "w": 1, "h": 1, "Filled": "true", "Color": "Yellow", "Layer": 0}
        elif(agent.estado == 2):
            portrayal = {"Shape": "rect",  "w": 1, "h": 1, "Filled": "true", "Color": "Green", "Layer": 0}
    return portrayal

if __name__ == '__main__':
    grid = CanvasGrid(agent_portrayal, 16, 16, 450, 450)

    server = ModularServer(City, [grid], "Reto unu", {})
    server.port = 8522
    server.launch()