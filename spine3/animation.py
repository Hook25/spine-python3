from . import timelines

class Animation:
    def __init__(self, name, timelines, duration):
        if not timelines: 
            raise Exception('Timelines cannot be None.')
        self.name = name
        self.timelines = timelines
        self.duration = duration

    def mix(self, skeleton, time, loop, alpha):
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
    def build_bone_timeline(timeline_name, keyframes, bone_index):
        if timeline_name == 'rotate':
            timeline_inst = timelines.RotateTimeline(bone_index)
        elif timeline_name == 'scale':
            timeline_inst = timelines.ScaleTimeline(bone_index)
        elif timeline_name == 'translate':
            timeline_inst = timelines.TranslateTimeline(bone_index)
        else:
            raise ValueError("Timeline %s is not supported" % timeline_name)
        timeline_inst.get_keyframes(keyframes)
        return timeline_inst

    @staticmethod
    def build_slot_timeline(timeline_name, keyframes, slot_index):
        if timeline_name == 'color':
            timeline_inst = timelines.ColorTimeline(slot_index)
        elif timeline_name == 'attachment':
            timeline_inst = timelines.AttachmentTimeline(slot_index)
        timeline_inst.get_keyframes(keyframes)
        return timeline_inst

    @staticmethod
    def _build_timelines(dct, id_getter_f, builder_f):
        to_r = []
        for bone_name, timeline_map in dct.items():
            index = id_getter_f(bone_name)
            for (timeline_name, values) in timeline_map.items():
                timeline_inst = builder_f(timeline_name, values, index)
                to_r.append(timeline_inst)

        return to_r

    @classmethod
    def build_from(cls, name, root, skeleton_data, scale):
        timelines_lst =  []

        bones = root.get('bones', {})

        timelines_lst += cls._build_timelines(bones, skeleton_data.find_bone_index,  cls.build_bone_timeline)

        slots = root.get('slots', {})

        timelines_lst += cls._build_timelines(slots, skeleton_data.find_slot_index, cls.build_slot_timeline)

        duration = max(tl.duration for tl in timelines_lst)
        return Animation(name, timelines_lst, duration)
