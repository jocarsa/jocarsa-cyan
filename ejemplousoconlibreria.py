from minidb import *

if __name__ == "__main__":

    connector = TinyDbConnector("clientes")

    record_to_insert = {"name": "John", "age": 30}
    if connector.insert_record(record_to_insert):
        print("Record inserted successfully!")

    another_record = {"name": "Alice", "age": 25}
    if connector.insert_record(another_record):
        print("Another record inserted successfully!")

    all_records = connector.select_records()
    print(f"Found {len(all_records)} record(s) in the database.")
    for idx, rec in enumerate(all_records, start=1):
        print(f"[Record {idx}]")
        print(f"  Filename: {rec['filename']}")
        print(f"  Content:  {rec['content']}")
