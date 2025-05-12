"""
Classful IPv4 Networking Quiz
Based on CCNA 200-301 Official Cert Guide Library, Second Edition
Chapter 12 Review

Features:
- Study Mode: Tables visible, 90% goal, no timer
- Test Mode: No tables, 100% goal, 10-second timer per question
- UI with colors and visual representations
- Improved error handling and educational feedback
- Spaced repetition for challenging questions
"""

from typing import (
    Optional,
    Tuple,
    Literal,
    Final,
    TypeAlias,
    Union,
    Dict,
    Any,
    List,
    Callable,
    cast,
    Set,
)
from dataclasses import dataclass, field
from enum import Enum, auto
import random
import time
import os
import sys
import threading
import re
import functools
from datetime import datetime

# Try to import colorama for enhanced terminal output
# If not available, create dummy color objects
try:
    from colorama import init, Fore, Style

    init(autoreset=True)  # Initialize colorama
    COLOR_SUPPORT = True
except ImportError:
    # Create dummy color objects if colorama is not installed
    class DummyColors:
        def __getattr__(self, name):
            # Return empty string for any color attribute
            return ""

    Fore = DummyColors()
    Style = DummyColors()
    COLOR_SUPPORT = False
    print("Note: Install colorama for enhanced UI: pip install colorama")

IPAddress: TypeAlias = str
NetworkClass: TypeAlias = (
    Literal["A", "B", "C", "D", "E", "Reserved (0.x.x.x)", "Reserved (127.x.x.x)"]
    | None
)
ClassFilter: TypeAlias = Optional[Literal["A", "B", "C"]]
OctetCount: TypeAlias = Union[int, Literal["N/A - Special class"]]
IPRange: TypeAlias = Tuple[str, str]
QuizMode: TypeAlias = Literal["study", "test"]


class DifficultyLevel(Enum):
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()


IP_PATTERN = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$")

CLASS_RANGES: Final[Dict[str, Tuple[int, int]]] = {
    "A": (1, 126),
    "B": (128, 191),
    "C": (192, 223),
    "D": (224, 239),
    "E": (240, 255),
}

RESERVED_PREFIXES: Final[
    Dict[int, Literal["Reserved (0.x.x.x)", "Reserved (127.x.x.x)"]]
] = {0: "Reserved (0.x.x.x)", 127: "Reserved (127.x.x.x)"}

# Properties from Table 12-2 and 12-3
CLASS_PROPERTIES: Final[Dict[str, Dict[str, Any]]] = {
    "A": {
        "purpose": "Unicast (large networks)",
        "network_octets": 1,
        "host_octets": 3,
        "valid_network_range": "1.0.0.0 - 126.0.0.0",
        "total_networks": 126,  # 2^7 - 2 (0 and 127 are reserved)
        "hosts_per_network": 16777214,  # 2^24 - 2
        "network_bits": 8,
        "host_bits": 24,
        "default_mask": "255.0.0.0",
    },
    "B": {
        "purpose": "Unicast (medium-sized networks)",
        "network_octets": 2,
        "host_octets": 2,
        "valid_network_range": "128.0.0.0 - 191.255.0.0",
        "total_networks": 16384,  # 2^14
        "hosts_per_network": 65534,  # 2^16 - 2
        "network_bits": 16,
        "host_bits": 16,
        "default_mask": "255.255.0.0",
    },
    "C": {
        "purpose": "Unicast (small networks)",
        "network_octets": 3,
        "host_octets": 1,
        "valid_network_range": "192.0.0.0 - 223.255.255.0",
        "total_networks": 2097152,  # 2^21
        "hosts_per_network": 254,  # 2^8 - 2
        "network_bits": 24,
        "host_bits": 8,
        "default_mask": "255.255.255.0",
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
        "default_mask": "N/A",
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
        "default_mask": "N/A",
    },
}


@dataclass(frozen=True)
class IPAddressInfo:
    """Comprehensive data structure for IP address information."""

    ip_address: str
    network_class: NetworkClass
    purpose: str
    network_octets: OctetCount
    host_octets: OctetCount
    network_bits: Union[int, str]
    host_bits: Union[int, str]
    network_id: Union[IPAddress, Literal["N/A - Special class"], None]
    broadcast: Union[IPAddress, Literal["N/A - Special class"], None]
    usable_range: Union[
        IPRange,
        Tuple[Literal["N/A - Special class"], Literal["N/A - Special class"]],
        Tuple[None, None],
    ]
    default_mask: Union[IPAddress, Literal["N/A - Special class"], None]
    valid_network_range: str
    total_networks: Union[int, str]
    hosts_per_network: Union[int, str]


@dataclass
class QuizQuestion:
    """Data structure defining a quiz question."""

    prompt: str
    validator: Callable[[str, Any], bool]
    correct_answer: Any
    feedback: str
    additional_info: str
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    attempts: int = 0
    correct_attempts: int = 0
    last_asked: datetime = field(default_factory=datetime.now)


@dataclass
class SpacedRepetitionStats:
    """Track statistics for spaced repetition learning."""

    question_stats: Dict[int, Tuple[int, int]] = field(
        default_factory=dict
    )  # {question_id: (attempts, correct)}
    difficult_questions: Set[int] = field(default_factory=set)

    def update_stats(self, question_id: int, correct: bool) -> None:
        """Update stats for a question."""
        attempts, correct_count = self.question_stats.get(question_id, (0, 0))
        attempts += 1
        if correct:
            correct_count += 1
        self.question_stats[question_id] = (attempts, correct_count)

        # If success rate is below 60%, mark as difficult
        if attempts >= 2 and (correct_count / attempts) < 0.6:
            self.difficult_questions.add(question_id)
        elif (
            question_id in self.difficult_questions
            and (correct_count / attempts) >= 0.75
        ):
            self.difficult_questions.discard(question_id)


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")

    print(f"{Fore.CYAN}{Style.BRIGHT}\n{'=' * 50}")
    print(f"{Fore.CYAN}{Style.BRIGHT}CLASSFUL IP NETWORKING QUIZ")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 50}\n")


def is_valid_ip(ip_addr: str) -> bool:
    """
    Validate if a string is a properly formatted IPv4 address.

    Args:
        ip_addr: The string to validate

    Returns:
        True if the string is a valid IPv4 address, False otherwise
    """
    match = IP_PATTERN.match(ip_addr)
    if not match:
        return False

    for group in match.groups():
        octet = int(group)
        if octet < 0 or octet > 255:
            return False

    return True


def validate_user_input(input_str: str, valid_options: List[str]) -> bool:
    """
    Validate if user input is in the list of valid options.

    Args:
        input_str: The user input to validate
        valid_options: List of valid options

    Returns:
        True if input is valid, False otherwise
    """
    return input_str.upper() in [
        opt.upper() for opt in valid_options if opt is not None
    ]


@functools.lru_cache(maxsize=128)
def get_ip_address(class_filter: ClassFilter = None) -> IPAddress:
    """
    Generate a random IP address.

    Args:
        class_filter: Generate IP of specific class ('A', 'B', or 'C')
                     If None, generates any valid Class A, B, or C IP

    Returns:
        A randomly generated IP address as a string
    """
    get_ip_address.cache_clear()

    selected_class = class_filter or random.choice(["A", "B", "C"])
    class_range = CLASS_RANGES[selected_class]
    first_octet = random.randint(class_range[0], class_range[1])

    while first_octet in RESERVED_PREFIXES:
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
    if not is_valid_ip(ip_addr):
        return None

    try:
        octets = ip_addr.split(".")
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

    if (
        network_class in CLASS_PROPERTIES
        and property_name in CLASS_PROPERTIES[network_class]
    ):
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


def get_default_mask(
    ip_addr: IPAddress,
) -> Union[IPAddress, Literal["N/A - Special class"], None]:
    """Return the default subnet mask for an IP address."""
    return get_property_for_ip(ip_addr, "default_mask")


def get_valid_network_range(ip_addr: IPAddress) -> str:
    """Get the valid network range for the IP's class."""
    network_range = get_property_for_ip(ip_addr, "valid_network_range")
    return str(network_range) if network_range else "N/A"


def get_network_id(
    ip_addr: IPAddress,
) -> Union[IPAddress, Literal["N/A - Special class"], None]:
    """
    Calculate the network ID of an IP address.

    Args:
        ip_addr: The IP address to analyze

    Returns:
        The network ID as a string, "N/A - Special class" for special cases, or None if invalid
    """
    if not is_valid_ip(ip_addr):
        return None

    network_class = get_network_class(ip_addr)
    network_octets = count_network_octets(ip_addr)

    try:
        octets = ip_addr.split(".")

        if network_class in ["A", "B", "C"] and isinstance(network_octets, int):
            result = octets[:network_octets] + ["0"] * (4 - network_octets)
            return ".".join(result)
        elif network_class in ["D", "E", "Reserved (0.x.x.x)", "Reserved (127.x.x.x)"]:
            return "N/A - Special class"
        else:
            return None
    except Exception as e:
        print(f"Error calculating network ID: {e}")
        return None


def get_broadcast_addr(
    ip_addr: IPAddress,
) -> Union[IPAddress, Literal["N/A - Special class"], None]:
    """
    Calculate the broadcast address of an IP address.

    Args:
        ip_addr: The IP address to analyze

    Returns:
        The broadcast address as a string, "N/A - Special class" for special cases, or None if invalid
    """
    if not is_valid_ip(ip_addr):
        return None

    network_class = get_network_class(ip_addr)
    network_octets = count_network_octets(ip_addr)

    try:
        octets = ip_addr.split(".")

        if network_class in ["A", "B", "C"] and isinstance(network_octets, int):
            result = octets[:network_octets] + ["255"] * (4 - network_octets)
            return ".".join(result)
        elif network_class in ["D", "E", "Reserved (0.x.x.x)", "Reserved (127.x.x.x)"]:
            return "N/A - Special class"
        else:
            return None
    except Exception as e:
        print(f"Error calculating broadcast address: {e}")
        return None


def get_usable_ip_range(
    ip_addr: IPAddress,
) -> Union[
    IPRange,
    Tuple[Literal["N/A - Special class"], Literal["N/A - Special class"]],
    Tuple[None, None],
]:
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

    if (
        network_class in ["A", "B", "C"]
        and isinstance(network_id, str)
        and isinstance(broadcast, str)
    ):
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


@functools.lru_cache(maxsize=64)
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
        "hosts_per_network": get_hosts_per_network(ip_addr),
    }


def get_ip_info(ip_addr: IPAddress) -> IPAddressInfo:
    """
    Create an IPAddressInfo object with all information about an IP address.

    Args:
        ip_addr: The IP address to analyze

    Returns:
        IPAddressInfo object containing all IP information
    """
    info_dict = get_ip_info_dict(ip_addr)
    return IPAddressInfo(**info_dict)


def present_ip_info(ip_addr: IPAddress) -> None:
    """
    Present all information about an IP address.

    Args:
        ip_addr: The IP address to display information about
    """
    ip_info = get_ip_info_dict(ip_addr)

    print(f"\n{Fore.GREEN}IP Address: {Fore.WHITE}{ip_info['ip_address']}")
    print(f"{Fore.GREEN}Class: {Fore.WHITE}{ip_info['network_class']}")
    print(f"{Fore.GREEN}Purpose: {Fore.WHITE}{ip_info['purpose']}")

    if ip_info["network_class"] in ["A", "B", "C"]:
        print(
            f"{Fore.GREEN}Network Octets: {Fore.WHITE}{ip_info['network_octets']} ({ip_info['network_bits']} bits)"
        )
        print(
            f"{Fore.GREEN}Host Octets: {Fore.WHITE}{ip_info['host_octets']} ({ip_info['host_bits']} bits)"
        )
        print(f"{Fore.GREEN}Network ID: {Fore.WHITE}{ip_info['network_id']}")
        print(f"{Fore.GREEN}Broadcast Address: {Fore.WHITE}{ip_info['broadcast']}")
        print(
            f"{Fore.GREEN}Usable IP Range: {Fore.WHITE}{ip_info['usable_range'][0]} to {ip_info['usable_range'][1]}"
        )
        print(f"{Fore.GREEN}Default Subnet Mask: {Fore.WHITE}{ip_info['default_mask']}")
        print(
            f"{Fore.GREEN}Valid Network Range: {Fore.WHITE}{ip_info['valid_network_range']}"
        )
        print(
            f"{Fore.GREEN}Total Networks in this Class: {Fore.WHITE}{ip_info['total_networks']}"
        )
        print(
            f"{Fore.GREEN}Hosts per Network: {Fore.WHITE}{ip_info['hosts_per_network']}"
        )

        print(f"\n{Fore.CYAN}Visual Representation of Address Structure:")
        if ip_info["network_class"] in ["A", "B", "C"]:
            display_visual_bit_division(str(ip_info["network_class"]))
    else:
        print(
            f"{Fore.YELLOW}This is a special class IP address, so standard network/host concepts do not apply."
        )


def display_visual_bit_division(network_class: str) -> None:
    """
    Display a visual representation of network/host bit division.

    Args:
        network_class: The class of network to display
    """
    if network_class not in ["A", "B", "C"]:
        return

    network_bits = int(CLASS_PROPERTIES[network_class]["network_bits"])
    host_bits = int(CLASS_PROPERTIES[network_class]["host_bits"])

    network_part = "1" * network_bits
    host_part = "0" * host_bits

    print(f"{Fore.WHITE}Binary: {Fore.BLUE}{network_part}{Fore.GREEN}{host_part}")
    print(
        f"{Fore.WHITE}        {Fore.BLUE}{'-' * network_bits}{Fore.GREEN}{'-' * host_bits}"
    )
    print(
        f"{Fore.WHITE}        {Fore.BLUE}{'Network' if network_bits > 7 else 'Net'}{' ' * max(0, network_bits - 7)}{Fore.GREEN}{' ' * max(0, host_bits - 4)}{'Host'}"
    )

    octets = []
    bits_remaining = network_bits + host_bits

    for i in range(4):
        if bits_remaining >= 8:
            if network_bits >= 8:
                octets.append((Fore.BLUE, "11111111"))
                network_bits -= 8
            elif network_bits > 0:
                octets.append(
                    (
                        f"{Fore.BLUE}",
                        "1" * network_bits + f"{Fore.GREEN}" + "0" * (8 - network_bits),
                    )
                )
                network_bits = 0
            else:
                octets.append((Fore.GREEN, "00000000"))
            bits_remaining -= 8

    print(f"\n{Fore.WHITE}Dotted Decimal: ", end="")

    for i, (color, bits) in enumerate(octets):
        decimal = int(bits.replace(f"{Fore.GREEN}", "").replace(f"{Fore.BLUE}", ""), 2)
        print(f"{color}{decimal}", end="")
        if i < 3:
            print(f"{Fore.WHITE}.", end="")
    print()


def display_classful_info_tables() -> None:
    """Display the reference tables for classful IP addressing."""
    # Table 12-2
    print(f"\n{Fore.CYAN}IP Address Classes Reference (Table 12-2):")
    print(f"{Fore.WHITE}+{'-' * 7}+{'-' * 21}+{'-' * 31}+")
    print(
        f"{Fore.WHITE}| {Fore.YELLOW}Class{Fore.WHITE} | {Fore.YELLOW}First Octet Values{Fore.WHITE}   | {Fore.YELLOW}Purpose{Fore.WHITE}                       |"
    )
    print(f"{Fore.WHITE}+{'-' * 7}+{'-' * 21}+{'-' * 31}+")

    for class_name in ["A", "B", "C", "D", "E"]:
        class_range = CLASS_RANGES[class_name]
        purpose = CLASS_PROPERTIES[class_name]["purpose"]
        print(
            f"{Fore.WHITE}| {Fore.CYAN}{class_name:<5}{Fore.WHITE} | {Fore.GREEN}{class_range[0]:<3}-{class_range[1]:<15}{Fore.WHITE} | {Fore.GREEN}{purpose:<29}{Fore.WHITE} |"
        )

    print(f"{Fore.WHITE}+{'-' * 7}+{'-' * 21}+{'-' * 31}+")
    print(f"{Fore.YELLOW}Reserved: {Fore.WHITE}0.x.x.x and 127.x.x.x")

    print(f"\n{Fore.CYAN}Key Facts for Classes A, B, and C (Table 12-3):")
    col_width = 20
    print(
        f"{Fore.WHITE}+{'-' * 26}+{'-' * col_width}+{'-' * col_width}+{'-' * col_width}+"
    )
    print(
        f"{Fore.WHITE}| {Fore.YELLOW}{'Property':<24}{Fore.WHITE} | {Fore.YELLOW}{'Class A':<{col_width-2}}{Fore.WHITE} | {Fore.YELLOW}{'Class B':<{col_width-2}}{Fore.WHITE} | {Fore.YELLOW}{'Class C':<{col_width-2}}{Fore.WHITE} |"
    )
    print(
        f"{Fore.WHITE}+{'-' * 26}+{'-' * col_width}+{'-' * col_width}+{'-' * col_width}+"
    )

    def print_property_row(property_name: str, getter: Callable[[str], Any]) -> None:
        values = [getter("A"), getter("B"), getter("C")]

        if "network numbers" in property_name:
            ranges_a = getter("A").split(" - ")
            ranges_b = getter("B").split(" - ")
            ranges_c = getter("C").split(" - ")

            if len(ranges_a) == 2 and len(ranges_b) == 2 and len(ranges_c) == 2:
                first_line = f"{Fore.WHITE}| {Fore.GREEN}{property_name:<24}{Fore.WHITE} | {Fore.CYAN}{ranges_a[0]:<{col_width-2}}{Fore.WHITE} | {Fore.CYAN}{ranges_b[0]:<{col_width-2}}{Fore.WHITE} | {Fore.CYAN}{ranges_c[0]:<{col_width-2}}{Fore.WHITE} |"
                second_line = f"{Fore.WHITE}| {'':<24} | {Fore.CYAN}to {ranges_a[1]:<{col_width-5}}{Fore.WHITE} | {Fore.CYAN}to {ranges_b[1]:<{col_width-5}}{Fore.WHITE} | {Fore.CYAN}to {ranges_c[1]:<{col_width-5}}{Fore.WHITE} |"
                print(first_line)
                print(second_line)
                return

        print(
            f"{Fore.WHITE}| {Fore.GREEN}{property_name:<24}{Fore.WHITE} | {Fore.CYAN}{str(values[0]):<{col_width-2}}{Fore.WHITE} | {Fore.CYAN}{str(values[1]):<{col_width-2}}{Fore.WHITE} | {Fore.CYAN}{str(values[2]):<{col_width-2}}{Fore.WHITE} |"
        )

    properties = [
        ("First octet range", lambda c: f"{CLASS_RANGES[c][0]}-{CLASS_RANGES[c][1]}"),
        ("Valid network numbers", lambda c: CLASS_PROPERTIES[c]["valid_network_range"]),
        ("Total networks", lambda c: CLASS_PROPERTIES[c]["total_networks"]),
        ("Hosts per network", lambda c: CLASS_PROPERTIES[c]["hosts_per_network"]),
        (
            "Network octets (bits)",
            lambda c: f"{CLASS_PROPERTIES[c]['network_octets']} ({CLASS_PROPERTIES[c]['network_bits']})",
        ),
        (
            "Host octets (bits)",
            lambda c: f"{CLASS_PROPERTIES[c]['host_octets']} ({CLASS_PROPERTIES[c]['host_bits']})",
        ),
        ("Default mask", lambda c: CLASS_PROPERTIES[c]["default_mask"]),
    ]

    for prop_name, getter in properties:
        print_property_row(prop_name, getter)

    print(
        f"{Fore.WHITE}+{'-' * 26}+{'-' * col_width}+{'-' * col_width}+{'-' * col_width}+"
    )
    print(
        f"\n{Fore.YELLOW}Note: {Fore.WHITE}Addresses beginning with 0 and 127 are reserved in Class A."
    )
    print(f"There are 126 Class A networks, not 128, due to these reservations.")

    print(f"\n{Fore.CYAN}Visual Representation of Address Structure:")

    for network_class in ["A", "B", "C"]:
        print(f"\n{Fore.YELLOW}Class {network_class}:")
        display_visual_bit_division(network_class)

    print(f"\n{Fore.GREEN}Press Enter to continue...")
    input()


def prompt_for_choice(
    prompt: str, options: List[Any], option_descriptors: List[str]
) -> Any:
    """
    Prompt for a choice from a list of options.

    Args:
        prompt: The prompt to display
        options: List of valid options
        option_descriptors: List of descriptions for each option

    Returns:
        The user's choice
    """
    print(f"\n{Fore.CYAN}{prompt}")
    for i, desc in enumerate(option_descriptors, 1):
        print(f"{Fore.WHITE}{i}. {desc}")

    while True:
        choice = input(
            f"{Fore.GREEN}Enter your choice (1-{len(options)}): {Fore.WHITE}"
        )
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print(
            f"{Fore.RED}Invalid choice. Please enter a number between 1 and {len(options)}."
        )


def ask_quiz_question(
    question_id: int,
    question: QuizQuestion,
    ip_addr: IPAddress,
    mode: QuizMode,
    sr_stats: SpacedRepetitionStats,
    max_attempts: int = 3,
) -> bool:
    """
    Ask a quiz question and validate the answer.

    Args:
        question_id: Unique identifier for this question
        question: The quiz question to ask
        ip_addr: The IP address being analyzed
        mode: The current quiz mode (study or test)
        sr_stats: Spaced repetition statistics
        max_attempts: Maximum number of attempts allowed

    Returns:
        True if answered correctly, False otherwise
    """
    question.attempts += 1
    question.last_asked = datetime.now()

    if mode == "study":
        for attempt in range(1, max_attempts + 1):
            print(f"\n{Fore.CYAN}IP Address: {Fore.WHITE}{ip_addr}")

            difficulty_color = {
                DifficultyLevel.EASY: Fore.GREEN,
                DifficultyLevel.MEDIUM: Fore.YELLOW,
                DifficultyLevel.HARD: Fore.RED,
            }
            print(
                f"{difficulty_color[question.difficulty]}Difficulty: {question.difficulty.name.capitalize()}"
            )

            user_answer = input(
                f"{Fore.YELLOW}Attempt {attempt}/{max_attempts}: {Fore.GREEN}{question.prompt}{Fore.WHITE}"
            )

            if question.validator(user_answer, question.correct_answer):
                print(f"{Fore.GREEN}✓ Correct!")
                question.correct_attempts += 1
                sr_stats.update_stats(question_id, True)
                return True
            else:
                if attempt < max_attempts:
                    print(f"{Fore.RED}✗ Incorrect. Try again.")
                else:
                    print(
                        f"{Fore.RED}✗ The correct answer is {Fore.CYAN}{question.feedback}"
                    )
                    print(f"{Fore.YELLOW}{question.additional_info}")
                    sr_stats.update_stats(question_id, False)
                    return False
    else:  # Test mode
        clear_screen()
        print(f"\n{Fore.YELLOW}[TEST MODE - 10 seconds per question]")
        print(f"\n{Fore.CYAN}IP Address: {Fore.WHITE}{ip_addr}")
        print(f"{Fore.CYAN}Question: {Fore.GREEN}{question.prompt}")

        timer_expired = False
        question_start_time = time.time()

        def timer_function():
            time.sleep(10)
            global timer_expired
            timer_expired = True

        t = threading.Thread(target=timer_function)
        t.daemon = True
        t.start()

        user_answer = input(f"{Fore.GREEN}Your answer: {Fore.WHITE}")

        answer_time = time.time() - question_start_time

        continue_message = f"{Fore.CYAN}Press any key to continue..."

        if timer_expired:
            print(f"{Fore.RED}✗ Time expired! Time taken: {answer_time:.2f} seconds")
            print(f"{Fore.YELLOW}The correct answer is {Fore.CYAN}{question.feedback}")
            print(f"{Fore.YELLOW}{question.additional_info}")
            sr_stats.update_stats(question_id, False)
            _ = input(continue_message)
            return False
        else:
            if question.validator(user_answer, question.correct_answer):
                print(f"{Fore.GREEN}✓ Correct! Time taken: {answer_time:.2f} seconds")
                question.correct_attempts += 1
                sr_stats.update_stats(question_id, True)
                _ = input(continue_message)
                return True
            else:
                print(f"{Fore.RED}✗ Incorrect. Time taken: {answer_time:.2f} seconds")
                print(
                    f"{Fore.YELLOW}The correct answer is {Fore.CYAN}{question.feedback}"
                )
                print(f"{Fore.YELLOW}{question.additional_info}")
                sr_stats.update_stats(question_id, False)
                _ = input(continue_message)
                return False

    return False


def display_progress_bar(completed: int, total: int, width: int = 30) -> None:
    """
    Display a colored progress bar.

    Args:
        completed: Number of completed items
        total: Total number of items
        width: Width of the progress bar
    """
    percentage = completed / total
    filled_width = int(width * percentage)

    # Determine color based on percentage
    if percentage >= 0.8:
        color = Fore.GREEN
    elif percentage >= 0.6:
        color = Fore.YELLOW
    else:
        color = Fore.RED

    bar = "█" * filled_width + "░" * (width - filled_width)
    print(
        f"{Fore.WHITE}Progress: [{color}{bar}{Fore.WHITE}] {percentage:.1%} ({completed}/{total})"
    )


def update_question_difficulty(question: QuizQuestion, correct: bool) -> None:
    """
    Update the difficulty of a question based on performance.

    Args:
        question: The question to update
        correct: Whether the answer was correct
    """
    if correct:
        # If answered correctly, potentially make it easier
        if (
            question.difficulty == DifficultyLevel.HARD
            and question.correct_attempts >= 2
        ):
            question.difficulty = DifficultyLevel.MEDIUM
        elif (
            question.difficulty == DifficultyLevel.MEDIUM
            and question.correct_attempts >= 3
        ):
            question.difficulty = DifficultyLevel.EASY
    else:
        # If answered incorrectly, potentially make it harder
        if question.difficulty == DifficultyLevel.EASY:
            question.difficulty = DifficultyLevel.MEDIUM
        elif question.difficulty == DifficultyLevel.MEDIUM:
            question.difficulty = DifficultyLevel.HARD


def run_quiz(mode: QuizMode) -> None:
    """
    Run the IP address quiz in the specified mode.

    Args:
        mode: The quiz mode (study or test)
    """
    # Initialize spaced repetition stats
    sr_stats = SpacedRepetitionStats()

    goal_percentage = 90 if mode == "study" else 100

    clear_screen()
    print(f"{Fore.WHITE}[{Fore.CYAN}{mode.upper()}{Fore.WHITE} MODE]")
    print(f"{Fore.YELLOW}Goal: {goal_percentage}% correct answers")
    if mode == "test":
        print(f"{Fore.YELLOW}Time limit: 10 seconds per question")
    print()

    if mode == "study":
        display_classful_info_tables()

    total_score = 0
    total_questions = 0

    while True:
        clear_screen()
        print(
            f"{Fore.WHITE}[{Fore.CYAN}{mode.upper()}{Fore.WHITE} MODE] - Goal: {goal_percentage}%"
        )
        if total_questions > 0:
            overall_percentage = (total_score / total_questions) * 100
            print(
                f"{Fore.YELLOW}Current performance: {total_score}/{total_questions} ({overall_percentage:.1f}%)"
            )
            display_progress_bar(total_score, total_questions)
        print()

        options: List[ClassFilter | Literal["view_tables", "end_quiz"]] = [
            "A",
            "B",
            "C",
            None,
        ]
        option_descriptors = [
            f"{Fore.CYAN}Class A",
            f"{Fore.CYAN}Class B",
            f"{Fore.CYAN}Class C",
            f"{Fore.CYAN}Random (A, B, or C)",
        ]

        if mode == "study":
            options.append("view_tables")
            option_descriptors.append(f"{Fore.YELLOW}View Reference Tables")

        options.append("end_quiz")
        option_descriptors.append(f"{Fore.RED}End Quiz")

        class_choice = prompt_for_choice(
            f"Select IP Class for quiz:", options, option_descriptors
        )

        if class_choice == "view_tables":
            clear_screen()
            display_classful_info_tables()
            continue
        elif class_choice == "end_quiz":
            break

        ip_addr = get_ip_address(class_choice)

        clear_screen()
        print(
            f"{Fore.WHITE}[{Fore.CYAN}{mode.upper()}{Fore.WHITE} MODE] - IP Address: {Fore.CYAN}{ip_addr}"
        )
        if mode == "test":
            print(f"{Fore.YELLOW}Time limit: 10 seconds per question")
        print(f"{Fore.WHITE}" + "=" * 50)

        ip_info = get_ip_info_dict(ip_addr)

        if ip_info["network_class"] not in ["A", "B", "C"]:
            print(
                f"\n{Fore.YELLOW}The generated IP {ip_addr} is Class {ip_info['network_class']}."
            )
            print(
                f"{Fore.YELLOW}This is a special class that doesn't apply to standard classful networking questions."
            )
            print(f"{Fore.YELLOW}Let's generate a new IP address for the quiz.")
            time.sleep(2)
            continue

        # Prepare quiz questions
        quiz_questions = [
            # 1. Class identification
            QuizQuestion(
                prompt="What is the class of this IP address? (A/B/C): ",
                validator=lambda ans, correct: ans.upper() == correct,
                correct_answer=ip_info["network_class"],
                feedback=ip_info["network_class"],
                additional_info=f"Class A: {CLASS_RANGES['A'][0]}-{CLASS_RANGES['A'][1]}, Class B: {CLASS_RANGES['B'][0]}-{CLASS_RANGES['B'][1]}, Class C: {CLASS_RANGES['C'][0]}-{CLASS_RANGES['C'][1]}",
            ),
            # 2. Network Purpose
            QuizQuestion(
                prompt="What is the purpose of this IP address class? (e.g., Unicast, Multicast): ",
                validator=lambda ans, correct: ans.lower() in correct.lower(),
                correct_answer=ip_info["purpose"],
                feedback=ip_info["purpose"],
                additional_info="Class A: Unicast (large networks)\nClass B: Unicast (medium-sized networks)\nClass C: Unicast (small networks)",
            ),
            # 3. Network Octets
            QuizQuestion(
                prompt="How many network octets does this IP address have? (1-3): ",
                validator=lambda ans, correct: ans.isdigit() and int(ans) == correct,
                correct_answer=ip_info["network_octets"],
                feedback=str(ip_info["network_octets"]) + " network octets",
                additional_info="Class A: 1 network octet, Class B: 2 network octets, Class C: 3 network octets",
            ),
            # 4. Host Octets
            QuizQuestion(
                prompt="How many host octets does this IP address have? (1-3): ",
                validator=lambda ans, correct: ans.isdigit() and int(ans) == correct,
                correct_answer=ip_info["host_octets"],
                feedback=str(ip_info["host_octets"]) + " host octets",
                additional_info="Class A: 3 host octets, Class B: 2 host octets, Class C: 1 host octet",
            ),
            # 5. Network Bits
            QuizQuestion(
                prompt="How many bits are in the network part of this IP address? (8/16/24): ",
                validator=lambda ans, correct: ans.isdigit() and int(ans) == correct,
                correct_answer=ip_info["network_bits"],
                feedback=str(ip_info["network_bits"]) + " bits",
                additional_info="Class A: 8 bits, Class B: 16 bits, Class C: 24 bits",
            ),
            # 6. Host Bits
            QuizQuestion(
                prompt="How many bits are in the host part of this IP address? (8/16/24): ",
                validator=lambda ans, correct: ans.isdigit() and int(ans) == correct,
                correct_answer=ip_info["host_bits"],
                feedback=str(ip_info["host_bits"]) + " bits",
                additional_info="Class A: 24 bits, Class B: 16 bits, Class C: 8 bits",
            ),
            # 7. Hosts per Network
            QuizQuestion(
                prompt="How many hosts per network does this IP address class support?\nOptions: A) 254   B) 65,534   C) 16,777,214\nEnter A, B, or C: ",
                validator=lambda ans, correct: ans.upper() == correct,
                correct_answer={"A": "C", "B": "B", "C": "A"}[ip_info["network_class"]],
                feedback={"A": "C: 16,777,214", "B": "B: 65,534", "C": "A: 254"}[
                    ip_info["network_class"]
                ],
                additional_info="Class A: 2^24 - 2 = 16,777,214 hosts\nClass B: 2^16 - 2 = 65,534 hosts\nClass C: 2^8 - 2 = 254 hosts",
            ),
            # 8. Network ID
            QuizQuestion(
                prompt="What is the network ID of this IP address?: ",
                validator=lambda ans, correct: ans.strip() == str(correct).strip(),
                correct_answer=ip_info["network_id"],
                feedback=ip_info["network_id"],
                additional_info="For network ID, keep the network octets and set all host octets to 0.",
            ),
            # 9. Broadcast Address
            QuizQuestion(
                prompt="What is the broadcast address of this IP address?: ",
                validator=lambda ans, correct: ans.strip() == str(correct).strip(),
                correct_answer=ip_info["broadcast"],
                feedback=ip_info["broadcast"],
                additional_info="For broadcast address, keep the network octets and set all host octets to 255.",
            ),
            # 10. Default Subnet Mask
            QuizQuestion(
                prompt="What is the default subnet mask for this IP address?: ",
                validator=lambda ans, correct: ans.strip() == str(correct).strip(),
                correct_answer=ip_info["default_mask"],
                feedback=ip_info["default_mask"],
                additional_info="Class A: 255.0.0.0, Class B: 255.255.0.0, Class C: 255.255.255.0",
            ),
        ]

        # Prioritize difficult questions if in study mode
        if mode == "study" and sr_stats.difficult_questions:
            # Sort questions to prioritize difficult ones
            quiz_questions.sort(
                key=lambda q: q.difficulty == DifficultyLevel.HARD
                and quiz_questions.index(q) in sr_stats.difficult_questions,
                reverse=True,
            )

        current_score = 0
        for i, question in enumerate(quiz_questions):
            # Update question difficulty based on stats
            question_id = i
            if question_id in sr_stats.question_stats:
                attempts, correct = sr_stats.question_stats[question_id]
                if attempts > 0:
                    success_rate = correct / attempts
                    if success_rate < 0.5:
                        question.difficulty = DifficultyLevel.HARD
                    elif success_rate < 0.8:
                        question.difficulty = DifficultyLevel.MEDIUM
                    else:
                        question.difficulty = DifficultyLevel.EASY

            if ask_quiz_question(question_id, question, ip_addr, mode, sr_stats):
                current_score += 1
                # Update question difficulty
                update_question_difficulty(question, True)
            else:
                # Update question difficulty
                update_question_difficulty(question, False)

        max_score = len(quiz_questions)
        current_percentage = (current_score / max_score) * 100

        clear_screen()
        print(
            f"{Fore.WHITE}[{Fore.CYAN}{mode.upper()}{Fore.WHITE} MODE] - IP Quiz Results"
        )
        print(f"{Fore.WHITE}" + "=" * 50)
        print(f"{Fore.CYAN}IP Address: {Fore.WHITE}{ip_addr}")
        print(
            f"{Fore.YELLOW}Your score: {current_score}/{max_score} ({current_percentage:.1f}%)"
        )

        if current_percentage >= goal_percentage:
            print(
                f"{Fore.GREEN}✓ Goal achieved! You scored {current_percentage:.1f}% (goal: {goal_percentage}%)"
            )
        else:
            print(
                f"{Fore.RED}✗ Goal not met. You scored {current_percentage:.1f}% (goal: {goal_percentage}%)"
            )

        total_score += current_score
        total_questions += max_score

        overall_percentage = (
            (total_score / total_questions) * 100 if total_questions > 0 else 0
        )
        print(f"\n{Fore.CYAN}Overall performance:")
        print(
            f"{Fore.WHITE}{total_score}/{total_questions} ({overall_percentage:.1f}%)"
        )
        display_progress_bar(total_score, total_questions)

        # Display information about difficult questions
        difficult_questions_list = list(sr_stats.difficult_questions)
        if difficult_questions_list:
            print(f"\n{Fore.YELLOW}Areas to focus on:")
            for qid in difficult_questions_list:
                attempts, correct = sr_stats.question_stats.get(qid, (0, 0))
                if attempts > 0:  # Only show questions that were attempted
                    success_rate = (correct / attempts) * 100
                    question_type = "Question type #" + str(qid + 1)
                    print(
                        f"{Fore.RED}- {question_type} (Success rate: {success_rate:.1f}%)"
                    )

        if mode == "study":
            print(
                f"\n{Fore.CYAN}Here's the complete information about this IP address:"
            )
            present_ip_info(ip_addr)

            # Visual representation of address structure
            print(f"\n{Fore.CYAN}Visual Representation of IP Address Structure:")
            # Convert network_class from NetworkClass type to str for display
            class_str = str(ip_info["network_class"])
            if class_str in ["A", "B", "C"]:
                display_visual_bit_division(class_str)

        print(f"\n{Fore.GREEN}Press Enter to continue...")
        input()

    if total_questions > 0:
        final_percentage = (total_score / total_questions) * 100

        clear_screen()
        print(f"{Fore.CYAN}Final Quiz Statistics [{mode.upper()} MODE]")
        print(f"{Fore.WHITE}" + "=" * 50)
        print(f"{Fore.YELLOW}Total Questions: {total_questions}")
        print(f"{Fore.YELLOW}Correct Answers: {total_score}")
        print(f"{Fore.YELLOW}Final Score: {final_percentage:.1f}%")
        display_progress_bar(total_score, total_questions)

        if final_percentage >= goal_percentage:
            print(
                f"\n{Fore.GREEN}✓ OVERALL GOAL ACHIEVED! You scored {final_percentage:.1f}% (goal: {goal_percentage}%)"
            )
        else:
            print(
                f"\n{Fore.RED}✗ OVERALL GOAL NOT MET. You scored {final_percentage:.1f}% (goal: {goal_percentage}%)"
            )

        if final_percentage >= 90:
            print(f"\n{Fore.GREEN}Excellent! You've mastered classful IP addressing.")
        elif final_percentage >= 75:
            print(
                f"\n{Fore.YELLOW}Good job! You have a solid understanding of classful IP addressing."
            )
        elif final_percentage >= 60:
            print(
                f"\n{Fore.YELLOW}Not bad! With a bit more practice, you'll master these concepts."
            )
        else:
            print(
                f"\n{Fore.RED}Keep practicing! Classful IP addressing takes time to master."
            )

        # Display areas for improvement
        difficult_questions_list = list(sr_stats.difficult_questions)
        if difficult_questions_list:
            print(f"\n{Fore.YELLOW}Areas for improvement:")
            # Only reference questions that were actually asked in this session
            for qid in difficult_questions_list:
                attempts, correct = sr_stats.question_stats.get(qid, (0, 0))
                if attempts > 0:  # Only show questions that were attempted
                    print(
                        f"{Fore.RED}- Question type #{qid+1} (Success rate: {(correct/attempts)*100:.1f}%)"
                    )

        print(f"\n{Fore.GREEN}Press Enter to return to main menu...")
        input()
    else:
        print(f"\n{Fore.YELLOW}No questions were answered.")
        time.sleep(2)


def show_welcome_message() -> None:
    """Display a welcome message with program information."""
    clear_screen()
    print(f"{Fore.CYAN}{Style.BRIGHT}Welcome to the Classful IPv4 Networking Quiz!")
    print(
        f"{Fore.WHITE}This program will help you learn and master classful IP addressing concepts."
    )
    print(f"{Fore.WHITE}Based on Chapter 12 of the CCNA 200-301 Official Cert Guide.\n")

    print(f"{Fore.YELLOW}Program Features:")
    print(f"{Fore.GREEN}• Interactive quizzes with immediate feedback")
    print(f"{Fore.GREEN}• Visual representations of network/host divisions")
    print(f"{Fore.GREEN}• Reference tables matching the CCNA certification book")
    print(f"{Fore.GREEN}• Spaced repetition system to focus on challenging concepts")
    print(f"{Fore.GREEN}• Two quiz modes: Study and Test\n")

    print(f"{Fore.YELLOW}Quiz Modes:")
    print(
        f"{Fore.WHITE}1. {Fore.CYAN}Study Mode: {Fore.WHITE}Reference tables visible, 90% goal, no timer"
    )
    print(
        f"{Fore.WHITE}2. {Fore.CYAN}Test Mode: {Fore.WHITE}No tables, 100% goal, 10-second timer per question\n"
    )

    input(f"{Fore.GREEN}Press Enter to continue...")


def main() -> None:
    """Run the IP address educational quiz program."""
    show_welcome_message()

    while True:
        clear_screen()
        print(f"{Fore.CYAN}{Style.BRIGHT}Classful IPv4 Networking Quiz")
        print(f"{Fore.WHITE}" + "=" * 50 + "\n")

        mode_options: List[QuizMode | Literal["exit"]] = ["study", "test", "exit"]
        mode_descriptors = [
            f"{Fore.CYAN}Study Mode {Fore.WHITE}- Learn at your own pace with reference tables",
            f"{Fore.CYAN}Test Mode {Fore.WHITE}- Challenge yourself with timed questions",
            f"{Fore.RED}Exit Program",
        ]

        mode_choice = prompt_for_choice(
            "Select quiz mode:", mode_options, mode_descriptors
        )

        if mode_choice == "exit":
            break

        run_quiz(mode_choice)

    clear_screen()
    print(
        f"{Fore.CYAN}{Style.BRIGHT}Thank you for using the Classful IPv4 Networking Quiz!"
    )
    print(f"{Fore.GREEN}Keep practicing to master classful IP addressing concepts.")
    print(f"{Fore.GREEN}Good luck with your CCNA exam!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print(f"\n{Fore.YELLOW}Quiz terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}An error occurred: {e}")
        sys.exit(1)
