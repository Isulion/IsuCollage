from dataclasses import dataclass

@dataclass
class Colors:
    # Couleurs système iOS Dark Mode
    SYSTEM_BLUE = '#0A84FF'
    SYSTEM_GRAY = '#8E8E93'
    SYSTEM_GRAY2 = '#636366'
    SYSTEM_GRAY6 = '#1C1C1E'
    SYSTEM_BLACK = '#000000'
    SYSTEM_WHITE = '#FFFFFF'
    
    # Couleurs sémantiques Dark Mode
    PRIMARY = SYSTEM_BLUE
    BACKGROUND = '#1C1C1E'  # Fond principal sombre
    SURFACE = '#2C2C2E'     # Surface des cartes
    TEXT = SYSTEM_WHITE
    TEXT_SECONDARY = SYSTEM_GRAY
    DIVIDER = SYSTEM_GRAY2

@dataclass
class Spacing:
    XS = 4
    S = 8
    M = 16
    L = 24
    XL = 32

@dataclass
class Typography:
    TITLE = ('SF Pro Display', 24, 'bold')
    SUBTITLE = ('SF Pro Display', 17)
    BODY = ('SF Pro Text', 15)
    CAPTION = ('SF Pro Text', 13)
    BUTTON = ('SF Pro Text', 17) 