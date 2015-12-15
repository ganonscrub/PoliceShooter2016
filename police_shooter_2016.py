import sys, pygame
import math
import random

pygame.mixer.pre_init( 44100, -16, 2, 512 )
pygame.init()

screen = pygame.display.set_mode( (700, 700) )

PLAYER_IMAGES = []
PLAYER_IMAGES.append( pygame.image.load( "img/player_right.png" ).convert_alpha() )
PLAYER_IMAGES.append( pygame.image.load( "img/player_upright.png" ).convert_alpha() )
PLAYER_IMAGES.append( pygame.image.load( "img/player_up.png" ).convert_alpha() )
PLAYER_IMAGES.append( pygame.image.load( "img/player_upleft.png" ).convert_alpha() )
PLAYER_IMAGES.append( pygame.image.load( "img/player_left.png" ).convert_alpha() )
PLAYER_IMAGES.append( pygame.image.load( "img/player_downleft.png" ).convert_alpha() )
PLAYER_IMAGES.append( pygame.image.load( "img/player_down.png" ).convert_alpha() )
PLAYER_IMAGES.append( pygame.image.load( "img/player_downright.png" ).convert_alpha() )

ENEMY_IMAGES = []
ENEMY_IMAGES.append( pygame.image.load( "img/enemy_right.png" ).convert_alpha() )
ENEMY_IMAGES.append( pygame.image.load( "img/enemy_upright.png" ).convert_alpha() )
ENEMY_IMAGES.append( pygame.image.load( "img/enemy_up.png" ).convert_alpha() )
ENEMY_IMAGES.append( pygame.image.load( "img/enemy_upleft.png" ).convert_alpha() )
ENEMY_IMAGES.append( pygame.image.load( "img/enemy_left.png" ).convert_alpha() )
ENEMY_IMAGES.append( pygame.image.load( "img/enemy_downleft.png" ).convert_alpha() )
ENEMY_IMAGES.append( pygame.image.load( "img/enemy_down.png" ).convert_alpha() )
ENEMY_IMAGES.append( pygame.image.load( "img/enemy_downright.png" ).convert_alpha() )
ENEMY_IMAGES.append( pygame.image.load( "img/red_x.png" ).convert_alpha() )
ENEMY_IMAGES.append( pygame.image.load( "img/red_x_small.png" ).convert_alpha() )

BACKGROUND_MENU = pygame.image.load( "img/menu_bg.png" ).convert()

SOUND_GUNSHOT = pygame.mixer.Sound( "snd/glock18-1.wav" )
SOUND_GUNSHOT.set_volume( 0.1 )

JUSTICETEXT_FONT = pygame.font.SysFont( "monospace", 16 )

JUSTICE_TEXTS = []

PLAYER_SPEED = 0.1
ENEMY_SPEED = 0.075

class BulletShape:
    def __init__( self, angle, pos, screen ):
        self.scr = screen
        self.posX = pos[0]
        self.posY = pos[1]

        self.angle = angle
        self.speed = 1.0

    def draw( self ):
        self.rect = pygame.draw.circle( self.scr, (255,255,255), (int(self.posX),int(self.posY)), 2 )

    def update( self, dt ):
        self.posX += math.cos( self.angle ) * self.speed * dt
        self.posY += math.sin( self.angle ) * self.speed * dt
        self.draw()

class Player( pygame.sprite.Sprite ):
    def __init__( self, screen ):
        super(Player,self).__init__()

        self.shootSound = SOUND_GUNSHOT
        self.reloadSound = pygame.mixer.Sound( "snd/reload.wav" )
        self.justiceSound = pygame.mixer.Sound( "snd/justice.wav" )
        self.justiceSound.set_volume( 0.25 )
        self.deadSound = pygame.mixer.Sound( "snd/dead.wav" )
        self.emptySound = pygame.mixer.Sound( "snd/empty.wav" )

        self.screen = screen

        self.images = PLAYER_IMAGES

        self.image = self.images[0]
        
        self.rect = self.image.get_rect()
        
        self.bullets = []
        self.maxBulletAge = 500
        
        self.maxAmmoInMagazine = 20
        self.currentAmmoInMagazine = self.maxAmmoInMagazine
        self.reserveAmmo = 100

        self.moveSpeed = PLAYER_SPEED

        self.score = 0

        self.health = 100

        self.scoreFont = pygame.font.SysFont( "monospace", 28 )
        self.scoreFont.set_bold( True )
        self.uiFont = pygame.font.SysFont( "monospace", 24 )

        self.posX = screen.get_width() / 2
        self.posY = screen.get_height() / 2
        self.rect.x = self.posX
        self.rect.y = self.posY

    def getHurt( self ):
        self.health -= 10

    def move( self, x, y, dt ):
        self.posX += x * self.moveSpeed * dt
        self.posY += y * self.moveSpeed * dt
        self.rect.x = self.posX
        self.rect.y = self.posY
        
    def getBulletRects( self ):
        ret = []
        for i in range( len(self.bullets) ):
            ret.append( self.bullets[i].rect )
        return ret
    
    def gunReload( self ):
        if self.reserveAmmo > 0 and self.currentAmmoInMagazine < self.maxAmmoInMagazine:
            self.reloadSound.play()
            roundsNeeded = self.maxAmmoInMagazine - self.currentAmmoInMagazine
            self.reserveAmmo -= roundsNeeded
            self.currentAmmoInMagazine += roundsNeeded
            if self.reserveAmmo < 0:
                self.currentAmmoInMagazine += self.reserveAmmo
                self.reserveAmmo = 0

    def shoot( self ):
        if self.currentAmmoInMagazine > 0:
            self.shootSound.stop()
            self.shootSound.play()
            dx = float( pygame.mouse.get_pos()[0] - ( self.rect.x + 16 ) )
            dy = float( pygame.mouse.get_pos()[1] - ( self.rect.y + 16 ) )
            if dx == 0:
                dx = 0.000001
                
            angle = math.atan( dy / dx )
            if dx < 0:
                angle += math.pi
            newBullet = BulletShape( angle, ( self.rect.x + 16, self.rect.y + 16 ), self.screen )
            self.bullets.append( newBullet )
            self.currentAmmoInMagazine -= 1

    def setSprite( self ):
        section = 2 * math.pi / len(self.images)

        dx = float( pygame.mouse.get_pos()[0] - (self.rect.x + 16) )
        dy = float( pygame.mouse.get_pos()[1] - (self.rect.y + 16) )
        if dx == 0:
            dx = 0.000001
            
        angle = math.atan( dy / dx )
        cut = angle / section
        target = round( cut, 0 )

        if target == 0 and dx > 0:
            self.image = self.images[0]
        elif target == 0 and dx < 0:
            self.image = self.images[4]

        elif target == 1 and dy > 0:
            self.image = self.images[7]
        elif target == 1 and dy < 0:
            self.image = self.images[3]

        elif target == -1 and dy > 0:
            self.image = self.images[5]
        elif target == -1 and dy < 0:
            self.image = self.images[1]

        elif target == 2 and dy > 0:
            self.image = self.images[6]
        elif target == 2 and dy < 0:
            self.image = self.images[3]

        elif target == -2 and dy > 0:
            self.image = self.images[5]
        elif target == -2 and dy < 0:
            self.image = self.images[2]

    def update( self, dt ):        
        self.setSprite()
        
        for i in range( len(self.bullets) ):
            self.bullets[i].update( dt )

        wid = screen.get_width()
        hei = screen.get_height()
        
        for i in range( len(self.bullets) - 1, -1, -1 ):
            bX = self.bullets[i].posX
            bY = self.bullets[i].posY
            if bX < 0 or bX > wid or bY < 0 or bY > hei:
                self.bullets.remove( self.bullets[i] )

class JusticeText:
    def __init__( self, screen, posX, posY ):
        self.scr = screen
        self.posX = posX
        self.posY = posY

        self.textX = posX
        self.textY = posY

        self.font = JUSTICETEXT_FONT
        self.ticker = 0

        self.life = 1000
        self.elapsed = 0
        self.timer = pygame.time.Clock()
        self.dead = False

    def update( self, dt ):
        self.textX = math.sin( self.ticker ) * 10 + self.posX
        self.textY -= 0.03
        self.ticker += 0.01 * dt

        if self.elapsed > self.life:
            self.dead = True

        self.elapsed += self.timer.tick()

    def draw( self ):
        toDraw = self.font.render( "Justice +1", True, (255,255,0))
        self.scr.blit( toDraw, (self.textX - toDraw.get_width() / 2,self.textY) )

def handleJusticeTexts( arr, dt ):
    for i in range( len(arr) - 1, -1, -1 ):
        arr[i].update( dt )
        arr[i].draw()
        if arr[i].dead:
            arr.remove( arr[i] )

class Enemy( pygame.sprite.Sprite ):
    def __init__( self, screen, player, spritelist, enemylist ):
        super(Enemy,self).__init__()

        self.shootSound = SOUND_GUNSHOT

        self.screen = screen
        self.player = player
        self.image = pygame.image.load( "img/player.png" ).convert_alpha()

        self.spritelist = spritelist

        self.images = ENEMY_IMAGES
        
        self.rect = self.image.get_rect()
        
        self.bullets = []
        self.maxBulletAge = 500
        
        self.timeSinceLastShoot = 0
        self.minTimeToShoot = 1000
        self.shootTimer = pygame.time.Clock()

        self.moveSpeed = ENEMY_SPEED
        self.maxDistToPlayer = 200

        self.posX = 0.0
        self.posY = 0.0

        self.dead = False

    def setPos( self, newX, newY ):
        self.posX = newX
        self.posY = newY
        self.rect.x = self.posX
        self.rect.y = self.posY

    def shoot( self ):
        self.shootSound.play()
        dx = float( (self.player.rect.x + 16) - (self.rect.x + 16) )
        dy = float( (self.player.rect.y + 16) - (self.rect.y + 16) )
        if dx == 0:
            dx = 0.000001
            
        angle = math.atan( dy / dx )
        if dx < 0:
            angle += math.pi
        newBullet = BulletShape( angle, ( self.rect.x, self.rect.y ), self.screen )
        self.bullets.append( newBullet )

    def getBulletRects( self ):
        ret = []
        for i in range( len(self.bullets) ):
            ret.append( self.bullets[i].rect )
        return ret

    def die( self ):
        self.dead = True
        self.image = self.images[9]
        self.setPos( self.posX + (self.image.get_width() / 2), self.posY + (self.image.get_height() / 2) )

    def setSprite( self ):
        section = 2 * math.pi / len(self.images)

        dx = float( (self.player.rect.x + 16) - (self.rect.x + 16) )
        dy = float( (self.player.rect.y + 16) - (self.rect.y + 16) )
        if dx == 0:
            dx = 0.000001
            
        angle = math.atan( dy / dx )
        cut = angle / section
        target = round( cut, 0 )

        if target == 0 and dx > 0:
            self.image = self.images[0]
        elif target == 0 and dx < 0:
            self.image = self.images[4]

        elif target == 1 and dy > 0:
            self.image = self.images[7]
        elif target == 1 and dy < 0:
            self.image = self.images[3]

        elif target == -1 and dy > 0:
            self.image = self.images[5]
        elif target == -1 and dy < 0:
            self.image = self.images[1]

        elif target == 2 and dy > 0:
            self.image = self.images[6]
        elif target == 2 and dy < 0:
            self.image = self.images[3]

        elif target == -2 and dy > 0:
            self.image = self.images[5]
        elif target == -2 and dy < 0:
            self.image = self.images[2]

    def move( self, dt ):
        dx = float( (self.player.rect.x + 16) - (self.rect.x + 16) )
        dy = float( (self.player.rect.y + 16) - (self.rect.y + 16) )
        if dx == 0:
            dx = 0.000001
        
        tarPos = (self.player.rect.x + 16, self.player.rect.y + 16)
        distToPlayer = math.sqrt( (dx**2) + (dy**2) )

        angle = math.atan( dy / dx )
        if dx < 0:
            angle += math.pi
        
        if distToPlayer > self.maxDistToPlayer:
            self.posX += math.cos( angle ) * self.moveSpeed * dt
            self.posY += math.sin( angle ) * self.moveSpeed * dt
            self.rect.x = self.posX
            self.rect.y = self.posY
        elif self.timeSinceLastShoot > self.minTimeToShoot:
            self.shoot()
            self.timeSinceLastShoot = 0

    def update( self, dt ):
        if not self.dead:
            self.setSprite()

            self.move( dt )
            
            for i in range( len(self.bullets) ):
                self.bullets[i].update( dt )

            wid = screen.get_width()
            hei = screen.get_height()
        
            for i in range( len(self.bullets) - 1, -1, -1 ):
                bX = self.bullets[i].posX
                bY = self.bullets[i].posY
                if bX < 0 or bX > wid or bY < 0 or bY > hei:
                    self.bullets.remove( self.bullets[i] )

            self.timeSinceLastShoot += self.shootTimer.tick()

def runMenu( screen ):
    pygame.mixer.music.load( "mus/menu.ogg" )
    pygame.mixer.music.play()  
    
    done = False

    menuFont = pygame.font.SysFont( "monospace", 28 )
    menuFont.set_bold( True )    
    gameTitle = menuFont.render( "POLICE SHOOTER 2016", True, (0,0,0) )
    
    playGameSelected = False
    exitGameSelected = False

    mid = screen.get_height() / 2

    playStart = mid + 30
    exitStart = playStart + 25

    while not done:        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                done = True
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    done = True
                    return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:                
                if playGameSelected:
                    pygame.mixer.music.fadeout(500)
                    return True
                if exitGameSelected:
                    pygame.mixer.music.stop()
                    return False

        if pygame.mouse.get_pos()[1] > playStart and pygame.mouse.get_pos()[1] < playStart + 25:
            playGame = menuFont.render( "Play Game", True, (255,0,0) )
            playGameSelected = True
        else:
            playGame = menuFont.render( "Play Game", True, (0,0,0) )
            playGameSelected = False

        if pygame.mouse.get_pos()[1] > exitStart and pygame.mouse.get_pos()[1] < exitStart + 25:
            exitGame = menuFont.render( "Exit", True, (255,0,0) )
            exitGameSelected = True
        else:
            exitGame = menuFont.render( "Exit", True, (0,0,0) )
            exitGameSelected = False
        
        screen.fill( (96, 96, 96) )

        screen.blit( BACKGROUND_MENU, BACKGROUND_MENU.get_rect() )

        screen.blit( gameTitle, ((screen.get_width() / 2) - (gameTitle.get_width() / 2), mid - 50 ) )
        screen.blit( playGame, ((screen.get_width() / 2) - (playGame.get_width() / 2), playStart ) )        
        screen.blit( exitGame, ((screen.get_width() / 2) - (exitGame.get_width() / 2), exitStart) )
        
        pygame.display.flip()

        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()

def spawnEnemy( screen, player, spritegroup, enemylist ):
    w = screen.get_width()
    h = screen.get_height()

    x = w / 4
    y = h / 4
    
    possiblePoints = [ (-32,-32), (w+32,-32), (-32,h+32), (w+32,h+32),
                       (x,-32), (x*2,-32), (x*3,-32), (x*4,-32),
                       (x,-32), (x*2,-32), (x*3,-32), (x*4,-32),
                       (-32,y), (-32,y*2), (-32,y*3), (-32,y*4),
                       (x,h+32), (x*2,h+32), (x*3,h+32), (x*4,h+32),
                       (w+32,y), (w+32,y*2), (w+32,y*3), (w+32,y*4)]
    
    newEnemy = Enemy( screen, player, spritegroup, enemylist )

    randPoint = random.choice( possiblePoints )

    newEnemy.setPos( randPoint[0], randPoint[1] )
    spritegroup.add( newEnemy )
    enemylist.append( newEnemy )

def runGame():
    pygame.mixer.music.load( "mus/game.ogg" )
    pygame.mixer.music.play() 
    
    done = False

    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()

    player = Player( screen )
    all_sprites.add( player )

    enemyList = []

    spawnEnemy( screen, player, all_sprites, enemyList )
    spawnEnemy( screen, player, all_sprites, enemyList )
    spawnEnemy( screen, player, all_sprites, enemyList )
    spawnEnemy( screen, player, all_sprites, enemyList )
    spawnEnemy( screen, player, all_sprites, enemyList )
    
    enemiesSpawned = 5
    enemiesKilled = 0
    shotsFired = 0

    right = screen.get_width()
    bot = screen.get_height()
    
    while not done:
        dt = clock.tick()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
                elif event.key == pygame.K_r:
                    player.gunReload()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if player.currentAmmoInMagazine > 0:
                    shotsFired += 1                    
                    player.shoot()
                else:
                    player.emptySound.stop()
                    player.emptySound.play()
                
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_w]:
            player.move( 0, -1, dt )
        if pressed[pygame.K_s]:
            player.move( 0, 1, dt )
        if pressed[pygame.K_a]:
            player.move( -1, 0, dt )
        if pressed[pygame.K_d]:
            player.move( 1, 0, dt )
        
        screen.fill( (60,196,60) )

        all_sprites.update( dt )
        all_sprites.draw( screen )

        for i in range( len(enemyList) ):
            curEnemy = enemyList[i]
            playerCollide = player.rect.collidelist( curEnemy.getBulletRects() )
            if playerCollide != -1:
                curEnemy.bullets.remove( curEnemy.bullets[playerCollide] )
                player.getHurt()
                
        for i in range( len(enemyList) ):
            curEnemy = enemyList[i]
            enemyCollide = curEnemy.rect.collidelist( player.getBulletRects() )
            if enemyCollide != -1:
                if enemyList[i].dead == False:
                    player.bullets.remove( player.bullets[enemyCollide] )
                    JUSTICE_TEXTS.append( JusticeText( screen, enemyList[i].rect.x + 16, enemyList[i].rect.y ) )
                    enemyList[i].die()
                    player.justiceSound.play()
                    spawnEnemy( screen, player, all_sprites, enemyList )

                    enemiesKilled += 1
                    player.score += 1
                    enemiesSpawned += 1

        screen.blit( player.uiFont.render( "Ammo Remaining: " + str(player.reserveAmmo), True, (255,255,255) ), (right-275,bot-50) )
        screen.blit( player.uiFont.render( "Magazine: " + str(player.currentAmmoInMagazine), True, (255,255,255) ), (right-275,bot-30) )

        healthColor = (0,0,255)
        if player.health < 80 and player.health > 40:
            healthColor = (255,255,0)
        elif player.health <= 40:
            healthColor = (255,0,0)
        screen.blit( player.uiFont.render( "Health: " + str(player.health), True, healthColor ), (10,bot-30) )

        if player.currentAmmoInMagazine == 0:
            if player.reserveAmmo == 0:
                screen.blit( player.uiFont.render( "Out of Ammo!", True, (255,0,0) ), (player.rect.x-40,player.rect.y+40) )
            else:
                screen.blit( player.uiFont.render( "Press R to reload!", True, (255,0,0) ), (player.rect.x-60,player.rect.y+40) )

        screen.blit( player.scoreFont.render( "Justice: " + str(player.score), True, (0,0,0) ), (0,0) )

        handleJusticeTexts( JUSTICE_TEXTS, dt )
        
        pygame.display.flip()

        if player.health <= 0:
            player.deadSound.play()
            pygame.mixer.music.fadeout(1000) 
            return [ enemiesSpawned, enemiesKilled, shotsFired ]

        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()

def runStats( statsArr ):
    pygame.mixer.music.load( "mus/stats.ogg" )
    pygame.mixer.music.play()

    statsitemSound = pygame.mixer.Sound( "snd/statsitem.wav" )
    statsitemlastSound = pygame.mixer.Sound( "snd/statsitemlast.wav" )
    
    done = False

    textTimer = pygame.time.Clock()
    elapsed = 0

    font = pygame.font.SysFont( "monospace", 32 )

    textSpawned = font.render( "Enemies Spawned: " + str(statsArr[0]), True, (255,255,255) )
    textJustice = font.render( "Justice Attained: " + str(statsArr[1]), True, (255,255,255) )
    textFired = font.render( "Shots Fired: " + str(statsArr[2]), True, (255,255,255) )
    textReturn = font.render( "Press Esc to return to menu", True, (255,255,255) )

    font.set_bold( True )

    if statsArr[2] == 0:
        textAccuracy = font.render( "Overall Accuracy: 0%", True, (255,255,255) )
    else:
        textAccuracy = font.render( "Overall Accuracy: " + str( round( float(statsArr[1]) / float(statsArr[2]) * 100, 0 ) ) + "%", True, (255,255,255) )

    w = screen.get_width()

    spawnedAdd = False
    justiceAdd = False
    firedAdd = False
    accuracyAdd = False
    
    while not done:        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True

        screen.fill( (98,30,30) )

        if elapsed > 1500:
            screen.blit( textSpawned, ( w / 2 - textSpawned.get_width() / 2, 200 ) )
            if not spawnedAdd:
                spawnedAdd = True
                statsitemSound.play()
                
        if elapsed > 3000:
            screen.blit( textJustice, ( w / 2 - textJustice.get_width() / 2, 250 ) )
            if not justiceAdd:
                justiceAdd = True
                statsitemSound.play()

        if elapsed > 4500:
            screen.blit( textFired, ( w / 2 - textFired.get_width() / 2, 300 ) )
            if not firedAdd:
                firedAdd = True
                statsitemSound.play()

        if elapsed > 6500:
            screen.blit( textAccuracy, ( w / 2 - textAccuracy.get_width() / 2, 400 ) )
            if not accuracyAdd:
                accuracyAdd = True
                statsitemlastSound.play()

        if elapsed > 7500:
            screen.blit( textReturn, ( w / 2 - textAccuracy.get_width() / 2, 450 ) )
        
        pygame.display.flip()

        elapsed += textTimer.tick()

        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play()
        
    pygame.mixer.music.fadeout(1000)

def run():
    random.seed()
    
    while runMenu( screen ) == True:
        stats = runGame()
        if stats:
            runStats( stats )
    
    pygame.display.quit()
        
run()
