import random,constraint,sys
class PktGen:
    PARAMETER= (2**4) 
    p = constraint.Problem()
    p.addVariable('data', [[random.randint(0,20) for i in range(15)]])
    p.addVariable('cfgOP',[0,1])
    
    p.addVariable('cfgD',range(1,PARAMETER))
    
    p.addVariable('cfgA',[8])
    p.addVariable('lenD',range(1,PARAMETER))
    
    p.addVariable('overrideBit',[0,1])
    
    
    
    while True:
       p.addConstraint(lambda data: 
                                 sum(data) <= 255 ,
                                 ['data'])
       solution=p.getSolutions()
     
       if solution:
           print('old')
           print(solution[0]['data'])
           break
       else:
           del p._variables['data']
           p.addVariable('data', [[random.randint(0,55) for i in range(15)]])
           print('new')
            
                                        
     
    
    
constr_random_input=PktGen()   


dataIn=random.choice(constr_random_input.solution)
print(dataIn)

    
