import csv
import os
from datetime import datetime


class DataRecorder:
    def __init__(self):
        self.file_name = self.generate_csv_name()

    @staticmethod
    def generate_csv_name():
        current_time = datetime.now()
        timestamp = current_time.strftime("%Y%m%d_%H%M%S")
        file_name = f"data_{timestamp}.csv"
        with open(file_name, 'w', newline='') as file:
            pass
        return file_name

    def append_to_csv(self, data):
        fieldnames = data[0].keys()
        print(fieldnames)
        with open(self.file_name, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if file.tell() == 0:
                writer.writeheader()

            for row in data:
                writer.writerow(row)
