import random


def rock_paper_scissors():
    """A simple Rock-Paper-Scissors game."""
    choices = ['rock', 'paper', 'scissors']
    score = {'wins': 0, 'losses': 0, 'ties': 0}

    print("Welcome to Rock-Paper-Scissors!")
    rounds = 0

    while True:
        rounds += 1
        computer = random.choice(choices)
        player = input("Enter rock, paper, or scissors (or 'quit' to exit): ").lower()

        if player == 'quit':
            print("Thanks for playing!")
            break
        if player not in choices:
            print("Invalid choice. Please try again.")
            rounds -= 1
            continue

        print(f"You chose {player}, computer chose {computer}.")

        if player == computer:
            result = 'tie'
            score['ties'] += 1
            print("It's a tie!")
        elif (player == 'rock' and computer == 'scissors') or \
             (player == 'paper' and computer == 'rock') or \
             (player == 'scissors' and computer == 'paper'):
            result = 'win'
            score['wins'] += 1
            print("You win this round!")
        else:
            result = 'loss'
            score['losses'] += 1
            print("You lose this round.")

    print(f"\nFinal results after {rounds-1} rounds:")
    print(f"Wins: {score['wins']}, Losses: {score['losses']}, Ties: {score['ties']}")


if __name__ == "__main__":
    rock_paper_scissors()
