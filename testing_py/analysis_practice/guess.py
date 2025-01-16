secret_number = 9
i = 0
while i  < 3:
    guess = int(input("Guess: "))
    if guess == secret_number:
        print("You guessed it right")
        break
    i += 1
    
