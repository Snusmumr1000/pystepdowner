from compute import add, mul, pow, sub


def main() -> None:
    a = 2
    b = 3
    c = add(a, b)  # 5
    m = add(1, 2)
    d = mul(a, b)  # 6
    e = sub(a, b)  # -1
    f = pow(a, b)  # 8

    print(c)
    print(d)
    print(e)
    print(f)
    print(m)


if __name__ == "__main__":
    main()
