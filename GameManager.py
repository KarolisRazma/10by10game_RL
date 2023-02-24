import random
import os
import Color as c
import Chip as ch
import Board as b
import Player as p

class GameManager:
    def __init__(self):
        self.board = b.Board()
        self.container = []
        self.players = [p.Player("Mister One"), p.Player("Mister Two")] # create players
        self.createContainer() # fill container
        self.initialChips() # players take 2 chips

        # place chip in the board's center
        index = self.selectRandomlyFromContainer()
        self.placeChipOnBoard(self.getChipFromContainer(index), 2, 2)
        self.removeChipFromContainer(index)

        # select starting player randomly
        random.shuffle(self.players)

    def gameLoop(self):
        turn = 0
        while True:
            os.system("clear")
            self.board.display()
            self.displayScore()
            self.displayTurn(turn)
            self.displayUserChips(turn)
            self.displayChipsLeftInContainer()

            # get index (of chip) and row/col 
            rowColChip = self.userInput()
            row = int(rowColChip[0]) - 1
            col = int(rowColChip[1]) - 1
            chipIndex = int(rowColChip[2])

            selectedChip = self.players[turn].useChip(chipIndex)  # take chip from player's hand
            self.placeChipOnBoard(selectedChip, row, col)  # player place one chip on the board

            combinationsOfTen = self.findTens()  # check if somehow there is value of 10 on the board

            # player takes these chips
            # except the one placed this round
            if combinationsOfTen:
                os.system("clear")
                self.board.display()
                self.displayCombinations(combinationsOfTen)

                index = input("Select combination: ") # choose which combination to collect
                index = int(index)
                selectedCombination = combinationsOfTen[index]

                for chip in selectedCombination:
                    # tile where the chip belongs
                    tile = self.board.getTileAtIndex(chip.getRow() * 5 + chip.getCol())

                    # if its the same chip that was placed this round, player can't take it
                    if row == chip.getRow() and col == chip.getCol():
                        continue

                    # return to container
                    if tile.getColor() == c.Color.RED:
                        self.container.append(chip)
                        self.removeChipFromBoard(chip.getRow(), chip.getCol())

                    # take a chip from board
                    # and collect one more from the container
                    if tile.getColor() == c.Color.BLUE:
                        # from board
                        self.removeChipFromBoard(chip.getRow(), chip.getCol())
                        self.players[turn].capturedChips.append(chip)
                        self.players[turn].score += 1
                        # from container
                        randomIndex = self.selectRandomlyFromContainer()
                        self.players[turn].capturedChips.append(self.getChipFromContainer(randomIndex))
                        self.players[turn].score += 1
                        self.removeChipFromContainer(randomIndex)

                    # collect chip normally
                    if tile.getColor() == c.Color.WHITE:
                        self.removeChipFromBoard(chip.getRow(), chip.getCol())
                        self.players[turn].capturedChips.append(chip)
                        self.players[turn].score += 1

            # in the end of the round
            # check for end game conditions
            endGameFlag = self.isEndGame()
            if endGameFlag > 0:
                if endGameFlag == 1:
                    print("Player1: {} won".format(self.players[turn].id))
                if endGameFlag == 2:
                    print("Player2: {} won".format(self.players[turn].id))
                if endGameFlag == 3:
                    if self.players[0].score < self.players[1].score:
                        print("Player1: {} won".format(self.players[turn].id))
                    if self.players[0].score > self.players[1].score:
                        print("Player2: {} won".format(self.players[turn].id))
                    else:
                        print("Draw")
                break

            # draw new chip from the container
            index = self.selectRandomlyFromContainer()
            self.drawChipFromContainer(index, turn)
            self.removeChipFromContainer(index)

            # next player's turn
            turn = 0 if turn == 1 else 1

    # game logic, finding rows of ten
    # find every possible line of value 10
    ##############################################
    def findTens(self):
        combinationsOfTen = []

        # diagonally
        indexesStart = [0, 1, 2, 5, 10]
        indexesEnd = [24, 19, 14, 23, 22]
        combinationsOfTen += self.findChipsInLine(indexesStart, indexesEnd, 6)

        indexesStart = [2, 3, 4, 9, 14]
        indexesEnd = [10, 15, 20, 21, 22]
        combinationsOfTen += self.findChipsInLine(indexesStart, indexesEnd, 4)

        # vertically
        indexesStart = [0, 1, 2, 3, 4]
        indexesEnd = [20, 21, 22, 23, 24]
        combinationsOfTen += self.findChipsInLine(indexesStart, indexesEnd, 5)

        # horizontally
        indexesStart = [0, 5, 10, 15, 20]
        indexesEnd = [4, 9, 14, 19, 24]
        combinationsOfTen += self.findChipsInLine(indexesStart, indexesEnd, 1)
        return combinationsOfTen

    # find possible line of value 10 (diagonally or vertically or horizontally)
    def findChipsInLine(self, indexesStart, indexesEnd, indexGrowth):
        combinationsOfTen = []
        for (indexStart, indexEnd) in zip(indexesStart, indexesEnd):
            chipsInLine = []
            sum = 0
            while indexStart <= indexEnd:
                if self.board.isTileEmpty(indexStart):
                    sum = 0
                    chipsInLine = []
                    indexStart += indexGrowth
                    continue
                else:
                    sum += self.board.chips[indexStart].getValue()
                    chipsInLine.append(self.board.chips[indexStart])
                if sum == 10:
                    temp = chipsInLine.copy()
                    combinationsOfTen.append(temp)
                    sum -= chipsInLine[0].getValue()
                    del chipsInLine[0]
                if sum > 10:
                    sum -= chipsInLine[0].getValue()
                    del chipsInLine[0]
                indexStart += indexGrowth
        return combinationsOfTen
    ##############################################

    # testing methods (will be deleted later on)
    # user input, printing to screen methods
    ########################################
    def userInput(self):
        rowColChip = input("Select row,col,chip: ")
        return rowColChip

    def displayChipsLeftInContainer(self):
        return len(self.container)

    def displayUserChips(self, turn):
        chips = self.players[turn].chips
        for (i, chip) in zip(range(len(chips)), chips):
            print("[{}]. Value: {}".format(i, chip.getValue()))

    def displayTurn(self, turn):
        print("It's now {} turn".format(self.players[turn].id))

    def displayCombinations(self, combinationsOfTen):
        for (i, comb) in zip(range(len(combinationsOfTen)), combinationsOfTen):
            for chip in comb:
                print(
                    "[{}] Row: {}, Col: {}, Value: {}".format(i, chip.getRow() + 1, chip.getCol() + 1, chip.getValue()))

    def displayScore(self):
        player1 = self.players[0]
        player2 = self.players[1]
        print("Player1: {} and score {}".format(player1.id, player1.score))
        print("Player2: {} and score {}".format(player2.id, player2.score))
    #############################

    # misc
    #############################
    def initialChips(self):
        # player 1 picks 2 initial chips
        index = self.selectRandomlyFromContainer()
        self.drawChipFromContainer(index, 0)
        self.removeChipFromContainer(index)
        index = self.selectRandomlyFromContainer()
        self.drawChipFromContainer(index, 0)
        self.removeChipFromContainer(index)
        # player 2 picks 2 initial chips
        index = self.selectRandomlyFromContainer()
        self.drawChipFromContainer(index, 1)
        self.removeChipFromContainer(index)
        index = self.selectRandomlyFromContainer()
        self.drawChipFromContainer(index, 1)
        self.removeChipFromContainer(index)

    def isEndGame(self):
        if self.players[0].score >= 10:
            return 1
        if self.players[1].score >= 10:
            return 2
        if self.players[0].score < 10 and self.players[1].score < 10 and not self.container:
            return 3
        return 0
    #############################

    # BOARD METHODS
    #############################
    # expected to get row and column already configured to be an index (row-- and column--)
    def placeChipOnBoard(self, chip, row, column):
        chip.setRow(row)
        chip.setCol(column)
        self.board.chips[row * 5 + column] = chip

    # expected to get row and column already configured to be an index (row-- and column--)
    # removes chip from the board
    def removeChipFromBoard(self, row, column):
        self.board.chips[row * 5 + column] = None

    # expected to get row and column already configured to be an index (row-- and column--)
    def collectChipFromBoard(self, row, column, playerIndex):
        self.players[playerIndex].capturedChips.append(self.board.chips[row * 5 + column])
    #############################

    # CONTAINER METHODS
    #############################
    def removeChipFromContainer(self, index):
        del self.container[index]

    # turn is current player's turn (to take chip from container or take actions)
    def drawChipFromContainer(self, index, turn):
        self.players[turn].chips.append(self.container[index])

    # returns index
    def selectRandomlyFromContainer(self):
        return random.randint(0, len(self.container) - 1)

    def getChipFromContainer(self, index):
        return self.container[index]

    def createContainer(self):
        for i in range(28):
            if i < 7:
                self.container.append(ch.Chip(1))
                continue
            if i < 14:
                self.container.append(ch.Chip(2))
                continue
            if i < 21:
                self.container.append(ch.Chip(3))
                continue
            self.container.append(ch.Chip(4))
    #############################
