import mysql.connector
import yaml

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())



db_conn = mysql.connector.connect(host=app_config['datastore']['hostname'], 
                                  user=app_config['datastore']['user'], 
                                  password=app_config['datastore']['password'], 
                                  database=app_config['datastore']['db'])

db_cursor = db_conn.cursor()
db_cursor.execute('''
          CREATE TABLE bullet_efficiency
          (id INT NOT NULL AUTO_INCREMENT,
          player_id VARCHAR(250) NOT NULL,
          gun_id VARCHAR(50) NOT NULL,
          round_start_magazine_count INTEGER NOT NULL,
          round_end_magazine_count INTEGER NOT NULL,
          gun_cost INTEGER NOT NULL, 
          date_created VARCHAR(100) NOT NULL,
          trace_id VARCHAR(100) NOT NULL,
          CONSTRAINT bullet_efficiency_pk PRIMARY KEY (id) )
          ''')



db_cursor.execute('''
          CREATE TABLE ability_efficiency
          (id INT NOT NULL AUTO_INCREMENT,
          player_id VARCHAR(250) NOT NULL,
          agent_id VARCHAR(50) NOT NULL,
          round_start_ability_count INTEGER NOT NULL,
          round_end_ability_count INTEGER NOT NULL,
          ability_cost INTEGER NOT NULL,
          date_created VARCHAR(100) NOT NULL,
          trace_id VARCHAR(100) NOT NULL,
          CONSTRAINT ability_efficiency_pk PRIMARY KEY (id) )        
          ''')


db_conn.commit()
db_conn.close()