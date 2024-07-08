class Pawn:
    def __init__(self, id) -> None:
        self.id = id
        self.first_name = ""
        self.last_name = ""
        self.nick_name = ""
        self.parents = []
        self.gender = ""
        self.age = 0

    def getName(self):
        return self.nick_name
