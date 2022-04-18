from matplotlib.pyplot import title
import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy_garden.xcamera import XCamera
from kivy.uix.camera import Camera
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty
from kivy.properties import BooleanProperty, StringProperty
import sample
import connection
import questio_answer
import pandas as pd

conn = None
cur = None
menu = None

file_path = 'img1.jpg'
file = file_path[:-4]
file_folder_path = '/Users/anupamadeo/project/mtechproject/backend/images/'
json_folder_path = '/Users/anupamadeo/project/mtechproject/backend/json/'
menu_folder_path = '/Users/anupamadeo/project/mtechproject/backend/dataframe/'
file_path = file_folder_path + file + '.jpg'
json_path = json_folder_path + file + '.json'
menu_path = menu_folder_path + file + '_menu' + '.csv'
menu_dish = menu_folder_path + file + '_menu_dish' + '.csv'
menu_price = menu_folder_path + file + '_menu_price' + '.csv'
menu_dish_type = menu_folder_path + file + '_menu_dish_type' + '.csv'
ner_model_path = '/Users/anupamadeo/project/mtechproject/backend/ner_model'


class MainWindow(Screen):
    pass


class SecondWindow(Screen):

    def next(self):
        show_popup().open()

    def image_process(self,):
        print('file_path : ', file_path)
        sample.get_ocr(file_path)
        file = file_path[-8:-4]
        print('file : ', file)

    def image_process(self, file_path):
        global conn, menu, cur
        sample.get_dataframe(ner_model_path, json_path,
                             menu_dish, menu_price, menu_dish_type)
        sample.make_dataframe(menu_dish, menu_price, menu_dish_type)
        sample.get_dish_types(menu_path, menu_dish_type)
        menu = pd.read_csv(menu_path)
        conn, cur = connection.create_connection()
        connection.create_database(cursor=cur)
        connection.use_db(cursor=cur)
        connection.create_table(cursor=cur)
        connection.insert_values(connection=conn, cursor=cur, menu=menu)
        print('_______')


class ThirdWindow(Screen):
    data_items = StringProperty()

    query = ObjectProperty(None)
    answer = ObjectProperty(None)

    def btn(self):
        self.data_items = ""
        question = self.query.text
        sql_query = questio_answer.find_query(menu, cur, question)
        result = connection.execute_query(cur, sql_query)
        print('required answer is : ')
        data = ' '
        for row in result:
            for col in row:
                self.data_items = self.data_items + "   " + str(col)

    def btn1(self):
        self.query.text = " "
        self.answer.text = " "

    def remove_connection(self):
        connection.delete_table(cur)
        connection.delete_database(cur)
        print('done')

    def next1(self):
        show_popup1().open()


class WindowManager(ScreenManager):
    pass


class P(FloatLayout):
    pass


class P1(FloatLayout):
    def remove_connection(self):
        connection.delete_table(cur)
        connection.delete_database(cur)
        print('done')


kv = Builder.load_file('my.kv')


class MyMainApp(App):

    def build(self):
        global menu_path, conn, cur, menu
        return kv


def show_popup():
    show = P()
    popupWindow = Popup(title="Message", content=show,
                        size_hint=(None, None), size=(420, 400))
    return popupWindow


def show_popup1():
    show = P1()
    popupWindow = Popup(title="Message", content=show,
                        size_hint=(None, None), size=(420, 400))
    return popupWindow


if __name__ == '__main__':
    MyMainApp().run()
