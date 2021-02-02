# Invaders_to_review

# Pygame basics
https://www.pygame.org/wiki/about

Every visible object in pygame is a `Surface`.  
Surface can be "blitted" (blit is a short for "block image transfer") on any other Surface.  
So visible text is a surface, image is a surface, even simple rectangle filled with black color is a surface.  

There are images and `sprites`, which are, by and large, images with advanced features like grouping and collision detection.  
Objects like player ship, UFOs, projectiles and explosions are sprites.  

To create a text surface we need to render it from font.  
So we load a font and call `font.render` with arguments like `text` and `color`.   

To position every surface onto another surface we should use `Rect`.   
https://www.pygame.org/docs/ref/rect.html

So if we have a `screen` surface and a `ship` image, we can blit `Ship` to `screen` this way:  
  `surface.blit(ship, some_rect)`

# Project structure  
Main class is `Game`.  
It contains `Window` and `ResourceManager` instances.  
`Game` is running a main loop, switching scenes and handling basic events like `QUIT`.   

There's 3 scenes in the game.  
Menu, main scene and final scene (`you lose` screen).  
Every scene has 3 common methods.  
`handle_event(self, event)` to handle particular event like `KEYDOWN`.    
`update` to update state of every object in a scene.  
`draw` to draw every object to the given surface.  

All game object represented as sprites and widgets.  
Sprites: Player, Enemy, Projectile, Explosion.  
Widgets: Menu, LabelPanel, EnergyBar.    

Scenes create these objects, update their state and draw them.
