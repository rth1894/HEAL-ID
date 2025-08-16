import pymysql
from typing import List

class DatabaseConnection:
    _instance = None
    valid_doctor_ids: List[str] = []
    valid_aadhar_numbers: List[str] = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connect()
            cls._instance.initialize_valid_ids()
        return cls._instance
    
    def connect(self):
        self.connection = pymysql.connect(
            host="localhost",
            user="python",
            password="Password@123",
            database="heal_id",
        )
        self.cursor = self.connection.cursor()
    
    def initialize_valid_ids(self):
        self.valid_doctor_ids = self.get_valid_doctor_ids()
        self.valid_aadhar_numbers = self.get_valid_aadhar_numbers()
    
    def get_valid_doctor_ids(self):
        self.cursor.execute("SELECT Doctor_ID FROM Doctors")
        return [str(row[0]) for row in self.cursor.fetchall()]

    def get_valid_aadhar_numbers(self):
        self.cursor.execute("SELECT Aadhar_number FROM Personal_Information")
        return [str(row[0]) for row in self.cursor.fetchall()]

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        if self.connection:
            self.connection.close()

# Create an instance of DatabaseConnection
db = DatabaseConnection()
