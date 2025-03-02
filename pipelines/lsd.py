import psycopg2
import config

lsd_conn = psycopg2.connect(
    f"host='{config.LSD_HOST}' dbname='{config.LSD_DB}' password='{config.LSD_PASSWORD}'")
