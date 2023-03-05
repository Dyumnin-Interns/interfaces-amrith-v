import cocotb
from cocotb.triggers import RisingEdge, Timer,ReadOnly,NextTimeStep,FallingEdge, ReadWrite
from cocotb_bus.drivers import BusDriver
from cocotb_bus.monitors import BusMonitor
import os
import random
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
import constraint
import crv


def scoreboard(actual_value):

    global expected_value
    cocotb.log.info(f'   In Decimal  {str(int(str(actual_value),2))} ')
    assert int(str(actual_value),2) == expected_value.pop(0), "Scoreboard Matching Failed" 

#coverage

@CoverPoint("top.d_in",  # noqa F405
            xf=lambda d_in: d_in,
            bins=[i for i in range(20)]
            )



#@CoverCross("top.cross.D",items=["top.d_in"])



def cvr(d_in):
    pass
   
@CoverPoint("top.d_out",  # noqa F405
            xf=lambda d_out: d_out,
            bins=[i for i in range(256)]
            )
            
def out_cvr(d_out):
    pass
       
    
@cocotb.test()
async def acc_test(dut):

    global expected_value
    
    dut.RST_N.value=1                                                                              #toggle reset
    await Timer(1,'ns')
    dut.RST_N.value=0
    await RisingEdge(dut.CLK)  
    dut.RST_N.value=1

    data_in_list=(crv.dataIn['data'])
    lenD=(crv.dataIn['lenD'])
    cfgA=(crv.dataIn['cfgA'])
    cfgOP=(crv.dataIn['cfgOP'])
    cfgD=(crv.dataIn['cfgD'])
    overrideBit=(crv.dataIn['overrideBit'])
    
    
    input_driver= InputDriver(dut,'din',dut.CLK)                                                   #create an object 'input_driver' of class InputDriver, this will be the input driver
    out_driver=OutputDriver(dut,'dout',dut.CLK,scoreboard)                                         #create an object 'out_driver' of class OutputDriver, this will be the output driver
    

    
    #random.shuffle(data_in_list[0:15])
    data_in=tuple(data_in_list)
    print(data_in)
   
    len_data=lenD
    len_driver= InputDriver(dut,'len',dut.CLK)                                                     #create another object of InputDriver, this will be the len driver 
    len_driver.append(len_data)                                                                    #send the len data to the len driver
    

    
    #config space
    cfg_data=cfgD                                                                                  #cfg data is set to the length of the input data set
    cfg_address= [4,cfgA]                                                                          #cfg address is set 
    cfg_op=cfgOP

    override_bit=overrideBit
    cfg_data_in={"override_bit":override_bit,"len_reg":min(cfg_data,len(data_in))} 
    cfg_dict={ "data": cfg_data_in, "address":cfg_address,"op":cfg_op}
    cfg_driver= ConfigDriver(dut,'cfg',dut.CLK)                                                    #cfg driver object is created from class ConfigDriver, this will be the configuration driver  
    cfg_driver.append(cfg_dict)



  
    for i in range(15):   
        input_driver.append(data_in[i])                                                            #send the input values to be added in sequence using for loop to the input driver
        cvr(data_in[i])

  
          
    cocotb.log.info (f"Cfg Op {cfg_op} Override { override_bit} Address {cfg_address[0]} Cfg Data {cfg_data} len {len_data}")     
   
    #initialize the expected value 
    expected_value=[] 
    
    #Calculate the expected value based on the randomly generated input data 
    while True:
        
        if str(len_driver.bus.data.value)==str(format(len_data,'b').zfill(8)) :
            
            for i in range(len_data):
                expected_value.append(data_in[i])
            break
        elif (cfg_op & override_bit==1 and
                str(cfg_driver.bus.data_in.value)== str(format(cfg_data,'b').zfill(32))):
                
            for i in range(min(cfg_data,len(data_in))):
                expected_value.append(data_in[i]) 
            break
                
        await Timer(10,'ns')
    expected_value=[sum(expected_value)]  

        
    cocotb.log.info(f" Data Input {data_in} Expected value {expected_value}")   
    


 
    
    #Create input and output monitors
    IOMonitor(dut,'din',dut.CLK,callback=cover)                                                          
    IOMonitor(dut,'dout',dut.CLK,callback=cover)  
    
    
   
    while len(expected_value)!=0:                                                                  #run the code as long as the expected output hasn't been popped i.e. run it until assertion 
        await Timer(10,'ns')
    await Timer(500,'ns')   
    out_cvr(int(str(out_driver.bus.data.value),2))    
    coverage_db.report_coverage(cocotb.log.info, bins=True)
    coverage_file = os.path.join(os.getenv('RESULT_PATH', "./"), 'coverage.xml')
    coverage_db.export_to_xml(filename=coverage_file)
   
    
    '''
    len_driver.clear()
    cfg_driver.clear()
    input_driver.clear()
    '''
    
    
 
 
 
            #DRIVERS   


class InputDriver(BusDriver):                                                                      #create the input and len driver. this is inherited from BusDriver
    _signals = ['rdy', 'en', 'data']
    def __init__(self,dut,name,clk):
        BusDriver.__init__(self,dut,name,clk) 
        self.bus.en.value=0                                                                        #set the enable to 0 initially   
        self.clk=clk                                                                               #connect the dut clock to synchronize the drivers


    async def _driver_send(self,value,sync=True):
        for _ in range(random.randint(0,8)):
            await RisingEdge(self.clk)  

        if self.bus.rdy.value!=1:
            await RisingEdge(self.bus.rdy)                                                         #if the rdy line is not asserted, wait until it is 1.
          
        self.bus.en.value=1                                                                        #then set enable to high       
        self.bus.data.value=value                                                                  #the input values to be added or len value to set bits are passed
        await ReadOnly()
        
        if self.bus.rdy.value!=1:
            await Timer(1,'ps')
            self.bus.en.value=0
            await RisingEdge(self.bus.rdy)
            self.bus.en.value=1
        await ReadOnly()   
        await RisingEdge(self.clk)
        self.bus.en.value = 0                                                                      #enable pulse goes low
        await NextTimeStep()
         
        
        


class ConfigDriver(BusDriver):
    _signals = ['rdy', 'en','op', 'data_in','address','data_out']
    def __init__(self,dut,name,clk):
        BusDriver.__init__(self,dut,name,clk) 
        self.bus.en.value=0  
        self.clk=clk    

        

    async def _driver_send(self,value,sync=True):
        
        for _ in range(random.randint(0,8)):
            await RisingEdge(self.clk)  
        
        if self.bus.rdy.value!=1:
            await RisingEdge(self.bus.rdy)
        cocotb.log.info(f" Driver {self}" )      
        self.bus.en.value=1
        self.bus.op.value= value["op"]                                                             #set the op to 0 to read from len port (override en will always be 0) or 1 to read from len register 
        self.bus.address.value=value["address"][0]                                                 #config address may or may not be first set to 4 to toggle the override
        self.bus.data_in.value=value["data"]["override_bit"]                                       #cfg data is set to either 0 or 1 for toggling override
        await ReadOnly()
        await RisingEdge(self.clk)
        self.bus.address.value=value["address"][1]
        self.bus.data_in.value=value["data"]["len_reg"]                                            #after a posedge, seperate the address and data from DS and assign them to respective ports
        await ReadOnly()   
        
        await Timer(20,'ns')
        self.bus.address.value=4                                                                   #Set the address to 4 and cfg_data [1] to trigger the pause line.  
        self.bus.op.value=1 
        self.bus.data_in.value=2                                                                   #set pause
        await ReadOnly()
                                                                          
       
        
        
        await RisingEdge(self.clk)
        self.bus.address.value=0                                                                   #Read the current count, programmed length and busy line at addr 0
        self.bus.op.value=0
        await ReadOnly()
        if self.bus.op.value==0 and self.bus.address.value==0:                                     #continously monitors count, length and busy until the accumulation ends. 
            while True:
                cocotb.log.info(f"Current Count {self.bus.data_out.value & 0xFF} \
                                  Programmed Length {(self.bus.data_out.value)>>8 & 0xFF} \
                                  Busy {(self.bus.data_out.value)>>16 & 0x1}")      
                if (((self.bus.data_out.value & 0xFF) +1) == 
                    (self.bus.data_out.value>>8 & 0xFF)) and self.bus.data_out.value>>16 & 0x1==0:
                    
                    cocotb.log.info(f"Current Count {self.bus.data_out.value & 0xFF} \
                                      Programmed Length {(self.bus.data_out.value)>>8 & 0xFF} \
                                      Busy {(self.bus.data_out.value)>>16 & 0x1}")      
                    break
                await Timer(100,'ns')
                
                
        await RisingEdge(self.clk)

        self.bus.op.value=1
        self.bus.address.value=4
        self.bus.data_in.value=0                                                                   #Turn off pause
        
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
        for _ in range (random.randint(0,8)):
            await RisingEdge(self.clk)
            
        if self.bus.rdy.value!=1:
             await RisingEdge(self.bus.rdy)  
        self.bus.en.value=1
        await ReadOnly()
        self.callback(self.bus.data.value)                                                     #send the accumulator result to the scoreboard for verifying/assertion
        await RisingEdge(self.clk)
        await NextTimeStep()
        self.bus.en.value = 0
   

         
            
            # MONITOR
        
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
            #cocotb.log.info(f" RDY {self.bus.rdy.value} EN {self.bus.en.value}  TXN {txn}")
            self._recv({'previous': prev, 'current': phases[txn]})
            prev = phases[txn] 
            




@CoverPoint(f"top.D.present_state",  # noqa F405
            xf=lambda x: x['current'],
            bins=['Idle', 'Rdy', 'Txn'],
            )
@CoverPoint(f"top.D.previous_state",  # noqa F405
            xf=lambda x: x['previous'],
            bins=['Idle', 'Rdy', 'Txn'],
            )
@CoverCross("top.cross.ifc.D",
            items=[
                "top.D.previous_state", "top.D.present_state"
            ]
            )
                   
def cover(state):
    return state
             
