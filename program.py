"""
Classful IPv4 Networking Quiz
Based on CCNA 200-301 Official Cert Guide Library, Second Edition
Chapter 12 Review

Features:
- Study Mode: Tables visible, 90% goal, no timer
- Test Mode: No tables, 100% goal, 10-second timer per question
"""

from typing import Optional, Tuple, Literal, Final, TypeAlias, Union, Dict, Any, List, Callable, cast
from dataclasses import dataclass
import random
import time
import os
import sys
import threading

IPAddress: TypeAlias = str
NetworkClass: TypeAlias = Literal["A", "B", "C", "D", "E", "Reserved (0.x.x.x)", "Reserved (127.x.x.x)"] | None
ClassFilter: TypeAlias = Optional[Literal["A", "B", "C"]]
OctetCount: TypeAlias = Union[int, Literal["N/A - Special class"]]
IPRange: TypeAlias = Tuple[str, str]

QuizMode: TypeAlias = Literal["study", "test"]

CLASS_RANGES: Final[Dict[str, Tuple[int, int]]] = {
    "A": (1, 126),
    "B": (128, 191),
    "C": (192, 223),
    "D": (224, 239),
    "E": (240, 255)
}

RESERVED_PREFIXES: Final[Dict[int, Literal["Reserved (0.x.x.x)", "Reserved (127.x.x.x)"]]] = {
    0: "Reserved (0.x.x.x)",
    127: "Reserved (127.x.x.x)"
}

# properties from Table 12-2 and 12-3
CLASS_PROPERTIES: Final[Dict[str, Dict[str, Any]]] = {
    "A": {
        "purpose": "Unicast (large networks)",
        "network_octets": 1,
        "host_octets": 3,
        "valid_network_range": "1.0.0.0–126.0.0.0",
        "total_networks": 126,  # 2^7 - 2 (0 and 127 are reserved)
        "hosts_per_network": 16777214,  # 2^24 - 2
        "network_bits": 8,
        "host_bits": 24,
        "default_mask": "255.0.0.0"
    },
    "B": {
        "purpose": "Unicast (medium-sized networks)",
        "network_octets": 2,
        "host_octets": 2,
        "valid_network_range": "128.0.0.0–191.255.0.0",
        "total_networks": 16384,  # 2^14
        "hosts_per_network": 65534,  # 2^16 - 2
        "network_bits": 16,
        "host_bits": 16,
        "default_mask": "255.255.0.0"
    },
    "C": {
        "purpose": "Unicast (small networks)",
        "network_octets": 3,
        "host_octets": 1,
        "valid_network_range": "192.0.0.0–223.255.255.0",
        "total_networks": 2097152,  # 2^21
        "hosts_per_network": 254,  # 2^8 - 2
        "network_bits": 24,
        "host_bits": 8,
        "default_mask": "255.255.255.0"
    },
    "D": {
        "purpose": "Multicast",
        "network_octets": "N/A",
        "host_octets": "N/A",
        "valid_network_range": "224.0.0.0-239.255.255.255",
        "total_networks": "N/A",
        "hosts_per_network": "N/A",
        "network_bits": "N/A",
        "host_bits": "N/A",
        "default_mask": "N/A"
    },
    "E": {
        "purpose": "Reserved (formerly experimental)",
        "network_octets": "N/A",
        "host_octets": "N/A",
        "valid_network_range": "240.0.0.0-255.255.255.255",
        "total_networks": "N/A",
        "hosts_per_network": "N/A",
        "network_bits": "N/A",
        "host_bits": "N/A",
        "default_mask": "N/A"
    }
}

@dataclass
class QuizQuestion:
    """Data structure defining a quiz question."""
    prompt: str
    validator: Callable[[str, Any], bool]
    correct_answer: Any
    feedback: str
    additional_info: str


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

    print("\n" + "=" * 50)
    print("CLASSFUL IP NETWORKING QUIZ")
    print("=" * 50 + "\n")

def get_ip_address(class_filter: ClassFilter = None) -> IPAddress:
    """
    Generate a random IP address.

    Args:
        class_filter: Generate IP of specific class ('A', 'B', or 'C')
                     If None, generates any valid Class A, B, or C IP

    Returns:
        A randomly generated IP address as a string
    """
    selected_class = class_filter or random.choice(['A', 'B', 'C'])
    class_range = CLASS_RANGES[selected_class]
    first_octet = random.randint(class_range[0], class_range[1])

    other_octets = [random.randint(0, 255) for _ in range(3)]

    return f"{first_octet}.{other_octets[0]}.{other_octets[1]}.{other_octets[2]}"

def get_first_octet(ip_addr: IPAddress) -> Optional[int]:
    """
    Extract the first octet from an IP address.

    Args:
        ip_addr: The IP address to check

    Returns:
        First octet as an integer or None if invalid
    """
    try:
        octets = ip_addr.split(".")
        if len(octets) != 4:
            return None

        return int(octets[0])
    except (ValueError, IndexError):
        return None

def get_network_class(ip_addr: IPAddress) -> NetworkClass:
    """
    Determine the class of an IP address.

    Args:
        ip_addr: The IP address to check

    Returns:
        The network class as a string or None if invalid
    """
    first_octet = get_first_octet(ip_addr)
    if first_octet is None:
        return None

    if first_octet in RESERVED_PREFIXES:
        return RESERVED_PREFIXES[first_octet]

    for class_name, (start, end) in CLASS_RANGES.items():
        if start <= first_octet <= end:
            # Cast class_name to ensure type safety
            if class_name in ("A", "B", "C", "D", "E"):
                return cast(Literal["A", "B", "C", "D", "E"], class_name)

    return None

def get_property_for_ip(ip_addr: IPAddress, property_name: str) -> Any:
    """
    Get a specific property for an IP address based on its class.

    Args:
        ip_addr: The IP address to analyze
        property_name: The name of the property to retrieve

    Returns:
        The value of the requested property or None if invalid/not applicable
    """
    network_class = get_network_class(ip_addr)

    if network_class in CLASS_PROPERTIES and property_name in CLASS_PROPERTIES[network_class]:
        return CLASS_PROPERTIES[network_class][property_name]
    elif network_class in ["Reserved (0.x.x.x)", "Reserved (127.x.x.x)"]:
        return "N/A - Special class"
    else:
        return None

def count_network_octets(ip_addr: IPAddress) -> OctetCount:
    """Count the number of network octets in an IP address."""
    return get_property_for_ip(ip_addr, "network_octets")

def count_host_octets(ip_addr: IPAddress) -> OctetCount:
    """Count the number of host octets in an IP address."""
    return get_property_for_ip(ip_addr, "host_octets")

def get_network_purpose(ip_addr: IPAddress) -> str:
    """Get the purpose of the network class of an IP address."""
    purpose = get_property_for_ip(ip_addr, "purpose")
    return str(purpose) if purpose else "Reserved for special use"

def get_total_networks(ip_addr: IPAddress) -> Union[int, str]:
    """Get the total number of networks available for the IP's class."""
    return get_property_for_ip(ip_addr, "total_networks")

def get_hosts_per_network(ip_addr: IPAddress) -> Union[int, str]:
    """Get the number of hosts per network for the IP's class."""
    return get_property_for_ip(ip_addr, "hosts_per_network")

def get_network_bits(ip_addr: IPAddress) -> Union[int, str]:
    """Get the number of bits in the network part of an IP address."""
    return get_property_for_ip(ip_addr, "network_bits")

def get_host_bits(ip_addr: IPAddress) -> Union[int, str]:
    """Get the number of bits in the host part of an IP address."""
    return get_property_for_ip(ip_addr, "host_bits")

def get_default_mask(ip_addr: IPAddress) -> Union[IPAddress, Literal["N/A - Special class"], None]:
    """Return the default subnet mask for an IP address."""
    return get_property_for_ip(ip_addr, "default_mask")

def get_valid_network_range(ip_addr: IPAddress) -> str:
    """Get the valid network range for the IP's class."""
    network_range = get_property_for_ip(ip_addr, "valid_network_range")
    return str(network_range) if network_range else "N/A"

def get_network_id(ip_addr: IPAddress) -> Union[IPAddress, Literal["N/A - Special class"], None]:
    """
    Calculate the network ID of an IP address.

    Args:
        ip_addr: The IP address to analyze

    Returns:
        The network ID as a string, "N/A - Special class" for special cases, or None if invalid
    """
    network_class = get_network_class(ip_addr)
    network_octets = count_network_octets(ip_addr)

    try:
        octets = ip_addr.split(".")
        if len(octets) != 4:
            return None

        if network_class in ["A", "B", "C"] and isinstance(network_octets, int):
            result = octets[:network_octets] + ["0"] * (4 - network_octets)
            return ".".join(result)
        elif network_class in ["D", "E", "Reserved (0.x.x.x)", "Reserved (127.x.x.x)"]:
            return "N/A - Special class"
        else:
            return None
    except Exception:
        return None

def get_broadcast_addr(ip_addr: IPAddress) -> Union[IPAddress, Literal["N/A - Special class"], None]:
    """
    Calculate the broadcast address of an IP address.

    Args:
        ip_addr: The IP address to analyze

    Returns:
        The broadcast address as a string, "N/A - Special class" for special cases, or None if invalid
    """
    network_class = get_network_class(ip_addr)
    network_octets = count_network_octets(ip_addr)

    try:
        octets = ip_addr.split(".")
        if len(octets) != 4:
            return None

        if network_class in ["A", "B", "C"] and isinstance(network_octets, int):
            result = octets[:network_octets] + ["255"] * (4 - network_octets)
            return ".".join(result)
        elif network_class in ["D", "E", "Reserved (0.x.x.x)", "Reserved (127.x.x.x)"]:
            return "N/A - Special class"
        else:
            return None
    except Exception:
        return None

def get_usable_ip_range(ip_addr: IPAddress) -> Union[IPRange, Tuple[Literal["N/A - Special class"], Literal["N/A - Special class"]], Tuple[None, None]]:
    """
    Calculate the usable IP range of an IP address.

    Args:
        ip_addr: The IP address to analyze

    Returns:
        A tuple containing the first and last usable IP addresses,
        or ("N/A - Special class", "N/A - Special class") for special cases
    """
    network_id = get_network_id(ip_addr)
    broadcast = get_broadcast_addr(ip_addr)
    network_class = get_network_class(ip_addr)

    if network_class in ["A", "B", "C"] and isinstance(network_id, str) and isinstance(broadcast, str):
        network_id_octets = network_id.split(".")

        # First usable is network ID + 1 in the last octet
        first_usable_octets = network_id_octets.copy()
        first_usable_octets[3] = "1"
        first_usable = ".".join(first_usable_octets)

        # Last usable is broadcast - 1 in the last octet
        broadcast_octets = broadcast.split(".")
        last_usable_octets = broadcast_octets.copy()
        last_usable_octets[3] = "254"
        last_usable = ".".join(last_usable_octets)

        return (first_usable, last_usable)
    elif network_class in ["D", "E", "Reserved (0.x.x.x)", "Reserved (127.x.x.x)"]:
        return ("N/A - Special class", "N/A - Special class")
    else:
        return (None, None)

def get_ip_info_dict(ip_addr: IPAddress) -> Dict[str, Any]:
    """
    Gather all information about an IP address into a dictionary.

    Args:
        ip_addr: The IP address to analyze

    Returns:
        Dictionary containing all IP information
    """
    return {
        "ip_address": ip_addr,
        "network_class": get_network_class(ip_addr),
        "purpose": get_network_purpose(ip_addr),
        "network_octets": count_network_octets(ip_addr),
        "host_octets": count_host_octets(ip_addr),
        "network_bits": get_network_bits(ip_addr),
        "host_bits": get_host_bits(ip_addr),
        "network_id": get_network_id(ip_addr),
        "broadcast": get_broadcast_addr(ip_addr),
        "usable_range": get_usable_ip_range(ip_addr),
        "default_mask": get_default_mask(ip_addr),
        "valid_network_range": get_valid_network_range(ip_addr),
        "total_networks": get_total_networks(ip_addr),
        "hosts_per_network": get_hosts_per_network(ip_addr)
    }

def present_ip_info(ip_addr: IPAddress) -> None:
    """
    Present all information about an IP address.

    Args:
        ip_addr: The IP address to display information about
    """
    ip_info = get_ip_info_dict(ip_addr)

    print(f"\nIP Address: {ip_info['ip_address']}")
    print(f"Class: {ip_info['network_class']}")
    print(f"Purpose: {ip_info['purpose']}")

    if ip_info['network_class'] in ["A", "B", "C"]:
        print(f"Network Octets: {ip_info['network_octets']} ({ip_info['network_bits']} bits)")
        print(f"Host Octets: {ip_info['host_octets']} ({ip_info['host_bits']} bits)")
        print(f"Network ID: {ip_info['network_id']}")
        print(f"Broadcast Address: {ip_info['broadcast']}")
        print(f"Usable IP Range: {ip_info['usable_range'][0]} to {ip_info['usable_range'][1]}")
        print(f"Default Subnet Mask: {ip_info['default_mask']}")
        print(f"Valid Network Range: {ip_info['valid_network_range']}")
        print(f"Total Networks in this Class: {ip_info['total_networks']}")
        print(f"Hosts per Network: {ip_info['hosts_per_network']}")
    else:
        print("This is a special class IP address, so standard network/host concepts do not apply.")

def display_classful_info_tables() -> None:
    """Display the reference tables for classful IP addressing."""
    # Table 12-2
    print("\nIP Address Classes Reference (Table 12-2):")
    print("+" + "-" * 7 + "+" + "-" * 21 + "+" + "-" * 31 + "+")
    print("| Class | First Octet Values   | Purpose                       |")
    print("+" + "-" * 7 + "+" + "-" * 21 + "+" + "-" * 31 + "+")

    for class_name in ["A", "B", "C", "D", "E"]:
        class_range = CLASS_RANGES[class_name]
        purpose = CLASS_PROPERTIES[class_name]["purpose"]
        print(f"| {class_name:<5} | {class_range[0]:<3}-{class_range[1]:<15} | {purpose:<29} |")

    print("+" + "-" * 7 + "+" + "-" * 21 + "+" + "-" * 31 + "+")
    print("Reserved: 0.x.x.x and 127.x.x.x")

    print("\nKey Facts for Classes A, B, and C (Table 12-3):")
    col_width = 20
    print("+" + "-" * 26 + "+" + "-" * col_width + "+" + "-" * col_width + "+" + "-" * col_width + "+")
    print(f"| {'Property':<24} | {'Class A':<{col_width-2}} | {'Class B':<{col_width-2}} | {'Class C':<{col_width-2}} |")
    print("+" + "-" * 26 + "+" + "-" * col_width + "+" + "-" * col_width + "+" + "-" * col_width + "+")

    def print_property_row(property_name: str, getter: Callable[[str], Any]) -> None:
        values = [getter('A'), getter('B'), getter('C')]

        if "network numbers" in property_name:
            ranges_a = getter('A').split('–')
            ranges_b = getter('B').split('–')
            ranges_c = getter('C').split('–')

            if len(ranges_a) == 2 and len(ranges_b) == 2 and len(ranges_c) == 2:
                first_line = f"| {property_name:<24} | {ranges_a[0]:<{col_width-2}} | {ranges_b[0]:<{col_width-2}} | {ranges_c[0]:<{col_width-2}} |"
                second_line = f"| {'':<24} | to {ranges_a[1]:<{col_width-5}} | to {ranges_b[1]:<{col_width-5}} | to {ranges_c[1]:<{col_width-5}} |"
                print(first_line)
                print(second_line)
                return

        print(f"| {property_name:<24} | {str(values[0]):<{col_width-2}} | {str(values[1]):<{col_width-2}} | {str(values[2]):<{col_width-2}} |")

    properties = [
        ("First octet range", lambda c: f"{CLASS_RANGES[c][0]}-{CLASS_RANGES[c][1]}"),
        ("Valid network numbers", lambda c: CLASS_PROPERTIES[c]["valid_network_range"]),
        ("Total networks", lambda c: CLASS_PROPERTIES[c]["total_networks"]),
        ("Hosts per network", lambda c: CLASS_PROPERTIES[c]["hosts_per_network"]),
        ("Network octets (bits)", lambda c: f"{CLASS_PROPERTIES[c]['network_octets']} ({CLASS_PROPERTIES[c]['network_bits']})"),
        ("Host octets (bits)", lambda c: f"{CLASS_PROPERTIES[c]['host_octets']} ({CLASS_PROPERTIES[c]['host_bits']})"),
        ("Default mask", lambda c: CLASS_PROPERTIES[c]["default_mask"])
    ]

    for prop_name, getter in properties:
        print_property_row(prop_name, getter)

    print("+" + "-" * 26 + "+" + "-" * col_width + "+" + "-" * col_width + "+" + "-" * col_width + "+")
    print("\nNote: Addresses beginning with 0 and 127 are reserved in Class A.")
    print("There are 126 Class A networks, not 128, due to these reservations.")

    print("\nPress Enter to continue...")
    input()

def prompt_for_choice(prompt: str, options: List[Any], option_descriptors: List[str]) -> Any:
    """
    Prompt for a choice from a list of options.

    Args:
        prompt: The prompt to display
        options: List of valid options
        option_descriptors: List of descriptions for each option

    Returns:
        The user's choice
    """
    print(f"\n{prompt}")
    for i, desc in enumerate(option_descriptors, 1):
        print(f"{i}. {desc}")

    while True:
        choice = input(f"Enter your choice (1-{len(options)}): ")
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print(f"Invalid choice. Please enter a number between 1 and {len(options)}.")

def ask_quiz_question(question, ip_addr: IPAddress, mode: QuizMode, max_attempts: int = 3) -> bool:
    """
    Ask a quiz question and validate the answer.

    Args:
        question: The quiz question to ask
        ip_addr: The IP address being analyzed
        mode: The current quiz mode (study or test)
        max_attempts: Maximum number of attempts allowed

    Returns:
        True if answered correctly, False otherwise
    """

    if mode == "study":
        for attempt in range(1, max_attempts + 1):
            print(f"\nIP Address: {ip_addr}")
            user_answer = input(f"Attempt {attempt}/{max_attempts}: {question.prompt}")

            if question.validator(user_answer, question.correct_answer):
                print("✓ Correct!")
                return True
            else:
                if attempt < max_attempts:
                    print("✗ Incorrect. Try again.")
                else:
                    print(f"✗ The correct answer is {question.feedback}")
                    print(question.additional_info)
                    return False
    else:
        clear_screen()
        print(f"\n[TEST MODE - 10 seconds per question]")
        print(f"\nIP Address: {ip_addr}")
        print(f"Question: {question.prompt}")

        timer_expired = False
        question_start_time = time.time()

        t = threading.Thread(target=lambda: time.sleep(10) or setattr(sys.modules[__name__], 'timer_expired', True))
        t.daemon = True
        t.start()

        user_answer = input("Your answer: ")

        answer_time = time.time() - question_start_time

        continue_message = "Press any key to continue..."

        if timer_expired:
            print(f"✗ Time expired! Time taken: {answer_time:.2f} seconds")
            print(f"The correct answer is {question.feedback}")
            print(question.additional_info)
            _ = input(continue_message)
            return False
        else:
            if question.validator(user_answer, question.correct_answer):
                print(f"✓ Correct! Time taken: {answer_time:.2f} seconds")
                _ = input(continue_message)
                return True
            else:
                print(f"✗ Incorrect. Time taken: {answer_time:.2f} seconds")
                print(f"The correct answer is {question.feedback}")
                print(question.additional_info)
                _ = input(continue_message)
                return False

    return False

def run_quiz(mode: QuizMode) -> None:
    """
    Run the IP address quiz in the specified mode.

    Args:
        mode: The quiz mode (study or test)
    """
    goal_percentage = 90 if mode == "study" else 100

    clear_screen()
    print(f"[{mode.upper()} MODE]")
    print(f"Goal: {goal_percentage}% correct answers")
    if mode == "test":
        print("Time limit: 10 seconds per question")
    print()

    if mode == "study":
        display_classful_info_tables()

    total_score = 0
    total_questions = 0

    while True:
        clear_screen()
        print(f"[{mode.upper()} MODE] - Goal: {goal_percentage}%")
        if total_questions > 0:
            overall_percentage = (total_score / total_questions) * 100
            print(f"Current performance: {total_score}/{total_questions} ({overall_percentage:.1f}%)")
        print()

        options: List[ClassFilter | Literal["view_tables", "end_quiz"]] = ['A', 'B', 'C', None]
        option_descriptors = [
            "Class A",
            "Class B",
            "Class C",
            "Random (A, B, or C)"
        ]

        if mode == "study":
            options.append('view_tables')
            option_descriptors.append("View Reference Tables")

        options.append('end_quiz')
        option_descriptors.append("End Quiz")

        class_choice = prompt_for_choice(f"Select IP Class for quiz:", options, option_descriptors)

        if class_choice == 'view_tables':
            clear_screen()
            display_classful_info_tables()
            continue
        elif class_choice == 'end_quiz':
            break

        ip_addr = get_ip_address(class_choice)

        clear_screen()
        print(f"[{mode.upper()} MODE] - IP Address: {ip_addr}")
        if mode == "test":
            print("Time limit: 10 seconds per question")
        print("=" * 50)

        ip_info = get_ip_info_dict(ip_addr)

        if ip_info['network_class'] not in ["A", "B", "C"]:
            print(f"\nThe generated IP {ip_addr} is Class {ip_info['network_class']}.")
            print("This is a special class that doesn't apply to standard classful networking questions.")
            print("Let's generate a new IP address for the quiz.")
            time.sleep(2)
            continue

        quiz_questions = [
            # 1. Class identification
            QuizQuestion(
                prompt="What is the class of this IP address? (A/B/C): ",
                validator=lambda ans, correct: ans.upper() == correct,
                correct_answer=ip_info['network_class'],
                feedback=ip_info['network_class'],
                additional_info=f"Class A: {CLASS_RANGES['A'][0]}-{CLASS_RANGES['A'][1]}, Class B: {CLASS_RANGES['B'][0]}-{CLASS_RANGES['B'][1]}, Class C: {CLASS_RANGES['C'][0]}-{CLASS_RANGES['C'][1]}"
            ),

            # 2. Network Purpose
            QuizQuestion(
                prompt="What is the purpose of this IP address class? (e.g., Unicast, Multicast): ",
                validator=lambda ans, correct: ans.lower() in correct.lower(),
                correct_answer=ip_info['purpose'],
                feedback=ip_info['purpose'],
                additional_info="Class A: Unicast (large networks)\nClass B: Unicast (medium-sized networks)\nClass C: Unicast (small networks)"
            ),

            # 3. Network Octets
            QuizQuestion(
                prompt="How many network octets does this IP address have? (1-3): ",
                validator=lambda ans, correct: ans.isdigit() and int(ans) == correct,
                correct_answer=ip_info['network_octets'],
                feedback=str(ip_info['network_octets']) + " network octets",
                additional_info="Class A: 1 network octet, Class B: 2 network octets, Class C: 3 network octets"
            ),

            # 4. Host Octets
            QuizQuestion(
                prompt="How many host octets does this IP address have? (1-3): ",
                validator=lambda ans, correct: ans.isdigit() and int(ans) == correct,
                correct_answer=ip_info['host_octets'],
                feedback=str(ip_info['host_octets']) + " host octets",
                additional_info="Class A: 3 host octets, Class B: 2 host octets, Class C: 1 host octet"
            ),

            # 5. Network Bits
            QuizQuestion(
                prompt="How many bits are in the network part of this IP address? (8/16/24): ",
                validator=lambda ans, correct: ans.isdigit() and int(ans) == correct,
                correct_answer=ip_info['network_bits'],
                feedback=str(ip_info['network_bits']) + " bits",
                additional_info="Class A: 8 bits, Class B: 16 bits, Class C: 24 bits"
            ),

            # 6. Host Bits
            QuizQuestion(
                prompt="How many bits are in the host part of this IP address? (8/16/24): ",
                validator=lambda ans, correct: ans.isdigit() and int(ans) == correct,
                correct_answer=ip_info['host_bits'],
                feedback=str(ip_info['host_bits']) + " bits",
                additional_info="Class A: 24 bits, Class B: 16 bits, Class C: 8 bits"
            ),

            # 7. Hosts per Network
            QuizQuestion(
                prompt="How many hosts per network does this IP address class support?\nOptions: A) 254   B) 65,534   C) 16,777,214\nEnter A, B, or C: ",
                validator=lambda ans, correct: ans.upper() == correct,
                correct_answer={"A": "C", "B": "B", "C": "A"}[ip_info['network_class']],
                feedback={"A": "C: 16,777,214", "B": "B: 65,534", "C": "A: 254"}[ip_info['network_class']],
                additional_info="Class A: 2^24 - 2 = 16,777,214 hosts\nClass B: 2^16 - 2 = 65,534 hosts\nClass C: 2^8 - 2 = 254 hosts"
            ),

            # 8. Network ID
            QuizQuestion(
                prompt="What is the network ID of this IP address?: ",
                validator=lambda ans, correct: ans == correct,
                correct_answer=ip_info['network_id'],
                feedback=ip_info['network_id'],
                additional_info="For network ID, keep the network octets and set all host octets to 0."
            ),

            # 9. Broadcast Address
            QuizQuestion(
                prompt="What is the broadcast address of this IP address?: ",
                validator=lambda ans, correct: ans == correct,
                correct_answer=ip_info['broadcast'],
                feedback=ip_info['broadcast'],
                additional_info="For broadcast address, keep the network octets and set all host octets to 255."
            ),

            # 10. Default Subnet Mask
            QuizQuestion(
                prompt="What is the default subnet mask for this IP address?: ",
                validator=lambda ans, correct: ans == correct,
                correct_answer=ip_info['default_mask'],
                feedback=ip_info['default_mask'],
                additional_info="Class A: 255.0.0.0, Class B: 255.255.0.0, Class C: 255.255.255.0"
            )
        ]

        current_score = 0
        for question in quiz_questions:
            if ask_quiz_question(question, ip_addr, mode):
                current_score += 1

        max_score = len(quiz_questions)

        current_percentage = (current_score / max_score) * 100

        clear_screen()
        print(f"[{mode.upper()} MODE] - IP Quiz Results")
        print("=" * 50)
        print(f"IP Address: {ip_addr}")
        print(f"Your score: {current_score}/{max_score} ({current_percentage:.1f}%)")

        if current_percentage >= goal_percentage:
            print(f"✓ Goal achieved! You scored {current_percentage:.1f}% (goal: {goal_percentage}%)")
        else:
            print(f"✗ Goal not met. You scored {current_percentage:.1f}% (goal: {goal_percentage}%)")

        total_score += current_score
        total_questions += max_score

        overall_percentage = (total_score / total_questions) * 100 if total_questions > 0 else 0
        print("\nOverall performance:")
        print(f"{total_score}/{total_questions} ({overall_percentage:.1f}%)")

        if mode == "study":
            print("\nHere's the complete information about this IP address:")
            present_ip_info(ip_addr)

        print("\nPress Enter to continue...")
        input()

    if total_questions > 0:
        final_percentage = (total_score / total_questions) * 100

        clear_screen()
        print(f"Final Quiz Statistics [{mode.upper()} MODE]")
        print("=" * 50)
        print(f"Total Questions: {total_questions}")
        print(f"Correct Answers: {total_score}")
        print(f"Final Score: {final_percentage:.1f}%")

        if final_percentage >= goal_percentage:
            print(f"✓ OVERALL GOAL ACHIEVED! You scored {final_percentage:.1f}% (goal: {goal_percentage}%)")
        else:
            print(f"✗ OVERALL GOAL NOT MET. You scored {final_percentage:.1f}% (goal: {goal_percentage}%)")

        if final_percentage >= 90:
            print("\nExcellent! You've mastered classful IP addressing.")
        elif final_percentage >= 75:
            print("\nGood job! You have a solid understanding of classful IP addressing.")
        elif final_percentage >= 60:
            print("\nNot bad! With a bit more practice, you'll master these concepts.")
        else:
            print("\nKeep practicing! Classful IP addressing takes time to master.")

        print("\nPress Enter to return to main menu...")
        input()
    else:
        print("\nNo questions were answered.")
        time.sleep(2)

def main() -> None:
    """Run the IP address educational quiz program."""
    clear_screen()
    print("Welcome to IP Address Classful Networking Quiz!")
    print("This program will help you learn about classful IP addressing.\n")

    print("Quiz Modes:")
    print("1. Study Mode: Reference tables visible, 90% goal, no timer")
    print("2. Test Mode: No tables, 100% goal, 10-second timer per question")

    while True:
        mode_options: List[QuizMode | Literal["exit"]] = ["study", "test", "exit"]
        mode_descriptors = ["Study Mode", "Test Mode", "Exit Program"]

        mode_choice = prompt_for_choice("Select quiz mode:", mode_options, mode_descriptors)

        if mode_choice == "exit":
            break

        run_quiz(mode_choice)

    clear_screen()
    print("Thank you for using the IP Address Classful Networking Quiz!")
    print("Keep practicing to master classful IP addressing concepts.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print("\nQuiz terminated by user.")
        sys.exit(0)
