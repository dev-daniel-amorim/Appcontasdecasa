#aqui é para criacao de label ou image clicavel com beahivor
from kivymd.uix.label import MDLabel
from kivy.uix.image import Image
from kivy.uix.button import ButtonBehavior



class MDLabelButton(ButtonBehavior, MDLabel):
    pass

class ImageButton(ButtonBehavior, Image):
    pass

