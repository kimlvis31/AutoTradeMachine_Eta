import multiprocessing
import threading
import termcolor

_MESSAGETYPE_PRDEDIT   = 0
_MESSAGETYPE_PRDREMOVE = 1
_MESSAGETYPE_FAR       = 2
_MESSAGETYPE_FARR      = 3

_THREADTYPE_MT = 0
_THREADTYPE_AT = 1
_THREADTYPES = (_THREADTYPE_MT, _THREADTYPE_AT)

_RID_INITIALAVAILABLES = 1000

_PRD_INVALIDADDRESS    = '#INVALIDADDRESS#'
_FAR_INVALIDFUNCTIONID = '#INVALIDFUNCTIONID#'
class IPCAssistant:
    #Initialization ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, processName, queues):
        self.processName = processName
        self.__ownerProcessLoopCondition = None
        self.__queues    = queues
        
        #Dictionary Formatting of Internal Fast-Call Functions
        self.__messageInterpreters = {_MESSAGETYPE_PRDEDIT:   self.__messageInterpreter_PRDEDIT,
                                      _MESSAGETYPE_PRDREMOVE: self.__messageInterpreter_PRDREMOVE,
                                      _MESSAGETYPE_FAR:       self.__messageInterpreter_FAR,
                                      _MESSAGETYPE_FARR:      self.__messageInterpreter_FARR}
        self.__prdGetters_byIterable = {1:  self.__prdGetter_byI1,
                                        2:  self.__prdGetter_byI2,
                                        3:  self.__prdGetter_byI3,
                                        4:  self.__prdGetter_byI4,
                                        5:  self.__prdGetter_byI5,
                                        6:  self.__prdGetter_byI6,
                                        7:  self.__prdGetter_byI7,
                                        8:  self.__prdGetter_byI8,
                                        9:  self.__prdGetter_byI9,
                                        10: self.__prdGetter_byI10}
        self.__prdEditors_byIterable = {1:  self.__prdEditer_byI1,
                                        2:  self.__prdEditer_byI2,
                                        3:  self.__prdEditer_byI3,
                                        4:  self.__prdEditer_byI4,
                                        5:  self.__prdEditer_byI5,
                                        6:  self.__prdEditer_byI6,
                                        7:  self.__prdEditer_byI7,
                                        8:  self.__prdEditer_byI8,
                                        9:  self.__prdEditer_byI9,
                                        10: self.__prdEditer_byI10}
        self.__prdRemovers_byIterable = {1:  self.__prdRemover_byI1,
                                         2:  self.__prdRemover_byI2,
                                         3:  self.__prdRemover_byI3,
                                         4:  self.__prdRemover_byI4,
                                         5:  self.__prdRemover_byI5,
                                         6:  self.__prdRemover_byI6,
                                         7:  self.__prdRemover_byI7,
                                         8:  self.__prdRemover_byI8,
                                         9:  self.__prdRemover_byI9,
                                         10: self.__prdRemover_byI10}

        #Message Control
        self.__PRD = dict()
        for otherProcessName in [processName for processName in self.__queues if processName != self.processName]: self.__PRD[otherProcessName] = dict()
        self.__FARs_MT  = list()
        self.__FARRs_MT = list()
        self.__FARHandlers  = dict()
        self.__FARRHandlers = dict()

        #RID Control
        self.requestIDs_Availables = set(range(0, _RID_INITIALAVAILABLES))
        self.requestIDs_nPrepared  = len(self.requestIDs_Availables)

        #Assistant Thread
        self.__continueLoop = True
        self.__thread_MessageReceiver = threading.Thread(target = self.__receiveMessages, args = (), daemon = False)
        self.__thread_MessageReceiver.start()
    #Initialization END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Termination ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def terminate(self):
        self.__continueLoop = False
    #Termination END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Process ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __receiveMessages(self):
        while (self.__continueLoop == True):
            try: 
                message = self.__queues[self.processName].get(timeout = 0.01)
                processFrom    = message[0]
                messageType    = message[1]
                messageContent = message[2:]
                self.__messageInterpreters[messageType](processFrom, messageContent)
            except: pass

    #---PRDEDIT
    def __messageInterpreter_PRDEDIT(self, processName, content):
        try:
            prdAddress = content[0]
            prdContent = content[1]
            prdAddress_type = type(prdAddress)
            if   ((prdAddress_type == list) or (prdAddress_type == tuple)): self.__prdEditors_byIterable[len(prdAddress)](processName, prdAddress, prdContent)
            elif ((prdAddress_type == str)  or (prdAddress_type == int)):   self.__PRD[processName][prdAddress] = prdContent
        except Exception as e: print(termcolor.colored("[IPCA@{:s}] PRDEDIT from {:s} failed\n *".format(self.portName, processName), 'light_red'), termcolor.colored(e, 'light_red'))
    def __prdEditer_byI1(self, processName, ad, prdContent):  self.__PRD[processName][ad[0]] = prdContent
    def __prdEditer_byI2(self, processName, ad, prdContent):  self.__PRD[processName][ad[0]][ad[1]] = prdContent
    def __prdEditer_byI3(self, processName, ad, prdContent):  self.__PRD[processName][ad[0]][ad[1]][ad[2]] = prdContent
    def __prdEditer_byI4(self, processName, ad, prdContent):  self.__PRD[processName][ad[0]][ad[1]][ad[2]][ad[3]] = prdContent
    def __prdEditer_byI5(self, processName, ad, prdContent):  self.__PRD[processName][ad[0]][ad[1]][ad[2]][ad[3]][ad[4]] = prdContent
    def __prdEditer_byI6(self, processName, ad, prdContent):  self.__PRD[processName][ad[0]][ad[1]][ad[2]][ad[3]][ad[4]][ad[5]] = prdContent
    def __prdEditer_byI7(self, processName, ad, prdContent):  self.__PRD[processName][ad[0]][ad[1]][ad[0]][ad[3]][ad[4]][ad[5]][ad[6]] = prdContent
    def __prdEditer_byI8(self, processName, ad, prdContent):  self.__PRD[processName][ad[0]][ad[1]][ad[2]][ad[3]][ad[4]][ad[5]][ad[6]][ad[7]] = prdContent
    def __prdEditer_byI9(self, processName, ad, prdContent):  self.__PRD[processName][ad[0]][ad[1]][ad[2]][ad[3]][ad[4]][ad[5]][ad[6]][ad[7]][ad[8]] = prdContent
    def __prdEditer_byI10(self, processName, ad, prdContent): self.__PRD[processName][ad[0]][ad[1]][ad[2]][ad[3]][ad[4]][ad[5]][ad[6]][ad[7]][ad[8]][ad[9]] = prdContent

    #---PRDREMOVE
    def __messageInterpreter_PRDREMOVE(self, processName, content):
        try:
            prdAddress = content[0]
            prdAddress_type = type(prdAddress)
            if   ((prdAddress_type == list) or (prdAddress_type == tuple)): self.__prdRemovers_byIterable[len(prdAddress)](processName, prdAddress)
            elif ((prdAddress_type == str)  or (prdAddress_type == int)):   del self.__PRD[processName][prdAddress]
        except Exception as e: print(termcolor.colored("[IPCA@{:s}] PRDREMOVE from {:s} failed\n *".format(self.portName, processName), 'light_red'), termcolor.colored(e, 'light_red'))
    def __prdRemover_byI1(self, processName, ad):  del self.__PRD[processName][ad[0]]
    def __prdRemover_byI2(self, processName, ad):  del self.__PRD[processName][ad[0]][ad[1]]
    def __prdRemover_byI3(self, processName, ad):  del self.__PRD[processName][ad[0]][ad[1]][ad[2]]
    def __prdRemover_byI4(self, processName, ad):  del self.__PRD[processName][ad[0]][ad[1]][ad[2]][ad[3]]
    def __prdRemover_byI5(self, processName, ad):  del self.__PRD[processName][ad[0]][ad[1]][ad[2]][ad[3]][ad[4]]
    def __prdRemover_byI6(self, processName, ad):  del self.__PRD[processName][ad[0]][ad[1]][ad[2]][ad[3]][ad[4]][ad[5]]
    def __prdRemover_byI7(self, processName, ad):  del self.__PRD[processName][ad[0]][ad[1]][ad[0]][ad[3]][ad[4]][ad[5]][ad[6]]
    def __prdRemover_byI8(self, processName, ad):  del self.__PRD[processName][ad[0]][ad[1]][ad[2]][ad[3]][ad[4]][ad[5]][ad[6]][ad[7]]
    def __prdRemover_byI9(self, processName, ad):  del self.__PRD[processName][ad[0]][ad[1]][ad[2]][ad[3]][ad[4]][ad[5]][ad[6]][ad[7]][ad[8]]
    def __prdRemover_byI10(self, processName, ad): del self.__PRD[processName][ad[0]][ad[1]][ad[2]][ad[3]][ad[4]][ad[5]][ad[6]][ad[7]][ad[8]][ad[9]]

    #---FAR
    def __messageInterpreter_FAR(self, processName, content):
        requester      = processName
        functionID     = content[0]
        functionParams = content[1]
        requestID      = content[2]
        if (functionID in self.__FARHandlers):
            farHandler = self.__FARHandlers[functionID]
            if   (farHandler[1] == _THREADTYPE_MT): self.__FARs_MT.append((processName,) + content)
            elif (farHandler[1] == _THREADTYPE_AT):
                try:
                    mode = 0b00
                    mode |= 0b01*(requestID     !=None)
                    mode |= 0b10*(functionParams!=None)
                    if   (mode == 0b00): functionResult = farHandler[0](requester)
                    elif (mode == 0b01): functionResult = farHandler[0](requester, requestID)
                    elif (mode == 0b10): functionResult = farHandler[0](requester, **functionParams)
                    elif (mode == 0b11): functionResult = farHandler[0](requester, requestID, **functionParams)
                    if ((farHandler[2] == True) and (requestID != None)): self.sendFARR(requester, functionResult, requestID)
                except Exception as e: print(termcolor.colored("[IPCA@{:s}] An unexpected error while attempting to process a FAR at AT\n * (Requester: {:s}, Content: {:s})\n *".format(self.processName, requester, str(content)), 'light_red'), termcolor.colored(e, 'light_red'))
        else:
            if (requestID != None): self.sendFARR(requester, _FAR_INVALIDFUNCTIONID, requestID)

    #---FARR
    def __messageInterpreter_FARR(self, processName, content):
        responder      = processName
        functionResult = content[0]
        requestID      = content[1]
        complete       = content[2]
        farrHandler = self.__FARRHandlers[requestID]
        farrHandler_func   = farrHandler[0]
        farrHandler_thread = farrHandler[1]
        if   (farrHandler_thread == _THREADTYPE_MT): self.__FARRs_MT.append((processName,) + content)
        elif (farrHandler_thread == _THREADTYPE_AT):
            farrHandler_func(responder, requestID, functionResult)
            if (complete == True):
                self.__retrieveRequestID(requestID)
                del self.__FARRHandlers[requestID]

    #---RID Issuance & Retreival
    def __issueRequestID(self):
        if (0 < len(self.requestIDs_Availables)): return self.requestIDs_Availables.pop()
        else: 
            newRequestID = self.requestIDs_nPrepared
            self.requestIDs_nPrepared += 1
            return newRequestID
    def __retrieveRequestID(self, requestID):
        if (requestID not in self.requestIDs_Availables):
            if (requestID == self.requestIDs_nPrepared-1):
                if (_RID_INITIALAVAILABLES <= requestID): self.requestIDs_nPrepared -= 1
            else: self.requestIDs_Availables.add(requestID)
        else: print(termcolor.colored("[IPCA@{:s}] Unexpected requestID retrieval attempted: 'RequestID: {:d}'".format(self.portName, requestID), 'light_red'))

    #---MT FAR&FARR Processing
    def processFARs(self):
        while (0 < len(self.__FARs_MT)):
            far = self.__FARs_MT.pop(0)
            requester      = far[0]
            functionID     = far[1]
            functionParams = far[2]
            requestID      = far[3]
            if (functionID in self.__FARHandlers):
                farHandler = self.__FARHandlers[functionID]
                mode = 0b00
                mode |= 0b01*(requestID     !=None)
                mode |= 0b10*(functionParams!=None)
                if   (mode == 0b00): functionResult = farHandler[0](requester)
                elif (mode == 0b01): functionResult = farHandler[0](requester, requestID)
                elif (mode == 0b10): functionResult = farHandler[0](requester, **functionParams)
                elif (mode == 0b11): functionResult = farHandler[0](requester, requestID, **functionParams)
                if ((farHandler[2] == True) and (requestID != None)): self.sendFARR(requester, functionResult, requestID)
            else:
                if (requestID != None): self.sendFARR(requester, _FAR_INVALIDFUNCTIONID, requestID)
    def processFARRs(self):
        while (0 < len(self.__FARRs_MT)):
            farr = self.__FARRs_MT.pop(0)
            responder      = farr[0]
            functionResult = farr[1]
            requestID      = farr[2]
            complete       = farr[3]
            terminate = self.__FARRHandlers[requestID][0](responder, requestID, functionResult)
            if (complete == True):
                self.__retrieveRequestID(requestID)
                del self.__FARRHandlers[requestID]
    #Process END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Interfaces -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __sendMessage(self, targetProcess, msgType, msg):
        try: self.__queues[targetProcess].put((self.processName, msgType) + msg); return True
        except Exception as e: print(termcolor.colored("[IPCA@{:s}] An unexpected error occurred while attmepting to send a message to '{:s}'\n *".format(self.processName, targetProcess), 'light_red'), termcolor.colored(e, 'light_red')); return False

    def formatPRD(self, processName, prdAddress, prdContent):
        prdAddress_type = type(prdAddress)
        if   ((prdAddress_type == list) or (prdAddress_type == tuple)): self.__prdEditors_byIterable[len(prdAddress)](processName, prdAddress, prdContent)
        elif ((prdAddress_type == str)  or (prdAddress_type == int)):   self.__PRD[processName][prdAddress] = prdContent

    def getPRD(self, processName, prdAddress):
        try:
            prdAddress_type = type(prdAddress)
            if   ((prdAddress_type == list) or (prdAddress_type == tuple)): return self.__prdGetters_byIterable[len(prdAddress)](processName, prdAddress)
            elif ((prdAddress_type == str)  or (prdAddress_type == int)):   return self.__PRD[processName][prdAddress]
        except: return _PRD_INVALIDADDRESS
    def __prdGetter_byI1(self, processName, ad):  return self.__PRD[processName][ad[0]]
    def __prdGetter_byI2(self, processName, ad):  return self.__PRD[processName][ad[0]][ad[1]]
    def __prdGetter_byI3(self, processName, ad):  return self.__PRD[processName][ad[0]][ad[1]][ad[2]]
    def __prdGetter_byI4(self, processName, ad):  return self.__PRD[processName][ad[0]][ad[1]][ad[2]][ad[3]]
    def __prdGetter_byI5(self, processName, ad):  return self.__PRD[processName][ad[0]][ad[1]][ad[2]][ad[3]][ad[4]]
    def __prdGetter_byI6(self, processName, ad):  return self.__PRD[processName][ad[0]][ad[1]][ad[2]][ad[3]][ad[4]][ad[5]]
    def __prdGetter_byI7(self, processName, ad):  return self.__PRD[processName][ad[0]][ad[1]][ad[0]][ad[3]][ad[4]][ad[5]][ad[6]]
    def __prdGetter_byI8(self, processName, ad):  return self.__PRD[processName][ad[0]][ad[1]][ad[2]][ad[3]][ad[4]][ad[5]][ad[6]][ad[7]]
    def __prdGetter_byI9(self, processName, ad):  return self.__PRD[processName][ad[0]][ad[1]][ad[2]][ad[3]][ad[4]][ad[5]][ad[6]][ad[7]][ad[8]]
    def __prdGetter_byI10(self, processName, ad): return self.__PRD[processName][ad[0]][ad[1]][ad[2]][ad[3]][ad[4]][ad[5]][ad[6]][ad[7]][ad[8]][ad[9]]

    def sendPRDEDIT(self, targetProcess, prdAddress, prdContent):
        return self.__sendMessage(targetProcess, _MESSAGETYPE_PRDEDIT, (prdAddress, prdContent))

    def sendPRDREMOVE(self, targetProcess, prdAddress):
        return self.__sendMessage(targetProcess, _MESSAGETYPE_PRDREMOVE, (prdAddress,))

    def removePRD(self, targetProcess, prdAddress):
        try:
            prdAddress_type = type(prdAddress)
            if   ((prdAddress_type == list) or (prdAddress_type == tuple)): self.__prdRemovers_byIterable[len(prdAddress)](targetProcess, prdAddress)
            elif ((prdAddress_type == str)  or (prdAddress_type == int)):   del self.__PRD[targetProcess][prdAddress]
        except: pass

    def sendFAR(self, targetProcess, functionID, functionParams, farrHandler = None, farrHandlerThread = _THREADTYPE_MT):
        if (farrHandlerThread not in _THREADTYPES): raise Exception(termcolor.colored("[IPCA@{:s}] Unacceptable 'farrHandlerThread' passed: '{:s}'".format(self.processName, str(farrHandlerThread)), 'light_red'))
        if (farrHandler == None): requestID = None
        else:                     requestID = self.__issueRequestID()
        msgDispatchResult = self.__sendMessage(targetProcess, _MESSAGETYPE_FAR, (functionID, functionParams, requestID))
        if (msgDispatchResult == True):
            if (requestID != None): self.__FARRHandlers[requestID] = (farrHandler, farrHandlerThread)
            return requestID
        else: return None
        
    def sendFARR(self, targetProcess, functionResult, requestID, complete = True):
        return self.__sendMessage(targetProcess, _MESSAGETYPE_FARR, (functionResult, requestID, complete))

    def addFARHandler(self, functionID, handlerFunction, executionThread, immediateResponse = True):
        self.__FARHandlers[functionID] = (handlerFunction, executionThread, immediateResponse)
    def removeFARHandler(self, functionID):
        if (functionID in self.__FARHandlers): del self.__FARHandlers[functionID]
    #Interfaces END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    