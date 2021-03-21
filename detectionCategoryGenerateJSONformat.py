import json
import collections
from pathlib import Path

supercategoryList = ['exteriorwall', 'corner guard', 'wall protection', 'chairguard',
                 'molding','curtain wall','baseboard', 'column', 'beam','door','door trim',
                 'exterior window','interior window','window trim','window sill','ceiling light','wall mounted light','bathroom vanity light',
                 'base cabinet single','base cabinet double','upper cabinet double','upper cabinet single','vanity cabinet single', 'vanity cabinet double',
                 'countertop ','island countertop','plumbing fixture','hvac','furniture','special equipment',
                 'plumbing','electrical fixture','security','staircase step','staircase handrail','ramp']


entries = Path('D:\\Users\\racha\\Downloads\\HIL_ObjectsDetectionLayout Mar 20 2021 19_05 Rachana\\')

 # define the pattern


currentPattern = "*.JSON"
for currentFile in entries.glob(currentPattern):

    with open(currentFile,mode='r', encoding='utf-8') as f:
        data = json.load(f)
        
    image_width = data['metadata']['width']
    image_height = data['metadata']['height']
    filename = data['metadata']['name']
    
    image_details = {"image": {"width": image_width, "height": image_height,"filename": filename}}
    
    image_info = {"dataset": "Detection_layout",
                  "image": {"width": image_width, "height": image_height,"filename": filename}
                  }
    
    print('&&&&&&&&&&&&&&&&&&&& image_info &&&&&&&&&&&&&&&&&&&&&&&', image_info)
    layoutdict = { 
                 "interior_wall":[], 
                 "floor": [],
                 "ceiling": [],
                 "objects":[]
            }
    
    width_left = [0,0]
    width_right = [0,0]
    height_top = [0,0]
    heightbottom = [0,0]
    baseboard = 'False'
    chairguard = 'False'
    protection = 'False'
    molding = 'Flase'
    
    
    numofwalls = 0
    numofceilings = 0
    numoffloors = 0
    number_of_surface_polygons = {}
    
    attr = []
    wall = 'wall_'
    floor = 'floor_'
    ceiling = 'ceiling_'
    
    
    subcategoryList = []
    detectedsupercategory = set()
    
    ### Function to find the number of walls, ceilings and floor in the given image ###
    
    def number_of_surface_polygons(data):
        
        numofwalls = 0
        numofceilings = 0
        numoffloors = 0
        numOfSurfaces = {}
        
        for i in data['instances']: 
            if i['className'] in supercategoryList:
                detectedsupercategory.add(i['className'] )
             
            attr = i['attributes']
            #print('########### attr ######', attr)
            for dictionary in attr:
                if(dictionary["name"] == 'interior_wall_layout'):
                    numofwalls +=1
                if(dictionary["name"] == 'ceiling_layout'):
                    numofceilings +=1
                if(dictionary["name"] == 'floor_layout'):
                    numoffloors +=1
        numOfSurfaces = {'numofwalls':numofwalls,'numofceilings':numofceilings,'numoffloors':numoffloors, 'detectedsupercategory':detectedsupercategory}
        return numOfSurfaces
         
            
    
    number_of_surface_polygons = number_of_surface_polygons(data)
    
    numofwalls =  number_of_surface_polygons['numofwalls']
    numofceilings = number_of_surface_polygons['numofceilings']
    numoffloors = number_of_surface_polygons['numoffloors']
    detectedsupercategory = number_of_surface_polygons['detectedsupercategory']
    #print('number_of_surface_polygons', numofwalls, numofceilings,numoffloors)  
    
    
    
    def reorderedinstances(data,numofwalls,numoffloors,numofceilings):
        interior_wall_orderedinstances = collections.defaultdict(list)
        ceiling_orderedinstances = collections.defaultdict(list)
        floor_orderedinstances = collections.defaultdict(list)
        objects_orderedinstances = collections.defaultdict(list)
        
        for i in data['instances']:  
            attr = i['attributes']
        
            for x in range(1,numofwalls+1):
                for dictionary in attr:
                    if(dictionary["name"] == wall+str(x)):
                        interior_wall_orderedinstances[wall+str(x)].append(i)
            for x in range(1,numoffloors+1):
                 for dictionary in attr:
                    if(dictionary["name"] == floor+str(x)):
                        floor_orderedinstances[floor+str(x)].append(i)
            for x in range(1,numofceilings+1):
                 for dictionary in attr:
                    if(dictionary["name"] == ceiling+str(x)):
                        ceiling_orderedinstances[ceiling+str(x)].append(i)
            for supercategory in detectedsupercategory:
                if supercategory in i['className']:
                    objects_orderedinstances[supercategory].append(i)
                        
        orderedinstances = {'interior_wall_orderedinstances': interior_wall_orderedinstances,
                            'floor_orderedinstances':floor_orderedinstances,
                            'ceiling_orderedinstances': ceiling_orderedinstances,
                            'objects_orderedinstances': objects_orderedinstances}
        return orderedinstances
    
    
     
    orderedinstances = reorderedinstances(data,numofwalls,numoffloors,numofceilings)
    #print('~~~~~~~~~~~~ orderedinstances ~~~~~~~~~~~~~~~', orderedinstances)
    
    interior_wall_orderedinstances = orderedinstances['interior_wall_orderedinstances']
    #print('interior_wall_orderedinstances', interior_wall_orderedinstances)
    
    
    ######## INTERIOR_WALL _MEASUREMENT ############
    
    measurement_interiorwall={}
    
    interiorwall_detectionCategory = ['concrete','tile','brick','gypsum','wood','wallpaper','texture','others','exception case']
    
    for key in interior_wall_orderedinstances:
        subcategoryList  = []
        detectionList = []
        baseboard = 'False'
        chairguard = 'False'
        protection = 'False'
        molding = 'Flase'
        for i in interior_wall_orderedinstances[key]:
        
            for dictionary in i['attributes']:
                if(dictionary['name']=='width'):
                    width = i['points']
                    #print(width)
                if(dictionary['name']=='height'):
                    height = i['points']
                    #print(height)
                if(dictionary['name']=='interior_wall_layout'):
                    layout = i['points']
                    layout_polygon = [layout[x:x+2] for x in range(0, len(layout), 2)]
                    #print(layout_polygon)
                if(dictionary['name']) == 'molding_true':
                    molding = 'True'
                if(dictionary['name']) == 'baseboard_true':
                    baseboard = 'True'
                if(dictionary['name']) == 'chairguard_true':
                    chairguard = 'True'
                if(dictionary['name']) == 'protection':
                    protection = 'True'
                if(dictionary['name'] in interiorwall_detectionCategory) : 
                    subcategoryList.append(dictionary['name'])
                        
        measurement_interiorwall = {"width_left": [width[0],width[1]],
                  "width_right": [width[2],width[3]],
                  "height_top": [height[0],height[1]],
                  "height_bottom":[height[2],height[3]],
                  "baseboard": baseboard,
                  "chairguard": chairguard,
                  "protection": protection,
                  "molding": molding }
            
        
    
        for sl in subcategoryList:   
            detection = {'subcategory': sl, 'detection_polygon':layout_polygon}
            detectionList.append(detection)
        #print('detectionList',detectionList)
        
        
        interior_wall_dict = {"layout_polygon":layout_polygon,
                          "measurement":measurement_interiorwall,
                          "detection":detectionList}
        
        
        layoutdict['interior_wall'].append (interior_wall_dict)
       # print('%%%%%%%%%%%%%%%%%%%%   layoutdict  %%%%%%%%%%%%%%%%', layoutdict['interior_wall'])
        
     ###################  FLOOR ######################
        
    floorDetectionCategory = ['concrete','tile','laminate','wood','marble','stone','carpet','others','vinyl','exception case']
    thickness_top = []
    thickness_bottom  = []
    level = 0
    
    floor_orderedinstances = orderedinstances['floor_orderedinstances']
    
    for key in floor_orderedinstances:
        floorSubcategoryList  = []
        floorDetectionList = []
        for i in floor_orderedinstances[key]:
        
            for dictionary in i['attributes']:
                try:
                    if(dictionary['name']=='thickness'):
                        #print('################888888888888#####################')
                        thickness = i['points']
                        thickness_top = [thickness[0],thickness[1]]
                        thickness_bottom = [thickness[2],thickness[3]]
                except:
                    #print('#####################################')
                    thickness_top = [], thickness_bottom = []
                    
                if('level' in dictionary['name']):
                    level = dictionary['name'].split('level_')[1]
                    #print('******************************** level*********, level)
                if(dictionary['name']=='floor_layout'):
                    layout = i['points']
                    floor_layout_polygon = [layout[x:x+2] for x in range(0, len(layout), 2)]
                    #print(layout_polygon)
                if(dictionary['name'] in floorDetectionCategory) : 
                    floorSubcategoryList.append(dictionary['name'])
        
               
        measurement_floor = {"thickness_top": "None" if len(thickness_top)==0 else thickness_top, 
                  "thickness_bottom": "None" if len(thickness_bottom)==0 else thickness_bottom, 
                  "level" : level}
            
        #print('measurement_floor', measurement_floor)
    
        for sl in floorSubcategoryList:   
            detection = {'subcategory': sl, 'detection_polygon':floor_layout_polygon}
            floorDetectionList.append(detection)
        #print('detectionList',floorDetectionList)
        
        
        floor_dict = {"layout_polygon":floor_layout_polygon,
                          "measurement":measurement_floor,
                          "detection":floorDetectionList}
        
        #print('********* floorDICT ************',floor_dict)
        layoutdict['floor'].append(floor_dict)
        #print('########  floor_dict  #########', layoutdict)
        
        
    ############### CEILING #########################
        
    ceilingDetectionCategory = ['stucco','concrete','gypsum','wood','others','exposed']
    height_top = []
    height_bottom  = []
    thickness_top = []
    thickness_bottom  = []
    
    ceiling_orderedinstances = orderedinstances['ceiling_orderedinstances']
    
    for key in ceiling_orderedinstances:
        ceilingSubcategoryList  = []
        ceilingDetectionList = []
        for i in ceiling_orderedinstances[key]:
        
            for dictionary in i['attributes']:
                try:
                    if(dictionary['name']=='thickness'):
                        thickness = i['points']
                        thickness_top = [thickness[0],thickness[1]]
                        thickness_bottom = [thickness[2],thickness[3]]
                except:
                        thickness_top = [], thickness_bottom = []
                    
                if(dictionary['name']=='height'):
                       height = i['points']
                       height_top = [height[0],height[1]]
                       height_bottom = [height[2],height[3]]
                       
                if(dictionary['name']=='ceiling_layout'):
                    layout = i['points']
                    ceiling_layout_polygon = [layout[x:x+2] for x in range(0, len(layout), 2)]
                    #print(layout_polygon)
                    
                if(dictionary['name'] in ceilingDetectionCategory) : 
                    ceilingSubcategoryList.append(dictionary['name'])
        
                        
                        
        measurement_ceiling = { "height_top": ["None" if len(height_top)==0 else height[0],height[1]],
                                "height_bottom":["None" if len(height_bottom)==0 else height[2],height[3]],
                                "thickness_top": "None" if len(thickness_top)==0 else thickness_top, 
                                "thickness_bottom": "None" if len(thickness_bottom)==0 else thickness_bottom, 
                             }
            
        #print('measurement_ceiling', measurement_ceiling)
        
        for sl in ceilingSubcategoryList:   
            detection = {'subcategory': sl, 'detection_polygon':ceiling_layout_polygon}
            ceilingDetectionList.append(detection)
        #print('detectionList',ceilingDetectionList)
        
        
        ceiling_dict = {"layout_polygon":ceiling_layout_polygon,
                          "measurement":measurement_ceiling,
                          "detection":ceilingDetectionList}
        
        #print(ceiling_dict)
        layoutdict['ceiling'].append(ceiling_dict)
        #print('layoutdict', layoutdict['ceiling'])
        
        ################# OBJECTS ##############
        objects_orderedinstances = orderedinstances['objects_orderedinstances']
        detected_objects_dict = {'detctedobjects': [] }
        depth_front = []
        depth_back = []
        subcategoryName = 'None'
        for key in objects_orderedinstances:
            #print('KEY', key)
            for i in objects_orderedinstances[key]:
                #print('i', i)
                for dictionary in i['attributes']:
                    if(dictionary['name']=='width'):
                        width = i['points']
                    elif(dictionary['name']=='height'):
                        height = i['points']
                    elif(dictionary['name']=='depth'):
                        depth = i['points']
                        depth_front = [depth[0],depth[1]]
                        depth_back = [depth[2],depth[3]]
                    elif(dictionary['name']=='height'):
                        height = i['points']
                        height_top = [height[0],height[1]]
                        height_bottom = [height[2],height[3]]
                    else:
                        subcategoryName = dictionary['name']

                supercategory = key
                subcategory = subcategoryName
                measurement_objects = {"width_left": [width[0],width[1]],
                                       "width_right": [width[2],width[3]],
                                       "height_top": [height[0],height[1]],
                                       "height_bottom":[height[2],height[3]],
                                       "depth_front": "None" if len(depth_front)==0 else depth_front,
                                       "depth_back": "None" if len(depth_back)==0 else depth_back
                                       }


                objects_dict = {"supercategory":supercategory,
                "subcategory":subcategory,
                "measurement":measurement_objects}
        
            
            detected_objects_dict['detctedobjects'].append(objects_dict )
            #print('########## detected_objects_dict ###########', detected_objects_dict)
    
            layoutdict['objects'] = detected_objects_dict['detctedobjects']

        #print('############# OBJ DICT ###########', layoutdict['objects'])
    #print('@@@@@@@@@@@@layoutdictionary @@@@@@@@@@ ',[image_info,layoutdict])    
    
    # convert into JSON:
    detection_layout = json.dumps([image_info,layoutdict])

# the result is a JSON string:
    #print('********** final data **********', detection_layout)
    
    newFormatFile = currentFile.name+'new'
    
    with open(newFormatFile+'.JSON', 'w') as outfile:
        json.dump([image_info,layoutdict], outfile)

# Closing file 
f.close() 