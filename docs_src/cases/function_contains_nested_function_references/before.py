def a() -> str:
    def b() -> str:
        def d() -> str:
            return "d"

        def e() -> str:
            return d()

        return e()

    def c() -> str:
        return b()

    return c()
