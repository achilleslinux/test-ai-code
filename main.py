
def perform_division():
    try:
        number = int(10)
        divisor = int(5)

        if divisor == 0:
            print("Divisor cannot be zero.")
            return

        count = 0
        original = number

        while number % divisor == 0:
            number //= divisor
            count += 1
            print(f"Step {count}: Result = {number}")

        if count == 0:
            print(f"{original} is not divisible by {divisor}.")
        else:
            print(f"Final result after {count} divisions: {number}")

    except ValueError:
        print("Please enter valid integers.")

if __name__ == "__main__":
    perform_division()
    ##
    



