
import spacy
import glob
import pandas as pd
import en_core_web_sm
from PIL import Image
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer, util
import numpy as np


final_qa_model_path = '/Users/anupamadeo/project/mtechproject/backend/final_qa_model'


dict1 = {'What is the price of ______': "select price from menu where dish = ______",
         'Is ______ available in the restaurant': "SELECT IF((select count(*) from menu where ______ in (select dish from menu)) >0, 'YES', 'NO')"
         }
dict2 = {
    'what are the different options in ______': "select dish from menu where dish_type = ______",
    'which is the cheapest ______ available at the restaurant': """select dish from menu 
where dish_type = ______ and float_price =  (select min(float_price) from menu where dish_type = ______) """
}

dict3 = {
    'which is the cheapest dish':  "select dish from menu where float_price= (select min(float_price) from menu)",
    'What are the options available at the restaurant': "select distinct dish_type from menu"

}

documents_with_dish_entity = [
    'What is the price of ______', 'Is ______ available in the restaurant']

documents_with_dish_type_entity = [
    'what are the different options in ______',

    'which is the cheapest ______ available at the restaurant']

documents = ['which is the cheapest dish',
             'What are the options available at the restaurant']


def find_correct_predefined_question(user_question, predefined_questions):
    score = []

    model = SentenceTransformer('stsb-roberta-large')
    for i in range(len(predefined_questions)):
        sentence1 = predefined_questions[i]
        sentence2 = user_question

        embedding1 = model.encode(sentence1, convert_to_tensor=True)
        embedding2 = model.encode(sentence2, convert_to_tensor=True)
        # compute similarity scores of two embeddings
        cosine_score = util.pytorch_cos_sim(embedding1, embedding2)
        score.append(cosine_score)

    j = np.argmax(score)
    question = predefined_questions[j]
    return(question)


def find_query(menu, cursor, question):

    user_question = question

    nlp = spacy.load(final_qa_model_path, disable=['tokenizer'])

    doc = nlp(user_question)
    extracted_dish = ''
    extracted_entity = ''
    for ent in doc.ents:
        extracted_dish = str(ent.text)
        extracted_entity = str(ent.label_)

        extracted_dish = " ".join(extracted_dish.split())
    #print('extracted entity : ', extracted_entity)

    tokens = user_question.split(' ')
    if (('item' in tokens or 'dish' in tokens) and ('least' in tokens or 'cheapest' in tokens or 'lowest' in tokens)):
        extracted_dish = ''
        extracted_entity = ''

    predefined_questions = []
    modified_dict1 = {}
    modified_dict2 = {}
    modified_dict3 = {}

    if extracted_entity == 'DISH':

        for question in documents_with_dish_entity:
            new_question = question.replace('______',  "'"+extracted_dish+"'")
            new_query = str(dict1[question]).replace(
                '______',  "'"+extracted_dish+"'")
            predefined_questions.append(new_question)
            modified_dict1[new_question] = new_query

    elif extracted_entity == 'DISH TYPE':
        for question in documents_with_dish_type_entity:
            new_question = question.replace(
                '______', "'"+extracted_dish+"'")
            new_query = str(dict2[question]).replace(
                '______',  "'"+extracted_dish+"'")
            predefined_questions.append(new_question)
            modified_dict2[new_question] = new_query

    else:

        predefined_questions = documents
        for question in predefined_questions:
            query = dict3[question]
            modified_dict3[question] = query

    question = find_correct_predefined_question(
        user_question, predefined_questions)

    final_dict = {**modified_dict1, **modified_dict2, **modified_dict3}
    print('final pre-defined question : ', question)
    print('final dict query ', final_dict[question])
    return final_dict[question]
