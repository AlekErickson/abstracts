import numpy as np

def get_crosscuts(grid):
    """Find all 2x2 crosscuts in the grid."""
    crosscuts = []
    n = len(grid)
    for i in range(n-1):
        for j in range(n-1):
            subgrid = grid[i:i+2, j:j+2]
            if (np.sum(subgrid) == 2 and
                abs(subgrid[0, 0] - subgrid[1, 1]) == abs(subgrid[0, 1] - subgrid[1, 0]) == 0):
                crosscuts.append(((i, j), (i+1, j+1)) if subgrid[0, 0] == 1 else ((i, j+1), (i+1, j)))
    return crosscuts

def count_crosscuts(grid):
    """Count the number of crosscuts in the grid."""
    crosscuts = get_crosscuts(grid)
    return len(crosscuts)


def get_resolving_stones(grid, crosscuts, player):
    """Find all resolving stone options for the player."""
    resolving_stones = set()
    for crosscut in crosscuts:
        for stone in crosscut:
            if grid[stone] == player:
                resolving_stones.add(stone)
    return list(resolving_stones)



def swap(grid, stone, enemy):
    """Swap the positions of the resolving stone and the enemy."""
    grid[stone], grid[enemy] = grid[enemy], grid[stone]

def resolve(grid, player):
    """Resolve the grid according to the rules."""
    crosscuts = get_crosscuts(grid)
    while crosscuts:
        resolving_stones = get_resolving_stones(grid, crosscuts, player)
        if not resolving_stones:
            break

        print("Available resolving stones:", resolving_stones)
        resolving_input = input("Select the resolving stone (row column): ")
        resolving_stone = tuple(map(int, resolving_input.split()))

        # Check if the selected resolving stone is valid
        if resolving_stone not in resolving_stones:
            print("Invalid resolving stone. Please try again.")
            continue

        enemies = [enemy for crosscut in crosscuts for enemy in crosscut if grid[enemy] == 1 - player and resolving_stone in crosscut]
        if enemies:
            print("Available enemy stones:", enemies)
            enemy_input = input("Select the enemy stone to swap with (row column): ")
            enemy_stone = tuple(map(int, enemy_input.split()))

            # Check if the selected enemy stone is valid
            if enemy_stone not in enemies:
                print("Invalid enemy stone. Please try again.")
                continue

            swap(grid, resolving_stone, enemy_stone)
        else:
            break  # no valid swaps found

        crosscuts = get_crosscuts(grid)

    return grid


def generate_random_grid(size):
    # Generate a random grid of size x size
    grid = np.random.randint(2, size=(size, size))
    return grid

# Example usage
size = 5
grid = generate_random_grid(size)
print(grid)


num_crosscuts = count_crosscuts(grid)
print("Number of crosscuts:", num_crosscuts)

#resolved_grid = resolve(grid, 1)
#print(resolved_grid)


#WORKING TO AT LEAST GET THE CROSSCUTS


