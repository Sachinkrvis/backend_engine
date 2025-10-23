# app/worker_listen.py
import select, psycopg2, json, os

DSN = os.getenv("SYNC_DATABASE_URL")


def handle_new_redflag(payload):
    print("NEW REDFLAG:", payload)
    # create recommendation_state or call API


def listen_loop():
    conn = psycopg2.connect(DSN)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("LISTEN new_redflag;")
    print("Listening for new_redflag...")
    while True:
        select.select([conn], [], [])
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            payload = json.loads(notify.payload)
            handle_new_redflag(payload)


if __name__ == "__main__":
    listen_loop()
