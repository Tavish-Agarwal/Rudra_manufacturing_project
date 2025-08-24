# 1. Mold Class
class Mold:
    def __init__(self, mold_id, volume, weight, heating_time, heating_temperature, cooling_time,
                 mounting_time, distance_from_center, available_quantity):
        self.mold_id = mold_id
        self.volume = volume
        self.weight = weight
        self.heating_time = heating_time
        self.heating_temperature = heating_temperature
        self.cooling_time = cooling_time
        self.mounting_time = mounting_time
        self.distance_from_center = distance_from_center
        self.available_quantity = available_quantity

    # 1.1
    def calculate_torque(self):
        """Returns torque (Nm) = weight * distance_from_center"""
        return self.weight * self.distance_from_center

    # 1.2
    def get_cycle_time(self):
        """Returns total cycle time for one mold (sum of heating, cooling, mounting times)"""
        return self.heating_time + self.cooling_time + self.mounting_time

    # 1.3
    def check_availability(self, required_quantity):
        """Checks if required quantity is available"""
        return required_quantity <= self.available_quantity

    # 1.4
    def check_compatibility_with(self, other_mold, temp_tolerance=0.02, time_tolerance=0.02):
        """Returns True if other_mold is compatible on the same arm"""
        temp_diff = abs(self.heating_temperature - other_mold.heating_temperature) / self.heating_temperature
        time_diff = abs(self.heating_time - other_mold.heating_time) / self.heating_time
        return temp_diff <= temp_tolerance and time_diff <= time_tolerance

    # 1.5
    def get_parameter_range(self):
        """Returns dictionary with key process parameters for this mold"""
        return {
            'heating_time': self.heating_time,
            'heating_temperature': self.heating_temperature,
            'cooling_time': self.cooling_time,
            'mounting_time': self.mounting_time
        }


# 2. Spider Class (Modified)
class Spider:
    def __init__(self, spider_type, attachment_sites, volume, weight, attachment_distance):
        self.spider_type = spider_type        # e.g., '2-way', '4-way'
        self.attachment_sites = attachment_sites   # int: 8 or 16
        self.volume = volume
        self.weight = weight
        self.attachment_distance = attachment_distance  # distance between attachment points

    # 2.1
    def get_capacity(self):
        """Returns number of mold sites available on this spider"""
        return self.attachment_sites

    # 2.2
    def check_spatial_fit(self, arm_volume):
        """Checks if spider fits in arm's volume (True/False)"""
        return self.volume <= arm_volume

    # 2.3
    def check_volumetric_fit(self, remaining_volume):
        """Checks if the spider plus loaded molds fit into allowed volume"""
        return self.volume <= remaining_volume

    # 2.4
    def get_available_attachment_volume(self, used_sites):
        """Returns number of available mold attachment sites left"""
        return max(0, self.attachment_sites - used_sites)


# 3. Arm Class
class Arm:
    def __init__(self, arm_id, mounting_spots, max_volume, weight_capacity, torque_left_side, torque_right_side):
        self.arm_id = arm_id
        self.mounting_spots = mounting_spots
        self.max_volume = max_volume
        self.weight_capacity = weight_capacity
        self.torque_left_side = torque_left_side
        self.torque_right_side = torque_right_side
        self.current_molds = []
        self.current_spiders = []

    # 3.1
    def check_spatial_constraint(self):
        """Checks if current molds and spiders fit within arm volume"""
        total_volume = sum([mold.volume for mold in self.current_molds])
        total_volume += sum([spider.volume for spider in self.current_spiders])
        return total_volume <= self.max_volume

    # 3.2
    def check_balance_constraint(self, tolerance=0.1):
        """Checks if torque balance is within tolerance"""
        balance_torque = self.calculate_balance_torque()
        return abs(balance_torque) <= tolerance

    # 3.3
    def calculate_balance_torque(self):
        """Calculates net torque on the arm (positive = right side heavy)"""
        net_torque = self.torque_right_side - self.torque_left_side
        for mold in self.current_molds:
            net_torque += mold.calculate_torque()
        return net_torque

    # 3.4
    def add_balancing_weight(self, weight, position):
        """Adds balancing weight at specified position to reduce torque imbalance"""
        if position == 'left':
            self.torque_left_side += weight * 1.0  # assuming 1m distance
        elif position == 'right':
            self.torque_right_side += weight * 1.0

    # 3.5
    def check_torque_balance(self, balancing_weights):
        """Checks torque balance with given balancing weights configuration"""
        temp_left = self.torque_left_side
        temp_right = self.torque_right_side
        for weight in balancing_weights:
            if weight.position == 'left':
                temp_left += weight.weight
            else:
                temp_right += weight.weight
        return abs(temp_right - temp_left) <= 0.1

    # 3.6
    def check_temperature_compatibility(self):
        """Verifies all molds have compatible heating temperatures"""
        if len(self.current_molds) <= 1:
            return True
        base_temp = self.current_molds[0].heating_temperature
        for mold in self.current_molds[1:]:
            if not self.current_molds[0].check_compatibility_with(mold):
                return False
        return True

    # 3.7
    def check_duration_compatibility(self):
        """Verifies all molds have compatible heating durations"""
        if len(self.current_molds) <= 1:
            return True
        for i in range(len(self.current_molds) - 1):
            if not self.current_molds[i].check_compatibility_with(self.current_molds[i+1]):
                return False
        return True


# 4. BalancingWeight Class
class BalancingWeight:
    def __init__(self, weight_options, position):
        self.weight_options = weight_options  # List of available weights in kg
        self.position = position  # 'left' or 'right'
        self.weight = 0  # Current weight applied

    # 4.1
    def apply_weight(self, weight_value):
        """Sets the balancing weight to specified value if available"""
        if weight_value in self.weight_options:
            self.weight = weight_value
            return True
        return False

    # 4.2
    def calculate_balance_contribution(self, distance_from_center=1.0):
        """Calculates torque contribution of this balancing weight"""
        return self.weight * distance_from_center

    # 4.3
    def calculate_optimal_weights(self, target_torque, available_positions):
        """Returns optimal weight configuration to achieve target torque"""
        optimal_config = []
        remaining_torque = abs(target_torque)
        
        for position in available_positions:
            for weight in sorted(self.weight_options, reverse=True):
                if weight <= remaining_torque:
                    optimal_config.append({'weight': weight, 'position': position})
                    remaining_torque -= weight
                    break
        return optimal_config

    # 4.4
    def minimize_weight_count(self, target_torque):
        """Returns minimum number of weights needed for target torque"""
        weights_needed = 0
        remaining_torque = abs(target_torque)
        
        for weight in sorted(self.weight_options, reverse=True):
            while weight <= remaining_torque:
                remaining_torque -= weight
                weights_needed += 1
        return weights_needed


# 5. RTXMachine Class
class RTXMachine:
    def __init__(self, machine_id, machine_count=1):
        self.machine_id = machine_id
        self.machine_count = machine_count
        self.arms_list = []  # List of Arm objects
        self.current_cycle = 0
        self.daily_cycles_completed = 0
        self.max_daily_cycles = 7

    # 5.1
    def validate_arrangement(self):
        """Validates current mold arrangement across all arms"""
        for arm in self.arms_list:
            if not arm.check_spatial_constraint():
                return False, f"Spatial constraint violated on arm {arm.arm_id}"
            if not arm.check_balance_constraint():
                return False, f"Balance constraint violated on arm {arm.arm_id}"
            if not arm.check_temperature_compatibility():
                return False, f"Temperature compatibility failed on arm {arm.arm_id}"
            if not arm.check_duration_compatibility():
                return False, f"Duration compatibility failed on arm {arm.arm_id}"
        return True, "All constraints satisfied"

    # 5.2
    def execute_cycle(self):
        """Executes one complete cycle if constraints are satisfied"""
        is_valid, message = self.validate_arrangement()
        if not is_valid:
            return False, message
        
        if self.daily_cycles_completed >= self.max_daily_cycles:
            return False, "Daily cycle limit reached"
        
        self.current_cycle += 1
        self.daily_cycles_completed += 1
        return True, f"Cycle {self.current_cycle} completed successfully"

    # 5.3
    def change_arrangement(self, setup_time_loss=0):
        """Changes mold arrangement with optional setup time penalty"""
        cycles_lost = setup_time_loss
        self.max_daily_cycles = max(0, self.max_daily_cycles - cycles_lost)
        return f"Arrangement changed, {cycles_lost} cycles lost to setup"


# 6. Order Class
class Order:
    def __init__(self, order_id, mold_requirements, deadline):
        self.order_id = order_id
        self.mold_requirements = mold_requirements  # Dict: {mold_id: quantity}
        self.deadline = deadline
        self.completion_status = {}  # Track progress per mold type
        self.is_complete = False

    # 6.1
    def update_progress(self, mold_id, quantity_produced):
        """Updates production progress for specific mold type"""
        if mold_id not in self.completion_status:
            self.completion_status[mold_id] = 0
        self.completion_status[mold_id] += quantity_produced
        
        # Check if this mold requirement is fulfilled
        if mold_id in self.mold_requirements:
            required = self.mold_requirements[mold_id]
            if self.completion_status[mold_id] >= required:
                self.completion_status[mold_id] = required

    # 6.2
    def check_completion(self):
        """Checks if entire order is completed"""
        for mold_id, required_qty in self.mold_requirements.items():
            completed_qty = self.completion_status.get(mold_id, 0)
            if completed_qty < required_qty:
                self.is_complete = False
                return False
        
        self.is_complete = True
        return True


def main():
    print("----- Mold Class Tests -----")
    # Create test mold objects
    mold1 = Mold(mold_id="A1", volume=10, weight=5, heating_time=3, heating_temperature=200, cooling_time=2, mounting_time=1, distance_from_center=0.5, available_quantity=100)
    mold2 = Mold(mold_id="A2", volume=12, weight=8, heating_time=3.06, heating_temperature=203, cooling_time=1.5, mounting_time=1, distance_from_center=0.4, available_quantity=30)
    mold3 = Mold(mold_id="A3", volume=0, weight=0, heating_time=0, heating_temperature=0, cooling_time=0, mounting_time=0, distance_from_center=0, available_quantity=0)

    # Test calculate_torque
    print("Torque mold1:", mold1.calculate_torque())             # 5 * 0.5 = 2.5
    print("Torque mold2:", mold2.calculate_torque())             # 8 * 0.4 = 3.2
    print("Torque mold3 (edge, zero):", mold3.calculate_torque()) # 0

    # Test get_cycle_time
    print("Cycle time mold1:", mold1.get_cycle_time())           # 3 + 2 + 1 = 6
    print("Cycle time mold2:", mold2.get_cycle_time())           # 3.06 + 1.5 + 1 = 5.56
    print("Cycle time mold3:", mold3.get_cycle_time())           # 0

    # Test check_availability
    print("Avail mold1, req=20:", mold1.check_availability(20))          # True
    print("Avail mold1, req=100:", mold1.check_availability(100))        # True
    print("Avail mold1, req=120:", mold1.check_availability(120))        # False
    print("Avail mold3, req=1 (edge):", mold3.check_availability(1))     # False

    # Test check_compatibility_with (default tolerance)
    print("Compatibility mold1, mold2 (should be True):", mold1.check_compatibility_with(mold2))  # Check within defaults
    # Test incompatibility by increasing temp/time diff
    mold4 = Mold(mold_id="A4", volume=5, weight=2, heating_time=10, heating_temperature=270, cooling_time=2, mounting_time=1, distance_from_center=0.5, available_quantity=10)
    print("Compatibility mold1, mold4 (should be False):", mold1.check_compatibility_with(mold4))
    # Very tight tolerance
    print("Compatibility mold1, mold2, tight tol (should be False):", mold1.check_compatibility_with(mold2, temp_tolerance=0.005, time_tolerance=0.005))

    # Test get_parameter_range
    print("Parameter range mold1:", mold1.get_parameter_range())
    print("Parameter range mold4:", mold4.get_parameter_range())

if __name__ == "__main__":
    main()
