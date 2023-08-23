## Create virtual enviroment 

```
python -m venv venv 
```
Active enviroment 
```
.\venv\Scripts\activate 
```
Install package
```
pip install -r requirements.txt 
```

# How to run alembic and create tables in database
1. Create database in mysql
- Run as administrator with MySQL Shell
- Create and select the database
    ```
    mysql> CREATE DATABASE aime;
    mysql> use aime;
    ```
2. Edit .env
- Edit: DB_HOST, DB_NAME, DB_USER, DB_PASSWORD in .env

3. Install package
- pip install alembic

4. Run local
- Creating migrations
```
alembic revision --autogenerate -m "Adding User and Ai_Agent and Sample_Voice and Sample_Dialog Table" 
```
revision = '7772b2cbc3af'

- To run the migration use the following command 
```
alembic upgrade head
```
# How to add and drop a column
1. Add a column 
- Creating migrations
```
alembic revision -m "Add a column"  
```
revision = 'e302bfdb0e10'

- add a new column to the ai_agents table:
```
def upgrade() -> None:
    op.add_column('ai_agents', sa.Column('introduction2', sa.Integer))
```
- run
```
alembic upgrade e302bfdb0e10
```

2. Drop a column 
```
def downgrade() -> None:
    op.drop_column('ai_agents', 'introduction2')
```
```
alembic downgrade 7772b2cbc3af
```



