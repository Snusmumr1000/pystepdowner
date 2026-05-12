def a() -> str:
    def c() -> str:
        return b()

    def b() -> str:
        def e() -> str:
            return d()

        def d() -> str:
            return "d"

        return e()

    return c()
