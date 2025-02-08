#!/usr/bin/env python3

import subprocess

def main():
    # The JSON data you want to insert
    json_data = '{"name":"Borja","age":28}'

    print("Inserting data...")
    insert_proc = subprocess.run(
        ["/var/www/html/jocarsa-cyan/cyan.out", "clientes", "insert", json_data],
        capture_output=True,
        text=True
    )

    if insert_proc.returncode != 0:
        print("Error inserting data:", insert_proc.stderr)
        return
    else:
        print(insert_proc.stdout)

    print("\nRetrieving data...")
    select_proc = subprocess.run(
        ["/var/www/html/jocarsa-cyan/cyan.out", "clientes", "select"],
        capture_output=True,
        text=True
    )

    if select_proc.returncode != 0:
        print("Error retrieving data:", select_proc.stderr)
        return
    else:
        print(select_proc.stdout)

if __name__ == "__main__":
    main()
