'''
Created on Mar 17, 2018

@author: loitg
'''

class obj:
    def __init__(self):
        pass

clconfig = obj()
clconfig.date = (["%Y/%m/%d","%Y-%m-%d","%d-%m-%[yY]([ ]\(%a\))?","%d/%m/%[yY]","(%a[ ])?%d %m %Y","%d %b %Y","%d %b' %y","%b %d, %Y","%d\.%m\.%[yY]"],
                 [0.08      ,0.08      ,0.15                     ,0.3          , 0.15             , 0.05     ,0.04      ,0.05       ,0.1])
clconfig.fonts = [
    (0.10,'receipts/general_fairprice/PRINTF Regular.ttf', 0.6,0.9),
    (0.08,'receipts/general_fairprice/LEFFC2.TTF', 0.8, 1.5),
    (0.30,'receipts/general_fairprice/Merchant Copy.ttf', 0.7, 1.0),
    (0.08,'receipts/general_fairprice/Merchant Copy.ttf', 1.0, 1.2),
    (0.10,'receipts/dotted/fake receipt.ttf', 0.45, 0.85),
    (0.08,'receipts/dotted/jd_lcd_rounded.ttf',0.65, 0.95),
    (0.08,'receipts/westgate/PKMN-Mystery-Dungeon.ttf',0.7,1.3),
    (0.08,'receipts/westgate/PetMe2Y.ttf',0.8,1.5),
    (0.11,'receipts/westgate/karmasut.ttf',0.6,0.8),
    ] # Receipt CL


cmndconfig = obj()
cmndconfig.date = (["%d-%m-%Y", "%Y", "%-d-%-m-%Y"], [0.6,0.1,0.31])
cmndconfig.fontvalues = [
    (0.5, 'cmnd/chu_in/zai_Olivetti-UnderwoodStudio21Typewriter.otf', (0.9, 1.1), (0.9, 1.1)),
    (0.5, 'cmnd/chu_in/Kingthings Trypewriter 2.ttf', (0.9, 1.1), (0.9, 1.1)),
    (0.5, 'cmnd/chu_in/pala.ttf', (0.9, 1.1), (0.9, 1.1)),
    (0.5, 'cmnd/chu_in/palab.ttf', (0.9, 1.1), (0.9, 1.1)),
    
    ]

cmndconfig.fontkeys = [
    (1.0, 'cmnd/keys/arial.ttf', (0.9, 1.1), (0.9, 1.1)),
    ]

cmndconfig.fontid = [
    (0.17, 'cmnd/so_do/9thyssen.ttf', (0.9, 1.1), (1.9, 2.1)),
    (0.17, 'cmnd/so_do/CheltenhamEFBookCondensed Regular.otf', (0.9, 1.1), (1.9, 2.1)),
    (0.16, 'cmnd/so_do/Cheltenham_Book.ttf', (0.9, 1.1), (1.9, 2.1)),
    (0.25, 'cmnd/so_den/UTM Helve.ttf', (0.9, 1.1), (1.9, 2.1)),
    (0.25, 'cmnd/so_den/UTM HelveBold.ttf', (0.9, 1.1), (1.9, 2.1)),
    ] # CMND 9