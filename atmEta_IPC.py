import threading
import termcolor
import time
import traceback
import queue
from collections import deque
from datetime import datetime, timezone, tzinfo

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
        self.__queues    = queues
        
        #Dictionary Formatting of Internal Fast-Call Functions
        self.__messageInterpreters = {_MESSAGETYPE_PRDEDIT:   self.__messageInterpreter_PRDEDIT,
                                      _MESSAGETYPE_PRDREMOVE: self.__messageInterpreter_PRDREMOVE,
                                      _MESSAGETYPE_FAR:       self.__messageInterpreter_FAR,
                                      _MESSAGETYPE_FARR:      self.__messageInterpreter_FARR}

        #Message Control
        self.__PRD = dict()
        for otherProcessName in [processName for processName in self.__queues if processName != self.processName]: 
            self.__PRD[otherProcessName] = dict()
        self.__FARs_MT      = deque()
        self.__FARRs_MT     = deque()
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



    #System -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __logger(self, message, color):
        time_str = datetime.fromtimestamp(time.time()).strftime("%Y/%m/%d %H:%M:%S")
        print(termcolor.colored(f"[IPC@{self.processName}-{time_str}] {message}", color))
    #System END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Process ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __receiveMessages(self):
        #[1]: Instances
        myQueue = self.__queues[self.processName]
        mis     = self.__messageInterpreters
        logger  = self.__logger
        #[2]: Message Receiver Thread Loop
        while self.__continueLoop:
            #[2-1]: Expected Handling
            try: 
                processFrom, messageType, messageContent = myQueue.get(timeout = 1)
                mis[messageType](processFrom, messageContent)
            #[2-2]: On Queue Empty - Simply Ignore (When Queue Timeout Occurs While Being Empty)
            except queue.Empty:
                continue
            #[2-3]: Unexpected Exception (Exception During Loop Discontinuation Can Be Ignored)
            except Exception as e: 
                if self.__continueLoop:
                    logger(message = (f"An Unexpected Error Occurred While Attempting To Receive Message From The Queue\n"
                                      f" * Error:          {e}\n"
                                      f" * Detailed Trace: {traceback.format_exc()}"),
                           color   = 'light_red')

    #---PRDEDIT
    def __messageInterpreter_PRDEDIT(self, processName, content):
        try:
            prdAddress = content[0]
            prdContent = content[1]
            #[1]: Root Target
            target = self.__PRD[processName]
            #[2]: Tuple Or List Address
            if isinstance(prdAddress, (tuple, list)):
                for key in prdAddress[:-1]:
                    target = target[key]
                target[prdAddress[-1]] = prdContent
            #[3]: Singular Address
            else:
                target[prdAddress] = prdContent
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Handle PRD Edit Message\n"
                                     f" * Target Process: {processName}\n"
                                     f" * Content:        {content}\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"),
                          color   = 'light_red')

    #---PRDREMOVE
    def __messageInterpreter_PRDREMOVE(self, processName, content):
        try:
            prdAddress = content[0]
            #[1]: Root Target
            target = self.__PRD[processName]
            #[2]: Tuple Or List Address
            if isinstance(prdAddress, (tuple, list)):
                for key in prdAddress[:-1]:
                    target = target[key]
                del target[prdAddress[-1]]
            #[3]: Singular Address
            else:
                del target[prdAddress]
        except Exception as e: 
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Handle PRD Removal Message\n"
                                     f" * Target Process: {processName}\n"
                                     f" * Content:        {content}\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"),
                          color   = 'light_red')

    #---FAR
    def __messageInterpreter_FAR(self, processName, content):
        #[1]: Identity
        requester = processName
        functionID, functionParams, requestID = content

        #[2]: Function ID Check
        farHandler = self.__FARHandlers.get(functionID, None)
        if farHandler is None:
            if requestID is not None: self.sendFARR(requester, _FAR_INVALIDFUNCTIONID, requestID)
            self.__logger(message = (f"A FAR For An Unregistered Function ID Detected\n"
                                     f" * Requester:       {requester}\n"
                                     f" * Function ID:     {functionID}\n"
                                     f" * Function Params: {functionParams}\n"
                                     f" * Request ID:      {requestID}"),
                          color   = 'light_red')
            return
            
        #[3]: FAR Handling
        hFunc, eThread, immedResponse = farHandler
        #---[3-1]: Handle On Main Thread - Add To Queue
        if eThread == _THREADTYPE_MT: 
            self.__FARs_MT.append((processName, functionID, functionParams, requestID))

        #---[3-2]: Handle On Assistant Thread - Handle Now
        elif eThread == _THREADTYPE_AT:
            try:
                #[2-1-3]: Parameters
                args = [requester,]
                if requestID is not None:
                    args.append(requestID)
                kwargs = functionParams if isinstance(functionParams, dict) else {}

                #[2-1-4]: Function Execution
                functionResult = hFunc(*args, **kwargs)

                #[2-1-5]: Dispatch Result (If Response Is Needed Immediately And Response Is Expected)
                if immedResponse and requestID is not None:
                    self.sendFARR(requester, functionResult, requestID)
            except Exception as e:
                self.__logger(message = (f"An Unexpected Error Occurred While Processing A FAR on Assistant Thread\n"
                                        f" * Error:          {e}\n"
                                        f" * Detailed Trace: {traceback.format_exc()}"),
                              color   = 'light_red')

    #---FARR
    def __messageInterpreter_FARR(self, processName, content):
        #[1]: Identity
        responder = processName
        functionResult, requestID, complete = content

        #[2]: Handler Check
        hFunc, eThread = self.__FARRHandlers[requestID]

        #[3]: FARR Handling
        #---[3-1]: Handle On Main Thread - Add To Queue
        if eThread == _THREADTYPE_MT: 
            self.__FARRs_MT.append((processName,) + content)

        #---[3-2]: Handle On Assistant Thread - Handle Now
        elif eThread == _THREADTYPE_AT:
            try:
                hFunc(responder, requestID, functionResult)
                if complete:
                    self.__retrieveRequestID(requestID)
                    del self.__FARRHandlers[requestID]
            except Exception as e:
                self.__logger(message = (f"An Unexpected Error Occurred While Processing A FARR on Assistant Thread\n"
                                        f" * Error:          {e}\n"
                                        f" * Detailed Trace: {traceback.format_exc()}"),
                              color   = 'light_red')

    #---RID Issuance & Retreival
    def __issueRequestID(self):
        rIDs_avails = self.requestIDs_Availables
        if rIDs_avails: 
            return rIDs_avails.pop()
        else:
            newRequestID = self.requestIDs_nPrepared
            self.requestIDs_nPrepared += 1
            return newRequestID
        
    def __retrieveRequestID(self, requestID):
        rIDs_avails = self.requestIDs_Availables
        if requestID not in rIDs_avails:
            if requestID == self.requestIDs_nPrepared-1 and _RID_INITIALAVAILABLES <= requestID:
                self.requestIDs_nPrepared -= 1
            else: 
                rIDs_avails.add(requestID)
        else:
            self.__logger(message = (f"Unexpected Request ID Retrieval Attempted\n"
                                     f" * RequestID: {requestID}"),
                          color   = 'light_magenta')

    #---MT FAR&FARR Processing
    def processFARs(self):
        #[1]: Instances
        fars_MT     = self.__FARs_MT
        farHandlers = self.__FARHandlers
        logger      = self.__logger
        sendFARR    = self.sendFARR

        while fars_MT:
            #[2-1]: Expected Processing
            try:
                #[2-1-1]: Queue Pop
                requester, functionID, functionParams, requestID = fars_MT.popleft()

                #[2-1-2]: Handler
                farHandler = farHandlers[functionID]
                hFunc, eThread, immedResponse = farHandler

                #[2-1-3]: Parameters
                args = [requester,]
                if requestID is not None:
                    args.append(requestID)
                kwargs = functionParams if isinstance(functionParams, dict) else {}

                #[2-1-4]: Function Execution
                functionResult = hFunc(*args, **kwargs)

                #[2-1-5]: Dispatch Result (If Response Is Needed Immediately And Response Is Expected)
                if immedResponse and requestID is not None:
                    sendFARR(requester, functionResult, requestID)

            #[2-2]: Exception Handling
            except Exception as e:
                logger(message = (f"An Unexpected Error Occurred While Attempting To Process FAR\n"
                                  f" * Error:          {e}\n"
                                  f" * Detailed Trace: {traceback.format_exc()}"),
                       color   = 'light_red')

    def processFARRs(self):
        #[1]: Instances
        farrs_MT     = self.__FARRs_MT
        farrHandlers = self.__FARRHandlers
        logger       = self.__logger
        #[2]: Process Loop
        while farrs_MT:
            #[2-1]: Expected Processing
            try:
                responder, functionResult, requestID, complete = farrs_MT.popleft()
                farrHandlers[requestID][0](responder, requestID, functionResult)
                if complete:
                    self.__retrieveRequestID(requestID)
                    del farrHandlers[requestID]
            #[2-2]: Exception Handling
            except Exception as e:
                logger(message = (f"An Unexpected Error Occurred While Attempting To Process FARR\n"
                                  f" * Error:          {e}\n"
                                  f" * Detailed Trace: {traceback.format_exc()}"),
                       color   = 'light_red')
    #Process END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Interfaces -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __sendMessage(self, targetProcess, msgType, msg):
        try: 
            self.__queues[targetProcess].put((self.processName, msgType, msg))
            return True
        except Exception as e: 
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Send A Message\n"
                                     f" * Target Process: {targetProcess}\n"
                                     f" * Message Type:   {msgType}\n"
                                     f" * Message:        {msg}\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"),
                          color   = 'light_red')
            return False

    def formatPRD(self, processName, prdAddress, prdContent):
        try:
            #[1]: Root Target
            target = self.__PRD[processName]
            #[2]: Tuple Or List Address
            if isinstance(prdAddress, (tuple, list)):
                for key in prdAddress[:-1]:
                    target = target[key]
                target[prdAddress[-1]] = prdContent
            #[3]: Singular Address
            else:
                target[prdAddress] = prdContent
        except Exception as e:
            self.__logger(message = (f"An Unexpected Error Occurred While Attempting To Format PRD\n"
                                     f" * Target Process: {processName}\n"
                                     f" * PRD Address:    {prdAddress}\n"
                                     f" * PRD Content:    {prdContent}\n"
                                     f" * Error:          {e}\n"
                                     f" * Detailed Trace: {traceback.format_exc()}"),
                          color   = 'light_red')

    def getPRD(self, processName, prdAddress):
        try:
            #[1]: Starting Point
            result = self.__PRD[processName]
            #[2]: Tuple or List Address
            if isinstance(prdAddress, (tuple, list)):
                for key in prdAddress:
                    result = result[key]
                return result
            #[3]: Singular Address
            return result[prdAddress]
        except:
            return _PRD_INVALIDADDRESS

    def sendPRDEDIT(self, targetProcess, prdAddress, prdContent):
        return self.__sendMessage(targetProcess = targetProcess, 
                                  msgType       = _MESSAGETYPE_PRDEDIT, 
                                  msg           = (prdAddress, prdContent))

    def sendPRDREMOVE(self, targetProcess, prdAddress):
        return self.__sendMessage(targetProcess = targetProcess, 
                                  msgType       = _MESSAGETYPE_PRDREMOVE, 
                                  msg           = (prdAddress,))

    def removePRD(self, targetProcess, prdAddress):
        try:
            #[1]: Starting Point
            target = self.__PRD[targetProcess]
            #[2]: Tuple or List Address
            if isinstance(prdAddress, (tuple, list)):
                for key in prdAddress[:-1]:
                    target = target[key]
                del target[prdAddress[-1]]
            #[3]: Singular Address
            else:
                del target[prdAddress]
        except: pass

    def sendFAR(self, targetProcess, functionID, functionParams, farrHandler = None, farrHandlerThread = _THREADTYPE_MT):
        #[1]: Handler Thread Check
        if farrHandlerThread not in _THREADTYPES: 
            self.__logger(message = (f"An Unexpected FARR Handler Thread Type Detected While Attempting To Send FAR\n"
                                     f" * FARR Handler Thread: {farrHandlerThread}"),
                          color   = 'light_red')
            return None

        #[2]: Request ID
        requestID = None if farrHandler is None else self.__issueRequestID()

        #[3]: Message Dispatch Attempt
        if self.__sendMessage(targetProcess = targetProcess, 
                              msgType       = _MESSAGETYPE_FAR, 
                              msg           = (functionID, functionParams, requestID)):
            if requestID is not None: 
                self.__FARRHandlers[requestID] = (farrHandler, farrHandlerThread)
            return requestID
        else: 
            return None
        
    def sendFARR(self, targetProcess, functionResult, requestID, complete = True):
        return self.__sendMessage(targetProcess = targetProcess, 
                                  msgType       = _MESSAGETYPE_FARR, 
                                  msg           = (functionResult, requestID, complete))

    def addFARHandler(self, functionID, handlerFunction, executionThread, immediateResponse = True):
        self.__FARHandlers[functionID] = (handlerFunction, 
                                          executionThread, 
                                          immediateResponse)

    def removeFARHandler(self, functionID):
        self.__FARHandlers.pop(functionID, None)
    #Interfaces END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    