import time
import random
import json
import os
from typing import Dict, List, Tuple
from collections import defaultdict

class Infrastructure:
    def __init__(self):
        self.power_grid = set()
        self.road_network = set()
        self.water_grid = set()
        
    def to_dict(self) -> dict:
        return {
            'power_grid': list(self.power_grid),
            'road_network': list(self.road_network),
            'water_grid': list(self.water_grid)
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        infrastructure = cls()
        infrastructure.power_grid = set(tuple(x) for x in data['power_grid'])
        infrastructure.road_network = set(tuple(x) for x in data['road_network'])
        infrastructure.water_grid = set(tuple(x) for x in data['water_grid'])
        return infrastructure
        
    def add_connection(self, x: int, y: int, infra_type: str):
        if infra_type == 'POWER':
            self.power_grid.add((x, y))
        elif infra_type == 'ROAD':
            self.road_network.add((x, y))
        elif infra_type == 'WATER':
            self.water_grid.add((x, y))
            
    def remove_connection(self, x: int, y: int, infra_type: str):
        if infra_type == 'POWER':
            self.power_grid.discard((x, y))
        elif infra_type == 'ROAD':
            self.road_network.discard((x, y))
        elif infra_type == 'WATER':
            self.water_grid.discard((x, y))
            
    def has_connection(self, x: int, y: int, infra_type: str) -> bool:
        if infra_type == 'POWER':
            return (x, y) in self.power_grid
        elif infra_type == 'ROAD':
            return (x, y) in self.road_network
        elif infra_type == 'WATER':
            return (x, y) in self.water_grid
        return False

class Economy:
    def __init__(self):
        self.employment_rate = 0.95
        self.gdp = 0
        self.inflation_rate = 0.02
        self.business_confidence = 0.75
        self.sectors = {
            'R': {'jobs': 0, 'income': 0},
            'C': {'jobs': 0, 'income': 0},
            'I': {'jobs': 0, 'income': 0}
        }
    
    def to_dict(self) -> dict:
        return {
            'employment_rate': self.employment_rate,
            'gdp': self.gdp,
            'inflation_rate': self.inflation_rate,
            'business_confidence': self.business_confidence,
            'sectors': self.sectors
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        economy = cls()
        economy.employment_rate = data['employment_rate']
        economy.gdp = data['gdp']
        economy.inflation_rate = data['inflation_rate']
        economy.business_confidence = data['business_confidence']
        economy.sectors = data['sectors']
        return economy
        
    def update_economy(self, building_counts: Dict[str, int], population: int):
        # Update jobs and income for each sector
        self.sectors['R']['jobs'] = building_counts['R'] * 5
        self.sectors['C']['jobs'] = building_counts['C'] * 20
        self.sectors['I']['jobs'] = building_counts['I'] * 50
        
        self.sectors['R']['income'] = building_counts['R'] * 1000
        self.sectors['C']['income'] = building_counts['C'] * 2000 * self.business_confidence
        self.sectors['I']['income'] = building_counts['I'] * 5000 * self.business_confidence
        
        self.gdp = sum(sector['income'] for sector in self.sectors.values())
        
        total_jobs = sum(sector['jobs'] for sector in self.sectors.values())
        self.employment_rate = min(1.0, total_jobs / max(population, 1))
        
        self.business_confidence = min(1.0, (self.employment_rate + 0.5) / 1.5)
        
        return self.calculate_tax_income(population)
    
    def calculate_tax_income(self, population: int) -> float:
        residential_tax = self.sectors['R']['income'] * 0.05
        commercial_tax = self.sectors['C']['income'] * 0.08
        industrial_tax = self.sectors['I']['income'] * 0.12
        return residential_tax + commercial_tax + industrial_tax

class City:
    def __init__(self, name: str):
        self.name = name
        self.money = 10000
        self.population = 0
        self.happiness = 100
        self.grid_size = 10
        self.grid = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.infrastructure = Infrastructure()
        self.economy = Economy()
        self.tax_rate = 10
        self.buildings = []
        self.time_elapsed = 0
        self.maintenance_costs = defaultdict(float)

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'money': self.money,
            'population': self.population,
            'happiness': self.happiness,
            'grid_size': self.grid_size,
            'grid': self.grid,
            'infrastructure': self.infrastructure.to_dict(),
            'economy': self.economy.to_dict(),
            'tax_rate': self.tax_rate,
            'buildings': self.buildings,
            'time_elapsed': self.time_elapsed,
            'maintenance_costs': dict(self.maintenance_costs)
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        city = cls(data['name'])
        city.money = data['money']
        city.population = data['population']
        city.happiness = data['happiness']
        city.grid_size = data['grid_size']
        city.grid = data['grid']
        city.infrastructure = Infrastructure.from_dict(data['infrastructure'])
        city.economy = Economy.from_dict(data['economy'])
        city.tax_rate = data['tax_rate']
        city.buildings = data['buildings']
        city.time_elapsed = data['time_elapsed']
        city.maintenance_costs = defaultdict(float, data['maintenance_costs'])
        return city

    def get_building_cost(self, building_type: str) -> int:
        costs = {
            'R': 1000,   # Residential
            'C': 2000,   # Commercial
            'I': 3000,   # Industrial
            'P': 1500,   # Park
            'H': 5000,   # Hospital
            'S': 3000,   # School
            'F': 2500,   # Fire Station
            'POWER': 500,  # Power line
            'ROAD': 300,   # Road
            'WATER': 400   # Water pipe
        }
        return costs.get(building_type, 0)

    def get_building_name(self, code: str) -> str:
        names = {
            'R': 'Residential Zone',
            'C': 'Commercial Zone',
            'I': 'Industrial Zone',
            'P': 'Park',
            'H': 'Hospital',
            'S': 'School',
            'F': 'Fire Station',
            'POWER': 'Power Line',
            'ROAD': 'Road',
            'WATER': 'Water Pipe',
            None: 'Empty'
        }
        return names.get(code, 'Unknown')

    def is_connected(self, x: int, y: int) -> bool:
        # Check if location has all required infrastructure
        has_power = self.infrastructure.has_connection(x, y, 'POWER')
        has_road = self.infrastructure.has_connection(x, y, 'ROAD')
        has_water = self.infrastructure.has_connection(x, y, 'WATER')
        return has_power and has_road and has_water

    def build(self, x: int, y: int, building_type: str) -> bool:
        if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
            print("Invalid coordinates!")
            return False

        if self.grid[y][x] is not None and building_type not in ['POWER', 'ROAD', 'WATER']:
            print("This spot is already occupied!")
            return False

        cost = self.get_building_cost(building_type)
        if self.money < cost:
            print("Not enough money!")
            return False

        if building_type in ['POWER', 'ROAD', 'WATER']:
            self.infrastructure.add_connection(x, y, building_type)
        else:
            self.grid[y][x] = building_type
            self.buildings.append((x, y, building_type))
            
        self.money -= cost
        self.maintenance_costs[building_type] += cost * 0.01  # 1% maintenance cost
        self.update_city_stats()
        return True

    def update_city_stats(self):
        # Count buildings
        building_counts = {'R': 0, 'C': 0, 'I': 0, 'P': 0, 'H': 0, 'S': 0, 'F': 0}
        for row in self.grid:
            for cell in row:
                if cell:
                    building_counts[cell] += 1

        # Update population based on residential zones and infrastructure
        base_population = building_counts['R'] * 100
        infrastructure_modifier = sum(1 for x in range(self.grid_size) 
                                   for y in range(self.grid_size) 
                                   if self.is_connected(x, y)) / (self.grid_size * self.grid_size)
        self.population = int(base_population * (0.5 + 0.5 * infrastructure_modifier))

        # Calculate happiness based on various factors
        self.happiness = min(100, 50 + 
                           building_counts['P'] * 5 +     # Parks
                           building_counts['H'] * 10 +    # Hospitals
                           building_counts['S'] * 7 +     # Schools
                           infrastructure_modifier * 20 -  # Infrastructure
                           max(0, self.tax_rate - 10) * 2)  # Tax penalty

        # Update economy and collect taxes
        tax_income = self.economy.update_economy(building_counts, self.population)
        self.money += tax_income * (self.tax_rate / 100)

        # Apply maintenance costs
        total_maintenance = sum(self.maintenance_costs.values())
        self.money -= total_maintenance

    def simulate_turn(self):
        self.time_elapsed += 1
        self.update_city_stats()
        
        # Random events with economic impact
        if random.random() < 0.1:  # 10% chance of event
            events = [
                ("Economic boom! Businesses are thriving.", 
                 lambda: self.apply_economic_event(1000, 0.1, 0.05)),
                ("Recession hits the city.", 
                 lambda: self.apply_economic_event(-500, -0.05, -0.1)),
                ("New technology brings efficiency improvements.", 
                 lambda: self.reduce_maintenance_costs(0.9)),
                ("Infrastructure aging causes increased maintenance.", 
                 lambda: self.increase_maintenance_costs(1.1))
            ]
            event, effect = random.choice(events)
            print(f"\nEvent: {event}")
            effect()

    def apply_economic_event(self, money_change: int, employment_change: float, confidence_change: float):
        self.money += money_change
        self.economy.employment_rate = max(0.1, min(1.0, self.economy.employment_rate + employment_change))
        self.economy.business_confidence = max(0.1, min(1.0, self.economy.business_confidence + confidence_change))

    def reduce_maintenance_costs(self, factor: float):
        for building_type in self.maintenance_costs:
            self.maintenance_costs[building_type] *= factor

    def increase_maintenance_costs(self, factor: float):
        for building_type in self.maintenance_costs:
            self.maintenance_costs[building_type] *= factor

def display_grid(city: City):
    print("\n  " + " ".join(str(i) for i in range(city.grid_size)))
    for y in range(city.grid_size):
        print(f"{y}", end=" ")
        for x in range(city.grid_size):
            cell = city.grid[y][x]
            infra = []
            if city.infrastructure.has_connection(x, y, 'POWER'):
                infra.append('P')
            if city.infrastructure.has_connection(x, y, 'ROAD'):
                infra.append('R')
            if city.infrastructure.has_connection(x, y, 'WATER'):
                infra.append('W')
            
            if cell:
                print(cell, end=" ")
            elif infra:
                print('+', end=" ")  # Show infrastructure with +
            else:
                print('.', end=" ")
        print()

def display_stats(city: City):
    print(f"\n=== {city.name} Statistics ===")
    print(f"Money: ${city.money:,.2f}")
    print(f"Population: {city.population:,}")
    print(f"Happiness: {city.happiness}%")
    print(f"Tax Rate: {city.tax_rate}%")
    print(f"Employment Rate: {city.economy.employment_rate*100:.1f}%")
    print(f"Business Confidence: {city.economy.business_confidence*100:.1f}%")
    print(f"GDP: ${city.economy.gdp:,.2f}")
    print(f"Time Elapsed: {city.time_elapsed} turns")

def display_help():
    print("\nAvailable Commands:")
    print("build x y type - Build at coordinates (x,y). Types:")
    print("                 R(esidential), C(ommercial), I(ndustrial)")
    print("                 P(ark), H(ospital), S(chool), F(ire Station)")
    print("                 POWER, ROAD, WATER (infrastructure)")
    print("demolish x y   - Remove building at coordinates (x,y)")
    print("map           - Display city map")
    print("stats        - Display city statistics")
    print("audit        - Display detailed city report")
    print("tax rate     - Set tax rate (0-20)")
    print("economy      - Display detailed economic report")
    print("help         - Show this help message")
    print("exit         - Exit game")

def audit_city(city: City):
    print(f"\n=== Detailed Audit of {city.name} ===")
    
    # Building counts and costs
    building_counts = {'R': 0, 'C': 0, 'I': 0, 'P': 0, 'H': 0, 'S': 0, 'F': 0}
    total_investment = 0
    for row in city.grid:
        for cell in row:
            if cell:
                building_counts[cell] += 1
                total_investment += city.get_building_cost(cell)

    # Infrastructure coverage
    total_cells = city.grid_size * city.grid_size
    power_coverage = len(city.infrastructure.power_grid) / total_cells * 100
    road_coverage = len(city.infrastructure.road_network) / total_cells * 100
    water_coverage = len(city.infrastructure.water_grid) / total_cells * 100

    print("\nBuilding Inventory:")
    for building_type, count in building_counts.items():
        if count > 0:
            print(f"{city.get_building_name(building_type)}: {count}")

    print(f"\nInfrastructure Coverage:")
    print(f"Power Grid: {power_coverage:.1f}%")
    print(f"Road Network: {road_coverage:.1f}%")
    print(f"Water System: {water_coverage:.1f}%")

    print(f"\nFinancial Summary:")
    print(f"Total Infrastructure Investment: ${total_investment:,.2f}")
    print(f"Current Liquid Assets: ${city.money:,.2f}")
    print(f"Monthly Maintenance Costs: ${sum(city.maintenance_costs.values()):,.2f}")
    
    # Economic analysis
    print("\nEconomic Analysis:")
    print(f"GDP per Capita: ${city.economy.gdp/max(city.population, 1):,.2f}")
    for sector in ['R', 'C', 'I']:
        print(f"{city.get_building_name(sector)} sector:")
        print(f"  Jobs: {city.economy.sectors[sector]['jobs']:,}")
        print(f"  Income: ${city.economy.sectors[sector]['income']:,.2f}")

def display_economy(city: City):
    print(f"\n=== Economic Report for {city.name} ===")
    print(f"\nMacroeconomic Indicators:")
    print(f"GDP: ${city.economy.gdp:,.2f}")
    print(f"GDP per Capita: ${city.economy.gdp/max(city.population, 1):,.2f}")
    print(f"Employment Rate: {city.economy.employment_rate*100:.1f}%")
    print(f"Business Confidence: {city.economy.business_confidence*100:.1f}%")
    print(f"Inflation Rate: {city.economy.inflation_rate*100:.1f}%")

    print("\nSector Analysis:")
    total_jobs = sum(sector['jobs'] for sector in city.economy.sectors.values())
    total_income = sum(sector['income'] for sector in city.economy.sectors.values())
    
    for sector_code, sector_data in city.economy.sectors.items():
        sector_name = city.get_building_name(sector_code)
        jobs_percentage = (sector_data['jobs'] / max(total_jobs, 1)) * 100
        income_percentage = (sector_data['income'] / max(total_income, 1)) * 100
        
        print(f"\n{sector_name}:")
        print(f"  Jobs: {sector_data['jobs']:,} ({jobs_percentage:.1f}% of workforce)")
        print(f"  Income: ${sector_data['income']:,.2f} ({income_percentage:.1f}% of economy)")
        print(f"  Revenue per Job: ${sector_data['income']/max(sector_data['jobs'], 1):,.2f}")

    print("\nFiscal Analysis:")
    monthly_tax_income = city.economy.calculate_tax_income(city.population) * (city.tax_rate / 100)
    total_maintenance = sum(city.maintenance_costs.values())
    net_income = monthly_tax_income - total_maintenance
    
    print(f"Monthly Tax Revenue: ${monthly_tax_income:,.2f}")
    print(f"Monthly Maintenance Costs: ${total_maintenance:,.2f}")
    print(f"Net Monthly Income: ${net_income:,.2f}")
    
    print("\nGrowth Metrics:")
    tax_burden = (monthly_tax_income / max(city.economy.gdp, 1)) * 100
    jobs_per_resident = total_jobs / max(city.population, 1)
    print(f"Tax Burden: {tax_burden:.1f}% of GDP")
    print(f"Jobs per Resident: {jobs_per_resident:.2f}")
    print(f"City Wealth Rating: {'Wealthy' if city.money > 100000 else 'Stable' if city.money > 50000 else 'Growing' if city.money > 10000 else 'Struggling'}")

def save_game(city: City, filename: str):
    """Save the current game state to a file."""
    save_data = city.to_dict()
    
    # Ensure the saves directory exists
    os.makedirs('saves', exist_ok=True)
    
    # Save to file
    filepath = os.path.join('saves', f"{filename}.json")
    with open(filepath, 'w') as f:
        json.dump(save_data, f)
    print(f"\nGame saved successfully to {filepath}")

def load_game(filename: str) -> City:
    """Load a game state from a file."""
    filepath = os.path.join('saves', f"{filename}.json")
    try:
        with open(filepath, 'r') as f:
            save_data = json.load(f)
        return City.from_dict(save_data)
    except FileNotFoundError:
        print(f"No save file found at {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error reading save file at {filepath}")
        return None

def list_saved_games():
    """List all available save files."""
    if not os.path.exists('saves'):
        print("No saved games found.")
        return []
    
    saves = [f[:-5] for f in os.listdir('saves') if f.endswith('.json')]
    if not saves:
        print("No saved games found.")
    else:
        print("\nAvailable saved games:")
        for save in saves:
            print(f"- {save}")
    return saves


def demolish(city: City, x: int, y: int) -> bool:
    """Demolish a building or infrastructure at the given coordinates."""
    if not (0 <= x < city.grid_size and 0 <= y < city.grid_size):
        print("Invalid coordinates!")
        return False

    demolished = False
    # Remove building if present
    if city.grid[y][x] is not None:
        building_type = city.grid[y][x]
        city.grid[y][x] = None
        city.buildings = [(bx, by, bt) for bx, by, bt in city.buildings if bx != x or by != y]
        demolished = True
    
    # Remove infrastructure
    for infra_type in ['POWER', 'ROAD', 'WATER']:
        if city.infrastructure.has_connection(x, y, infra_type):
            city.infrastructure.remove_connection(x, y, infra_type)
            demolished = True

    if demolished:
        print("Successfully demolished!")
        city.update_city_stats()
        return True
    else:
        print("Nothing to demolish at these coordinates.")
        return False

def display_help():
    print("\nAvailable Commands:")
    print("build x y type - Build at coordinates (x,y). Types:")
    print("                 R(esidential), C(ommercial), I(ndustrial)")
    print("                 P(ark), H(ospital), S(chool), F(ire Station)")
    print("                 POWER, ROAD, WATER (infrastructure)")
    print("demolish x y   - Remove building at coordinates (x,y)")
    print("map           - Display city map")
    print("stats        - Display city statistics")
    print("audit        - Display detailed city report")
    print("economy      - Display detailed economic report")
    print("save name    - Save current game")
    print("load name    - Load a saved game")
    print("saves        - List all saved games")
    print("tax rate     - Set tax rate (0-20)")
    print("help         - Show this help message")
    print("exit         - Exit game")

def main():
    print("Welcome to Text SimCity!")
    print("\n1. New Game")
    print("2. Load Game")
    choice = input("\nEnter your choice (1/2): ")
    
    city = None
    if choice == "2":
        saves = list_saved_games()
        if saves:
            save_name = input("Enter the name of the save to load: ")
            city = load_game(save_name)
    
    if city is None:
        city_name = input("Enter your city name: ")
        city = City(city_name)
    
    print(f"\nYou are now the mayor of {city.name}")
    display_help()

    while True:
        try:
            command = input("\nEnter command: ").lower().split()
            
            if not command:
                continue

            if command[0] == "exit":
                save_choice = input("Would you like to save before exiting? (y/n): ")
                if save_choice.lower() == 'y':
                    save_name = input("Enter save name: ")
                    save_game(city, save_name)
                break
                
            elif command[0] == "save" and len(command) > 1:
                save_name = command[1]
                save_game(city, save_name)
                
            elif command[0] == "load" and len(command) > 1:
                save_name = command[1]
                loaded_city = load_game(save_name)
                if loaded_city:
                    city = loaded_city
                    print(f"Loaded game: {city.name}")
                    
            elif command[0] == "saves":
                list_saved_games()
                
            elif command[0] == "help":
                display_help()
                
            elif command[0] == "map":
                display_grid(city)
                
            elif command[0] == "stats":
                display_stats(city)
                
            elif command[0] == "audit":
                audit_city(city)
                
            elif command[0] == "economy":
                display_economy(city)
                
            elif command[0] == "tax" and len(command) > 1:
                try:
                    new_rate = float(command[1])
                    if 0 <= new_rate <= 20:
                        city.tax_rate = new_rate
                        print(f"Tax rate set to {new_rate}%")
                        city.update_city_stats()
                    else:
                        print("Tax rate must be between 0 and 20%")
                except ValueError:
                    print("Invalid tax rate")
                    
            elif command[0] == "build" and len(command) >= 4:
                try:
                    x = int(command[1])
                    y = int(command[2])
                    building_type = command[3].upper()
                    if city.build(x, y, building_type):
                        print(f"Successfully built {city.get_building_name(building_type)}")
                        city.simulate_turn()
                        display_grid(city)
                except ValueError:
                    print("Invalid coordinates")
                    
            elif command[0] == "demolish" and len(command) >= 3:
                try:
                    x = int(command[1])
                    y = int(command[2])
                    if demolish(city, x, y):
                        city.simulate_turn()
                        display_grid(city)
                except ValueError:
                    print("Invalid coordinates")
                    
            else:
                print("Invalid command. Type 'help' for available commands.")
                
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Please try again or type 'help' for available commands.")
        
        # Simulate a turn after each valid command
        city.simulate_turn()

if __name__ == "__main__":
    main()