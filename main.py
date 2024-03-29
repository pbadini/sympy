from sympy import *
from tkinter import *
from repeatingtimer import  RepeatingTimer
import math

class Link():
    def __init__(self, x0, y0, x1, y1, **kwargs):
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.length =  sqrt((x1 - x0)**2 + (y1 - y0)**2)
        self.mass = 1
        if 'father' in kwargs:
            self.father = kwargs['father']
        else:
            self.father = None

    def update(self, angle):
        if self.father:
            self.x0 = self.father.x1
            self.y0 = self.father.y1

        self.x1 = math.sin(angle) * self.length + self.x0
        self.y1 = math.cos(angle) * self.length + self.y0
        

class Lagrangian():
    def __init__(self, links):
        self.links = links
        self.g = 10
        self.t = Symbol('t')
    
    def position(self):
        self.angles = []
        self.angular_velocity = []
        self.angular_acc = []
        for i, _ in enumerate(self.links):
            self.angles.append(Function('theta'+ str(i + 1))(self.t))
            self.angular_velocity.append(Function('theta'+ str(i + 1) + "'")(self.t))
            self.angular_acc.append(Function('theta'+ str(i + 1) + "''")(self.t))
        
        self.x = []
        self.y = []      
        for i, link in enumerate(self.links):
            self.x.append(1 * sin(self.angles[i]) * link.length)
            self.y.append(-1 * cos(self.angles[i]) * link.length)
            for j in range(i):
                self.x[i] += sin(self.angles[j]) * self.links[j].length
                self.y[i] += -cos(self.angles[j]) * self.links[j].length
    
    def derivate(self, expression, derivator):
        d_exp = []
        for i, exp in enumerate(expression):
            exp = diff(exp, derivator)
            for angle, ang_vel, ang_acc in zip(self.angles, self.angular_velocity, self.angular_acc):
                exp = exp.subs(Derivative(angle, self.t), ang_vel)
                exp = exp.subs(Derivative(ang_vel, self.t), ang_acc)
            d_exp.append(exp)
        return d_exp

    def addtion(self, expression_1, expression_2):
        exp_vel  = []
        for vel_1, vel_2 in zip(expression_1, expression_2):
            exp_vel.append(simplify(vel_1 + vel_2))

        return exp_vel
    
    def square(self, expression):
        exp_squared = []
        for exp in expression:
            exp_squared.append(exp**2)
        return  exp_squared
    
    def kinetic(self, velocity):
        self.kinetic_energy = [0]
        for i, vel in enumerate(velocity):
            self.kinetic_energy[0] += vel * self.links[i].mass * 0.5
    
    def potential(self):
        self.potential_energy = [0]
        for i, link in enumerate(self.links):
            self.potential_energy[0] += -1 * link.mass * self.g * link.length * cos(self.angles[i])
            for j in range(i):
                self.potential_energy[0] += -self.links[j].mass * self.g * self.links[j].length * cos(self.angles[j])
    
    def lagrang(self):
        self.L = [self.kinetic_energy[0] - self.potential_energy[0]]

links = []
links.append(Link(250, 250, 325, 250))
links.append(Link(325, 250, 400, 250, father = links[0]))
#links.append(Link(400, 250, 475, 250, father = links[1]))
lag = Lagrangian(links)
lag.position()
print('x: ', lag.x)
vx = lag.derivate(lag.x, 't')
print('vx: ',vx)
vy = lag.derivate(lag.y, 't')
v2x = lag.square(vx)
v2y = lag.square(vy)
print('v2x: ',v2x)
vel2 = lag.addtion(v2x, v2y)
print('vel2: ',vel2)
lag.kinetic(vel2)
lag.potential()
print('KE: ',lag.kinetic_energy)
print('PE: ',lag.potential_energy)
lag.lagrang()
print('L: ',lag.L)
dL = []
for i in range(2):
    dL_dv = lag.derivate(lag.L, lag.angular_velocity[i])
    #print('dL_dv: ',dL_dv)
    dL_dt = [simplify(lag.derivate(dL_dv, 't')[0])]
    #print('dL_dt: ',dL_dt)
    dL_da = lag.derivate(lag.L, lag.angles[i])
    #print('dL_da: ',dL_da)
    dL.append(simplify(dL_dt[0] -dL_da[0]))
    print('dL: ', dL[i])
#solution , = linsolve([dL[0], dL[1], dL[2]], lag.angular_acc[0], lag.angular_acc[1], lag.angular_acc[2])
solution , = linsolve([dL[0], dL[1]], lag.angular_acc[0], lag.angular_acc[1])
solution = simplify(solution)





angle = [math.pi/2, math.pi/2]
ang_vel = [0, 0]
ang_acc = [0, 0]
ang_acc[0] = lambdify([lag.angular_velocity[0], lag.angular_velocity[1], lag.angles[0], lag.angles[1]], solution[0])
ang_acc[1] = lambdify([lag.angular_velocity[0], lag.angular_velocity[1], lag.angles[0], lag.angles[1]], solution[1])

root = Tk()
canvas = Canvas(root,  width = 500, height = 500, bg = "gray")
link_img = []
for link in links:
    link_img.append(canvas.create_line(link.x0, link.y0, link.x1,  link.y1, width = 4, fill = 'red'))

acc = [0, 0]
def step():
    global  angle
    
    acc[0] = ang_acc[0](ang_vel[0], ang_vel[1], angle[0], angle[1])
    acc[1] = ang_acc[1](ang_vel[0], ang_vel[1], angle[0], angle[1])
    for i in range(len(angle)):
        ang_vel[i] += acc[i]*0.2
        angle[i] += ang_vel[i]*0.2


    print(angle[0], angle[1])

    for i in range(len(angle)):
        links[i].update(angle[i]) 
        canvas.coords(link_img[i], links[i].x0, links[i].y0, links[i].x1,  links[i].y1)

t = RepeatingTimer(0.025, step)
t.start()


canvas.grid(column = 0, row = 0)
root.mainloop();

