from . import timelines

def readCurve(timeline, keyframeIndex, valueMap):
    try:
        curve = valueMap['curve']
    except KeyError:
        return timeline

    if curve == 'stepped':
        timeline.setStepped(keyframeIndex)
    else:
        timeline.setCurve(
            keyframeIndex, 
            *(float(x) for x in curve)
        )
    return timeline

class Animation:
    def __init__(self, name, timelines, duration):
        if not timelines: 
            raise Exception('Timelines cannot be None.')
        self.name = name
        self.timelines = timelines
        self.duration = duration

    def mix(self, skeleton, time, loop, alpha):
        if not skeleton:
            raise Exception('Skeleton cannot be None.')

        if loop and self.duration:
            time = time % self.duration
        if loop and self.duration:
            time = time % self.duration

        for timeline in self.timelines:
            timeline.apply(skeleton, time, alpha)

    def apply(self, skeleton, time, loop):
        if not skeleton:
            raise Exception('Skeleton cannot be None.')
        
        if loop and self.duration:
            time = time % self.duration

        for timeline in self.timelines:
            timeline.apply(skeleton, time, 1)

    @classmethod
    def build_from(cls, name, root, skeleton_data, scale):
        if not skeleton_data:
            raise Exception('skeleton_data cannot be null.')

        timelines_lst =  []
        duration = 0.0

        bones = root.get('bones', {})

        for boneName in bones.keys():
            boneIndex = skeleton_data.findBoneIndex(boneName)
            if boneIndex == -1:
                raise Exception('Bone not found: %s' % boneName)
            
            timelineMap = bones[boneName]

            for timelineName in timelineMap.keys():
                values = timelineMap[timelineName]
                
                if timelineName == 'rotate':
                    timeline_inst = timelines.RotateTimeline(len(values))
                    timeline_inst.boneIndex = boneIndex
                    
                    keyframeIndex = 0
                    for valueMap in values:
                        time = valueMap['time']
                        timeline_inst.setKeyframe(keyframeIndex, time, valueMap['angle'])
                        timeline_inst = readCurve(timeline_inst, keyframeIndex, valueMap)
                        keyframeIndex += 1
                    timelines_lst.append(timeline_inst)
                    if timeline_inst.getDuration() > duration:
                        duration = timeline_inst.getDuration()
                elif timelineName == 'translate' or timelineName == 'scale':
                    timeline_inst = None
                    timelineScale = 1.0
                    if timelineName == 'scale':
                        timeline_inst = timelines.ScaleTimeline(len(values))
                    else:
                        timeline_inst = timelines.TranslateTimeline(len(values))
                        timelineScale = scale
                    timeline_inst.boneIndex = boneIndex
                    
                    keyframeIndex = 0
                    for valueMap in values:
                        time = valueMap['time']
                        timeline_inst.setKeyframe(keyframeIndex,
                                             valueMap['time'],
                                             valueMap.get('x', 0.0),
                                             valueMap.get('y', 0.0))
                        timeline_inst = readCurve(timeline_inst, keyframeIndex, valueMap)
                        keyframeIndex += 1
                    timelines_lst.append(timeline_inst)
                    if timeline_inst.getDuration() > duration:
                        duration = timeline_inst.getDuration()
                else:
                    raise Exception('Invalid timeline type for a bone: %s (%s)' % (timelineName, boneName))


        slots = root.get('slots', {})

        for slotName in slots.keys():
            slotIndex = skeleton_data.findSlotIndex(slotName)
            if slotIndex == -1:
                raise Exception('Slot not found: %s' % slotName)
            
            timelineMap = slots[slotName]
            for timelineName in timelineMap.keys():
                values = timelineMap[timelineName]
                if timelineName == 'color':
                    timeline_inst = timelines.ColorTimeline(len(values))
                    timeline_inst.slotIndex = slotIndex
                    
                    keyframeIndex = 0
                    for valueMap in values:
                        timeline_inst.setKeyframe(keyframeIndex, 
                                             valueMap['time'], 
                                             int(valueMap['color'][0:2], 16),
                                             int(valueMap['color'][2:4], 16),
                                             int(valueMap['color'][4:6], 16),
                                             int(valueMap['color'][6:8], 16))
                        timeline_inst = readCurve(timeline_inst, keyframeIndex, valueMap)
                        keyframeIndex += 1
                    timelines_lst.append(timeline_inst)
                    if timeline_inst.getDuration > duration:
                        duration = timeline_inst.getDuration()

                elif timelineName == 'attachment':
                    timeline_inst = timelines.AttachmentTimeline(len(values))
                    timeline_inst.slotIndex = slotIndex
                    
                    keyframeIndex = 0
                    for valueMap in values:
                        valueName = valueMap['name']
                        timeline_inst.setKeyframe(keyframeIndex, valueMap['time'], '' if not valueName else valueName)
                        keyframeIndex += 1
                    timelines_lst.append(timeline_inst)
                    if timeline_inst.getDuration() > duration:
                        duration = timeline_inst.getDuration()
                else:
                    raise Exception('Invalid timeline type for a slot: %s (%s)' % (timelineName, slotName))

        animation = Animation(name, timelines_lst, duration)
        return animation
                        
