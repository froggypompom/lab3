class PIDcontroller:
    def __init__(self, p):
        #self.p_p = 0.02
        #self.p_p = [0.02, 1, 0.0001]
        self.p_p = p
        self.last_CTE = None
        self.I = 0

    def process(self, CTE):

        if self.last_CTE is not None:
            D = CTE - self.last_CTE
        else:
            D = 0
        
        self.I += CTE

        self.last_CTE = CTE
        return (-self.p_p[0] * CTE) - (self.p_p[1] * D) - ( self.p_p[2] * self.I )

