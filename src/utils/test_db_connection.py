from src.utils.db_connection import get_source_connection, get_target_connection


def main():
    source_connection = get_source_connection()
    target_connection = get_target_connection()

    source_cursor = source_connection.cursor()
    target_cursor = target_connection.cursor()

    source_cursor.execute("SELECT current_database();")
    target_cursor.execute("SELECT current_database();")

    source_database = source_cursor.fetchone()[0]
    target_database = target_cursor.fetchone()[0]

    print("Source Database:", source_database)
    print("Target Database:", target_database)

    source_cursor.close()
    target_cursor.close()

    source_connection.close()
    target_connection.close()


if __name__ == "__main__":
    main()