class TemperatureAgent:
    def __init__(self):
        self.prev_action = None
        self.heater_status = "OFF"
        self.threshold = 22
    
    def get_percept(self, temp):
        if temp < self.threshold:
            return "cold"
        else:
            return "warm"
    
    def decide_action(self, current_temp):
        percept = self.get_percept(current_temp)
        
        if percept == "cold":
            if self.heater_status != "ON":
                action = "Heater ON"
                self.heater_status = "ON"
            else:
                action = "Already ON"
        else:
            if self.heater_status != "OFF":
                action = "Heater OFF"
                self.heater_status = "OFF"
            else:
                action = "Already OFF"
        
        self.prev_action = action
        return action


def main():
    print("Temperature Controller")
    print("-" * 30)
    
    agent = TemperatureAgent()
    
    test_temps = [18, 15, 25, 24, 19, 20, 26, 17]
    
    print("Threshold:", agent.threshold, "C")
    print()
    
    for temp in test_temps:
        print("Temp:", temp, "C")
        action = agent.decide_action(temp)
        print("Action:", action)
        print("Status:", agent.heater_status)
        print()
    
    print("Done")


if __name__ == "__main__":
    main()
