"""
@author: mineself
"""
try:  # import as appropriate for 2.x vs. 3.x
    import tkinter as tk
    import tkinter.messagebox as tkMessageBox
except:
    import Tkinter as tk
    import tkMessageBox

# MAIN class, create the window components
class SpaceInvaders(object):
    '''
    Main Game class
    '''
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Space Invaders")
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.scoreboard = scoreBoard(self)
        self.scoreboard.printscoreboard()
        self.game =None

    def getFrame(self):
        return self.frame

    def getRoot(self):
        return self.root

    def play(self):
        self.root.mainloop()

    #switch from the scoreboard to the game
    def switchToGame(self, score):
        self.game = Game(self.frame, score)
        self.game.start_animation()

class scoreBoard(object):
    def __init__(self,main):
        self.main = main
        self.newUser = tk.StringVar()
        self.newUser_entry = tk.Entry(main.getFrame(),textvariable = self.newUser, font=('calibre',10))
        self.sb = Resultat()
        self.sb.fromFile("scores.txt")
        #array to delete all paacked elements when the game starts
        self.packed = []

    def submit(self):
        newScore = Score(self.newUser.get(),0)
        self.unpackall()
        self.main.switchToGame(newScore)

    def submitold(self, oldscore):
        #the user already exists we reset his score to 0 for now
        oldscore = Score(oldscore.getUser(),0)
        self.unpackall()
        self.main.switchToGame(oldscore)

    def printscoreboard(self):
        i = 0
        for scores in self.sb.getListeScores():
            scoreprt = scores.getUser() + " " + scores.getScore()
            temp = tk.Label(self.main.getFrame(), text=scoreprt)
            #if user choose already existing user
            bouton = tk.Button(self.main.getFrame(), text="choose", command=lambda i=i: self.submitold(self.sb.getListeScores()[i]))
            temp.pack()
            bouton.pack()
            self.packed.append(temp)
            self.packed.append(bouton)
            i+=1
        self.newUser_entry.pack()
        self.packed.append(self.newUser_entry)
        sub_btn=tk.Button(self.main.getFrame(),text = 'Nouvel utilisateur', command = self.submit)
        sub_btn.pack()
        self.packed.append(sub_btn)

    def unpackall(self):
        list = self.main.getRoot().pack_slaves()
        for l in self.packed:
            l.destroy()

class Game(object):
    def __init__(self, frame, score):
        self.frame = frame
        self.fleet = Fleet()
        self.textElements = []
        self.score = score
        self.status = 0 # game playing, if 1 = win if -1 = lost
        self.height = 900
        self.width  = 1600
        self.canvas = tk.Canvas(self.frame, width=self.width, height=self.height, background="black")
        self.canvas.pack()
        self.defender = Defender()
        self.defender.install_in(self.canvas)
        self.fleet.install_in(self.canvas)

    def animation(self):
        if(self.status == 0):
            self.move_bullets()
            self.move_aliens_fleet()
            self.canvas.after(10, self.animation)
        elif(self.status == -1):
            self.addtext(self.width/2,self.height/2, "Game over, you Lost\n Score: " + str(self.score.getScore()), 30)
            self.saveScore()
        elif(self.status == 1):
            self.addtext(self.width/2,self.height/2, "Game over, you Won\n Score: " + str(self.score.getScore()), 30)
            self.saveScore()

    def start_animation(self):
        self.frame.focus_set()
        self.frame.bind("<Key>", self.keypress)
        self.canvas.after(300, self.animation)

    def move_bullets(self):
        bullettouchedAlien = self.fleet.manage_touched_aliens_by(self.canvas, self.defender)
        if bullettouchedAlien != -1:
            self.score.addScore(10)
            self.canvas.delete(bullettouchedAlien.getId())
            self.defender.getFired_bullets().remove(bullettouchedAlien)
        for bullets in self.defender.getFired_bullets():
            #returned : tuple with the object bullet and a boolean = True if the bullet is out of the canvas
            toDelete = bullets.move_in(self.canvas)
            if toDelete[1]:
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

    def saveScore(self):
        resultat = Resultat()
        resultat.fromFile("scores.txt")
        resultat.addScore(self.score)
        resultat.toFile("scores.txt")

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
        #create the defender in the center of the canvas
        self.id = canvas.create_rectangle(x/2,y , x/2+self.width, y+self.height, fill="red")


    def move_in(self,canvas, dx):
        #if the defender is in the canvas
        if(canvas.coords(self.id)[-2] < int(canvas.cget("width")) and canvas.coords(self.id)[0]>0):
            canvas.move(self.id, dx, 0)

    def fire(self, canvas):
        #if less than 8 bullets exist
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
        #create a bullet on top of the defender with the radius wanted
        self.id=canvas.create_oval(x-self.radius, y-self.radius, x+self.radius, y+self.radius, fill = self.color)

    def move_in(self, canvas):
        canvas.move(self.id, 0, -self.speed)
        if canvas.coords(self.id)[3] <= 0: # if bullet out of the frame
            return(self, True) #return the bullet and a boolean to delete it
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
            # find if the bullet is in the fleet area
            overlapped = canvas.find_overlapping(bx, by, b1x, b1y)
            # if the bullet touches an alien and it's not the defender
            if (len(overlapped) == 2 and overlapped[0] != 1):
                for alien in self.aliens_fleet:
                    if alien.getId() == overlapped[0] and alien.getAlive() == True:
                        alien.touched_by(canvas, bullets)
                        self.fleet_size -=1
                        return bullets
        #touches nothing
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
        self.alien = tk.PhotoImage(file="images/explosion.gif")
        canvas.itemconfig(self.id, image = self.alien)
        self.alive = False
        #remove the alien
        canvas.after(60,self.deleteAlien, canvas)


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

# object to manage scores before, during and after the game
class Score(object):
    def __init__(self, user, score):
        self.currentScore = score
        self.currentUser = user

    def getScore(self):
        return self.currentScore

    def getUser(self):
        return self.currentUser

    def setScore(self, value):
        self.currentScore =value

    def addScore(self, points):
        self.currentScore += points

class Resultat(object):
    def __init__(self):
        self.listeScores = []

    def addScore(self,score):
        alreadyexist = 1
        for user in self.listeScores:
            if score.getUser() == user.getUser():
                user.setScore(score.getScore())
                alreadyexist = 0
                break;
        if alreadyexist == 1:
            self.listeScores.append(score)

    def getListeScores(self):
        return self.listeScores

    def toFile(self,file):
        f=open(file,"w")
        for player in self.listeScores:
            f.write(player.getUser() + " " + str(player.getScore()) + "\n")

    def fromFile(self,file):
        f= open(file,"r")
        lines = f.readlines()
        #for each lines in the txtfile
        for l in lines:
            #split on spaces
            temp = l.split()
            #append the list with an objet score(user,score)
            self.listeScores.append(Score(temp[0],temp[1]))


SpaceInvaders().play()
