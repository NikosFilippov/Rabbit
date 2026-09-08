import numpy as np
import matplotlib.pyplot as plt
import numpy as np
# % matplotlib inline

n = np.arange(45)
theta = n * (3 - np.sqrt(5)) * np.pi
r = 0.1 * np.sqrt(n)
x = r * np.cos(theta)
y = r * np.sin(theta)
circle = plt.Circle((0.0, 0.0), radius=0.75, fc='deepskyblue')
fig, ax = plt.subplots()
ax.add_patch(circle)
ax.axis('scaled')
ax.scatter(x, y, s=320, marker='*', color='gold', zorder=3)
ax.plot(x,y,color='tomato')
ax.axis('off')
x= np.random.randint(1,100)
xlow=1
xhigh=100
flag = True
c=0
while flag and c<=5:
    print("Type a number between ",xlow," - ",xhigh,":")
    y = int(input())
    while y<xlow or y>xhigh:
        print('Nope the guess was outside the range')
        print("Type a number between ",xlow," - ",xhigh,":")
        y = int(input())
    if y == x:
        flag =False
        print("You guessed correctly you win")
        plt.show()
    elif y>x:
        xhigh = y-1
        print("your guess was too high try lower")
        print("you have ",5-c," tries left")
    else:
        xlow = y+1
        print("your guess was too low try higher")
        print("you have ",5-c," tries left")


    c+=1
if flag:
    print("Sorry you exceeded the 5 tries better luck next time")
