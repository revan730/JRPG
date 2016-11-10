# -*- coding: utf-8 -*-
import pygame as pg
from ResourceHelpers import StringsHelper
from Player import Usable, Armor, Weapon

LBL_BLUE = '#00E6E6'

class MenuItem:
    """
    Represents text menu item,which can be active or inactive
    """
    def __init__(self, identifier, text, font, size, color_inactive, color_active, x, y, centered=True):
        """
        Initialize menu item
        :param text: text of item
        :param font: font file
        :param size: size
        :return:
        """
        self.id = identifier
        self.caption = text
        self.color_active = color_active
        self.color_inactive = color_inactive
        self.font = pg.font.Font(font, size)
        self.set_inactive()
        if centered:
            self.rect = self.image.get_rect(center=(x, y))
        else:
            self.rect = self.image.get_rect(x=x, y=y)

    def set_active(self):
        self.image = self.font.render(self.caption, True, pg.Color(self.color_active))

    def set_inactive(self):
        self.image = self.font.render(self.caption, True, pg.Color(self.color_inactive))


class Label:
    """
    Represents text label
    """
    def __init__(self, text, color, font_file, size, x, y):
        self.color = color
        self.font_file = font_file
        self.size = size
        self.x = x
        self.y = y
        self.set(text)


    def set(self, text):
        """
        Sets label text
        :param text: text string
        :return:
        """
        self.font = pg.font.Font(self.font_file, self.size)
        self.image = self.font.render(text, True, pg.Color(self.color))
        self.rect = self.image.get_rect(x=self.x, y=self.y)

class InfoItem:
    """
    Represents text item with caption and value,cannot be selected
    """
    def __init__(self, text, value, font, size, x, y):
        self.caption = text
        self.font_size = size
        self.label_color = LBL_BLUE
        self.value_color = 'white'
        self.font = pg.font.Font(font, size)
        self.x = x
        self.y = y
        self.set_value(value)

    def set_value(self, value):
        """
        Set value for item
        :param value: string value
        :return:
        """
        self.value = str(value)
        self.label_text = self.font.render(self.caption, True, pg.Color(self.label_color))
        self.label_rect = self.label_text.get_rect(x=self.x, y=self.y)
        self.value_text = self.font.render(self.value, True, pg.Color(self.value_color))
        self.value_rect = self.value_text.get_rect(center=(self.x + 100, self.y + 5))


class Window:
    """
    Basic window class for menu's,like pause,battle action,inventory
    """
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.quit = False
        self.bg = pg.Surface((width, height))
        self.bg.fill(pg.Color('#000060'))
        self.menu_items = []

    def draw(self, surface):
        surface.blit(self.bg, (self.x, self.y))

    def update(self, key):
        """
        Update window state
        :param key: pygame key code of pressed key
        :return:
        """
        pass


class MessageWindow(Window):
    """
    Window which shows message text
    """

    def __init__(self, x, y, width, height, message):
        super().__init__(x, y, width, height)
        self.lbl = Label(message, 'white', None, 24, self.x + self.width / 2, self.y + self.height / 2)

    def draw(self, surface):
        super().draw(surface)
        surface.blit(self.lbl.image, self.lbl.rect)

    def update(self, key):
        if key == pg.K_RETURN or key == pg.K_f:
            self.quit = True


class SelectCharacterWindow(Window):
    """
    Dialog window which prints all player party characters to select.Stores selection in 'selected'
    field
    """

    def __init__(self, x, y, width, height, party):
        super().__init__(x ,y, width, height)
        self.selected = None
        item_strings = []
        self.index = 0
        self.party = party
        for i in party:
            item_strings.append(str(i))
        self.add_items(item_strings)
        self.set_cursor()

    def add_items(self, item_strings):
        font_size = 36

        x = self.x + self.width / 2
        padding = self.height / 2 + self.y - font_size / 2  # starting padding for first item to be near window center
        y = padding
        ind = 0
        for i in item_strings:
            item = MenuItem(ind, i, None, font_size, 'white', 'green', x, y)
            self.menu_items.append(item)
            y += font_size
            ind += 1

    def draw(self, surface):
        super().draw(surface)
        for i in self.menu_items:
            surface.blit(i.image, i.rect)

    def update(self, key):
        if key == pg.K_w or key == pg.K_UP:
            self.prev_item()
        elif key == pg.K_s or key == pg.K_DOWN:
            self.next_item()
        elif key == pg.K_RETURN or key == pg.K_f:
            self.choose_item()

    def next_item(self):
        if self.index + 1 < len(self.menu_items):
            self.menu_items[self.index].set_inactive()
            self.index += 1
            self.set_cursor()

    def prev_item(self):
        if self.index > 0:
            self.menu_items[self.index].set_inactive()
            self.index -= 1
            self.set_cursor()

    def choose_item(self):
        self.selected = self.party[self.index]
        self.quit = True

    def set_cursor(self):
        self.menu_items[self.index].set_active()

class PauseWindow(Window):
    """
    Pause window which is called by game state when it's paused
    """
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        helper = StringsHelper("en")
        menu_strings = helper.get_strings("pause_menu")
        self.add_items(menu_strings)
        self.cursor_pos = 0
        self.set_cursor()

    def add_items(self, item_strings):
        font_size = 36

        x = self.x + self.width / 2
        padding = self.height / 2 + self.y - font_size / 2  # starting padding for first item to be near window center
        y = padding
        for i in sorted(item_strings.keys()):
            item = MenuItem(i, item_strings[i], None, font_size, 'white', 'green', x, y)
            self.menu_items.append(item)
            y += font_size

    def draw(self, surface):
        super().draw(surface)
        for i in self.menu_items:
            surface.blit(i.image, i.rect)

    def update(self, key):
        if key == pg.K_w or key == pg.K_UP:
            self.prev_item()
        elif key == pg.K_s or key == pg.K_DOWN:
            self.next_item()
        elif key == pg.K_RETURN or key == pg.K_f:
            self.choose_item()

    def next_item(self):
        if self.cursor_pos + 1 < len(self.menu_items):
            self.menu_items[self.cursor_pos].set_inactive()
            self.cursor_pos += 1
            self.set_cursor()

    def prev_item(self):
        if self.cursor_pos > 0:
            self.menu_items[self.cursor_pos].set_inactive()
            self.cursor_pos -= 1
            self.set_cursor()

    def choose_item(self):
        if self.cursor_pos == 0:
            self.quit = True
        elif self.cursor_pos == 1:
            quit_event = pg.event.Event(pg.QUIT)
            pg.event.post(quit_event)

    def set_cursor(self):
        self.menu_items[self.cursor_pos].set_active()


class PartyWindow(Window):
    """
    Party window which shows information about party members stats
    """
    def __init__(self, x, y, width, height, party):
        super().__init__(x, y, width, height)
        self.party = party
        self.current_member = party[0]
        self.index = 0
        helper = StringsHelper("en")
        self.first_column_strings = helper.get_strings("party_menu_info_first")
        self.second_column_strings = helper.get_strings("party_menu_info_second")
        self.spell_string = helper.get_string("party_menu_info_others", "sp")
        self.spell_items = []
        self.drawables = []
        self.set_character()

    def update(self, key):  # TODO: Refactor
        if key == pg.K_d or key == pg.K_RIGHT:
            self.index += 1
            if self.index > len(self.party) - 1:
                self.index = 0
        elif key == pg.K_a or key == pg.K_LEFT:
            self.index -= 1
            if self.index < 0:
                self.index = len(self.party) - 1
        self.current_member = self.party[self.index]
        self.set_character()

    def set_character(self):
        self.drawables.clear()
        self.set_portrait()
        self.add_info_items()

    def set_portrait(self):
        self.portrait = self.current_member.portrait
        rect = self.portrait[1]
        rect.x = self.x + self.width * 0.01
        rect.y = self.y + self.height * 0.01
        self.drawables.append(Label(self.current_member.name, LBL_BLUE, None,  24, rect.x + rect.width + 10, rect.y + 10))
        self.drawables.append(Label(str(self.current_member), LBL_BLUE, None, 24, rect.x + rect.width + 10, rect.y + 25))

    def add_info_items(self): # TODO: Font size must be selected to match screen resolution
        font_size = 18
        atrs = self.current_member.get_attributes()
        worn_items = self.current_member.get_worn_items()
        x = self.x + self.width * 0.01
        padding_first = self.y + self.height * 0.1 + self.portrait[1].height - font_size / 2  # starting padding for first item to be near window center
        y = padding_first
        for i in sorted(self.first_column_strings.keys()):
            self.drawables.append(InfoItem(self.first_column_strings[i], atrs[i[2:]], None, font_size, x, y))
            y += self.height * 0.06

        y = padding_first
        x = self.drawables[-1].value_rect.x + self.width * 0.05
        for i in sorted(self.second_column_strings.keys()):
            item = worn_items[i[2:]]
            value = str(item)
            self.drawables.append(InfoItem(self.second_column_strings[i], value, None, font_size, x, y))
            y += self.height * 0.06

        self.add_spells(self.drawables[-1].value_rect.x, padding_first, font_size)

    def add_spells(self, left_x, padding_first, font_size):
        x = left_x + self.width * 0.20
        y = padding_first - self.height * 0.06
        self.drawables.append(Label(self.spell_string, LBL_BLUE, None, 24, x, y))
        for i in self.current_member.spells:
            y += self.height * 0.06
            lbl = Label(str(i), 'white', None, font_size, x, y)
            self.drawables.append(lbl)

    def draw(self, surface):
        super().draw(surface)
        surface.blit(*self.portrait)
        for i in self.drawables:
            if type(i) is InfoItem:
                surface.blit(i.label_text, i.label_rect)
                surface.blit(i.value_text, i.value_rect)
            else:
                surface.blit(i.image, i.rect)


class InventoryWindow(Window):
    """
    Inventory window which shows content of party inventory,allows interaction with it
    """

    def __init__(self, x, y, width, height, party):
        super().__init__(x, y, width, height)
        self.party = party
        self.index = 0
        self.drawables = []
        self.description = None
        self.menu_items = []
        self.load_items()
        self.set_cursor()
        self.dialog = None

    def load_items(self):
        font_size = 18
        y = self.y + self.height * 0.1 + font_size / 2
        x = self.x + self.width * 0.01

        self.drawables.clear()
        self.menu_items.clear()
        for i in self.party.inventory:
            item = MenuItem(i,str(i),None,font_size,'white',LBL_BLUE,x ,y, False)
            self.drawables.append(item)
            self.menu_items.append(item)
            y+= self.height * 0.06


    def draw(self, surface):
        super().draw(surface)
        for i in self.drawables:
            surface.blit(i.image, i.rect)
        surface.blit(self.description.image, self.description.rect)
        if self.dialog is not None:
            self.dialog.draw(surface)

    def update(self, key):
        if self.dialog is not None:
            self.dialog.update(key)
            if self.dialog.quit == True:
                if type(self.dialog) is SelectCharacterWindow:
                    self.apply_selection(self.dialog.selected)
                self.dialog = None
        else:
            if key == pg.K_DOWN or key == pg.K_s:
                self.next_item()
            elif key == pg.K_UP or key == pg.K_w:
                self.prev_item()
            elif key == pg.K_RETURN or key == pg.K_f:
                self.choose_item()

    def set_cursor(self):
        self.menu_items[self.index].set_active()
        text = self.party.inventory[self.index].info
        self.description = Label(text, 'white', None, 18, self.x + self.width * 0.01, self.y + self.height * 0.05)

    def next_item(self):
        if self.index + 1 < len(self.menu_items):
            self.menu_items[self.index].set_inactive()
            self.index += 1
            self.set_cursor()

    def prev_item(self):
        if self.index > 0:
            self.menu_items[self.index].set_inactive()
            self.index -= 1
            self.set_cursor()

    def create_message(self, msg):
        self.dialog = MessageWindow(self.width / 2, self.height / 2, 100, 100, msg)

    def create_character_dialog(self):
        self.dialog = SelectCharacterWindow(self.width / 2, self.height / 2, 100, 100, self.party)

    def apply_selection(self, target):
        if type(self.party.inventory[self.index]) is Weapon:
            self.party.inventory.append(target.weapon)
            target.weapon = self.party.inventory[self.index]
        elif type(self.party.inventory[self.index]) is Armor:
            self.party.inventory.append(target.armor)

        del self.party.inventory[self.index]

        self.load_items()
        self.set_cursor()

    def choose_item(self):
        item = self.party.inventory[self.index]
        if type(item) is Usable:
            self.create_message('This item can be only used in battle')
        else:
            self.create_character_dialog()
