from . import timelines

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
            time %= self.duration

        for timeline in self.timelines:
            try:
                timeline.apply(skeleton, time, alpha)
            except timelines.SoonError:
                pass

    def apply(self, skeleton, time, loop):
        self.mix(skeleton, time, loop, 1)

    @staticmethod
    def build_timeline_inst(timeline_name, keyframes, bone_index):
        if timeline_name == 'rotate':
            timeline_inst = timelines.RotateTimeline()
        elif timeline_name == 'scale':
            timeline_inst = timelines.ScaleTimeline()
        elif timeline_name == 'translate':
            timeline_inst = timelines.TranslateTimeline()
        else:
            raise ValueError("Timeline %s is not supported" % timeline_name)
        timeline_inst.bone_index = bone_index
                
        timeline_inst.get_keyframes(keyframes)
        return timeline_inst
        
    
    @classmethod
    def build_from(cls, name, root, skeleton_data, scale):
        if not skeleton_data:
            raise Exception('skeleton_data cannot be null.')

        timelines_lst =  []
        duration = 0.0

        bones = root.get('bones', {})

        for bone_name in bones:
            bone_index = skeleton_data.find_bone_index(bone_name)
            timeline_map = bones[bone_name]

            for (timeline_name, values) in timeline_map.items():
                timeline_inst = cls.build_timeline_inst(timeline_name, values, bone_index)
                timelines_lst.append(timeline_inst)
                duration = max(duration, timeline_inst.duration)

        slots = root.get('slots', {})

        for slot_name in slots:
            slot_index = skeleton_data.find_slot_index(slot_name)
            
            timeline_map = slots[slot_name]
            for timeline_name in timeline_map.keys():
                values = timeline_map[timeline_name]
                if timeline_name == 'color':
                    timeline_inst = timelines.ColorTimeline()
                    timeline_inst.slot_index = slot_index
                    
                    key_frame_index = 0
                    for value_map in values:
                        timeline_inst.set_keyframe(
                            key_frame_index, 
                            value_map['time'], 
                            int(value_map['color'][0:2], 16),
                            int(value_map['color'][2:4], 16),
                            int(value_map['color'][4:6], 16),
                            int(value_map['color'][6:8], 16)
                        )
                        timeline_inst.read_curve(key_frame_index, value_map)
                        key_frame_index += 1
                    timelines_lst.append(timeline_inst)
                    if timeline_inst.duration > duration:
                        duration = timeline_inst.duration

                elif timeline_name == 'attachment':
                    timeline_inst = timelines.AttachmentTimeline()
                    timeline_inst.slot_index = slot_index
                    
                    key_frame_index = 0
                    timeline_inst.get_keyframes(values)
                    timelines_lst.append(timeline_inst)
                    if timeline_inst.duration > duration:
                        duration = timeline_inst.duration
                else:
                    raise Exception('Invalid timeline type for a slot: %s (%s)' % (timeline_name, slot_name))

        animation = Animation(name, timelines_lst, duration)
        return animation
                        
