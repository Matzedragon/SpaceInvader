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
        #self.color = ["red","blue","green","white","yellow","purple","pink"]
        #self.iColor = 0
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
        #self.canvas.configure(bg=self.color[self.iColor])
        #self.iColor=(self.iColor +1)%6
        self.move_bullets()
        self.move_aliens_fleet()
        self.canvas.after(10, self.animation)

    def start_animation(self):
        self.frame.focus_set()
        self.frame.bind("<Key>", self.keypress)
        self.canvas.after(300, self.animation)

    def move_bullets(self):
        bullettouchedAlien = self.fleet.manage_touched_aliens_by(self.canvas, self.defender)
        if bullettouchedAlien != -1:
            self.canvas.delete(bullettouchedAlien.id)
            self.defender.fired_bullets.remove(bullettouchedAlien)
        for bullets in self.defender.fired_bullets:
            #returned : tuple with the object bullet and a boolean = True if the bullet is out of the canvas
            toDelete = bullets.move_in(self.canvas)
            if toDelete[1]:
                self.defender.fired_bullets.remove(toDelete[0])

    def move_aliens_fleet(self):
        self.fleet.move_in(self.canvas)

    def keypress(self, event):
        if event.keysym == 'Left':
            self.defender.move_in(self.canvas,-10)
        elif event.keysym == 'Right':
            self.defender.move_in(self.canvas,10)
        elif event.keysym == 'space':
            self.defender.fire(self.canvas)


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
        # x, y = middle of the ball and located on top of the defender
        x = canvas.coords(self.shooter.id)[0] + self.shooter.width/2
        y = canvas.coords(self.shooter.id)[1] - self.radius
        self.id=canvas.create_oval(x-self.radius, y-self.radius, x+self.radius, y+self.radius, fill = self.color)

    def move_in(self, canvas):
        canvas.move(self.id, 0, -5)
        if canvas.coords(self.id)[3] <= 0: # if bullet out of the frame
            return(self, True)
        else:
            return(self,False)

class Fleet(object):
    def __init__(self):
        self.speed = 3
        self.aliens_lines = 5
        self.aliens_columns = 10
        self.aliens_inner_gap = 20
        self.alien_x_delta = 5
        self.alien_y_delta = 15
        self.fleet_size = self.aliens_lines * self.aliens_columns
        self.aliens_fleet = []

    def install_in(self, canvas):
        #path to the picture
        image = "images/alien.gif"
        #load the picture so i can get the size of it
        self.alien = tk.PhotoImage(file=image)
        img_width = self.alien.width()
        img_heigth = self.alien.height()
        id = 0
        print(str(img_heigth) + " = image height")
        for y in range(self.aliens_lines):
            for x in range(self.aliens_columns):
                self.aliens_fleet.append(Alien())
                # x_img = starting position + (gap + img_size)* the number of aliens on one line
                # y_img = starting position + (gap + img_size)* the number of line of aliens
                x_img = self.alien_x_delta+((self.aliens_inner_gap+img_width)*x)
                y_img = self.alien_y_delta+((self.aliens_inner_gap+img_heigth)*y)

                self.aliens_fleet[-1].install_in(canvas,x_img,y_img,image,"alien")
                id+=1


    def move_in(self, canvas):
        decale = 0 # if the fleet is on an edge decale = 30 and all aliens go down
        self.xfleet,self.yfleet,self.x1fleet,self.y1fleet  = canvas.bbox("alien") #Coords of the fleet
        if(self.x1fleet >= int(canvas.cget("width")) or self.xfleet < 0): # if we are on an edge
            self.speed = -self.speed #reverse
            decale = 30 # go down
        for alien in self.aliens_fleet:
            alien.move_in(canvas, self.speed, decale)


    def manage_touched_aliens_by(self,canvas,defender):
        for bullets in defender.fired_bullets:
            bx,by,b1x,b1y = canvas.coords(bullets.id)
            # se trouve dans la flotte
            overlapped = canvas.find_overlapping(bx, by, b1x, b1y)
            # if the bullet touches an alien and it's not the defender
            if (len(overlapped) == 2 and overlapped[0] != 1):
                for alien in self.aliens_fleet:
                    if alien.id == overlapped[0] and alien.alive == True:
                        alien.touched_by(canvas, bullets)
                        return bullets
        return -1


class Alien(object):

    def __init__(self):
        self.id = None
        self.alive = True

    def touched_by(self, canvas, projectile):
        self.alive = False
        canvas.delete(self.id)
        print("alien " + str(self.id) + " touché !")
        #remove the alien pic

    def install_in(self, canvas, x, y, image, tag):
        #load the picture
        self.alien = tk.PhotoImage(file=image)
        img_width = self.alien.width()/2
        img_heigth = self.alien.height()/2
        # create the pic on the canvas
        self.id = canvas.create_image(x+img_width, y+img_heigth,image=self.alien, tag=tag)

    def move_in(self, canvas, dx, dy):
        canvas.move(self.id,dx,dy)

SpaceInvaders().play()
