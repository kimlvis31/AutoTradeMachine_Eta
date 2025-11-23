import torch
import numpy

_NUMPYDTYPE = numpy.float32
_TORCHDTYPE = torch.float32
if (torch.cuda.is_available() == True): _TORCHDEVICE = 'cuda'
else:                                   _TORCHDEVICE = 'cpu'

_ANALYSISINPUTSIZE = {'SMA':        1,
                      'WMA':        1,
                      'EMA':        1,
                      'PSAR':       1,
                      'BOL':        3,
                      'IVP':        4,
                      'VOL':        1,
                      'MMACDSHORT': 1,
                      'MMACDLONG':  1,
                      'DMIxADX':    1,
                      'MFI':        1}

class neuralNetwork_MLP():
    def __init__(self, nKlines, analysisReferences, hiddenLayers, outputLayer, initialization = None, device = _TORCHDEVICE):
        #Network
        self.__nKlines            = nKlines
        self.__analysisReferences = analysisReferences
        self.__nAnalysisInputs    = sum([_ANALYSISINPUTSIZE[_aCode.split("_")[0]] for _aCode in analysisReferences])
        self.__device             = device
        self.__dimensions = {'inputLayer':   {'size': self.__nKlines*(6+self.__nAnalysisInputs)},
                             'hiddenLayers': hiddenLayers,
                             'outputLayer':  {'size': 1, 'type': outputLayer['type'], 'params': outputLayer['params']}}
        #Data Loader
        self.__dataSet               = None
        self.__dataSet_batchSize     = None
        self.__dataSet_nBatches      = None
        self.__dataSet_batchIndex    = None
        self.__dataSet_shuffle       = False
        self.__dataSet_accessIndexes = None
        #Neural Network Model
        self.__nnModel = torch.nn.Sequential()
        for _hlIndex, _hl in enumerate(self.__dimensions['hiddenLayers']):
            if (_hlIndex == 0): 
                self.__nnModel.append(torch.nn.Linear(in_features = self.__dimensions['inputLayer']['size'], out_features = _hl['size'], bias = True, device = self.__device, dtype = _TORCHDTYPE))
                if   (_hl['type'] == 'SIGMOID'): self.__nnModel.append(torch.nn.Sigmoid())
                elif (_hl['type'] == 'RELU'):    self.__nnModel.append(torch.nn.ReLU())
                elif (_hl['type'] == 'LEAKYRELU'):
                    if ('negative_slope' in _hl['params']): self.__nnModel.append(torch.nn.LeakyReLU(negative_slope = _hl['params']['negative_slope']))
                    else:                                   self.__nnModel.append(torch.nn.LeakyReLU())
                elif (_hl['type'] == 'SOFTMAX'): self.__nnModel.append(torch.nn.Softmax(dim = 0))
                elif (_hl['type'] == 'HTAN'):    self.__nnModel.append(torch.nn.Tanh())
            else:
                self.__nnModel.append(torch.nn.Linear(in_features = self.__dimensions['hiddenLayers'][_hlIndex-1]['size'], out_features = _hl['size'], bias = True, device = self.__device, dtype = _TORCHDTYPE))
                if   (_hl['type'] == 'SIGMOID'): self.__nnModel.append(torch.nn.Sigmoid())
                elif (_hl['type'] == 'RELU'):    self.__nnModel.append(torch.nn.ReLU())
                elif (_hl['type'] == 'LEAKYRELU'): 
                    if ('negative_slope' in _hl['params']): self.__nnModel.append(torch.nn.LeakyReLU(negative_slope = _hl['params']['negative_slope']))
                    else:                                   self.__nnModel.append(torch.nn.LeakyReLU())
                elif (_hl['type'] == 'SOFTMAX'): self.__nnModel.append(torch.nn.Softmax(dim = 0))
                elif (_hl['type'] == 'HTAN'):    self.__nnModel.append(torch.nn.Tanh())
        self.__nnModel.append(torch.nn.Linear(in_features = self.__dimensions['hiddenLayers'][-1]['size'], out_features = self.__dimensions['outputLayer']['size'], bias = True, device = self.__device, dtype = _TORCHDTYPE))
        if   (self.__dimensions['outputLayer']['type'] == 'SIGMOID'): self.__nnModel.append(torch.nn.Sigmoid())
        elif (self.__dimensions['outputLayer']['type'] == 'RELU'):    self.__nnModel.append(torch.nn.ReLU())
        elif (self.__dimensions['outputLayer']['type'] == 'LEAKYRELU'):
            if ('negative_slope' in self.__dimensions['outputLayer']['params']): self.__nnModel.append(torch.nn.LeakyReLU(negative_slope = self.__dimensions['outputLayer']['params']['negative_slope']))
            else:                                                                self.__nnModel.append(torch.nn.LeakyReLU())
        elif (self.__dimensions['outputLayer']['type'] == 'SOFTMAX'): self.__nnModel.append(torch.nn.Softmax(dim = 0))
        elif (self.__dimensions['outputLayer']['type'] == 'HTAN'):    self.__nnModel.append(torch.nn.Tanh())
        self.__optimizer    = None
        self.__lossFunction = None
        if (initialization != None): self.initializeParameters(initialization = initialization)

    def initializeParameters(self, initialization):
        _tensors_bias   = dict()
        _tensors_weight = dict()
        _nHiddenLayers = len(self.__dimensions['hiddenLayers'])
        #---Format Weight Arrays
        for _hiddenLayerIndex in range (0, _nHiddenLayers): _tensors_bias['{:d}'.format(_hiddenLayerIndex)] = torch.zeros(size = (self.__dimensions['hiddenLayers'][_hiddenLayerIndex]['size'],), device = self.__device, dtype = _TORCHDTYPE, requires_grad = True)
        _tensors_bias['o'] = torch.zeros(size = (self.__dimensions['outputLayer']['size'],), device = self.__device, dtype = _TORCHDTYPE, requires_grad = True)
        #---Format Weight Arrays
        _tensors_weight['i-0'] = torch.empty(size = (self.__dimensions['hiddenLayers'][0]['size'], self.__dimensions['inputLayer']['size']), device = self.__device, dtype = _TORCHDTYPE, requires_grad = True)
        for _hiddenLayerIndex in range (0, _nHiddenLayers-1): _tensors_weight['{:d}-{:d}'.format(_hiddenLayerIndex, _hiddenLayerIndex+1)] = torch.empty(size = (self.__dimensions['hiddenLayers'][_hiddenLayerIndex+1]['size'], self.__dimensions['hiddenLayers'][_hiddenLayerIndex]['size']), device = self.__device, dtype = _TORCHDTYPE, requires_grad = True)
        _tensors_weight['{:d}-o'.format(_nHiddenLayers-1)] = torch.empty(size = (self.__dimensions['outputLayer']['size'], self.__dimensions['hiddenLayers'][-1]['size']), device = self.__device, dtype = _TORCHDTYPE, requires_grad = True)
        #---Initialization
        try:
            _initType   = initialization['type']
            _initParams = initialization['params']
            if   (_initType == 'UNIFORM'):   _initFunc = torch.nn.init.uniform_
            elif (_initType == 'NORMAL'):    _initFunc = torch.nn.init.normal_
            elif (_initType == 'X_UNIFORM'): _initFunc = torch.nn.init.xavier_uniform_
            elif (_initType == 'X_NORMAL'):  _initFunc = torch.nn.init.xavier_normal_
            elif (_initType == 'K_UNIFORM'): _initFunc = torch.nn.init.kaiming_uniform_
            elif (_initType == 'K_NORMAL'):  _initFunc = torch.nn.init.kaiming_normal_
            _tensors_weight['i-0'] = _initFunc(tensor = _tensors_weight['i-0'], **_initParams)
            for _hiddenLayerIndex in range (0, _nHiddenLayers-1): _tensors_weight['{:d}-{:d}'.format(_hiddenLayerIndex, _hiddenLayerIndex+1)] = _initFunc(tensor = _tensors_weight['{:d}-{:d}'.format(_hiddenLayerIndex, _hiddenLayerIndex+1)], **_initParams)
            _tensors_weight['{:d}-o'.format(_nHiddenLayers-1)] = _initFunc(tensor = _tensors_weight['{:d}-o'.format(_nHiddenLayers-1)], **_initParams)
        except Exception as e: return str(e)
        #---Apply new parameters
        for _pIndex, _param in enumerate(self.__nnModel.parameters()):
            _layerIndex = int(_pIndex/2)
            #Weight
            if (_pIndex % 2 == 0):
                if   (_layerIndex == 0):              _layerConnectivity = 'i-0'
                elif (_layerIndex == _nHiddenLayers): _layerConnectivity = '{:d}-o'.format(_layerIndex-1)
                else:                                 _layerConnectivity = '{:d}-{:d}'.format(_layerIndex-1, _layerIndex)
                _param.data = _tensors_weight[_layerConnectivity]
            #Bias
            else:
                if (_layerIndex == _nHiddenLayers): _layerAddress = 'o'
                else:                               _layerAddress = '{:d}'.format(_layerIndex)
                _param.data = _tensors_bias[_layerAddress]
        #---Return 'True' to indicate successful initialization
        return True

    def getNKlines(self):
        return self.__nKlines

    def getAnalysisReferences(self):
        return self.__analysisReferences

    def getNAnalysisInputs(self):
        return self.__nAnalysisInputs

    def getConnections(self):
        _connections = list()
        _nHiddenLayers = len(self.__dimensions['hiddenLayers'])
        for _pIndex, _tensor in enumerate(self.__nnModel.parameters()):
            _layerIndex = int(_pIndex/2)
            #Weight
            if (_pIndex % 2 == 0):
                if   (_layerIndex == 0):              _layerConnectivity = 'i-0'
                elif (_layerIndex == _nHiddenLayers): _layerConnectivity = '{:d}-o'.format(_layerIndex-1)
                else:                                 _layerConnectivity = '{:d}-{:d}'.format(_layerIndex-1, _layerIndex)
                for _tensorAddress_r in range (len(_tensor)):
                    _tensor_row = _tensor[_tensorAddress_r]
                    for _tensorAddress_c in range (len(_tensor_row)): _connections.append(('weight', _layerConnectivity, (_tensorAddress_r, _tensorAddress_c), "{:.25f}".format(_tensor_row[_tensorAddress_c])))
            #Bias
            else:
                if (_layerIndex == _nHiddenLayers): _layerAddress = 'o'
                else:                               _layerAddress = '{:d}'.format(_layerIndex)
                for _tensorAddress in range (len(_tensor)): _connections.append(('bias', _layerAddress, _tensorAddress, "{:.25f}".format(_tensor[_tensorAddress])))
        return _connections

    def importConnectionsData(self, connections):
        _numpys_bias   = dict()
        _numpys_weight = dict()
        _nHiddenLayers = len(self.__dimensions['hiddenLayers'])
        #---Numpy Format Bias Arrays
        for _hiddenLayerIndex in range (0, _nHiddenLayers): _numpys_bias['{:d}'.format(_hiddenLayerIndex)] = numpy.zeros(shape = (self.__dimensions['hiddenLayers'][_hiddenLayerIndex]['size'],), dtype = _NUMPYDTYPE)
        _numpys_bias['o'] = numpy.zeros(shape = (self.__dimensions['outputLayer']['size'],), dtype = _NUMPYDTYPE)
        #---Numpy Format Weight Arrays
        _numpys_weight['i-0'] = numpy.zeros(shape = (self.__dimensions['hiddenLayers'][0]['size'], self.__dimensions['inputLayer']['size']), dtype = _NUMPYDTYPE)
        for _hiddenLayerIndex in range (0, _nHiddenLayers-1): _numpys_weight['{:d}-{:d}'.format(_hiddenLayerIndex, _hiddenLayerIndex+1)] = numpy.zeros(shape = (self.__dimensions['hiddenLayers'][_hiddenLayerIndex+1]['size'], self.__dimensions['hiddenLayers'][_hiddenLayerIndex]['size']), dtype = _NUMPYDTYPE)
        _numpys_weight['{:d}-o'.format(_nHiddenLayers-1)] = numpy.zeros(shape = (self.__dimensions['outputLayer']['size'], self.__dimensions['hiddenLayers'][-1]['size']), dtype = _NUMPYDTYPE)
        #---Network Data Import
        for _connection in connections:
            _type = _connection[0]
            if (_type == 'bias'): 
                _layerAddress = _connection[1]
                _arrayAddress = _connection[2]
                _value        = _NUMPYDTYPE(_connection[3])
                _numpys_bias[_layerAddress][_arrayAddress] = _value
            elif (_type == 'weight'):
                _layerConnectivity = _connection[1]
                _arrayAddress      = _connection[2]
                _value             = _NUMPYDTYPE(_connection[3])
                _numpys_weight[_layerConnectivity][_arrayAddress[0]][_arrayAddress[1]] = _value
        #---Update parameters
        _tensors_bias = dict(); _tensors_weight = dict()
        for _layerAddress      in _numpys_bias:   _tensors_bias[_layerAddress]        = torch.tensor(data = _numpys_bias[_layerAddress],        device = self.__device, dtype = _TORCHDTYPE)
        for _layerConnectivity in _numpys_weight: _tensors_weight[_layerConnectivity] = torch.tensor(data = _numpys_weight[_layerConnectivity], device = self.__device, dtype = _TORCHDTYPE)
        for _pIndex, _param in enumerate(self.__nnModel.parameters()):
            _layerIndex = int(_pIndex/2)
            #Weight
            if (_pIndex % 2 == 0):
                if   (_layerIndex == 0):              _layerConnectivity = 'i-0'
                elif (_layerIndex == _nHiddenLayers): _layerConnectivity = '{:d}-o'.format(_layerIndex-1)
                else:                                 _layerConnectivity = '{:d}-{:d}'.format(_layerIndex-1, _layerIndex)
                _param.data = _tensors_weight[_layerConnectivity]
            #Bias
            else:
                if (_layerIndex == _nHiddenLayers): _layerAddress = 'o'
                else:                               _layerAddress = '{:d}'.format(_layerIndex)
                _param.data = _tensors_bias[_layerAddress]

    def loadDataSet(self, dataSet, batch_size, shuffle = False):
        self.__dataSet = torch.tensor(data = dataSet, device = self.__device, dtype = _TORCHDTYPE, requires_grad = False)
        return self.updateBatchSize(batch_size = batch_size, shuffle = shuffle)

    def updateBatchSize(self, batch_size, shuffle = False):
        self.__dataSet_batchSize = batch_size
        _nSamples = self.__dataSet.size()[0]
        if (_nSamples % batch_size == 0): self.__dataSet_nBatches = int(_nSamples/self.__dataSet_batchSize)
        else:                             self.__dataSet_nBatches = int(_nSamples/self.__dataSet_batchSize)+1
        self.__dataSet_batchIndex = 0
        self.__dataSet_shuffle    = shuffle
        if (self.__dataSet_shuffle == True): self.__dataSet_accessIndexes = torch.randperm(n = _nSamples, device = self.__device)
        else:                                self.__dataSet_accessIndexes = torch.arange(start = 0, end = _nSamples, device = self.__device)
        return self.__dataSet_nBatches

    def unloadDataSet(self):
        self.__dataSet               = None
        self.__dataSet_batchSize     = None
        self.__dataSet_nBatches      = None
        self.__dataSet_batchIndex    = None
        self.__dataSet_shuffle       = False
        self.__dataSet_accessIndexes = None
        torch.cuda.empty_cache()

    def resetIterator(self):
        self.__dataSet_batchIndex = 0
        if (self.__dataSet_shuffle == True): self.__dataSet_accessIndexes = torch.randperm(self.__dataSet.size()[0], device = self.__device)

    def setOptimizer(self, learningRate, optimizerDescription):
        _optimizerType   = optimizerDescription['type']
        _optimizerParams = optimizerDescription['params']
        if (_optimizerParams == None): _optimizerParams = dict()
        if   (_optimizerType == 'SGD'):     self.__optimizer = torch.optim.SGD(params     = self.__nnModel.parameters(), lr=learningRate, **_optimizerParams)
        elif (_optimizerType == 'Adam'):    self.__optimizer = torch.optim.Adam(params    = self.__nnModel.parameters(), lr=learningRate, **_optimizerParams)
        elif (_optimizerType == 'RMSprop'): self.__optimizer = torch.optim.RMSprop(params = self.__nnModel.parameters(), lr=learningRate, **_optimizerParams)
        elif (_optimizerType == 'Adagrad'): self.__optimizer = torch.optim.Adagrad(params = self.__nnModel.parameters(), lr=learningRate, **_optimizerParams)
        elif (_optimizerType == 'AdamW'):   self.__optimizer = torch.optim.AdamW(params   = self.__nnModel.parameters(), lr=learningRate, **_optimizerParams)
        else:                               self.__optimizer = torch.optim.SGD(params     = self.__nnModel.parameters(), lr=learningRate, **_optimizerParams)

    def setLossFunction(self, lossFunctionDescription):
        _lossFunctionType   = lossFunctionDescription['type']
        _lossFunctionParams = lossFunctionDescription['params']
        if (_lossFunctionParams == None): _lossFunctionParams = dict()
        if   (_lossFunctionType == 'MSE'): self.__lossFunction = torch.nn.MSELoss(**_lossFunctionParams)
        elif (_lossFunctionType == 'MAE'): self.__lossFunction = torch.nn.L1Loss(**_lossFunctionParams)
        elif (_lossFunctionType == 'BCE'): self.__lossFunction = torch.nn.BCELoss(**_lossFunctionParams)

    def setTrainMode(self):
        self.__nnModel.train()

    def setEvaluationMode(self):
        self.__nnModel.eval()

    def forward(self, inputData):
        return self.__nnModel(inputData)

    def evaluateBatch(self):
        #Get samples
        _accessIndexes_thisBatch = self.__dataSet_accessIndexes[self.__dataSet_batchIndex*self.__dataSet_batchSize:(self.__dataSet_batchIndex+1)*self.__dataSet_batchSize]
        _idealOutputs = self.__dataSet[_accessIndexes_thisBatch,:1]
        _inputs       = self.__dataSet[_accessIndexes_thisBatch,1:]
        #Update batch index
        self.__dataSet_batchIndex += 1
        if (self.__dataSet_batchIndex == self.__dataSet_nBatches): self.__dataSet_batchIndex = 0
        #Compute outputs
        _outputs = self.__nnModel(_inputs)
        #Find loss
        _loss = self.__lossFunction(_outputs, _idealOutputs)
        #Return result
        return float(_loss.detach().item())

    def trainOnBatch(self):
        #Get samples
        _accessIndexes_thisBatch = self.__dataSet_accessIndexes[self.__dataSet_batchIndex*self.__dataSet_batchSize:(self.__dataSet_batchIndex+1)*self.__dataSet_batchSize]
        _idealOutputs = self.__dataSet[_accessIndexes_thisBatch,:1]
        _inputs       = self.__dataSet[_accessIndexes_thisBatch,1:]
        #Update batch index
        self.__dataSet_batchIndex += 1
        if (self.__dataSet_batchIndex == self.__dataSet_nBatches): self.__dataSet_batchIndex = 0
        #Reset optimizer grads
        self.__optimizer.zero_grad()
        #Compute outputs
        _outputs = self.__nnModel(_inputs)
        #Compute loss
        _loss = self.__lossFunction(_outputs, _idealOutputs)
        #Perform back propagation & parameters update
        _loss.backward()
        self.__optimizer.step()