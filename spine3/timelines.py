def binary_search(values, target):
    import bisect
    idx =  bisect.bisect_left(values, target, key=lambda x: x.time)
    return idx

def mod_m180_p180(val):
    return (val + 180) % 360 - 180

class SoonError(Exception): pass

class BezierCurveData:
    BEZIER_SEGMENTS = 10.0
    def __init__(self, curve = []):
        self.curve = curve
    @classmethod
    def from_points(cls, cx1, cy1, cx2, cy2):
        subdiv_step = 1.0 / cls.BEZIER_SEGMENTS
        subdiv_step2 = subdiv_step * subdiv_step
        subdiv_step3 = subdiv_step2 * subdiv_step
        pre1 = 3 * subdiv_step
        pre2 = 3 * subdiv_step2
        pre4 = 6 * subdiv_step2
        pre5 = 6 * subdiv_step3
        tmp1x = -cx1 * 2 + cx2
        tmp1y = -cy1 * 2 + cy2
        tmp2x = (cx1 - cx2) * 3 + 1
        tmp2y = (cy1 - cy2) * 3 + 1
        return cls(
            [
                cx1 * pre1 + tmp1x * pre2 + tmp2x * subdiv_step3,
                cy1 * pre1 + tmp1y * pre2 + tmp2y * subdiv_step3,
                tmp1x * pre4 + tmp2x * pre5,
                tmp1y * pre4 + tmp2y * pre5,
                tmp2x * pre5,
                tmp2y * pre5
            ]
        )

    def interpolate(self, percent):
        (dfx, dfy, ddfx, ddfy, dddfx, dddfy) = [0 for _ in range(6 - len(self.curve))] + self.curve
        x = dfx
        y = dfy
        i = self.BEZIER_SEGMENTS - 2
        while True:
            if x >= percent:
                lastX = x - dfx
                lastY = y - dfy
                return lastY + (y - lastY) * (percent - lastX) / (x - lastX)
            if i == 0:
                break
            i -= 1
            dfx += ddfx
            dfy += ddfy
            ddfx += dddfx
            ddfy += dddfy
            x += dfx
            y += dfy
        return y + (1 - y) * (percent - x) / (1 - x) # Last point is 1,1

class LinearCurveData:
    def interpolate(self, percent):
        return percent

class SteppedCurveData: 
    def interpolate(self, _): return 0
    
class InterpolableKeyframe:
    class ScalarCouple:
        def __init__(self, iterator):
            self.inner = list(iterator)
            assert len(self.inner) == 2, "Use ScalarList"
        def lin_interpolate(self, other, perc):
            i1, i2 = self.inner
            o1, o2 = other.inner
            dt1, dt2 = i1 - o1, i2 - o2
            dt1 *= perc
            dt2 *= perc
            return o1 + dt1, o2 + dt2
        @property
        def naked_value(self):
            return self.inner

    class ScalarList:
        def __init__(self, iterator):
            self.inner = list(iterator)
        def lin_interpolate(self, other, perc):
            dt = (c1 - c2 for (c1, c2) in zip(self.inner, other.inner))
            scaled = (c * perc for c in dt)
            return [base + scale for (base, scale) in zip(other.inner, scaled)]
        @property
        def naked_value(self):
            return self.inner

    class BoundedAngularScalar:
        def __init__(self, number):
            self.number = number
        def lin_interpolate(self, other, perc):
            dt = self.number - other.number
            dt = mod_m180_p180(dt)
            scale = dt * perc
            return other.number + scale 
        @property
        def naked_value(self):
            return self.number

    class ValueList:
        def __init__(self, value):
            self.value = value
        def lin_interpolate(self, other, perc):
            #NOTE: we do loose a bit of performance for the sake of generality
            perc = int(perc) 
            if perc == 1:
                return self.value
            return other.value
        @property
        def naked_value(self):
            return self.value

    def __init__(self, time, curve, point):
        self.time = time
        self.curve = curve
        self.value = point
    def interpolate(self, last_frame, lin_percent):
        act_percent = last_frame.curve.interpolate(lin_percent)
        return self.value.lin_interpolate(last_frame.value, act_percent)

class InterpolableTimeline:
    def __init__(self):
        self.keyframes : list[InterpolableKeyframe] = [ ]

    @property
    def duration(self):
        return self.keyframes[-1].time

    @property
    def start(self):
        return self.keyframes[0].time    
    
    def get_curve_percent(self, keyframe_index, percent):
        curve = self.keyframes[keyframe_index].curve
        return curve.interpolate(percent)

    def get_keyframes(self, keyframe_list):
        for keyframe in keyframe_list:
            data = self.read_data(keyframe)
            curve = self.read_curve(keyframe)
            self.keyframes.append(
                InterpolableKeyframe(keyframe["time"], curve, data)
            )
        self.keyframes.sort(key=lambda x:x.time)

    def get_current(self, time):
        if time <= self.start:
            raise SoonError()
        elif time >= self.duration:
            return self.keyframes[-1].value.naked_value
            
        frame_i = binary_search(self.keyframes, time)
        last_frame = self.keyframes[frame_i - 1]
        curr_frame = self.keyframes[frame_i]
        percent = 1 - (time - curr_frame.time) / (last_frame.time - curr_frame.time) 
        percent = min(max(percent, 0), 1)
        return (curr_frame.interpolate(last_frame, percent))
    @staticmethod
    def read_curve(value_map : dict):
        curve = value_map.get('curve', 'linear')
        if curve == 'linear':
            return LinearCurveData()
        elif curve == 'stepped':
            return SteppedCurveData()
        return BezierCurveData.from_points(
            *(float(x) for x in curve)
        )

class RotateTimeline(InterpolableTimeline):
    def __init__(self):
        super().__init__()
        self.bone_index = 0

    @staticmethod
    def read_data(keyframe):
        return InterpolableKeyframe.BoundedAngularScalar(keyframe["angle"])

    def apply(self, skeleton, time, alpha):
        curr = self.get_current(time)

        bone = skeleton.bones[self.bone_index]

        amount = bone.data.rotation + curr - bone.rotation
        amount = mod_m180_p180(amount)
        new_rotation = bone.rotation + amount * alpha
        bone.rotation = new_rotation

class TranslateTimeline(InterpolableTimeline):
    def __init__(self):
        super().__init__()
        self.bone_index = 0
        
    @staticmethod
    def read_data(keyframe):
        x, y = keyframe["x"], keyframe["y"]
        return InterpolableKeyframe.ScalarCouple((x, y))

    def apply(self, skeleton, time, alpha):
        curr = self.get_current(time)

        bone = skeleton.bones[self.bone_index]

        bone.x = bone.x + (bone.data.x + curr[0] - bone.x) * alpha
        bone.y = bone.y + (bone.data.y + curr[1] - bone.y) * alpha

class ScaleTimeline(TranslateTimeline):
    def __init__(self):
        super().__init__()

    def apply(self, skeleton, time, alpha):
        curr = self.get_current(time)

        bone = skeleton.bones[self.bone_index]

        bone.scale_x = (bone.scale_x + (bone.data.scale_x - 1 + curr[0] - bone.scale_x) * alpha)
        bone.scale_y = (bone.scale_y + (bone.data.scale_y - 1 + curr[1] - bone.scale_y) * alpha)

class ColorTimeline(InterpolableTimeline):
    def __init__(self):
        super().__init__()
        self.LAST_FRAME_TIME = -5
        self.FRAME_SPACING = -self.LAST_FRAME_TIME
        self.FRAME_R = 1
        self.FRAME_G = 2
        self.FRAME_B = 3
        self.FRAME_A = 4
        self.keyframes = [0]  #FIXME
        self.slot_index = 0

        
    def get_keyframe_count(self):
        return len(self.keyframes) / self.FRAME_SPACING


    def set_keyframe(self, keyframe_index, time, r, g, b, a):
        keyframe_index *= self.FRAME_SPACING
        self.keyframes[keyframe_index] = time
        self.keyframes[keyframe_index + 1] = r
        self.keyframes[keyframe_index + 2] = g
        self.keyframes[keyframe_index + 3] = b
        self.keyframes[keyframe_index + 4] = a


    def apply(self, skeleton, time, alpha):
        if time < self.keyframes[0]: # Time is before first frame.
            return 
        
        slot = skeleton.slots[self.slot_index]
        
        if time >= self.keyframes[self.LAST_FRAME_TIME]:      # -5
            i = len(self.keyframes) - 1
            slot.r = self.keyframes[i - 3] # -4
            slot.g = self.keyframes[i - 2] # -3
            slot.b = self.keyframes[i - 1] # -2
            slot.a = self.keyframes[i] # -1
        
        # Interpolate between the last frame and the current frame.
        frame_index = binary_search(self.keyframes, time)
        lastFrameR = self.keyframes[frame_index - 4]
        lastFrameG = self.keyframes[frame_index - 3]
        lastFrameB = self.keyframes[frame_index - 2]
        lastFrameA = self.keyframes[frame_index - 1]
        frame_time = self.keyframes[frame_index]
        percent = 1 - (time - frame_time) / (self.keyframes[frame_index + self.LAST_FRAME_TIME] - frame_time)
        if percent < 0.0:
            percent = 0.0
        if percent > 255:
            percent = 255
        percent = self.interpolate(frame_index / self.FRAME_SPACING - 1, percent)

        r = lastFrameR + (self.keyframes[frame_index + self.FRAME_R] - lastFrameR) * percent
        g = lastFrameG + (self.keyframes[frame_index + self.FRAME_G] - lastFrameG) * percent
        b = lastFrameB + (self.keyframes[frame_index + self.FRAME_B] - lastFrameB) * percent
        a = lastFrameA + (self.keyframes[frame_index + self.FRAME_A] - lastFrameA) * percent
        if alpha < 1:
            slot.r += (r - slot.r) * alpha
            slot.g += (g - slot.g) * alpha
            slot.b += (b - slot.b) * alpha
            slot.a += (a - slot.a) * alpha
        else:
            slot.r = r
            slot.g = g
            slot.b = b
            slot.a = a
        return 

class AttachmentTimeline(InterpolableTimeline):
    def __init__(self):
        super().__init__()
        self.slot_index = 0
    @staticmethod
    def read_data(keyframe):
        return InterpolableKeyframe.ValueList(keyframe["name"])
    def apply(self, skeleton, time, alpha):
        curr = self.get_current(time)
        if curr is None: return
        skeleton.slots[self.slot_index].set_attachment(skeleton.get_attachment_by_index(self.slot_index, curr))        
