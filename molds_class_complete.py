import pandas as pd

class Mold:
    def __init__(self, mold_id, volume, weight, heating_time, heating_temperature, cooling_time,
                 mounting_time, distance_from_center, available_quantity, mold_type='UNKNOWN'):
        self.mold_id = mold_id
        self.volume = volume
        self.weight = weight
        self.heating_time = heating_time
        self.heating_temperature = heating_temperature
        self.cooling_time = cooling_time
        self.mounting_time = mounting_time
        self.distance_from_center = distance_from_center
        self.available_quantity = available_quantity
        self.mold_type = mold_type

    def calculate_torque(self):
        return self.weight * self.distance_from_center

    def get_cycle_time(self):
        return self.heating_time + self.cooling_time + self.mounting_time

    def check_availability(self, required_quantity):
        return required_quantity <= self.available_quantity

    def check_compatibility_with(self, other_mold, temp_tolerance=0.02, time_tolerance=0.02):
        temp_diff = abs(self.heating_temperature - other_mold.heating_temperature) / self.heating_temperature
        time_diff = abs(self.heating_time - other_mold.heating_time) / self.heating_time
        return temp_diff <= temp_tolerance and time_diff <= time_tolerance

    def get_parameter_range(self):
        return {
            'heating_time': self.heating_time,
            'heating_temperature': self.heating_temperature,
            'cooling_time': self.cooling_time,
            'mounting_time': self.mounting_time
        }


class MoldDatabase:
    def __init__(self, csv_file='molds.csv'):
        self.csv_file = csv_file
        self.molds = {}
        self.load_data()

    def load_data(self):
        try:
            df = pd.read_csv(self.csv_file)
            df = df.dropna(subset=['Name'])
            for _, row in df.iterrows():
                mold = self._create_mold_from_row(row)
                self.molds[mold.mold_id] = mold
        except Exception as e:
            print(f"Error loading data: {e}")

    def _create_mold_from_row(self, row):
        length = float(row['Length (mm)']) / 1000 if pd.notna(row['Length (mm)']) else 0.5
        breadth = float(row['Breadth (mm)']) / 1000 if pd.notna(row['Breadth (mm)']) else 0.5
        height = float(row['Height (mm)']) / 1000 if pd.notna(row['Height (mm)']) else 0.5
        volume = length * breadth * height
        mold_type = str(row['Type']) if pd.notna(row['Type']) else 'UNKNOWN'
        return Mold(
            mold_id=str(row['Name']),
            volume=volume,
            weight=float(row['Weight (kg)(With Powder)']) if pd.notna(row['Weight (kg)(With Powder)']) else 5.0,
            heating_time=float(row['Oven Time']) if pd.notna(row['Oven Time']) else 3.0,
            heating_temperature=float(row['Oven Temperature']) if pd.notna(row['Oven Temperature']) else 200.0,
            cooling_time=float(row['Cooling Time']) if pd.notna(row['Cooling Time']) else 2.0,
            mounting_time=float(row['Molding/Demolding Time']) if pd.notna(row['Molding/Demolding Time']) else 1.0,
            distance_from_center=0.5,
            available_quantity=int(row['Count']) if pd.notna(row['Count']) else 1,
            mold_type=mold_type
        )

    def get_mold(self, mold_id):
        return self.molds.get(mold_id)

    def get_molds_by_type(self, mold_type):
        return [mold for mold in self.molds.values() if mold_type.upper() in mold.mold_type.upper()]

    def get_compatible_molds(self, reference_mold, tolerance=0.02):
        compatible = []
        for mold in self.molds.values():
            if mold.mold_id != reference_mold.mold_id:
                if reference_mold.check_compatibility_with(mold, tolerance, tolerance):
                    compatible.append(mold)
        return compatible

    def update_availability(self, mold_id, quantity_used):
        if mold_id in self.molds:
            self.molds[mold_id].available_quantity -= quantity_used

    def save_to_csv(self, filename='updated_molds.csv'):
        data = []
        for mold in self.molds.values():
            data.append({
                'Name': mold.mold_id,
                'Type': mold.mold_type,
                'Count': mold.available_quantity,
                'Weight (kg)(With Powder)': mold.weight,
                'Oven Time': mold.heating_time,
                'Oven Temperature': mold.heating_temperature,
                'Cooling Time': mold.cooling_time,
                'Molding/Demolding Time': mold.mounting_time
            })
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)