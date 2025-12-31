-- Создание пользователя 
CREATE USER shop_user WITH PASSWORD '000000';

-- Создание базы данных
CREATE DATABASE shop_db
    OWNER shop_user
    ENCODING 'UTF8';

