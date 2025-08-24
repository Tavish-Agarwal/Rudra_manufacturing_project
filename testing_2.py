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


def main():
    print("="*60)
    print("TESTING MOLD CLASS AND MOLDDATABASE CLASS")
    print("="*60)
    
    # Initialize database
    db = MoldDatabase('molds.csv')
    print(f"✓ Loaded {len(db.molds)} molds from CSV\n")

    # Get test molds
    mold1 = db.get_mold('CCIT 25')
    mold2 = db.get_mold('CCIT 50')
    mold3 = db.get_mold('CCIT 60')

    if not all([mold1, mold2, mold3]):
        print("❌ One or more test molds not found in database")
        return

    print("TESTING MOLD CLASS METHODS")
    print("-" * 40)
    
    # Test 1: calculate_torque()
    print("1. Testing calculate_torque():")
    print(f"   {mold1.mold_id}: Weight={mold1.weight}kg × Distance={mold1.distance_from_center}m = {mold1.calculate_torque()} N⋅m")
    print(f"   {mold2.mold_id}: Weight={mold2.weight}kg × Distance={mold2.distance_from_center}m = {mold2.calculate_torque()} N⋅m")
    print(f"   {mold3.mold_id}: Weight={mold3.weight}kg × Distance={mold3.distance_from_center}m = {mold3.calculate_torque()} N⋅m\n")

    # Test 2: get_cycle_time()
    print("2. Testing get_cycle_time():")
    print(f"   {mold1.mold_id}: {mold1.heating_time} + {mold1.cooling_time} + {mold1.mounting_time} = {mold1.get_cycle_time()} minutes")
    print(f"   {mold2.mold_id}: {mold2.heating_time} + {mold2.cooling_time} + {mold2.mounting_time} = {mold2.get_cycle_time()} minutes")
    print(f"   {mold3.mold_id}: {mold3.heating_time} + {mold3.cooling_time} + {mold3.mounting_time} = {mold3.get_cycle_time()} minutes\n")

    # Test 3: check_availability()
    print("3. Testing check_availability():")
    for qty in [1, 2, 5]:
        print(f"   {mold1.mold_id} (Available: {mold1.available_quantity}) - Need {qty}: {mold1.check_availability(qty)}")
    for qty in [1, 2, 5]:
        print(f"   {mold2.mold_id} (Available: {mold2.available_quantity}) - Need {qty}: {mold2.check_availability(qty)}")
    print()

    # Test 4: check_compatibility_with()
    print("4. Testing check_compatibility_with():")
    print(f"   {mold1.mold_id} vs {mold2.mold_id}: {mold1.check_compatibility_with(mold2)}")
    print(f"   {mold1.mold_id} vs {mold3.mold_id}: {mold1.check_compatibility_with(mold3)}")
    print(f"   {mold2.mold_id} vs {mold3.mold_id}: {mold2.check_compatibility_with(mold3)}")
    
    # Test compatibility with different tolerances
    print(f"   {mold1.mold_id} vs {mold2.mold_id} (10% tolerance): {mold1.check_compatibility_with(mold2, 0.1, 0.1)}")
    print()

    # Test 5: get_parameter_range()
    print("5. Testing get_parameter_range():")
    for mold in [mold1, mold2, mold3]:
        params = mold.get_parameter_range()
        print(f"   {mold.mold_id}: {params}")
    print()

    print("TESTING MOLDDATABASE CLASS METHODS")
    print("-" * 40)

    # Test 6: get_mold()
    print("6. Testing get_mold():")
    test_mold = db.get_mold('CCIT 125')
    if test_mold:
        print(f"   Found mold: {test_mold.mold_id}, Type: {test_mold.mold_type}")
    else:
        print("   Mold not found")
    
    non_existent = db.get_mold('NON_EXISTENT')
    print(f"   Non-existent mold: {non_existent}")
    print()

    # Test 7: get_molds_by_type()
    print("7. Testing get_molds_by_type():")
    for mold_type in ['TUB', 'PLAIN LID', 'VENDING LID']:
        molds = db.get_molds_by_type(mold_type)
        print(f"   {mold_type} molds: {len(molds)}")
        for mold in molds[:3]:  # Show first 3
            print(f"     - {mold.mold_id}")
        if len(molds) > 3:
            print(f"     ... and {len(molds) - 3} more")
    print()

    # Test 8: get_compatible_molds()
    print("8. Testing get_compatible_molds():")
    reference_mold = db.get_mold('CCIT 50')
    compatible_molds = db.get_compatible_molds(reference_mold, tolerance=0.05)
    print(f"   Compatible molds with {reference_mold.mold_id} (5% tolerance): {len(compatible_molds)}")
    for cmold in compatible_molds[:5]:  # Show first 5
        print(f"     - {cmold.mold_id} (Temp: {cmold.heating_temperature}, Time: {cmold.heating_time})")
    print()

    # Test 9: update_availability()
    print("9. Testing update_availability():")
    test_mold_id = 'CCIT 60'
    original_qty = db.get_mold(test_mold_id).available_quantity
    print(f"   Original availability for {test_mold_id}: {original_qty}")
    
    db.update_availability(test_mold_id, 1)
    new_qty = db.get_mold(test_mold_id).available_quantity
    print(f"   After using 1 unit: {new_qty}")
    
    # Test updating non-existent mold
    db.update_availability('NON_EXISTENT', 1)
    print("   ✓ Handled non-existent mold gracefully")
    print()

    # Test 10: save_to_csv()
    print("10. Testing save_to_csv():")
    db.save_to_csv('test_output_molds.csv')
    print("    ✓ Saved updated mold data to 'test_output_molds.csv'")
    
    # Verify the saved file
    try:
        saved_df = pd.read_csv('test_output_molds.csv')
        print(f"    ✓ Verification: Saved file contains {len(saved_df)} rows")
    except Exception as e:
        print(f"    ❌ Error verifying saved file: {e}")
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*60)


if __name__ == "__main__":
    main()
