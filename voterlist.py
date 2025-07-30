import json
import psycopg2

#
with open("db_config.json", "r") as cfg_file:
    db_config = json.load(cfg_file)

##
with open("voters_data.json", "r", encoding="utf-8") as data_file:
    data = json.load(data_file)
    unique_data = {entry["voter_id"]: entry for entry in data}.values()

###
conn = psycopg2.connect(**db_config)
cur = conn.cursor()

####
cur.execute("""
    CREATE TABLE IF NOT EXISTS voters_list (
        voter_id TEXT PRIMARY KEY,
        full_name_nepali TEXT,
        age INTEGER,
        gender TEXT,
        spouse_name TEXT,
        parents_name TEXT,
        state INTEGER,
        district INTEGER,
        vdc INTEGER,
        ward INTEGER,
        polling_station INTEGER
    )
""")
conn.commit()
#####
for voter in unique_data:
    try:
        cur.execute("""
            INSERT INTO voters_list (
                voter_id, full_name_nepali, age, gender, spouse_name, parents_name,
                state, district, vdc, ward, polling_station
            ) VALUES (
                %(voter_id)s, %(name)s, %(age)s, %(gender)s, %(spouse_name)s, %(parents_name)s,
                %(state)s, %(district)s, %(vdc)s, %(ward)s, %(reg)s
            )
            ON CONFLICT (voter_id) DO NOTHING
        """, voter)
    except psycopg2.Error as e:
        print(f" Failed to insert voter_id {voter.get('voter_id')}: {e}")
        conn.rollback()
    except Exception as e:
        print(f"An unexpected error occurred for voter_id {voter.get('voter_id')}: {e}")
        conn.rollback()


conn.commit()
cur.close()
conn.close()

print(" Unique voter records inserted into the 'voters_list' table.")