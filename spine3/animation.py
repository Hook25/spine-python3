from . import timelines

def read_curve(timeline, key_frame_index, value_map):
    try:
        curve = value_map['curve']
    except KeyError:
        return timeline

    if curve == 'stepped':
        timeline.set_stepped(key_frame_index)
    else:
        timeline.set_curve(
            key_frame_index, 
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

        for bone_name in bones.keys():
            bone_index = skeleton_data.find_bone_index(bone_name)
            if bone_index == -1:
                raise Exception('Bone not found: %s' % bone_name)
            
            timeline_map = bones[bone_name]

            for timeline_name in timeline_map.keys():
                values = timeline_map[timeline_name]
                
                if timeline_name == 'rotate':
                    timeline_inst = timelines.RotateTimeline(len(values))
                    timeline_inst.bone_index = bone_index
                    
                    key_frame_index = 0
                    for value_map in values:
                        time = value_map['time']
                        timeline_inst.set_keyframe(key_frame_index, time, value_map['angle'])
                        timeline_inst = read_curve(timeline_inst, key_frame_index, value_map)
                        key_frame_index += 1
                    timelines_lst.append(timeline_inst)
                    if timeline_inst.get_duration() > duration:
                        duration = timeline_inst.get_duration()
                elif timeline_name == 'translate' or timeline_name == 'scale':
                    timeline_inst = None
                    timelineScale = 1.0
                    if timeline_name == 'scale':
                        timeline_inst = timelines.ScaleTimeline(len(values))
                    else:
                        timeline_inst = timelines.TranslateTimeline(len(values))
                        timelineScale = scale
                    timeline_inst.bone_index = bone_index
                    
                    key_frame_index = 0
                    for value_map in values:
                        time = value_map['time']
                        timeline_inst.set_keyframe(key_frame_index,
                                             value_map['time'],
                                             value_map.get('x', 0.0),
                                             value_map.get('y', 0.0))
                        timeline_inst = read_curve(timeline_inst, key_frame_index, value_map)
                        key_frame_index += 1
                    timelines_lst.append(timeline_inst)
                    if timeline_inst.get_duration() > duration:
                        duration = timeline_inst.get_duration()
                else:
                    raise Exception('Invalid timeline type for a bone: %s (%s)' % (timeline_name, bone_name))


        slots = root.get('slots', {})

        for slot_name in slots.keys():
            slot_index = skeleton_data.find_slot_index(slot_name)
            if slot_index == -1:
                raise Exception('Slot not found: %s' % slot_name)
            
            timeline_map = slots[slot_name]
            for timeline_name in timeline_map.keys():
                values = timeline_map[timeline_name]
                if timeline_name == 'color':
                    timeline_inst = timelines.ColorTimeline(len(values))
                    timeline_inst.slot_index = slot_index
                    
                    key_frame_index = 0
                    for value_map in values:
                        timeline_inst.set_keyframe(key_frame_index, 
                            value_map['time'], 
                            int(value_map['color'][0:2], 16),
                            int(value_map['color'][2:4], 16),
                            int(value_map['color'][4:6], 16),
                            int(value_map['color'][6:8], 16)
                        )
                        timeline_inst = read_curve(timeline_inst, key_frame_index, value_map)
                        key_frame_index += 1
                    timelines_lst.append(timeline_inst)
                    if timeline_inst.get_duration > duration:
                        duration = timeline_inst.get_duration()

                elif timeline_name == 'attachment':
                    timeline_inst = timelines.AttachmentTimeline(len(values))
                    timeline_inst.slot_index = slot_index
                    
                    key_frame_index = 0
                    for value_map in values:
                        value_name = value_map['name']
                        timeline_inst.set_keyframe(key_frame_index, value_map['time'], '' if not value_name else value_name)
                        key_frame_index += 1
                    timelines_lst.append(timeline_inst)
                    if timeline_inst.get_duration() > duration:
                        duration = timeline_inst.get_duration()
                else:
                    raise Exception('Invalid timeline type for a slot: %s (%s)' % (timeline_name, slot_name))

        animation = Animation(name, timelines_lst, duration)
        return animation
                        
