import graphics as gp
import pygraphviz as viz
from tkinter import messagebox
from tkinter import filedialog
import math
import pandas as pd

class GUI():
    
    def __init__(self):
        self.win = gp.GraphWin('test',1080,720)
        self.toolH = 50
        self.drawTool()
        self.currentB = 0
        self.nodeList = []
        self.nodeText = []
        self.nodeColor = ['red','black','blue']
        self.nodeType = ['start','normal','end']

        self.lineList = []
        self.lineText = []  # 存储元素为三元素列表
        self.inputList = []

        self.LineNode1 = None
        self.LN1Idx = None
        self.LineNode2 = None
        self.LN2Idx = None
        self.chosenNode = None
        self.chosenIdx = None

        self.lineToSelf = []
        self.lineToSelfText = []
        self.lineToSelfNode = []


        self.dataDic = {}

    def createToolButton(self,posL,text):
        rec = gp.Rectangle(gp.Point(posL[0],5),gp.Point(posL[1],45))
        rec.draw(self.win)
        gp.Text(rec.getCenter(),text).draw(self.win)
        return rec

    def getChosenButton(self,pos):
        for button in self.toolButton:
            button.setOutline('black')
        for i in range(len(self.toolButtonPosList)):
            if(pos<=self.toolButtonPosList[i][1] and pos>=self.toolButtonPosList[i][0]):
                self.toolButton[i].setOutline('red')
                self.currentB = i
                return
        self.toolButton[self.currentB].setOutline('red')

    def drawTool(self):
        self.toolBack = gp.Rectangle(gp.Point(0,0),gp.Point(1080,50))
        self.toolBack.setFill('grey')
        self.toolBack.draw(self.win)
        self.toolButtonPosList = [[5,95],[100,190],[195,285],[290,380],[385,475],[480,570],[575,665],[670,760],[765,875]]
        self.toolButtonText = ['添加开始点','添加中间点','添加结束点','添加线','移动','删除','导入','保存','输出图']
        self.toolButton = []
        for i in range(len(self.toolButtonPosList)):
            self.toolButton.append(self.createToolButton(self.toolButtonPosList[i],self.toolButtonText[i]))
        
        self.input = gp.Entry(gp.Point(925,25),5)
        self.input.draw(self.win)

    def calDisNode(self,pos1,pos2):
        return math.sqrt((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)

    def checkNearNode(self,pos,typeCall):
        flag = False
        for i in range(len(self.nodeList)):
            center = [self.nodeList[i].getCenter().getX(),self.nodeList[i].getCenter().getY()]
            if(self.calDisNode(pos,center)<15):
                if(typeCall == 'check'):
                    messagebox.showinfo('提示','该位置有过近的相邻点')
                    return -1
                elif(typeCall == 'get'):
                    return i
        if(typeCall == 'check'):
            return 1
        elif(typeCall == 'get'):
            return -1


    def createNode(self,pos,act):
        if(self.checkNearNode(pos,'check')==-1):
            return
        text = self.input.getText()

        for i in range(len(self.nodeText)):
            if(self.nodeText[i].getText()==text):
                messagebox.showinfo('提示','已有同名结点')
                self.input.setText('')
                return

        if(len(text) == 0):
            messagebox.showinfo('提示','请填写该点名称')
            return
        node = gp.Circle(gp.Point(pos[0],pos[1]),15)
        node.setOutline(self.nodeColor[act])
        node.draw(self.win)
        self.nodeList.append(node)
        
        textN = gp.Text(node.getCenter(),text)
        textN.draw(self.win)
        self.nodeText.append(textN)
        self.dataDic[text] = [pos[0],pos[1],self.nodeType[act]]
        for i in range(len(self.inputList)):
            self.dataDic[text].append('None')

    def drawLine(self,node1,node2):
        pos1 = [node1.getX(),node1.getY()]
        pos2 = [node2.getX(),node2.getY()]
        distance = self.calDisNode(pos1,pos2)
        dx = 15/distance*(pos2[0]-pos1[0])
        dy = 15/distance*(pos1[1]-pos2[1])
        return gp.Line(gp.Point(pos1[0]+dx,pos1[1]-dy),gp.Point(pos2[0]-dx,pos2[1]+dy))

    def drawLineToSelf(self,node):
        pos = [node.getX(),node.getY()-15]
        line1 = gp.Line(gp.Point(pos[0],pos[1]),gp.Point(pos[0]+30,pos[1]-30))
        line1.setArrow('last')
        line1.draw(self.win)
        line2 = gp.Line(gp.Point(pos[0]+30,pos[1]-30),gp.Point(pos[0]-30,pos[1]-30))
        line2.setArrow('last')
        line2.draw(self.win)
        line3 = gp.Line(gp.Point(pos[0]-30,pos[1]-30),gp.Point(pos[0],pos[1]))
        line3.setArrow('last')
        line3.draw(self.win)
        return [line1,line2,line3]

    def createLine(self,pos):
        i = self.checkNearNode(pos,'get')
        
        if(i == -1):
            self.clearPanel()
            return
        if(self.LineNode1 == None):
            self.LineNode1 = self.nodeList[i]
            self.LN1Idx = i
            self.LineNode1.setFill('yellow')
        elif(self.LineNode2 == None):
            self.LineNode2 = self.nodeList[i]
            self.LN2Idx = i
            self.LineNode2.setFill('yellow')

        if(self.LineNode1!=None and self.LineNode2!=None):
            text = self.input.getText()
            for i in range(len(self.nodeText)):
                if(self.nodeText[i].getText() == text):
                    messagebox.showinfo('提示','该输入与已有状态重复')
                    self.clearPanel()
                    return
            if(len(text) == 0):
                messagebox.showinfo('提示','请填写该线段名称')
                self.clearPanel()
                return
            if(self.LN1Idx == self.LN2Idx):
                nodeText = self.nodeText[self.LN2Idx].getText()
                if(nodeText in self.lineToSelfNode):
                    idx = self.lineToSelfNode.index(nodeText)
                    inputList = self.lineToSelfText[idx].getText().split(',')
                    for inputN in inputList:
                        if(inputN == text):
                            messagebox.showinfo('提示','该两点间已有该转化')
                            self.clearPanel()
                            return
                    textN = self.lineToSelfText[idx]
                    textN.setText(textN.getText()+','+text)
                    if(text not in self.inputList):
                        self.inputList.append(text)
                        for node in self.dataDic.keys():
                            self.dataDic[node].append('None')
                    idx = self.inputList.index(text)
                    self.dataDic[self.nodeText[self.LN1Idx].getText()][idx+3] = self.nodeText[self.LN2Idx].getText()
                    self.clearPanel()
                    return
            else:
                for line in range(len(self.lineText)):
                    if(self.lineText[line][1]==self.nodeText[self.LN1Idx].getText() and self.lineText[line][2]==self.nodeText[self.LN2Idx].getText()):
                        inputList = self.lineText[line][0].getText().split(',')
                        for inputN in inputList:
                            if(inputN == text):
                                messagebox.showinfo('提示','该两点间已有该转化')
                                self.clearPanel()
                                return
                        self.lineText[line][0].setText(self.lineText[line][0].getText()+','+text)
                        if(text not in self.inputList):
                            self.inputList.append(text)
                            for node in self.dataDic.keys():
                                self.dataDic[node].append('None')
                        idx = self.inputList.index(text)
                        self.dataDic[self.nodeText[self.LN1Idx].getText()][idx+3] = self.nodeText[self.LN2Idx].getText()
                        self.clearPanel()
                        return
            # 指向自身
            if(self.LN1Idx == self.LN2Idx):
                self.lineToSelfNode.append(self.nodeText[self.LN1Idx].getText())
                center = [self.LineNode1.getCenter().getX(),self.LineNode1.getCenter().getY()]
                self.lineToSelf.append(self.drawLineToSelf(gp.Point(center[0],center[1])))
                textN = gp.Text(gp.Point(center[0],center[1]-55),text)
                self.lineToSelfText.append(textN)
                textN.draw(self.win)
                if(text not in self.inputList):
                    self.inputList.append(text)
                    for node in self.dataDic.keys():
                        self.dataDic[node].append('None')
                idx = self.inputList.index(text)
                self.dataDic[self.nodeText[self.LN1Idx].getText()][idx+3] = self.nodeText[self.LN2Idx].getText()
            else:
                line = self.drawLine(self.LineNode1.getCenter(),self.LineNode2.getCenter())
                line.setArrow('last')
                self.lineList.append(line)
                line.draw(self.win)
                # 线段text
                if(self.nodeList[self.LN1Idx].getCenter().getX()<self.nodeList[self.LN2Idx].getCenter().getX()):
                    textN = gp.Text(gp.Point(line.getCenter().getX(),line.getCenter().getY()-10),text)
                else:
                    textN = gp.Text(gp.Point(line.getCenter().getX(),line.getCenter().getY()+10),text)
                self.lineText.append([textN,self.nodeText[self.LN1Idx].getText(),self.nodeText[self.LN2Idx].getText()])
                textN.draw(self.win)
                # 填写datadic
                if(text not in self.inputList):
                    self.inputList.append(text)
                    for node in self.dataDic.keys():
                        self.dataDic[node].append('None')
                idx = self.inputList.index(text)
                self.dataDic[self.nodeText[self.LN1Idx].getText()][idx+3] = self.nodeText[self.LN2Idx].getText()
            self.LineNode1.setFill('white')
            self.LineNode2.setFill('white')
            self.LineNode1 = None
            self.LineNode2 = None
            self.LN1Idx = None
            self.LN2Idx = None
        return
    
    def reLine(self,pos,textIn):
        i = self.checkNearNode(pos,'get')
        if(self.LN1Idx == self.LN2Idx):
            nodeText = self.nodeText[self.LN2Idx].getText()
            if(nodeText in self.lineToSelfNode):
                idx = self.lineToSelfNode.index(nodeText)
                inputList = self.lineToSelfText[idx].getText().split(',')
                textN = self.lineToSelfText[idx]
                textN.setText(textN.getText()+','+textIn)
                if(textIn not in self.inputList):
                    self.inputList.append(textIn)
                    for node in self.dataDic.keys():
                        self.dataDic[node].append('None')
                idx = self.inputList.index(textIn)
                self.dataDic[self.nodeText[self.LN1Idx].getText()][idx+3] = self.nodeText[self.LN2Idx].getText()
                self.clearPanel()
                return
        else:
            for line in range(len(self.lineText)):
                if(self.lineText[line][1]==self.nodeText[self.LN1Idx].getText() and self.lineText[line][2]==self.nodeText[self.LN2Idx].getText()):
                    inputList = self.lineText[line][0].getText().split(',')
                    self.lineText[line][0].setText(self.lineText[line][0].getText()+','+textIn)
                    if(textIn not in self.inputList):
                        self.inputList.append(textIn)
                        for node in self.dataDic.keys():
                            self.dataDic[node].append('None')
                    idx = self.inputList.index(textIn)
                    self.dataDic[self.nodeText[self.LN1Idx].getText()][idx+3] = self.nodeText[self.LN2Idx].getText()
                    self.clearPanel()
                    return
        # 指向自身
        if(self.LN1Idx == self.LN2Idx):
            self.lineToSelfNode.append(self.nodeText[self.LN1Idx].getText())
            center = [self.LineNode1.getCenter().getX(),self.LineNode1.getCenter().getY()]
            self.lineToSelf.append(self.drawLineToSelf(gp.Point(center[0],center[1])))
            textN = gp.Text(gp.Point(center[0],center[1]-55),textIn)
            self.lineToSelfText.append(textN)
            textN.draw(self.win)
            if(textIn not in self.inputList):
                self.inputList.append(textIn)
                for node in self.dataDic.keys():
                    self.dataDic[node].append('None')
            idx = self.inputList.index(textIn)
            self.dataDic[self.nodeText[self.LN1Idx].getText()][idx+3] = self.nodeText[self.LN2Idx].getText()
        else:
            line = self.drawLine(self.LineNode1.getCenter(),self.LineNode2.getCenter())
            line.setArrow('last')
            self.lineList.append(line)
            line.draw(self.win)
            # 线段text
            if(self.nodeList[self.LN1Idx].getCenter().getX()<self.nodeList[self.LN2Idx].getCenter().getX()):
                textN = gp.Text(gp.Point(line.getCenter().getX(),line.getCenter().getY()-10),textIn)
            else:
                textN = gp.Text(gp.Point(line.getCenter().getX(),line.getCenter().getY()+10),textIn)
            self.lineText.append([textN,self.nodeText[self.LN1Idx].getText(),self.nodeText[self.LN2Idx].getText()])
            textN.draw(self.win)
            # 填写datadic
            if(textIn not in self.inputList):
                self.inputList.append(textIn)
                for node in self.dataDic.keys():
                    self.dataDic[node].append('None')
            idx = self.inputList.index(textIn)
            tempASD = self.nodeText[self.LN2Idx].getText()
            self.dataDic[self.nodeText[self.LN1Idx].getText()][idx+3] = tempASD
        self.LineNode1.setFill('white')
        self.LineNode2.setFill('white')
        self.LineNode1 = None
        self.LineNode2 = None
        self.LN1Idx = None
        self.LN2Idx = None
        return

    def moveNode(self,pos):
        if(self.chosenNode != None):
            if(self.checkNearNode(pos,'check') == -1):
                return
            text = self.nodeText[self.chosenIdx].getText()
            self.nodeText[self.chosenIdx].undraw()
            self.chosenNode.undraw()
            self.nodeList[self.chosenIdx]=gp.Circle(gp.Point(pos[0],pos[1]),15)
            self.chosenNode = self.nodeList[self.chosenIdx]
            self.nodeText[self.chosenIdx]=gp.Text(self.nodeList[self.chosenIdx].getCenter(),text)
            self.nodeList[self.chosenIdx].draw(self.win)
            self.nodeText[self.chosenIdx].draw(self.win)
            self.dataDic[text][0] = self.nodeList[self.chosenIdx].getCenter().getX()
            self.dataDic[text][1] = self.nodeList[self.chosenIdx].getCenter().getY()
            # for(i=3;i<len(self.dataDic['text']);i+=1):
            for i in range(3,len(self.dataDic[text])):
                if(self.dataDic[text][i]=='None'):
                    continue
                if(text == self.dataDic[text][i]):
                    for i in range(len(self.lineToSelfNode)):
                        if(text == self.lineToSelfNode[i]):
                            break
                    for line in self.lineToSelf[i]:
                        line.undraw()
                    self.lineToSelf[i] = self.drawLineToSelf(gp.Point(pos[0],pos[1]))
                    self.lineToSelfText[i].undraw()
                    self.lineToSelfText[i] = gp.Text(gp.Point(pos[0],pos[1]-55),self.lineToSelfNode[i])
                    self.lineToSelfText[i].draw(self.win)
                    continue
                for j in range(len(self.lineText)):
                    if(self.lineText[j][1] == text and self.lineText[j][2] == self.dataDic[text][i]):
                        self.lineList[j].undraw()
                        
                        for k in range(len(self.nodeText)):
                            if(self.nodeText[k].getText()==self.dataDic[text][i]):
                                break
                        self.lineList[j] = self.drawLine(self.nodeList[self.chosenIdx].getCenter(),self.nodeList[k].getCenter())
                        self.lineList[j].setArrow('last')
                        self.lineList[j].draw(self.win)

                        line = self.lineList[j]
                        textTemp = self.lineText[j][0].getText()
                        self.lineText[j][0].undraw()
                        if(self.chosenNode.getCenter().getX()<self.nodeList[k].getCenter().getX()):
                            self.lineText[j][0] = gp.Text(gp.Point(line.getCenter().getX(),line.getCenter().getY()-10),textTemp)
                        else:
                            self.lineText[j][0] = gp.Text(gp.Point(line.getCenter().getX(),line.getCenter().getY()+10),textTemp)
                        self.lineText[j][0].draw(self.win)
                        break
            for node in self.dataDic:
                # 射入
                if(node == text):
                    continue
                for i in range(3,len(self.dataDic[node])):
                    if(self.dataDic[node][i]=='None' or self.dataDic[node][i] !=text):
                        continue
                    for j in range(len(self.lineText)):
                        if(self.lineText[j][1] == node and self.lineText[j][2] == text):
                            print(self.lineText[j])
                            self.lineList[j].undraw()
                            for k in range(len(self.nodeText)):
                                if(self.nodeText[k].getText()==node):
                                    break
                            self.lineList[j] = self.drawLine(self.nodeList[k].getCenter(),self.nodeList[self.chosenIdx].getCenter())
                            self.lineList[j].setArrow('last')
                            self.lineList[j].draw(self.win)

                            line = self.lineList[j]
                            textTemp = self.lineText[j][0].getText()
                            self.lineText[j][0].undraw()
                            if(self.chosenNode.getCenter().getX()>self.nodeList[k].getCenter().getX()):
                                self.lineText[j][0] = gp.Text(gp.Point(line.getCenter().getX(),line.getCenter().getY()-10),textTemp)
                            else:
                                self.lineText[j][0] = gp.Text(gp.Point(line.getCenter().getX(),line.getCenter().getY()+10),textTemp)
                            self.lineText[j][0].draw(self.win)
            self.chosenNode = None
            self.chosenIdx = None
        else:
            i = self.checkNearNode(pos,'get')
            if(i == -1):
                self.clearPanel()
                return
            self.chosenIdx = i
            self.chosenNode = self.nodeList[self.chosenIdx]
            self.chosenNode.setFill('yellow')
        return

    def clearPanel(self):
        if(self.chosenNode != None):
            self.chosenNode.setFill('white')
            self.chosenNode = None
            self.chosenIdx = None
        if(self.LineNode1 != None):
            self.LineNode1.setFill('white')
            self.LineNode1 = None
            self.LN1Idx = None
        if(self.LineNode2 != None):
            self.LineNode2.setFill('white')
            self.LineNode2 = None
            self.LN2Idx = None
    
    def delCom(self,pos):
        idx = self.checkNearNode(pos,'get')
        if(idx != -1):
            nodeList = []
            name = self.nodeText[idx].getText()
            for i in range(len(self.lineText)):
                if(self.lineText[i][1]==name or self.lineText[i][2]==name):
                    nodeList.append(i)
            nodeList.reverse()
            for i in nodeList:
                self.lineText[i][0].undraw()
                del self.lineText[i]
                self.lineList[i].undraw()
                del self.lineList[i]
            self.nodeList[idx].undraw()
            del self.nodeList[idx]
            self.nodeText[idx].undraw()
            del self.nodeText[idx]
            del self.dataDic[name]
            for i in self.dataDic:
                for j in range(len(self.dataDic[i])):
                    if(j<3):continue
                    if(self.dataDic[i][j]==name):
                        self.dataDic[i][j] = 'None'
            return
        else:
            for i in range(len(self.lineText)):
                center = [self.lineText[i][0].getAnchor().getX(),self.lineText[i][0].getAnchor().getY()]
                if(self.calDisNode(pos,center)<10):
                    tempIdx = self.inputList.index(self.lineText[i][0].getText())
                    self.dataDic[self.lineText[i][1]][tempIdx+3] = 'None'
                    self.lineText[i][0].undraw()
                    del self.lineText[i]
                    self.lineList[i].undraw()
                    del self.lineList[i]
                    return

    def saveCsv(self):
        text = self.input.getText()
        finalList = []
        colIndex = ['node','posx','posy','type']
        colIndex.extend(self.inputList)
        for node in self.dataDic:
            tempDic = {}
            for i in range(len(colIndex)):
                if(i==0):
                    tempDic[colIndex[i]] = str(node)
                else:
                    tempDic[colIndex[i]] = str(self.dataDic[node][i-1])
            finalList.append(tempDic)
        df = pd.DataFrame(finalList)
        df.to_csv(text+'.csv')

    def clearWin(self):
        for i in self.nodeText:
            i.undraw()
        self.nodeText = []
        for i in self.nodeList:
            i.undraw()
        self.nodeList = []
        for i in self.lineList:
            i.undraw()
        self.lineList = []
        for i in self.lineText:
            i[0].undraw()
        self.lineText = []
        for i in self.lineToSelf:
            for j in i:
                j.undraw()
        self.lineToSelf = []
        for i in self.lineToSelfText:
            i.undraw()
        self.lineToSelfText = []
        self.lineToSelfNode = []
        self.inputList = []
        self.dataDic = {}
        self.clearPanel()

    def readCsv(self):
        Filepath = filedialog.askopenfilename()
        df = pd.read_csv(Filepath)
        print(list(df.columns))
        print(df.index)
        self.clearWin()
        nodeSort = []
        # 重现点
        for row in df.itertuples():
            print(row)
            tempRow = dict(row._asdict())
            nodeSort.append(str(tempRow['node']))
            node = gp.Circle(gp.Point(tempRow['posx'],tempRow['posy']),15)
            node.draw(self.win)
            node.setOutline(self.nodeColor[self.nodeType.index(str(tempRow['type']))])
            text = gp.Text(node.getCenter(),str(tempRow['node']))
            text.draw(self.win)
            self.nodeList.append(node)
            self.nodeText.append(text)
            self.dataDic[str(tempRow['node'])] = [tempRow['posx'],tempRow['posy'],tempRow['type']]
        # 重现线
        for row in df.itertuples():
            tempRow = dict(row._asdict())
            inputListT = list(tempRow.keys())[6:]
            break
        for i in range(len(inputListT)):
            inputListT[i] = str(inputListT[i])
        for row in df.itertuples():
            tempRow = dict(row._asdict())
            for col in inputListT:
                # if(tempRow[col]==tempRow[name]):
                if(str(tempRow[col]) == 'None'):
                    continue
                self.LineNode1 = self.nodeList[nodeSort.index(str(tempRow['node']))]
                self.LN1Idx = nodeSort.index(str(tempRow['node']))
                
                self.LineNode2 = self.nodeList[nodeSort.index(str(tempRow[col]))]
                self.LN2Idx = nodeSort.index(str(tempRow[col]))
                self.reLine([self.LineNode1.getCenter().getX(),self.LineNode1.getCenter().getY()],col)
    
    def createImg(self):
        text = self.input.getText()
        img = viz.AGraph(directed = True)
        for i in self.dataDic:
            img.add_node(i,color = self.nodeColor[self.nodeType.index(self.dataDic[i][2])])
        for i in self.dataDic:
            tempdic = {}
            for j in range(3,len(self.dataDic[i])):
                if(self.dataDic[i][j] == 'None'):
                    continue
                # if(self.dataDic[i][j] == i):
                if(self.dataDic[i][j] in tempdic.keys()):
                    tempdic[self.dataDic[i][j]] = tempdic[self.dataDic[i][j]]+','+self.inputList[j-3]
                else:
                    tempdic[self.dataDic[i][j]] = self.inputList[j-3]
            for j in tempdic.keys():
                img.add_edge(i,j,label = tempdic[j])
        
        img.layout('dot')
        img.draw(text+'.png',format='png')

    
    def clickAction(self,act,pos):
        if(act>=0 and act<=2):
            self.createNode(pos,act)
        elif(act == 3):
            self.createLine(pos)
        elif(act == 4):
            self.moveNode(pos)
        elif(act == 5):
            self.delCom(pos)

    def buttonAction(self):
        if(self.currentB == 7):
            self.saveCsv()
        elif(self.currentB == 6):
            self.readCsv()
        elif(self.currentB == 8):
            self.createImg()

    def run(self):
        self.getChosenButton(10)
        while True:
            pos = self.win.getMouse()
            if(pos.getY()>=5 and pos.getY()<=45):
                self.getChosenButton(pos.getX())
                self.buttonAction()
                self.clearPanel()
            elif(pos.getY()>70):
                self.clickAction(self.currentB,[pos.getX(),pos.getY()])

if __name__ == "__main__":
    Gui = GUI()
    Gui.run()