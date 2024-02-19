"""Script for the data pipeline from lmnh kiosks"""
from os import environ
import json
import sys

from datetime import datetime
import psycopg2
from psycopg2 import extensions
from psycopg2.extensions import connection

from dotenv import load_dotenv
from confluent_kafka import Consumer

MINIMUM_ID = 1
MAX_RATING_ID = 5


def get_db_connection() -> extensions.connection:
    """Establishes a connection to the museum database"""
    try:
        return psycopg2.connect(
            user=environ.get("DATABASE_USERNAME"),
            password=environ.get("DATABASE_PASSWORD"),
            host=environ.get("DATABASE_HOST"),
            port=environ.get("DATABASE_PORT"),
            database=environ.get("DATABASE_NAME")
        )
    except:
        print("Error connecting to database.")


def get_max_exhibit_id(conn: connection) -> int:
    """Retrieves the max id from the required table"""

    with conn.cursor() as cur:
        cur.execute(f"SELECT MAX(exhibit_id) FROM exhibit WHERE museum_id = 1;")
        return cur.fetchone()[0]


def check_date_and_time(msg_dict: dict) -> str:
    """Checks the time and date of the data to make sure 
    it exists and it's not too early or late in the day"""

    error = ""
    try:
        date = msg_dict["at"]
        datetime_object = datetime.fromisoformat(date).replace(tzinfo=None)
        datetime_str = f"{datetime_object.day}/{datetime_object.month}/{datetime_object.year}"
        earliest_time = datetime.strptime(
            f"{datetime_str} 08:45:00", "%d/%m/%Y %H:%M:%S")
        latest_time = datetime.strptime(
            f"{datetime_str} 18:15:00", "%d/%m/%Y %H:%M:%S")

        if datetime_object < earliest_time:
            error = "Invalid time - Too early"
        if datetime_object > latest_time:
            error = "Invalid time - Too late"

    except KeyError:
        error = "No date/time"

    return error


def check_exhibit(msg_dict: dict, conn: connection) -> str:
    """Checks the exhibit of the data to make sure it exists and is an integer."""
    error = ""
    try:
        exhibit_num = int(msg_dict["site"]) + 1
        max_exhibit_id = get_max_exhibit_id(conn)
        if exhibit_num > max_exhibit_id or exhibit_num < MINIMUM_ID:
            error = "Invalid exhibit"
    except KeyError:
        error = "No exhibit"
    except ValueError:
        error = "Invalid exhibit"

    return error


def check_rating(msg_dict: dict, conn: connection) -> str:
    """Checks the rating of the data to make sure it exists and is a valid rating."""
    error = ""
    try:
        value_num = int(msg_dict['val']) + 1
        if value_num > MAX_RATING_ID or value_num < MINIMUM_ID:
            error = "Invalid rating"

        try:
            if value_num == 0:
                error = ""
                type = int(msg_dict['type'])
                if type not in [0, -1]:
                    error = "Invalid emergency/assistance"
        except ValueError:
            error = "Invalid emergency/assistance"

    except KeyError:
        error = "No rating"
    except ValueError:
        error = "Invalid rating"
    except TypeError:
        error = "No rating"

    return error


def add_to_db(conn: connection, table: str, msg_dict: dict):
    """Adds a all the info from a dictionary to the appropriate table."""
    if table == "user_rating":
        query = f"""
            INSERT INTO {table}
                (recorded_at,
                exhibit_id,
                rating_id)
            VALUES 
            ('{msg_dict['at']}',
            {msg_dict['site']},
            {msg_dict['val']});
            """
    else:
        query = f"""
            INSERT INTO {table}
                (recorded_at,
                exhibit_id)
            VALUES
            ('{msg_dict['at']}',
            {msg_dict['site']});
        """

    with conn.cursor() as cur:
        cur.execute(query)
    conn.commit()


def log_to_file(msg_dict: dict, error: str):
    with open("invalid_inputs.txt", "a") as invalid_inputs:
        invalid_inputs.write(f"{msg_dict} - {error}\n")


def consume_messages(consumer: Consumer, conn: connection, should_log: bool):
    """Gets the messages from kofka and uploads them to the museum database."""

    consumer.subscribe([environ["TOPIC_1"]])
    try:
        while True:
            msg = consumer.poll(1)
            error = ""

            if msg:
                msg_dict = json.loads(msg.value().decode())

                datetime_error = check_date_and_time(msg_dict)
                if datetime_error:
                    error = datetime_error
                    if should_log:
                        log_to_file(msg_dict, error)

                exhibit_error = check_exhibit(msg_dict, conn)
                if exhibit_error:
                    error = exhibit_error
                    if should_log:
                        log_to_file(msg_dict, error)

                rating_error = check_rating(msg_dict, conn)
                if rating_error:
                    error = rating_error
                    if should_log:
                        log_to_file(msg_dict, error)

                if not error:
                    date = datetime.fromisoformat(
                        msg_dict["at"]).replace(tzinfo=None)
                    msg_dict["at"] = date.strftime("%Y-%m-%d %H:%M:%S")
                    msg_dict["val"] = int(msg_dict["val"]) + 1
                    msg_dict["site"] = int(msg_dict["site"]) + 1
                    table = ""

                    if 0 < msg_dict["val"] <= 5:
                        table = "user_rating"
                    elif msg_dict["val"] == 0:
                        if msg_dict["type"] == 0:
                            table = "assistance"
                        else:
                            table = "emergency"

                    add_to_db(conn, table, msg_dict)

            else:
                pass

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":

    load_dotenv()
    log = False

    kafka_consumer = Consumer({
        'bootstrap.servers': environ["BOOTSTRAP_SERVERS"],
        'security.protocol': environ["SECURITY_PROTOCOL"],
        'sasl.mechanisms': environ["SASL_MECHANISM"],
        'sasl.username': environ["USERNAME"],
        'sasl.password': environ["PASSWORD"],
        'group.id': environ["GROUP"],
        'auto.offset.reset': environ["AUTO_OFFSET"]
    })

    con = get_db_connection()

    args = [arg for arg in sys.argv[1:] if arg.startswith("-")]
    if args and args[0] == '-log':
        log = True

    consume_messages(kafka_consumer, con, log)
