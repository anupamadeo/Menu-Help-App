import spacy
import time
import glob
from io import BytesIO
from PIL import Image
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
import re
from PIL import Image
import requests
import connection
import question_answer
import warnings
warnings.filterwarnings("ignore")

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


def get_ocr(file_payth):

    endpoint = ''
    subscription_key = ''
    ocr_url = endpoint + "vision/v3.1/ocr"

    image_path = file_path

    image_data = open(image_path, "rb").read()
    # Set Content-Type to octet-stream
    headers = {'Ocp-Apim-Subscription-Key': subscription_key,
               'Content-Type': 'application/octet-stream'}
    params = {'language': 'unk', 'detectOrientation': 'true'}
    # put the byte array into your post request
    response = requests.post(ocr_url, headers=headers,
                             params=params, data=image_data)

    analysis = response.json()

    # Extract the word bounding boxes and text.
    line_infos = [region["lines"] for region in analysis["regions"]]
    word_infos = []
    for line in line_infos:
        for word_metadata in line:
            for word_info in word_metadata["words"]:
                word_infos.append(word_info)

    out_file = open(json_path, "w")

    json.dump(analysis, out_file, indent=6)

    out_file.close()
    print('done')


def get_dataframe(ner_model_path, json_path, menu_dish, menu_price, menu_dish_type):
    nlp = spacy.load(ner_model_path, disable=['tokenizer'])
    json_f = open(json_path)
    data = json.load(json_f)
    dishes = pd.DataFrame(columns=['dish', 'bbox'])
    prices = pd.DataFrame(columns=['price', 'bbox'])
    dish_types = pd.DataFrame(columns=['dish_type', 'bbox'])
    line_infos = [region["lines"] for region in data["regions"]]
    words = []
    bounding_boxes = []
    word_data = []
    word_bb = []
    for line in line_infos:
        for word_metadata in line:

            bounding_box = word_metadata['boundingBox']
            text = ''

            for word_info in word_metadata["words"]:
                word_data.append(word_info['text'])
                word_bb.append(word_info['boundingBox'])

                text = text+word_info['text']+' '

            doc = nlp(text)
            for ent in doc.ents:
                # print(ent.text,ent.label_)
                if ent.label == '':
                    print()

                if ent.label_ == 'DISH':
                    dishes = dishes.append(
                        {'dish': text, 'bbox': bounding_box}, ignore_index=True)
                if ent.label_ == 'PRICE':
                    prices = prices.append(
                        {'price': text, 'bbox': bounding_box}, ignore_index=True)
                if ent.label_ == 'DISH TYPE':
                    dish_types = dish_types.append(
                        {'dish_type': text, 'bbox': bounding_box}, ignore_index=True)
                if ent.text == '(non-veg)':
                    print(' TYPE : ', ent.label_)

    list1 = dishes['bbox'].str.split(',')

    text_bb1 = []
    text_bb2 = []
    text_bb3 = []
    text_bb4 = []
    for l in list1:

        text_bb1.append(int(l[0]))
        text_bb2.append(int(l[1]))
        text_bb3.append(int(l[2]))
        text_bb4.append(int(l[3]))

    dishes['text_bb1'] = text_bb1
    dishes['text_bb2'] = text_bb2
    dishes['text_bb3'] = text_bb3
    dishes['text_bb4'] = text_bb4

    list2 = prices['bbox'].str.split(',')

    price_bb1 = []
    price_bb2 = []
    price_bb3 = []
    price_bb4 = []
    for l in list2:

        price_bb1.append(int(l[0]))
        price_bb2.append(int(l[1]))
        price_bb3.append(int(l[2]))
        price_bb4.append(int(l[3]))

    prices['price_bb1'] = price_bb1
    prices['price_bb2'] = price_bb2
    prices['price_bb3'] = price_bb3
    prices['price_bb4'] = price_bb4

    list3 = dish_types['bbox'].str.split(',')

    dish_type_bb1 = []
    dish_type_bb2 = []
    dish_type_bb3 = []
    dish_type_bb4 = []
    for l in list3:

        dish_type_bb1.append(int(l[0]))
        dish_type_bb2.append(int(l[1]))
        dish_type_bb3.append(int(l[2]))
        dish_type_bb4.append(int(l[3]))

    dish_types['dish_type_bb1'] = dish_type_bb1
    dish_types['dish_type_bb2'] = dish_type_bb2
    dish_types['dish_type_bb3'] = dish_type_bb3
    dish_types['dish_type_bb4'] = dish_type_bb4

    dishes.to_csv(menu_dish, index=False)

    prices.to_csv(menu_price, index=False)
    dish_types.to_csv(menu_dish_type, index=False)


def make_dataframe(menu_dish, menu_price, menu_dish_type):
    menu = pd.DataFrame(columns=['dish', 'price'])
    dishes = pd.read_csv(menu_dish)
    dish_types = pd.read_csv(menu_dish_type)
    prices = pd.read_csv(menu_price)
    value = 1000
    difference = []
    ith_value = []
    jth_value = []

    for i in range(len(dishes)):
        value = 1000

        for j in range(len(prices)):

            diff = abs(dishes.loc[i, 'text_bb2'] -
                       prices.loc[j, 'price_bb2'])

            if diff < value:
                value = diff
                ith = i
                jth = j

        difference.append(value)
        ith_value.append(ith)
        jth_value.append(jth)
    for i in range(len(difference)):
        if difference[i] > np.mean(difference):
            continue
        else:
            menu = menu.append({'dish': dishes.loc[ith_value[i], 'dish'], 'price': prices.loc[jth_value[i],
                                                                                              'price'], 'text_bb2': dishes.loc[ith_value[i], 'text_bb2']}, ignore_index=True)

    menu.to_csv(menu_path, index=False)

    dish_names_in_dishes = dishes['dish'].values.tolist()
    dish_names_in_menus = menu['dish'].values.tolist()

    extra = [
        name for name in dish_names_in_dishes if name not in dish_names_in_menus]

    for name in extra:
        new_dish_type = dishes[dishes['dish'] == name]
        row = {'dish_type': new_dish_type['dish'].values[0],
               'bbox': new_dish_type['bbox'].values[0],
               'dish_type_bb1': new_dish_type['text_bb1'].values[0],
               'dish_type_bb2': new_dish_type['text_bb2'].values[0],
               'dish_type_bb3': new_dish_type['text_bb3'].values[0],
               'dish_type_bb4': new_dish_type['text_bb4'].values[0]}
        # print(new_dish_type)
        dish_types = dish_types.append(row, ignore_index=True)
        dish_types = dish_types.sort_values(by=['dish_type_bb2'])
        dish_types.to_csv(menu_dish_type, index=False)


def remove_special_chars(text):
    text = text.lower()
    text = re.sub('[^a-z0-9\s\n]', ' ', text)
    text = text.lstrip().rstrip()
    return text


def clean_price(text):
    text = text.lower()
    text = re.sub('[^a-z0-9\s\n.]', ' ', text)
    price = float(text)
    return price


def get_dish_types(menu_path, menu_dish_type):
    menu = pd.read_csv(menu_path)
    dish_types = pd.read_csv(menu_dish_type)

    if len(dish_types) == 0:
        for i in range(len(menu)):
            menu.loc[i, 'dish_type'] = 'not_available'

    if len(dish_types) == 1:
        for i in range(len(menu)):
            menu.loc[i, 'dish_type'] = dish_types.loc[0]['dish_type']

    y_start = 0
    y_end = 0

    for i in range(0, len(dish_types)-1):
        #print('dish_type ', dish_types.loc[i]['dish_type'])

        y_start = dish_types.loc[i]['dish_type_bb2']
        y_end = dish_types.loc[i+1]['dish_type_bb2']
        #print(y_start, y_end)

        for j in range(0, len(menu)-1):
            #print(i, j)
            #print(menu.loc[j]['text_bb2'], menu.loc[j]['dish'])
            if ((menu.loc[j]['text_bb2'] > y_start) & (menu.loc[j]['text_bb2'] < y_end)):
                menu.loc[j, 'dish_type'] = dish_types.loc[i]['dish_type']

    y_end = dish_types.loc[:]['dish_type_bb2'].values.max()
    i = dish_types[dish_types['dish_type_bb2'] == y_end].index.values[0]

    for j in range(0, len(menu)):

        if (menu.loc[j]['text_bb2'] > y_end):
            menu.loc[j, 'dish_type'] = dish_types.loc[i]['dish_type']
    menu = menu.fillna('not_available')
    menu['dish'] = menu['dish'].apply(lambda x: remove_special_chars(x))
    menu['dish_type'] = menu['dish_type'].apply(
        lambda x: remove_special_chars(x))
    menu['float_price'] = menu['price'].apply(
        lambda x: clean_price(x))
    menu[['dish', 'price', 'float_price', 'dish_type']].to_csv(
        menu_path, index=False)


