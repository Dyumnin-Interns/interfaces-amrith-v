import cocotb
from cocotb.triggers import RisingEdge, Timer,ReadOnly,NextTimeStep,FallingEdge
from cocotb_bus.drivers import BusDriver
from cocotb_bus.monitors import BusMonitor
import os
import random


def scoreboard(actual_value):

    global expected_value
    #cocotb.log.info('   In Decimal  ' + str(int(str(actual_value),2)))
    assert int(str(actual_value),2) == expected_value.pop(0), "Scoreboard Matching Failed" 
    

    
    
@cocotb.test()
async def acc_test(dut):

    global expected_value
    
    dut.RST_N.value=1                                                                              #toggle reset
    await Timer(1,'ns')
    dut.RST_N.value=0
    await RisingEdge(dut.CLK)  
    dut.RST_N.value=1
    
    #input data
    data_in=(10,20,10,20,40,33,33,34)                                                              #known input data sequence to be added
    input_driver= InputDriver(dut,'din',dut.CLK)                                                   #create an object 'input_driver' of class InputDriver, this will be the input driver
    out_driver=OutputDriver(dut,'dout',dut.CLK,scoreboard)                                         #create an object 'out_driver' of class OutputDriver, this will be the output driver
    
    #config space
    cfg_data_in=random.randint(1,8)                                                                                  #cfg data is set to the length of the desired input
    cfg_address=8                                                                                  #cfg address is set 
    cfg_op=random.randint(0,1)  
    cfg= ConfigDriver(dut,'cfg',dut.CLK)                                                           #cfg driver object is created from class ConfigDriver, this will be the configuration driver  
    cfg_dict={ "data": cfg_data_in, "address":cfg_address,"op":cfg_op}                             #combine the cfg data, op and address
    cfg.append(cfg_dict)                                                                           #queue and send it to the driver
    
    #len data
    len_data=5                                                                                     #set the length of the desired input using the len port
    len_driver= InputDriver(dut,'len',dut.CLK)                                                     #create another object of InputDriver, this will be the len driver 
    len_driver.append(len_data)                                                                    #send the len data to the len driver
    
    #set the expected value 
    expected_value=[] 
    if cfg_op==1:
        for i in range(cfg_data_in):
            expected_value.append(data_in[i])      
    else:
        for i in range(len_data):
            expected_value.append(data_in[i])
        
    expected_value=[sum(expected_value)]

    
    #input and output monitor
    #IOMonitor(dut,'din',dut.CLK,callback=cover)                                                      
    #IOMonitor(dut,'dout',dut.CLK,callback=cover)
          
  
    for i in range(8):
        input_driver.append(data_in[i])                                                            #send the input values to be added in sequence using for loop to the input driver
        await Timer(1,'ns')
    
    while len(expected_value)!=0:                                                                  #run the code as long as the expected output hasn't been popped i.e. run it until assertion 
        await Timer(10,'ns')
        
    await Timer(10,'ns')


class InputDriver(BusDriver):                                                                      #create the input and len driver. this is inherited from BusDriver
    _signals = ['rdy', 'en', 'data']
    def __init__(self,dut,name,clk):
        BusDriver.__init__(self,dut,name,clk) 
        self.bus.en.value=0                                                                        #set the enable to 0 initially   
        self.clk=clk                                                                               #connect the dut clock to synchronize the drivers


    async def _driver_send(self,value,sync=True):
        await RisingEdge(self.clk)  
        if self.bus.rdy.value!=1:
            await RisingEdge(self.bus.rdy)                                                         #if the rdy line is not asserted, wait until it is 1.
     
        self.bus.en.value=1                                                                        #then set enable to high
        self.bus.data.value=value                                                                  #the input values to be added or len value to set bits are passed
        await ReadOnly()
        await RisingEdge(self.clk)
        self.bus.en.value = 0                                                                      #enable pulse goes low
        await NextTimeStep()




class ConfigDriver(BusDriver):
    _signals = ['rdy', 'en','op', 'data_in','address']
    def __init__(self,dut,name,clk):
        BusDriver.__init__(self,dut,name,clk) 
        self.bus.en.value=0  
        self.clk=clk    
        self.bus.op.value=0



    async def _driver_send(self,value,sync=True):
        await RisingEdge(self.clk)
        if self.bus.rdy.value!=1:
            await RisingEdge(self.bus.rdy)
              
        self.bus.en.value=1
        self.bus.op.value= value["op"]                                                             #set the op to 0 to read from len port (override en will always be 0) or 1 to read from len register 
        self.bus.address.value=4                                                                   #config address is first set to 4 to toggle the override
        self.bus.data_in.value=1                                                                   #cfg data is set to 0 or 1 for toggling
        await RisingEdge(self.clk)
        self.bus.address.value=value["address"]
        self.bus.data_in.value=value["data"]                                                       #after a posedge, seperate the address and data and assign them to respective ports
        await ReadOnly()   
        await RisingEdge(self.clk)
        self.bus.en.value = 0                                               
        await NextTimeStep()
        
        
            
      
      


class OutputDriver(BusDriver):
    _signals = ['rdy', 'en', 'data'] 
    def __init__(self, dut, name, clk, sb_callback):
        BusDriver.__init__(self, dut, name, clk) 
        self.clk=clk
        self.bus.en.value=0
        self.callback = sb_callback
        self.append(0)


    async def _driver_send(self,value,sync=True):
        while True:
            await RisingEdge(self.clk)
            if self.bus.rdy.value!=1:
                await RisingEdge(self.bus.rdy)  
            self.bus.en.value=1
            await ReadOnly()
            self.callback(self.bus.data.value)                                                     #send the output accumulator result to the scoreboard for verifying/assertion
            await RisingEdge(self.clk)
            await NextTimeStep()
            self.bus.en.value = 0
   

         
            
            # MONITOR
                           
'''         
class IOMonitor(BusMonitor):
    _signals = ['rdy', 'en', 'data']

    async def _monitor_recv(self):
        fallingedge = FallingEdge(self.clock)        
        rdonly = ReadOnly()
        phases = {
            0: 'Idle',
            1: 'Rdy',
            3: 'Txn'
        }
        prev = 'Idle'
        while True:
            await fallingedge
            await rdonly
            txn = (self.bus.en.value << 1) | self.bus.rdy.value
            #cocotb.log.info(" TXN  =  " + str(txn))
            self._recv({'previous': prev, 'current': phases[txn]})
            prev = phases[txn] 

'''


             
           
