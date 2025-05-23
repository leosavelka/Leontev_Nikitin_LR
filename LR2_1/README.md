### Леонтьев С. В., Никитин Д. И. 
### Лабораторная работа №2

Поднимаем контейнеры
```shell
cd lab2
sudo docker compose up 
```
![](pic/1.png)

Подключаемся к primary

```shell
psql -h localhost -p 5433 -U postgres
```
![](pic/2.png)

Создаём тестовые данные:
```psql
CREATE TABLE name_table (id SERIAL, name TEXT);
INSERT INTO name_table (name) VALUES ('Leontev'), ('Saveliy'), ('Nikitin'), ('Dmitriy'), ('Popkin'), ('Vladimir');
SELECT * FROM name_table;

```
![](pic/3.png)

Подключаемся к standby:
```shell
psql -h localhost -p 5434 -U postgres
```
![](pic/4.png)

Проверяем наличие данных:

```psql
SELECT * FROM name_table;
```
![](pic/5.png)

Проверяем, что доступно только чтение:

```psql
INSERT INTO name_table (name) VALUES ('Sava'), ('Leon'), ('Dima'), ('Niki');
```
![](pic/6.png)

Стопим primary
```
docker stop pg_primary
```
![](pic/7.png)

Переводим standby в primary.
```psql
SELECT pg_promote();

INSERT INTO name_table (name) VALUES ('Sava'), ('Leon'), ('Dima'), ('Niki');
SELECT * FROM name_table;

```
![](pic/8.png)
