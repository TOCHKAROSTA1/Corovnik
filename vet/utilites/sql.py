import psycopg2
class sql:
    def __init__(self, ):
        self.database = psycopg2.connect(
            dbname="Cows",
            user="postgres",
            password="123",
            host="localhost",
            port="5432"
            )
        self.cursor = self.database.cursor()
    
    def create_record(self, table: str, update_data: dict):
        columns = ", ".join(update_data.keys())
        placeholders = ", ".join(["%s" for _ in update_data])
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        self.cursor.execute(query, tuple(update_data.values()))
        self.database.commit()
        return self.cursor.lastrowid
    def update(self, table: str, record_id: int, update_data: dict, key: str):
        set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
            
            # Формируем полный запрос
        query = f"UPDATE {table} SET {set_clause} WHERE {key} = %s"
            # Параметры: значения для обновления + ID
        params = tuple(update_data.values()) + (record_id,)
            # Выполняем запрос
        self.cursor.execute(query, params)
        self.database.commit()

    def delete_record(self, table: str, record: int):
        self.cursor.execute(f"""DELETE FROM {table} WHERE id={record}""")
        self.database.commit()
        return self.cursor.fetchall()
    
    def close(self):
        self.cursor.close()
        self.database.close()

    def clean_table(self, table: str):
        self.cursor.execute(f"DELETE FROM {table}")
        # Автоматически находим и сбрасываем sequence
        self.cursor.execute(f"""
            SELECT pg_get_serial_sequence('{table}', 'id');
        """)
        seq_name = self.cursor.fetchone()[0]
        if seq_name:
            self.cursor.execute(f"ALTER SEQUENCE {seq_name} RESTART WITH 1")
        self.database.commit()
    
    def record(self, table: str, record_id: int):
        self.cursor.execute(f"SELECT * FROM {table} WHERE id = %s", (record_id,))
        record = self.cursor.fetchone()
        return record

    def r(self, table: str):
        self.cursor.execute(f"SELECT * FROM {table}")
        record = self.cursor.fetchall()
        return record
    
    
if __name__ == "__main__":
    data = sql()
    data.clean_table("cows")
    data.clean_table("nutrition")
    data.close()