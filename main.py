def is_prime(number: int) -> bool:
    if number <= 1:
        return False
    if number == 2:
        return True
    if number % 2 == 0:
        return False

    divisor = 3
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 2
    return True


if __name__ == "__main__":
    value = int(input("Enter a number: "))
    if is_prime(value):
        print(f"{value} is a prime number.")
    else:
        print(f"{value} is not a prime number.")
