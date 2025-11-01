import mysql.connector
import sys

try:
    # Connect to database
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='db_asset'
    )
    cursor = conn.cursor()

    print('=' * 100)
    print('DATABASE STRUCTURE AND CONTENTS: db_asset')
    print('=' * 100)

    # Show all tables
    cursor.execute('SHOW TABLES')
    tables = [row[0] for row in cursor.fetchall()]
    print(f'\nTABLES ({len(tables)}): {", ".join(tables)}')

    # Show structure and data for each table
    for table in tables:
        print(f'\n\n{"=" * 100}')
        print(f'TABLE: {table}')
        print('=' * 100)
        
        # Show structure
        cursor.execute(f'DESCRIBE `{table}`')
        columns = cursor.fetchall()
        print('\nSTRUCTURE:')
        print(f'{"Field":<30} {"Type":<30} {"Null":<6} {"Key":<6} {"Default":<15} {"Extra":<20}')
        print('-' * 100)
        for col in columns:
            field, type_val, null_val, key, default, extra = col
            default_str = str(default) if default is not None else 'NULL'
            print(f'{field:<30} {type_val:<30} {null_val:<6} {key:<6} {default_str:<15} {extra:<20}')
        
        # Get column names
        cursor.execute(f'DESCRIBE `{table}`')
        col_names = [col[0] for col in cursor.fetchall()]
        
        # Count rows
        cursor.execute(f'SELECT COUNT(*) FROM `{table}`')
        total_count = cursor.fetchone()[0]
        
        # Show data
        cursor.execute(f'SELECT * FROM `{table}` LIMIT 10')
        data = cursor.fetchall()
        
        print(f'\nDATA: {total_count} total rows (showing first {min(len(data), 10)})')
        if data:
            print('-' * 100)
            # Print header
            header = ' | '.join([f'{col[:18]:<18}' for col in col_names])
            print(header)
            print('-' * 100)
            # Print rows
            for row in data:
                row_str = ' | '.join([f'{str(val)[:18]:<18}' if val is not None else f'{"NULL":<18}' for val in row])
                print(row_str)
        else:
            print('(empty table)')

    conn.close()
    print('\n' + '=' * 100)
    print('END OF DATABASE DUMP')
    print('=' * 100)

except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
