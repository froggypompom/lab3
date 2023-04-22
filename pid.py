class PIDcontroller:
    def __init__(self, p):
        self.p_p = p[0]
        self.p_d = p[1]
        self.p_i = p[2]
        self.SUM_CTE = 0
    
    def process(self, prev_CTE, CTE):
        self.SUM_CTE += CTE
        Delta_CTE = CTE - prev_CTE
        
        return (-self.p_p * CTE) - (self.p_d * Delta_CTE) - (self.p_i * self.SUM_CTE)
