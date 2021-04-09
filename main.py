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
        self.score = 0
        self.textElements = []
        self.status = 0 # game playing, if 1 = win if -1 = lost
        self.height = 900
        self.width  = 1600
        self.canvas = tk.Canvas(self.frame, width=self.width, height=self.height, background="black")
        self.canvas.pack()
        self.defender = Defender()
        self.defender.install_in(self.canvas)
        self.fleet.install_in(self.canvas)

    def animation(self):
        #self.canvas.configure(bg=self.color[self.iColor])
        #self.iColor=(self.iColor +1)%6
        if(self.status == 0):
            self.move_bullets()
            self.move_aliens_fleet()
        elif(self.status == -1):
            self.addtext(self.width/2,self.height/2, "Game over:\n you Lost", 30)
        elif(self.status == 1):
            self.addtext(self.width/2,self.height/2, "Game over:\n you Won", 50)
        self.canvas.after(10, self.animation)

    def start_animation(self):
        self.frame.focus_set()
        self.frame.bind("<Key>", self.keypress)
        self.canvas.after(300, self.animation)

    def move_bullets(self):
        bullettouchedAlien = self.fleet.manage_touched_aliens_by(self.canvas, self.defender)
        if bullettouchedAlien != -1:
            self.canvas.delete(bullettouchedAlien.getId())
            self.defender.getFired_bullets().remove(bullettouchedAlien)
        for bullets in self.defender.getFired_bullets():
            #returned : tuple with the object bullet and a boolean = True if the bullet is out of the canvas
            toDelete = bullets.move_in(self.canvas)
            if toDelete[1]:
                #self.canvas.delete(toDelete[0].getId())
                self.defender.getFired_bullets().remove(toDelete[0])

    def move_aliens_fleet(self):
        status = self.fleet.move_in(self.canvas)
        if status ==  -1:
            self.status = -1
        elif status == 1:
            self.status = 1

    def keypress(self, event):
        if event.keysym == 'Left':
            self.defender.move_in(self.canvas,-10)
        elif event.keysym == 'Right':
            self.defender.move_in(self.canvas,10)
        elif event.keysym == 'space':
            self.defender.fire(self.canvas)

    def addtext(self, x, y, text, size):
        # add the text id to the array so we can modify it / hide it /delete it later if needed
        self.textElements.append(self.canvas.create_text(x, y, text=text, fill="white",font=("Purisa", size)))


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

    def getFired_bullets(self):
        return self.fired_bullets

    def getId(self):
        return self.id

    def getWidth(self):
        return self.width

class Bullet(object):
    def __init__(self, shooter):
        self.radius = 5
        self.color = "red"
        self.speed = 3
        self.id = None
        self.shooter = shooter

    def install_in(self, canvas):
        # x, y = middle of the ball and located on top of the defender
        x = canvas.coords(self.shooter.getId())[0] + self.shooter.getWidth()/2
        y = canvas.coords(self.shooter.getId())[1] - self.radius
        self.id=canvas.create_oval(x-self.radius, y-self.radius, x+self.radius, y+self.radius, fill = self.color)

    def move_in(self, canvas):
        canvas.move(self.id, 0, -self.speed)
        if canvas.coords(self.id)[3] <= 0: # if bullet out of the frame
            return(self, True)
        else:
            return(self,False)

    def getId(self):
        return self.id

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
        #no more Alien, game won
        if(self.fleet_size <= 0):
            return 1
        decale = 0 # if the fleet is on an edge decale = 30 and all aliens go down
        self.xfleet,self.yfleet,self.x1fleet,self.y1fleet  = canvas.bbox("alien") #Coords of the fleet
        if(self.x1fleet >= int(canvas.cget("width")) or self.xfleet < 0): # if we are on an edge
            self.speed = -self.speed #reverse
            decale = 30 # go down
        for alien in self.aliens_fleet:
            alien.move_in(canvas, self.speed, decale)
        # if the fleet reaches the defender game lost
        if self.y1fleet > int(canvas.cget("height"))-50:
            return -1


    def manage_touched_aliens_by(self,canvas,defender):
        for bullets in defender.getFired_bullets():
            bx,by,b1x,b1y = canvas.coords(bullets.getId())
            # se trouve dans la flotte
            overlapped = canvas.find_overlapping(bx, by, b1x, b1y)
            # if the bullet touches an alien and it's not the defender
            if (len(overlapped) == 2 and overlapped[0] != 1):
                for alien in self.aliens_fleet:
                    if alien.getId() == overlapped[0] and alien.getAlive() == True:
                        alien.touched_by(canvas, bullets)
                        self.fleet_size -=1
                        return bullets
        return -1

    def getId(self):
        return self.id

    def getFleet_size(self):
        return self.fleet_size

class Alien(object):

    def __init__(self):
        self.alien = None
        self.id = None
        self.alive = True

    def touched_by(self, canvas, projectile):
        #change the image to explosion
        # TODO find a way to delay the removal of the alien of at least a way for the explosion to last
        self.alien = tk.PhotoImage(file="images/explosion.gif")
        canvas.itemconfig(self.id, image = self.alien)
        self.alive = False
        #remove the alien
        self.deleteAlien(canvas)


    def install_in(self, canvas, x, y, image, tag):
        #load the picture
        self.alien = tk.PhotoImage(file=image)
        img_width = self.alien.width()/2
        img_heigth = self.alien.height()/2
        # create the pic on the canvas
        self.id = canvas.create_image(x+img_width, y+img_heigth,image=self.alien, tag=tag)

    def move_in(self, canvas, dx, dy):
        canvas.move(self.id,dx,dy)

    def deleteAlien(self, canvas):
        canvas.delete(self.id)

    def getId(self):
        return self.id
    def getAlive(self):
        return self.alive

class TexteVC(object):

    def show(self, canvas):
        if(not self.visible):
            canvas.itemconfig(self.id, state = 'active')
            self.visible = 0

    def hide(self, canvas):
        if(self.visible):
            canvas.itemconfig(self.id, state="hidden")
            self.visible = 1

SpaceInvaders().play()
