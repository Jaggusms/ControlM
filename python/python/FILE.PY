import os
for dirPath, dirNames, fileNames in os.walk(os.getcwd()):
    #print(dirPath, dirNames, fileNames)
    for i in fileNames:  
        if not i.endswith(".py"):
            #os.remove(os.path.join(dirPath,i))
            print(i)

