#! -*- coding: utf-8 -*-
import pymysql
import toml
import os

basc_config = "./sync-config.toml"
config = toml.load(basc_config)
resource_db = config["source-db"][0]
target_db = config["target-db"]
sync_diff_inspector = "./sync_diff_inspector"
dist_config = "./dist-config.toml"
ignore_tables = ["INFORMATION_SCHEMA", "mysql", "METRICS_SCHEMA", "PERFORMANCE_SCHEMA"]


def save_config(config):
    with open(dist_config, "w+") as f:
        toml.dump(config, f)
    print("config write to ", dist_config)

def update_config(check_tables):
    config["table-config"] = []
    config["check-tables"] = check_tables
    print("CHECK_TABLES: ", check_tables)
    save_config(config)

def load_config():
    config = toml.load(basc_config)
    print("load config from ", basc_config)
    return config

def get_all_tables():
    "get all tables with check-tables format sync to downstream."

    all_tables = []
    db = resource_db
    schemas = list_schemas(db)
    for schema in schemas:
        rts = list_tables(resource_db, schema)
        tts = list_tables(target_db, schema)
        tables = []
        for t in rts:
            "table not sync"
            if t not in tts:
                if check_table(schema, t):
                    print(f"{schema}.{table} should be sync but actually not.")
                    exit()
            else:
                tables.append(t)
        if tables:
            new_check = {"schema": schema, "tables": tables}
            all_tables.append(new_check)
            print("ADD_TABLES:", new_check)
    return all_tables

def sync_diff_tables():
    sync_tables = get_all_tables()
    update_config(sync_tables)
    os.system(f"{sync_diff_inspector} -config {dist_config}")

def check_table(schema, table):
    cli = pymysql.connect(host=resource_db["host"], user=resource_db["user"], password=resource_db["password"], port=resource_db["port"], db=schema)
    with cli.cursor() as cursor:
        cursor.execute(f"show index in {table} where non_unique = 0 and `null` != 'YES';")
        r = cursor.fetchall()
        if len(r) > 0:
            cli.close()
            return True
        else:
            print(f"{schema}.{table} not need to sync.")
    

def list_tables(db, schema=None):
    table_list = []
    cli = pymysql.connect(host=db["host"], user=db["user"], password=db["password"], port=db["port"], db=schema)
    with cli.cursor() as cursor:
        cursor.execute("show full tables where table_type = 'BASE TABLE'")
        table_list = [tuple[0] for tuple in cursor.fetchall()]
    cli.close()
    return table_list

def list_schemas(db):
    schemes = []
    cli = pymysql.connect(host=db["host"], user=db["user"], password=db["password"], port=db["port"])
    with cli.cursor() as cursor:
        cursor.execute("show databases")
        r = cursor.fetchall()
        for s in r:
            if s[0] not in ignore_tables:
                schemes.append(s[0])
    cli.close()
    return schemes


if __name__ == "__main__":
    sync_diff_tables()
