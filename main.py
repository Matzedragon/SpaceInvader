"""
@author: mineself
"""
try:  # import as appropriate for 2.x vs. 3.x
    import tkinter as tk
    import tkinter.messagebox as tkMessageBox
except:
    import Tkinter as tk
    import tkMessageBox


class SpaceInvaders(object):
    '''
    Main Game class
    '''
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Space Invaders")
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.game = Game(self.frame)

    def play(self):
        self.game.start_animation()
        self.root.mainloop()

class Game(object):
    def __init__(self, frame):
        self.frame = frame
        self.fleet = Fleet()
        self.height = 900
        self.width  = 1600
        #self.width = self.fleet.get_width()
        self.canvas = tk.Canvas(self.frame, width=self.width, height=self.height, background="black")
        self.canvas.pack()
        self.defender = Defender()
        self.defender.install_in(self.canvas)
        self.fleet.install_in(self.canvas)

    def animation(self):
        self.move_bullets()
        self.canvas.after(10, self.animation)

    def start_animation(self):
        self.frame.focus_set()
        self.frame.bind("<Key>", self.keypress)
        self.canvas.after(300, self.animation)

    def move_bullets(self):
        for bullets in self.defender.fired_bullets:
            #returned : tuple with the object bullet and a boolean = True if the bullet is out of the canvas
            toDelete = bullets.move_in(self.canvas)
            if toDelete[1]:
                self.defender.fired_bullets.remove(toDelete[0])

    def move_aliens_fleet(self):
        print("TODO")

    def keypress(self, event):
        if event.keysym == 'Left':
            self.defender.move_in(self.canvas,-10)
        elif event.keysym == 'Right':
            self.defender.move_in(self.canvas,10)
        elif event.keysym == 'space':
            self.defender.fire (self.canvas)


class Defender(object):
    def __init__(self):
        self.width = 20
        self.height = 20
        self.move_delta = 20
        self.id = None
        self.max_fired_bullets = 8
        self.fired_bullets = []

    def install_in(self, canvas):
        x = int(canvas.cget("width"))
        y = int(canvas.cget("height"))-self.height
        self.id = canvas.create_rectangle(x/2,y , x/2+self.width, y+self.height, fill="red")


    def move_in(self,canvas, dx):
        canvas.move(self.id, dx, 0)

    def fire(self, canvas):
        if(len(self.fired_bullets) < 8):
            self.fired_bullets.append(Bullet(self))
            self.fired_bullets[-1].install_in(canvas)

class Bullet(object):
    def __init__(self, shooter):
        self.radius = 5
        self.color = "red"
        self.speed = 3
        self.id = None
        self.shooter = shooter

    def install_in(self, canvas):
        x = canvas.coords(self.shooter.id)[0]
        y = canvas.coords(self.shooter.id)[1] -  self.shooter.height
        x1 = canvas.coords(self.shooter.id)[2]
        y1 = canvas.coords(self.shooter.id)[3] - self.shooter.height
        self.id=canvas.create_oval(x, y, x1, y1, fill = self.color)

    def move_in(self, canvas):
        canvas.move(self.id, 0, -5)
        if canvas.coords(self.id)[3] <= 0:
            return(self, True)
        else:
            return(self,False)

class Fleet(object):
    def __init__(self):
        self.aliens_lines = 5
        self.aliens_columns = 10
        self.aliens_inner_gap = 20
        self.alien_x_delta = 5
        self.alien_y_delta = 15
        fleet_size = self.aliens_lines * self.aliens_columns
        self.aliens_fleet = [None] * fleet_size

    def install_in(self, canvas):
        #path to the picture
        image = "images/alien.gif"
        #load the picture so i can get the size of it
        self.alien = tk.PhotoImage(file=image)
        img_width = self.alien.width()
        img_heigth = self.alien.height()

        for y in range(self.aliens_lines):
            for x in range(self.aliens_columns):
                self.aliens_fleet.append(Alien())
                # x = starting position + (gap + img_size)* the number of aliens on one line
                # y = starting position + (gap + img_size)* the number of line of aliens
                self.aliens_fleet[-1].install_in(canvas,
                                                self.alien_x_delta+((self.aliens_inner_gap+img_width)*x),
                                                self.alien_y_delta+((self.aliens_inner_gap+img_heigth)*y),
                                                image,"tag?")


        def move_in(self, canvas):
            print("TODO")

        def manage_touched_aliens_by(self,canvas,defender):
            print("TODO")

class Alien(object):

    def __init__(self):
        self.id = None
        self.alive = True

    def touched_by(self, canvas, projectile):
        print("TODO")

    def install_in(self, canvas, x, y, image, tag):
        #load the picture
        self.alien = tk.PhotoImage(file=image)
        img_width = self.alien.width()
        img_heigth = self.alien.height()
        # create the pic on the canvas
        self.id = canvas.create_image(x+img_width, y+img_heigth,image=self.alien)

    def move_in(self, canvas, dx, dy):
        print("TODO")

SpaceInvaders().play()
