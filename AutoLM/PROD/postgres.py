import json

def create_table_and_insert_data(df, table_name, conn):
    # Create a cursor object
    cur = conn.cursor()
    
    # Create the table if it doesn't exist
    create_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {", ".join([f"{col} VARCHAR" for col in df.columns])}
        )
    """
    cur.execute(create_query)
    
    # Convert dictionary columns to strings
    df = df.applymap(lambda x: json.dumps(x) if isinstance(x, dict) else x)
    
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
