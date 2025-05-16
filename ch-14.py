import random
import time
import os
import math
import shutil
from datetime import datetime

class SubnetAnalyzer:
    """
    A comprehensive tool for learning and practicing subnet analysis,
    directly aligned with Chapter 14 from the CCNA exam preparation.
    """
    
    def __init__(self):
        self.clear_screen()
        self.stats = {
            "attempts": 0,
            "correct": 0,
            "streak": 0,
            "best_streak": 0,
            "total_time": 0,
            "fastest_time": float('inf'),
            "last_session": None,
            "mastery_levels": {
                "easy_masks_decimal": 0,
                "difficult_masks_decimal": 0,
                "binary_calculation": 0,
                "timed_drills": 0
            }
        }
        
        self.current_mode = "learning"  # "learning" or "exam_prep"
        self.calculation_method = "decimal"  # "decimal" or "binary"
        self.difficulty_level = "easy"  # "easy", "difficult", or "mixed"
        self.time_goal = 30  # seconds
        self.accuracy_goal = 90  # percent
        self.streak_goal = 10
        
        self.load_stats()
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def load_stats(self):
        """Load saved statistics if they exist."""
        try:
            with open('subnet_stats.txt', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if ':' in line:
                        key, value = line.strip().split(':', 1)
                        if key == 'last_session':
                            self.stats[key] = value.strip()
                        elif key in self.stats and key != 'mastery_levels':
                            try:
                                self.stats[key] = float(value.strip()) if '.' in value else int(value.strip())
                            except ValueError:
                                continue
                        elif key in self.stats['mastery_levels']:
                            try:
                                self.stats['mastery_levels'][key] = int(value.strip())
                            except ValueError:
                                continue
            print("Statistics loaded successfully!")
        except FileNotFoundError:
            print("No previous statistics found. Starting fresh!")
        except Exception as e:
            print(f"Error loading statistics: {e}")
    
    def save_stats(self):
        """Save statistics to a file."""
        try:
            with open('subnet_stats.txt', 'w') as f:
                for key, value in self.stats.items():
                    if key == 'mastery_levels':
                        for ml_key, ml_value in value.items():
                            f.write(f"{ml_key}: {ml_value}\n")
                    else:
                        f.write(f"{key}: {value}\n")
            print("Statistics saved successfully!")
        except Exception as e:
            print(f"Error saving statistics: {e}")
    
    def update_stats(self, correct, time_taken):
        """Update statistics after a practice attempt."""
        self.stats["attempts"] += 1
        self.stats["last_session"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if correct:
            self.stats["correct"] += 1
            self.stats["streak"] += 1
            self.stats["total_time"] += time_taken
            
            if self.stats["streak"] > self.stats["best_streak"]:
                self.stats["best_streak"] = self.stats["streak"]
            
            if time_taken < self.stats["fastest_time"]:
                self.stats["fastest_time"] = time_taken
            
            key = None
            if self.calculation_method == "decimal":
                if self.difficulty_level in ["easy", "mixed"]:
                    key = "easy_masks_decimal"
                else:
                    key = "difficult_masks_decimal"
            elif self.calculation_method == "binary":
                key = "binary_calculation"
            
            if key and time_taken <= self.time_goal:
                self.stats["mastery_levels"][key] += 1
        else:
            self.stats["streak"] = 0
        
        self.save_stats()
    
    def calculate_mastery_percentage(self):
        """Calculate overall mastery percentage based on various skills."""
        total_levels = sum(self.stats["mastery_levels"].values())
        max_possible = len(self.stats["mastery_levels"]) * 100  # Assuming 100 is "perfect" mastery
        
        return min(100, int((total_levels / max_possible) * 100)) if max_possible > 0 else 0
    
    # ============= IP and Subnet Generation Functions =============
    
    def generate_random_ip(self):
        """Generate a random IP address."""
        return [random.randint(1, 254) for _ in range(4)]
    
    def generate_mask(self, difficulty="easy"):
        """Generate a subnet mask based on difficulty."""
        if difficulty == "easy":
            # Easy masks: 255.0.0.0, 255.255.0.0, 255.255.255.0
            prefix_len = random.choice([8, 16, 24])
            mask = [255] * (prefix_len // 8) + [0] * (4 - (prefix_len // 8))
            return mask
        else:
            # Difficult masks with one interesting octet
            possible_masks = [
                # Classful Class A network with different masks
                [255, 128, 0, 0], [255, 192, 0, 0], [255, 224, 0, 0], [255, 240, 0, 0],
                [255, 248, 0, 0], [255, 252, 0, 0], [255, 254, 0, 0],
                
                # Classful Class B network with different masks
                [255, 255, 128, 0], [255, 255, 192, 0], [255, 255, 224, 0], [255, 255, 240, 0],
                [255, 255, 248, 0], [255, 255, 252, 0], [255, 255, 254, 0],
                
                # Classful Class C network with different masks
                [255, 255, 255, 128], [255, 255, 255, 192], [255, 255, 255, 224],
                [255, 255, 255, 240], [255, 255, 255, 248], [255, 255, 255, 252]
            ]
            return random.choice(possible_masks)
    
    def generate_specific_problem(self, problem_type="random"):
        """Generate specific problem types mentioned in the book."""
        if problem_type == "pdf_example_1":
            # Example from book: 172.16.150.41, 255.255.192.0
            return [172, 16, 150, 41], [255, 255, 192, 0]
        elif problem_type == "pdf_example_2":
            # Example from book: 192.168.5.77, 255.255.255.224
            return [192, 168, 5, 77], [255, 255, 255, 224]
        elif problem_type == "quiz_1":
            # Quiz problem 1: 10.7.99.133, 255.255.255.0
            return [10, 7, 99, 133], [255, 255, 255, 0]
        elif problem_type == "quiz_2":
            # Quiz problem 2: 192.168.44.97, 255.255.255.252
            return [192, 168, 44, 97], [255, 255, 255, 252]
        elif problem_type == "quiz_3":
            # Quiz problem 3: 172.31.77.201, 255.255.255.224
            return [172, 31, 77, 201], [255, 255, 255, 224]
        elif problem_type == "quiz_4":
            # Quiz problem 4: 10.1.4.0, 255.255.254.0
            return [10, 1, 4, 0], [255, 255, 254, 0]
        else:
            # Random problem based on current difficulty
            ip = self.generate_random_ip()
            mask = self.generate_mask(self.difficulty_level)
            return ip, mask
    
    # ============= Subnet Analysis Methods =============
    
    def calculate_magic_number(self, mask_octet):
        """Calculate the magic number (256 - mask_value)."""
        return 256 - mask_octet
    
    def find_interesting_octet(self, mask):
        """Find the 'interesting octet' in a subnet mask."""
        for i in range(4):
            if mask[i] not in [0, 255]:
                return i
        return None  # No interesting octet (easy mask)
    
    def decimal_subnet_id(self, ip, mask):
        """Calculate subnet ID using decimal method."""
        subnet_id = []
        
        for i in range(4):
            if mask[i] == 255:
                # If mask octet is 255, copy the IP octet
                subnet_id.append(ip[i])
            elif mask[i] == 0:
                # If mask octet is 0, subnet ID octet is 0
                subnet_id.append(0)
            else:
                # This is the "interesting octet"
                magic_number = self.calculate_magic_number(mask[i])
                # Find multiple of magic_number closest to ip[i] without going over
                subnet_id.append((ip[i] // magic_number) * magic_number)
        
        return subnet_id
    
    def decimal_broadcast_address(self, subnet_id, mask):
        """Calculate broadcast address using decimal method."""
        broadcast = []
        
        for i in range(4):
            if mask[i] == 255:
                # If mask octet is 255, copy the subnet ID octet
                broadcast.append(subnet_id[i])
            elif mask[i] == 0:
                # If mask octet is 0, broadcast octet is 255
                broadcast.append(255)
            else:
                # This is the "interesting octet"
                magic_number = self.calculate_magic_number(mask[i])
                # Subnet ID + magic number - 1
                broadcast.append(subnet_id[i] + magic_number - 1)
        
        return broadcast
    
    def binary_subnet_id(self, ip, mask):
        """Calculate subnet ID using binary method as shown in the book."""
        binary_ip = self.to_binary(ip)
        binary_mask = self.to_binary(mask)
        
        # Applying the subnet ID calculation in binary
        binary_subnet_id = ''
        for i in range(32):
            if binary_mask[i] == '1':
                # Copy the IP bit if the mask bit is 1
                binary_subnet_id += binary_ip[i]
            else:
                # Set to 0 if the mask bit is 0
                binary_subnet_id += '0'
        
        # Convert back to decimal
        return self.from_binary(binary_subnet_id)
    
    def binary_broadcast_address(self, ip, mask):
        """Calculate broadcast address using binary method."""
        binary_ip = self.to_binary(ip)
        binary_mask = self.to_binary(mask)
        
        # Applying the broadcast address calculation in binary
        binary_broadcast = ''
        for i in range(32):
            if binary_mask[i] == '1':
                # Copy the IP bit if the mask bit is 1
                binary_broadcast += binary_ip[i]
            else:
                # Set to 1 if the mask bit is 0
                binary_broadcast += '1'
        
        # Convert back to decimal
        return self.from_binary(binary_broadcast)
    
    def to_binary(self, ip_or_mask):
        """Convert an IP address or mask to a 32-bit binary string."""
        binary = ''
        for octet in ip_or_mask:
            # Convert to 8-bit binary and remove '0b' prefix
            binary += bin(octet)[2:].zfill(8)
        return binary
    
    def from_binary(self, binary_str):
        """Convert a 32-bit binary string back to decimal [a,b,c,d] format."""
        result = []
        for i in range(0, 32, 8):
            octet_binary = binary_str[i:i+8]
            result.append(int(octet_binary, 2))
        return result
    
    def get_usable_range(self, subnet_id, broadcast):
        """Calculate the range of usable IP addresses in the subnet."""
        # First usable IP = Subnet ID + 1 (in the last octet)
        first_usable = subnet_id.copy()
        first_usable[3] += 1
        
        # Last usable IP = Broadcast Address - 1 (in the last octet)
        last_usable = broadcast.copy()
        last_usable[3] -= 1
        
        return first_usable, last_usable
    
    def ip_to_str(self, ip):
        """Convert IP array to string."""
        return ".".join(map(str, ip))
    
    def str_to_ip(self, ip_str):
        """Convert IP string to array."""
        return [int(octet) for octet in ip_str.split('.')]
    
    def validate_ip_input(self, ip_str):
        """Validate user input for IP address."""
        try:
            octets = ip_str.split('.')
            if len(octets) != 4:
                return False
            
            for octet in octets:
                num = int(octet)
                if num < 0 or num > 255:
                    return False
            
            return True
        except:
            return False
    
    # ============= Visualization Functions =============
    
    def binary_visualization(self, ip, mask, subnet_id, broadcast):
        """Create a visual representation of the binary subnet calculation process."""
        binary_ip = self.to_binary(ip)
        binary_mask = self.to_binary(mask)
        binary_subnet = self.to_binary(subnet_id)
        binary_broadcast = self.to_binary(broadcast)
        
        # Find the prefix length
        prefix_length = binary_mask.count('1')
        
        output = []
        output.append("\n🔍 Binary Calculation Visualization\n")
        
        # Display the mask with prefix and host parts clearly marked
        output.append("Subnet Mask Analysis:")
        output.append("Prefix Length: /" + str(prefix_length))
        
        # Visual representation of the structure
        structure = ['P'] * prefix_length + ['H'] * (32 - prefix_length)
        
        # Format the binary representation for better readability
        def format_binary(binary_str, structure=None):
            result = ""
            for i in range(32):
                if i > 0 and i % 8 == 0:
                    result += "."
                
                if structure:
                    # Color or highlight for prefix vs host bits
                    if structure[i] == 'P':
                        result += binary_str[i]  # Could use ANSI colors here
                    else:
                        result += binary_str[i]  # Different formatting
                else:
                    result += binary_str[i]
            
            return result
        
        output.append("\nStructure:       " + format_binary(''.join(structure)))
        output.append("Mask (binary):   " + format_binary(binary_mask))
        output.append("IP (binary):     " + format_binary(binary_ip, structure))
        output.append("\nSubnet ID Calculation (copy prefix bits, set host bits to 0):")
        output.append("Subnet (binary): " + format_binary(binary_subnet, structure))
        output.append("\nBroadcast Calculation (copy prefix bits, set host bits to 1):")
        output.append("Broadcast (bin): " + format_binary(binary_broadcast, structure))
        
        # Print the consolidated output
        print("\n".join(output))
    
    def draw_number_line(self, divisor, highlighted_range=None):
        """
        Draw a number line visualization for subnet divisions.
        
        Args:
            divisor: The magic number (size of subnet division)
            highlighted_range: Optional tuple (start, end) to highlight a specific range
        """
        max_value = 255
        labels = [i * divisor for i in range((max_value // divisor) + 1)]
        if labels[-1] != max_value:
            labels.append(max_value)

        try:
            width = shutil.get_terminal_size().columns
        except:
            width = 80

        min_width = 128
        max_width = 256
        usable = max(min_width, min(width - 10, max_width))
        length = usable - 1

        positions = [round(label / max_value * length) for label in labels]

        if divisor < 8:
            disp = [lbl for lbl in labels if lbl % 8 == 0 or lbl in (0, max_value)]
            disp_pos = [round(lbl / max_value * length) for lbl in disp]
            top = disp[::2]; top_pos = disp_pos[::2]
            bot = disp[1::2]; bot_pos = disp_pos[1::2]
        else:
            top = labels; top_pos = positions
            bot = []; bot_pos = []

        top_line = [' '] * usable
        for lbl, pos in zip(top, top_pos):
            s = str(lbl)
            start = max(0, min(pos - len(s) // 2, usable - len(s)))
            for i, ch in enumerate(s):
                top_line[start + i] = ch
        top_line = ''.join(top_line)

        if divisor < 8:
            top_tick = [' '] * usable
            for pos in top_pos: top_tick[pos] = '|'
            scale = ['-'] * usable
            for pos in positions: scale[pos] = '+'
            bot_tick = [' '] * usable
            for pos in bot_pos: bot_tick[pos] = '|'
            bot_line = [' '] * usable
            for lbl, pos in zip(bot, bot_pos):
                s = str(lbl)
                start = max(0, min(pos - len(s) // 2, usable - len(s)))
                for i, ch in enumerate(s):
                    bot_line[start + i] = ch
            bot_line = ''.join(bot_line)

            print(top_line)
            print(''.join(top_tick))
            print(''.join(scale))
            print(''.join(bot_tick))
            print(bot_line)
        else:
            tick = [' '] * usable
            for pos in positions: tick[pos] = '|'
            scale = ['-'] * usable
            for pos in positions: scale[pos] = '+'
            print(top_line)
            print(''.join(tick))
            print(''.join(scale))

        # Display ranges
        ranges = []
        for i in range(len(labels) - 1):
            start = labels[i]
            end = labels[i + 1] - 1 if i + 1 < len(labels) - 1 or labels[i + 1] != 255 else 255
            cell_value = f"[{start:>3} - {end:<3}]"
            
            # Add highlighting indicator if this range is specified
            if highlighted_range and start == highlighted_range[0] and end == highlighted_range[1]:
                cell_value = f"→ {cell_value} ←"
            
            ranges.append(cell_value)

        print("\nRanges:")
        max_rows = 16
        cols = math.ceil(len(ranges) / max_rows)
        rows = math.ceil(len(ranges) / cols)
        table = [''] * rows
        for i in range(rows):
            row_parts = []
            for j in range(cols):
                idx = i + j * rows
                if idx < len(ranges):
                    label = f"{idx + 1:>3}: "
                    cell = label + ranges[idx]
                    row_parts.append(cell.ljust(20))  # Increased padding for highlighted ranges
            table[i] = ' '.join(row_parts)
        print('\n'.join(table))
        print()
    
    def show_subnet_visualization(self):
        """Show subnet visualizations for different mask values."""
        while True:
            self.clear_screen()
            print("🔍 Subnet Visualizations")
            print("\nThese visualizations show how an octet (0-255) is divided based on the subnet mask.")
            print("Each '+' marks the start of a subnet range in the octet.")
            
            print("\nVisualization Options:")
            print("1. View by mask value")
            print("2. View all common mask values")
            print("3. Interactive visualization tool")
            print("4. Return to main menu")
            
            choice = input("\nSelect an option (1-4): ").strip()
            
            if choice == '1':
                mask_value = input("\nEnter mask value (128, 192, 224, 240, 248, 252, 254): ").strip()
                try:
                    mask_value = int(mask_value)
                    if mask_value not in [128, 192, 224, 240, 248, 252, 254]:
                        print("Invalid mask value. Try again.")
                        time.sleep(1)
                        continue
                    
                    magic_number = 256 - mask_value
                    print(f"\nVisualization for mask value {mask_value} (magic number {magic_number}):")
                    self.draw_number_line(magic_number)
                    input("Press Enter to continue...")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
                    time.sleep(1)
            
            elif choice == '2':
                mask_values = [128, 192, 224, 240, 248, 252, 254]
                
                for mask_value in mask_values:
                    magic_number = 256 - mask_value
                    print(f"\n===== Mask Value: {mask_value} (Magic Number: {magic_number}) =====")
                    self.draw_number_line(magic_number)
                    
                    if input("\nPress Enter for next mask or 'q' to quit: ").lower() == 'q':
                        break
            
            elif choice == '3':
                self.interactive_visualization()
            
            elif choice == '4':
                break
            
            else:
                print("Invalid choice. Please try again.")
                time.sleep(1)
    
    def interactive_visualization(self):
        """Interactive tool to visualize where an IP address falls in a subnet."""
        self.clear_screen()
        print("🔍 Interactive Subnet Visualization Tool")
        print("This tool helps you visualize how an IP address fits within subnet ranges.\n")
        
        # Get user input
        ip_str = input("Enter an IP address (e.g., 192.168.1.1): ").strip()
        mask_str = input("Enter a subnet mask (e.g., 255.255.255.0): ").strip()
        
        if not self.validate_ip_input(ip_str) or not self.validate_ip_input(mask_str):
            print("Invalid IP or mask format. Try again.")
            time.sleep(2)
            return
        
        ip = self.str_to_ip(ip_str)
        mask = self.str_to_ip(mask_str)
        
        # Find the interesting octet
        interesting_octet = self.find_interesting_octet(mask)
        
        if interesting_octet is None:
            # Easy mask
            print("\nThis is an easy mask with no interesting octet.")
            subnet_id = self.decimal_subnet_id(ip, mask)
            broadcast = self.decimal_broadcast_address(subnet_id, mask)
            print(f"Subnet ID: {self.ip_to_str(subnet_id)}")
            print(f"Broadcast: {self.ip_to_str(broadcast)}")
            input("\nPress Enter to continue...")
            return
        
        # Calculate subnet details
        magic_number = self.calculate_magic_number(mask[interesting_octet])
        subnet_id = self.decimal_subnet_id(ip, mask)
        broadcast = self.decimal_broadcast_address(subnet_id, mask)
        
        print(f"\nIP address: {ip_str}")
        print(f"Subnet mask: {mask_str}")
        print(f"Interesting octet: #{interesting_octet+1} (value: {ip[interesting_octet]})")
        print(f"Magic number: {magic_number}")
        print(f"Subnet ID: {self.ip_to_str(subnet_id)}")
        print(f"Broadcast: {self.ip_to_str(broadcast)}")
        
        # Visualize the subnet division
        print(f"\nVisualization for octet #{interesting_octet+1} with mask {mask[interesting_octet]}:")
        
        # Highlight the range containing the IP address
        range_start = subnet_id[interesting_octet]
        range_end = broadcast[interesting_octet]
        
        self.draw_number_line(magic_number, (range_start, range_end))
        
        input("\nPress Enter to continue...")
    
    def reference_table(self):
        """Display reference tables similar to Table 14-12 in the book."""
        self.clear_screen()
        print("📚 Subnet Reference Tables\n")
        
        # Create Table 14-12 equivalent
        print("Table: DDN Mask Values, Magic Numbers, and Prefixes")
        print("====================================================")
        print("| Mask Value | Magic Number |  Binary  | Prefix (if in...) |")
        print("|            |              |          | 2nd | 3rd | 4th   |")
        print("----------------------------------------------------")
        print("| 128        | 128          | 10000000 | /9  | /17 | /25   |")
        print("| 192        | 64           | 11000000 | /10 | /18 | /26   |")
        print("| 224        | 32           | 11100000 | /11 | /19 | /27   |")
        print("| 240        | 16           | 11110000 | /12 | /20 | /28   |")
        print("| 248        | 8            | 11111000 | /13 | /21 | /29   |")
        print("| 252        | 4            | 11111100 | /14 | /22 | /30   |")
        print("| 254        | 2            | 11111110 | /15 | /23 | /31   |")
        print("| 255        | 1            | 11111111 | /16 | /24 | /32   |")
        print("====================================================")
        
        print("\nKey Formulas:")
        print("1. Magic Number = 256 - Mask Value")
        print("2. Subnet ID = (IP value ÷ Magic Number) × Magic Number")
        print("3. Broadcast = Subnet ID + Magic Number - 1")
        print("4. First Usable = Subnet ID + 1")
        print("5. Last Usable = Broadcast - 1")
        
        input("\nPress Enter to continue...")
    
    # ============= Practice Modes =============
    
    def get_step_by_step_explanation(self, ip, mask, subnet_id, broadcast, calc_method="decimal"):
        """Generate a detailed step-by-step explanation of the subnet calculation."""
        method = calc_method or self.calculation_method
        first_usable, last_usable = self.get_usable_range(subnet_id, broadcast)
        
        explanation = []
        explanation.append("\n📝 Step-by-Step Explanation:")
        
        # Find the interesting octet if using decimal method
        interesting_octet = None
        if method == "decimal":
            interesting_octet = self.find_interesting_octet(mask)
            
            if interesting_octet is None:
                # Easy mask explanation
                explanation.append("\nThis is an easy mask (only 255s and 0s):")
                explanation.append("• For octets with mask 255: Copy the IP address value")
                explanation.append("• For octets with mask 0: Use 0 for subnet ID, 255 for broadcast")
                
                for i in range(4):
                    if mask[i] == 255:
                        explanation.append(f"  Octet #{i+1}: Mask=255 → Copy IP {ip[i]} to subnet ID")
                    else:
                        explanation.append(f"  Octet #{i+1}: Mask=0 → Subnet ID=0, Broadcast=255")
            else:
                # Difficult mask explanation
                magic_number = self.calculate_magic_number(mask[interesting_octet])
                explanation.append(f"\nThis mask has an interesting octet (#{interesting_octet+1}):")
                explanation.append(f"• Magic number = 256 - {mask[interesting_octet]} = {magic_number}")
                
                # Show multiples of the magic number
                multiples = []
                current = 0
                while current <= 255:
                    multiples.append(current)
                    current += magic_number
                
                explanation.append(f"• Multiples of {magic_number}: {', '.join(map(str, multiples))}")
                
                # Explain subnet ID calculation
                explanation.append(f"\nSubnet ID calculation:")
                for i in range(4):
                    if mask[i] == 255:
                        explanation.append(f"  Octet #{i+1}: Mask=255 → Copy IP {ip[i]} to subnet ID")
                    elif mask[i] == 0:
                        explanation.append(f"  Octet #{i+1}: Mask=0 → Set subnet ID to 0")
                    else:
                        explanation.append(f"  Octet #{i+1}: Interesting octet with IP={ip[i]}, Mask={mask[i]}")
                        explanation.append(f"    Find multiple of {magic_number} closest to {ip[i]} without going over")
                        explanation.append(f"    → {subnet_id[i]} is the subnet ID value in this octet")
                
                # Explain broadcast calculation
                explanation.append(f"\nBroadcast address calculation:")
                for i in range(4):
                    if mask[i] == 255:
                        explanation.append(f"  Octet #{i+1}: Mask=255 → Copy subnet ID {subnet_id[i]} to broadcast")
                    elif mask[i] == 0:
                        explanation.append(f"  Octet #{i+1}: Mask=0 → Set broadcast to 255")
                    else:
                        explanation.append(f"  Octet #{i+1}: Interesting octet")
                        explanation.append(f"    Broadcast = Subnet ID + Magic Number - 1")
                        explanation.append(f"    = {subnet_id[i]} + {magic_number} - 1 = {broadcast[i]}")
        
        elif method == "binary":
            # Binary calculation explanation
            binary_ip = self.to_binary(ip)
            binary_mask = self.to_binary(mask)
            binary_subnet = self.to_binary(subnet_id)
            binary_broadcast = self.to_binary(broadcast)
            
            prefix_length = binary_mask.count('1')
            
            explanation.append(f"\nBinary calculation method:")
            explanation.append(f"• Mask has a prefix length of /{prefix_length}")
            explanation.append(f"• For subnet ID: Copy prefix bits, set host bits to 0")
            explanation.append(f"• For broadcast: Copy prefix bits, set host bits to 1")
            
            # Format binary strings for better readability
            def format_binary(binary_str):
                return '.'.join([binary_str[i:i+8] for i in range(0, len(binary_str), 8)])
            
            explanation.append(f"\nIP (binary):      {format_binary(binary_ip)}")
            explanation.append(f"Mask (binary):    {format_binary(binary_mask)}")
            explanation.append(f"Subnet (binary):  {format_binary(binary_subnet)}")
            explanation.append(f"Broadcast (binary): {format_binary(binary_broadcast)}")
        
        # Common explanations regardless of method
        explanation.append(f"\nFinal Results:")
        explanation.append(f"• Subnet ID:      {self.ip_to_str(subnet_id)}")
        explanation.append(f"• Broadcast:      {self.ip_to_str(broadcast)}")
        explanation.append(f"• First Usable:   {self.ip_to_str(first_usable)}")
        explanation.append(f"• Last Usable:    {self.ip_to_str(last_usable)}")
        
        return "\n".join(explanation)
    
    def practice_problem(self, problem_type="random", show_timer=True):
        """Present a practice problem for subnet analysis."""
        self.clear_screen()
        
        # Generate the problem
        ip, mask = self.generate_specific_problem(problem_type)
        ip_str = self.ip_to_str(ip)
        mask_str = self.ip_to_str(mask)
        
        # Calculate correct answers
        if self.calculation_method == "decimal":
            subnet_id = self.decimal_subnet_id(ip, mask)
            broadcast = self.decimal_broadcast_address(subnet_id, mask)
        else:  # binary
            subnet_id = self.binary_subnet_id(ip, mask)
            broadcast = self.binary_broadcast_address(ip, mask)
        
        first_usable, last_usable = self.get_usable_range(subnet_id, broadcast)
        
        # Display the problem
        print("📝 Subnet Analysis Problem")
        
        if self.current_mode == "exam_prep":
            print(f"\nTime Goal: {self.time_goal} seconds")
        
        print(f"\nIP Address: {ip_str}")
        print(f"Subnet Mask: {mask_str}")
        
        # Mode-specific instructions
        if self.calculation_method == "binary":
            print("\nUse binary calculation method to find:")
        else:
            print("\nCalculate:")
        
        print("1. Subnet ID")
        print("2. Broadcast Address")
        print("3. First Usable Address")
        print("4. Last Usable Address")
        
        # Start timing if needed
        start_time = time.time()
        if show_timer and self.current_mode == "exam_prep":
            print("\nTimer started...")
        
        # Get user answers
        user_subnet = input("\nSubnet ID: ").strip()
        user_broadcast = input("Broadcast Address: ").strip()
        user_first = input("First Usable Address: ").strip()
        user_last = input("Last Usable Address: ").strip()
        
        # Stop timing
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Check answers
        correct_subnet = user_subnet == self.ip_to_str(subnet_id)
        correct_broadcast = user_broadcast == self.ip_to_str(broadcast)
        correct_first = user_first == self.ip_to_str(first_usable)
        correct_last = user_last == self.ip_to_str(last_usable)
        
        all_correct = correct_subnet and correct_broadcast and correct_first and correct_last
        
        # Update statistics
        self.update_stats(all_correct, elapsed_time)
        
        # Show results
        print("\n===== Results =====")
        if all_correct:
            print(f"✅ All answers are correct! Time: {elapsed_time:.2f} seconds")
            
            if self.current_mode == "exam_prep":
                if elapsed_time <= self.time_goal:
                    print(f"🎯 You met the time goal of {self.time_goal} seconds!")
                else:
                    print(f"⏱️ Try to answer faster next time (goal: {self.time_goal} seconds)")
            
            print(f"Current streak: {self.stats['streak']}")
        else:
            print(f"❌ Some answers were incorrect. Time: {elapsed_time:.2f} seconds")
            
            if not correct_subnet:
                print(f"Subnet ID: Your answer: {user_subnet}, Correct: {self.ip_to_str(subnet_id)}")
            if not correct_broadcast:
                print(f"Broadcast: Your answer: {user_broadcast}, Correct: {self.ip_to_str(broadcast)}")
            if not correct_first:
                print(f"First Usable: Your answer: {user_first}, Correct: {self.ip_to_str(first_usable)}")
            if not correct_last:
                print(f"Last Usable: Your answer: {user_last}, Correct: {self.ip_to_str(last_usable)}")
        
        # Offer explanation and visualization
        if not all_correct or elapsed_time > self.time_goal or input("\nWould you like to see the explanation? (y/n): ").lower().startswith('y'):
            print(self.get_step_by_step_explanation(ip, mask, subnet_id, broadcast, self.calculation_method))
            
            # Offer visualization
            if input("\nWould you like to see a visualization? (y/n): ").lower().startswith('y'):
                if self.calculation_method == "binary":
                    self.binary_visualization(ip, mask, subnet_id, broadcast)
                else:
                    interesting_octet = self.find_interesting_octet(mask)
                    if interesting_octet is not None:
                        magic_number = self.calculate_magic_number(mask[interesting_octet])
                        range_start = subnet_id[interesting_octet]
                        range_end = broadcast[interesting_octet]
                        print(f"\nVisualization of octet #{interesting_octet+1} with mask {mask[interesting_octet]}:")
                        self.draw_number_line(magic_number, (range_start, range_end))
        
        # Return to menu or next problem
        return input("\nContinue practicing? (y/n): ").lower().startswith('y')
    
    def pdf_practice_problems(self):
        """Practice specifically with problems from the book."""
        self.clear_screen()
        print("📚 Practice with Problems from Chapter 14")
        print("\nSelect a problem to practice:")
        print("1. Example 1: 172.16.150.41, 255.255.192.0")
        print("2. Example 2: 192.168.5.77, 255.255.255.224")
        print("3. Quiz Problem 1: 10.7.99.133, 255.255.255.0")
        print("4. Quiz Problem 2: 192.168.44.97, 255.255.255.252")
        print("5. Quiz Problem 3: 172.31.77.201, 255.255.255.224")
        print("6. Quiz Problem 4: 10.1.4.0, 255.255.254.0")
        print("7. Return to practice menu")
        
        choice = input("\nSelect an option (1-7): ").strip()
        
        if choice == '1':
            return self.practice_problem("pdf_example_1")
        elif choice == '2':
            return self.practice_problem("pdf_example_2")
        elif choice == '3':
            return self.practice_problem("quiz_1")
        elif choice == '4':
            return self.practice_problem("quiz_2")
        elif choice == '5':
            return self.practice_problem("quiz_3")
        elif choice == '6':
            return self.practice_problem("quiz_4")
        elif choice == '7':
            return True
        else:
            print("Invalid choice. Please try again.")
            time.sleep(1)
            return True
    
    def focused_practice(self):
        """Practice menu for focused learning on specific concepts."""
        while True:
            self.clear_screen()
            print("🎯 Focused Practice Menu")
            print("\nSelect a practice mode:")
            print("1. Easy Masks (Decimal Method)")
            print("2. Difficult Masks (Decimal Method)")
            print("3. Binary Calculation Method")
            print("4. Problems from the book")
            print("5. Random Mix")
            print("6. Return to main menu")
            
            choice = input("\nSelect an option (1-6): ").strip()
            
            old_method = self.calculation_method
            old_difficulty = self.difficulty_level
            
            if choice == '1':
                self.calculation_method = "decimal"
                self.difficulty_level = "easy"
                continue_practice = self.practice_problem()
            elif choice == '2':
                self.calculation_method = "decimal"
                self.difficulty_level = "difficult"
                continue_practice = self.practice_problem()
            elif choice == '3':
                self.calculation_method = "binary"
                self.difficulty_level = "mixed"
                continue_practice = self.practice_problem()
            elif choice == '4':
                continue_practice = self.pdf_practice_problems()
            elif choice == '5':
                self.calculation_method = random.choice(["decimal", "binary"])
                self.difficulty_level = random.choice(["easy", "difficult"])
                continue_practice = self.practice_problem()
            elif choice == '6':
                break
            else:
                print("Invalid choice. Please try again.")
                time.sleep(1)
                continue
            
            # Reset to original settings
            self.calculation_method = old_method
            self.difficulty_level = old_difficulty
            
            # Continue practicing in the same mode if requested
            while continue_practice:
                if choice == '4':
                    continue_practice = self.pdf_practice_problems()
                else:
                    continue_practice = self.practice_problem()
    
    def timed_practice(self):
        """Timed practice mode for exam preparation."""
        old_mode = self.current_mode
        self.current_mode = "exam_prep"
        
        self.clear_screen()
        print("⏱️ Timed Practice Mode")
        print(f"\nGoal: Answer problems correctly within {self.time_goal} seconds")
        print("This mode helps you prepare for the time constraints of the exam.")
        
        input("\nPress Enter to start...")
        
        continue_practice = True
        problem_count = 0
        correct_count = 0
        total_time = 0
        
        while continue_practice:
            self.clear_screen()
            print(f"Problem {problem_count + 1}")
            
            start_time = time.time()
            result = self.practice_problem(show_timer=True)
            end_time = time.time()
            
            elapsed = end_time - start_time
            total_time += elapsed
            problem_count += 1
            
            if self.stats["streak"] > 0:  # If the last problem was correct
                correct_count += 1
            
            print(f"\nStatistics so far:")
            print(f"Problems completed: {problem_count}")
            print(f"Correct answers: {correct_count}")
            print(f"Accuracy: {(correct_count / problem_count * 100):.1f}%")
            print(f"Average time: {(total_time / problem_count):.2f} seconds")
            
            continue_practice = result
        
        self.current_mode = old_mode
    
    def learning_progression(self):
        """Structured learning path that follows chapter progression."""
        self.clear_screen()
        print("📚 Subnet Analysis Learning Progression")
        print("\nThis path guides you through subnet analysis concepts in order.")
        
        stages = [
            {
                "name": "Introduction to Subnets",
                "description": "Learn the basic concepts of subnets and key terms.",
                "action": self.subnet_introduction
            },
            {
                "name": "Easy Masks with Decimal Method",
                "description": "Practice with easy masks (255.0.0.0, 255.255.0.0, 255.255.255.0).",
                "action": lambda: self.practice_with_settings("decimal", "easy")
            },
            {
                "name": "Difficult Masks with Decimal Method",
                "description": "Learn the 'interesting octet' concept and magic numbers.",
                "action": lambda: self.practice_with_settings("decimal", "difficult")
            },
            {
                "name": "Binary Calculation Method",
                "description": "Understand how to analyze subnets using binary math.",
                "action": lambda: self.practice_with_settings("binary", "mixed")
            },
            {
                "name": "Speed Drills",
                "description": "Practice for exam time constraints (20-30 seconds per problem).",
                "action": self.timed_practice
            }
        ]
        
        while True:
            self.clear_screen()
            print("📚 Learning Progression")
            print("\nSelect a stage to practice:")
            
            for i, stage in enumerate(stages):
                mastery = "🔒"  # Default: locked
                
                if i == 0:
                    mastery = "🔓"  # First stage is always unlocked
                elif i == 1 and self.stats["mastery_levels"]["easy_masks_decimal"] > 0:
                    mastery = "🔓"
                elif i == 2 and self.stats["mastery_levels"]["difficult_masks_decimal"] > 0:
                    mastery = "🔓"
                elif i == 3 and self.stats["mastery_levels"]["binary_calculation"] > 0:
                    mastery = "🔓"
                elif i == 4 and self.stats["mastery_levels"]["timed_drills"] > 0:
                    mastery = "🔓"
                
                progress = "✅" if self.stats["mastery_levels"].get(stage["name"].lower().replace(" ", "_"), 0) > 5 else "⏳"
                
                print(f"{i+1}. {mastery} {stage['name']} {progress}")
                print(f"   {stage['description']}")
            
            print(f"{len(stages)+1}. Return to main menu")
            
            choice = input("\nSelect a stage (1-6): ").strip()
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(stages):
                    stages[choice_num-1]["action"]()
                elif choice_num == len(stages)+1:
                    break
                else:
                    print("Invalid choice. Please try again.")
                    time.sleep(1)
            except ValueError:
                print("Invalid input. Please enter a number.")
                time.sleep(1)
    
    def subnet_introduction(self):
        """Introduction to subnet concepts."""
        self.clear_screen()
        print("🌐 Introduction to Subnet Analysis")
        
        # Basic subnet concept explanations
        print("\n=== What is a Subnet? ===")
        print("A subnet is a logical division of an IP network. Subnets allow network administrators to")
        print("divide a single network address into smaller network segments.\n")
        
        print("=== Key Subnet Concepts ===")
        print("• Subnet ID: The lowest address in the subnet - identifies the subnet")
        print("• Subnet Broadcast Address: The highest address in the subnet")
        print("• Usable IP Range: All addresses between the subnet ID+1 and broadcast-1")
        print("• Subnet Mask: Determines which portion of an IP address is the network address\n")
        
        input("Press Enter to continue...")
        
        self.clear_screen()
        print("=== Example of a Simple Subnet ===")
        print("Consider the IP address 192.168.1.1 with mask 255.255.255.0")
        print("\nThe subnet ID is 192.168.1.0")
        print("The broadcast address is 192.168.1.255")
        print("The usable range is 192.168.1.1 through 192.168.1.254")
        
        print("\n=== Easy vs. Difficult Masks ===")
        print("• Easy masks contain only 255s and 0s (e.g., 255.255.255.0)")
        print("• Difficult masks have one octet that is neither 0 nor 255 (e.g., 255.255.240.0)")
        print("  This octet is called the 'interesting octet'")
        
        input("\nPress Enter to practice with a simple example...")
        
        self.calculation_method = "decimal"
        self.difficulty_level = "easy"
        self.practice_problem("quiz_1")  # This is an easy mask example
        
        return True
    
    def practice_with_settings(self, method, difficulty):
        """Practice with specific settings."""
        old_method = self.calculation_method
        old_difficulty = self.difficulty_level
        
        self.calculation_method = method
        self.difficulty_level = difficulty
        
        continue_practice = True
        while continue_practice:
            continue_practice = self.practice_problem()
        
        self.calculation_method = old_method
        self.difficulty_level = old_difficulty
        
        return True
    
    # ============= Settings and Statistics =============
    
    def change_settings(self):
        """Change program settings."""
        while True:
            self.clear_screen()
            print("⚙️ Settings")
            
            print("\nCurrent Settings:")
            print(f"1. Mode: {self.current_mode.replace('_', ' ').title()}")
            print(f"2. Calculation Method: {self.calculation_method.title()}")
            print(f"3. Difficulty Level: {self.difficulty_level.title()}")
            print(f"4. Time Goal: {self.time_goal} seconds")
            print(f"5. Accuracy Goal: {self.accuracy_goal}%")
            print(f"6. Streak Goal: {self.streak_goal}")
            print("7. Return to main menu")
            
            choice = input("\nSelect a setting to change (1-7): ").strip()
            
            if choice == '1':
                mode_choice = input("Select mode (1. Learning, 2. Exam Prep): ").strip()
                if mode_choice == '1':
                    self.current_mode = "learning"
                elif mode_choice == '2':
                    self.current_mode = "exam_prep"
            
            elif choice == '2':
                method_choice = input("Select calculation method (1. Decimal, 2. Binary): ").strip()
                if method_choice == '1':
                    self.calculation_method = "decimal"
                elif method_choice == '2':
                    self.calculation_method = "binary"
            
            elif choice == '3':
                diff_choice = input("Select difficulty (1. Easy, 2. Difficult, 3. Mixed): ").strip()
                if diff_choice == '1':
                    self.difficulty_level = "easy"
                elif diff_choice == '2':
                    self.difficulty_level = "difficult"
                elif diff_choice == '3':
                    self.difficulty_level = "mixed"
            
            elif choice == '4':
                time_input = input(f"Enter new time goal in seconds (current: {self.time_goal}): ").strip()
                try:
                    time_val = int(time_input)
                    if 5 <= time_val <= 120:
                        self.time_goal = time_val
                except ValueError:
                    print("Invalid input. Please enter a number between 5 and 120.")
                    time.sleep(1)
            
            elif choice == '5':
                acc_input = input(f"Enter new accuracy goal percentage (current: {self.accuracy_goal}): ").strip()
                try:
                    acc_val = int(acc_input)
                    if 1 <= acc_val <= 100:
                        self.accuracy_goal = acc_val
                except ValueError:
                    print("Invalid input. Please enter a number between 1 and 100.")
                    time.sleep(1)
            
            elif choice == '6':
                streak_input = input(f"Enter new streak goal (current: {self.streak_goal}): ").strip()
                try:
                    streak_val = int(streak_input)
                    if 1 <= streak_val <= 100:
                        self.streak_goal = streak_val
                except ValueError:
                    print("Invalid input. Please enter a number between 1 and 100.")
                    time.sleep(1)
            
            elif choice == '7':
                break
            
            else:
                print("Invalid choice. Please try again.")
                time.sleep(1)
    
    def show_statistics(self):
        """Display detailed statistics on user performance."""
        self.clear_screen()
        print("📊 Your Statistics")
        
        # Basic statistics
        print("\n=== Overall Statistics ===")
        print(f"Total attempts: {self.stats['attempts']}")
        
        if self.stats['attempts'] > 0:
            accuracy = (self.stats['correct'] / self.stats['attempts']) * 100
            print(f"Correct answers: {self.stats['correct']} ({accuracy:.1f}%)")
            print(f"Average time: {(self.stats['total_time'] / self.stats['attempts']):.2f} seconds")
        
        print(f"Current streak: {self.stats['streak']}")
        print(f"Best streak: {self.stats['best_streak']}")
        
        if self.stats['fastest_time'] < float('inf'):
            print(f"Fastest time: {self.stats['fastest_time']:.2f} seconds")
        
        print("\n=== Mastery Levels ===")
        for skill, level in self.stats['mastery_levels'].items():
            skill_name = skill.replace('_', ' ').title()
            mastery = "⭐" * min(5, (level // 2))
            print(f"{skill_name}: {mastery} ({level}/10)")
        
        print(f"\nOverall Mastery: {self.calculate_mastery_percentage()}%")
        
        if self.stats['last_session']:
            print(f"\nLast practice session: {self.stats['last_session']}")
        
        print("\n=== Exam Readiness ===")
        if self.stats['attempts'] > 0:
            time_ready = self.stats['total_time'] / self.stats['attempts'] <= self.time_goal
            accuracy_ready = (self.stats['correct'] / self.stats['attempts']) * 100 >= self.accuracy_goal
            
            if time_ready and accuracy_ready:
                print("✅ You're meeting both time and accuracy goals!")
            elif time_ready:
                print("⏱️ You're meeting the time goal, but need to improve accuracy.")
            elif accuracy_ready:
                print("🎯 You're meeting the accuracy goal, but need to improve speed.")
            else:
                print("🔄 Keep practicing to improve both speed and accuracy.")
        else:
            print("Start practicing to track your exam readiness!")
        
        input("\nPress Enter to continue...")
    
    def reset_statistics(self):
        """Reset all statistics."""
        confirm = input("Are you sure you want to reset all statistics? (yes/no): ").strip().lower()
        
        if confirm == "yes":
            self.stats = {
                "attempts": 0,
                "correct": 0,
                "streak": 0,
                "best_streak": 0,
                "total_time": 0,
                "fastest_time": float('inf'),
                "last_session": None,
                "mastery_levels": {
                    "easy_masks_decimal": 0,
                    "difficult_masks_decimal": 0,
                    "binary_calculation": 0,
                    "timed_drills": 0
                }
            }
            
            self.save_stats()
            print("Statistics have been reset.")
            time.sleep(1)
        else:
            print("Reset cancelled.")
            time.sleep(1)
    
    # ============= Main Menu and Program Flow =============
    
    def show_main_menu(self):
        """Display the main menu and handle user selections."""
        while True:
            self.clear_screen()
            print("🌐 Subnet Analysis Master - CCNA Chapter 14 🌐")
            
            # Show mastery status if available
            if self.stats['attempts'] > 0:
                print(f"\nMastery Level: {self.calculate_mastery_percentage()}%")
                print(f"Current Streak: {self.stats['streak']}")
            
            print("\nMain Menu:")
            print("1. Learning Progression (Guided Path)")
            print("2. Focused Practice")
            print("3. Timed Practice (Exam Prep)")
            print("4. Reference Materials")
            print("5. Subnet Visualizations")
            print("6. View Statistics")
            print("7. Settings")
            print("8. Reset Statistics")
            print("9. Exit")
            
            choice = input("\nSelect an option (1-9): ").strip()
            
            if choice == '1':
                self.learning_progression()
            elif choice == '2':
                self.focused_practice()
            elif choice == '3':
                self.timed_practice()
            elif choice == '4':
                self.reference_table()
            elif choice == '5':
                self.show_subnet_visualization()
            elif choice == '6':
                self.show_statistics()
            elif choice == '7':
                self.change_settings()
            elif choice == '8':
                self.reset_statistics()
            elif choice == '9':
                print("\nThank you for using Subnet Analysis Master!")
                print("Keep practicing - you'll be a subnet expert in no time!")
                self.save_stats()
                break
            else:
                print("Invalid choice. Please try again.")
                time.sleep(1)

if __name__ == "__main__":
    analyzer = SubnetAnalyzer()
    analyzer.show_main_menu()
