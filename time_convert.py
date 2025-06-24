def time_to_raw(time_str: str) -> int:
    """
    Convert lap time from 'M:SS.mmm' format to 1/10000 seconds as an integer.
    Example: '1:12.383' -> 723830
    """
    try:
        mins, rest = time_str.split(":")
        secs, millis = rest.split(".")
        total_ms = (int(mins) * 60 + int(secs)) * 1000 + int(millis)
        return total_ms * 10  # convert to 1/10000 seconds
    except ValueError:
        raise ValueError("Input must be in the format M:SS.mmm")

# Get input from the user
if __name__ == "__main__":
    user_input = input("Enter lap time (M:SS.mmm): ")
    try:
        raw_time = time_to_raw(user_input)
        print(f"Raw time in 1/10000s: {raw_time}")
    except ValueError as e:
        print(e)