import re


def process_file(input_file):
    # Initialize data storage for each method
    data = {
        'RES': [],
        'DP': [],
        'DPLL': []
    }
    data2 = {
        'RES': [],
        'DP': [],
        'DPLL': []
    }

    with open(input_file, 'r') as f:
        for line in f:
            # Skip empty lines
            if not line.strip():
                continue

            # Extract components using regex
            match = re.match(
                r'^\s*([A-Z]+)\s*&.*?&\s*(\d+)\s*&\s*\d+\s*&\s*([\d.]+)\s*&\s*([\d.]+)\s*&\s*(True|False)\s*&\s*([\d.]+)\s*\\\\',
                line.strip()
            )
            if match:
                method = match.group(1)
                variables = match.group(2)
                time = match.group(3)
                memory = match.group(4)
                result = match.group(5)
                ratio = match.group(6)
                data[method].append(f"{ratio},{result},{method}")
                data2[method].append(f"{variables},{memory},{method}")
    # Write to separate files
    for method in ['RES', 'DP', 'DPLL']:
        with open(f'{method}_output,time.csv', 'w') as f:
            f.write("variables,time,method\n")
            f.write("\n".join(data[method]))
        with open(f'{method}_output,mem.csv', 'w') as f:
            f.write("variables,memory,method\n")
            f.write("\n".join(data2[method]))

    print("Files created successfully:")
    print("- RES_output,time.csv")
    print("- DP_output,time.csv")
    print("- DPLL_output,time.csv")

    print("- RES_output,mem.csv")
    print("- DP_output,mem.csv")
    print("- DPLL_output,mem.csv")


# Example usage:
if __name__ == "__main__":
    input_filename = "input_data.txt"  # Change this to your input file name
    process_file(input_filename)