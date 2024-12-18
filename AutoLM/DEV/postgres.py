import json

def create_table_and_insert_data(df, table_name, conn, trunc):
    # Create a cursor object
    cur = conn.cursor()

    #Map dicts to strings
    df = df.transform(lambda x: x.apply(lambda y: json.dumps(y) if isinstance(y, dict) else y))
    
    #Find dtypes of all cols
    column_defintions = col_defs(df)

    # Create the table if it doesn't exist
    create_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {", ".join(column_defintions)}
        )
        """

    cur.execute(create_query)
    print(f"Truncation flag value: {trunc}")
    if trunc == 1:
        try:
            truncate_query = f"TRUNCATE TABLE {table_name};"
            cur.execute(truncate_query)
            print('Table truncated ' + table_name)
        except Exception as e:
            print(f"Error truncating table {table_name}: {e}")
    
    # Insert data into the table
    for _, row in df.iterrows():
        cur.execute(
            f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({', '.join(['%s']*len(df.columns))})",
            row.tolist()
    )
    
    # Commit the transaction
    conn.commit()
    
    # Close the cursor
    cur.close()
    print(f"{table_name} loaded successfully!")

def map_dtype_to_psql(dtype):
    """
    Maps Pandas data types to PostgreSQL data types.
    
    Args:
    dtype (str): The Pandas data type.
    
    Returns:
    str: The corresponding PostgreSQL data type.
    """
    psql_types = {
        'int64': 'INTEGER',
        'float64': 'FLOAT',
        'object': 'TEXT',
        'datetime64': 'TIMESTAMP',
        'bool': 'BOOLEAN'
    }
    return psql_types.get(dtype, 'TEXT')

def col_defs(df):
    """
    Takes a pandas dataframe and populates a list with column names
    along with their data types for a SQL create query in PostgreSQL.
    
    Args:
    df (pandas.DataFrame): The input DataFrame.
    
    Returns:
    list: A list containing strings representing column definitions
          for a SQL create query.
    """
    column_defs = []
    for col_name, dtype in df.dtypes.items():
        sql_type = map_dtype_to_psql(dtype.name)
        column_defs.append(f"{col_name} {sql_type}")
    return column_defs
