
from mysql import connector
import pandas as pd


def create_connection():
    connection = connector.connect(
        host='localhost',
        user='root',
        password='deep@learning123')
    cursor = connection.cursor()
    return connection, cursor


def create_database(cursor):
    create_db = "create database restaurant_menu"
    cursor.execute(create_db)


def use_db(cursor):
    use_db = 'use restaurant_menu'
    cursor.execute(use_db)


def create_table(cursor):
    create_table = """ create table if not exists menu(
    dish varchar(255),
    price varchar(255),
    float_price float,
    dish_type varchar(255)
    ); """

    cursor.execute(create_table)


def insert_values(connection, cursor, menu):
    cols = ",".join([str(i) for i in menu.columns.tolist()])
    for i, row in menu.iterrows():
        sql = "INSERT INTO menu (" + cols + ") VALUES (" + \
            "%s,"*(len(row)-1) + "%s)"
        cursor.execute(sql, tuple(row))
        connection.commit()


def execute_query(cursor, query):
    cursor.execute(query)
    result = cursor.fetchall()
    return result


def delete_table(cursor):
    drop_table = "drop table menu"
    cursor.execute(drop_table)


def delete_database(cursor):
    drop_database = "drop database restaurant_menu"
    cursor.execute(drop_database)
