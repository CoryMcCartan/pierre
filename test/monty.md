# The Monty Hall Problem

Suppose you're on a game show, and you're given the choice of three doors:
Behind one door is a car; behind the others, goats. (Your goal, obviously,
is to end up with the car). 

    @priors
    door 1: 1/3 [0.333333]
    door 2: 1/3 [0.333333]
    door 3: 1/3 [0.333333]

You pick a door, say No. 1, and the host, who knows what's behind the doors,
opens another door, say No. 3, which has a goat. He then says to you, "Do you
want to pick door No. 2?" Is it to your advantage to switch your choice?

If the car were behind door 1, then the host would randomly pick between
doors 2 and 3 to reveal. If the car were behind door 2, the host would have to
show you door 3. If the car were behind door 3, then the host couldn't show us
that door.

    @evidence: shown door 3
    door 1: 1/2 [0.333333 ==0.333333==> 0.333333]
    door 2: 1 [0.333333 ==0.666667==> 0.666667]
    door 3: 0 [0.333333 ==0.000000==> 0.000000]

So we should switch!
