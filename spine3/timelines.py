from collections import namedtuple
from enum import Enum, auto

FrameInfo = namedtuple("FrameInfo", ["time", "data"])

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

class CurveTimeline:
    def __init__(self, keyframeCount):
        self.curves : list[self.CurveData] = [
            LinearCurveData() for _ in range(keyframeCount)
        ]

    def set_linear(self, keyframe_index):
        self.curves[keyframe_index] = LinearCurveData()    

    def set_stepped(self, keyframe_index):
        self.curves[keyframe_index] = SteppedCurveData()

    def set_curve(self, keyframe_index, cx1, cy1, cx2, cy2):
        self.curves[keyframe_index] = BezierCurveData.from_points(
            cx1 = cx1, 
            cy1 = cy1, 
            cx2 = cx2, 
            cy2 = cy2
        )

    def get_curve_percent(self, keyframe_index, percent):
        curve = self.curves[keyframe_index]
        return curve.interpolate(percent)

def binary_search(values, target):
    import bisect
    idx =  bisect.bisect_left(values, target, key=lambda x: x.time)
    return idx

def mod_m180_p180(val):
    return (val + 180) % 360 - 180

class RotateTimeline(CurveTimeline):
    def __init__(self, keyframeCount):
        super().__init__(keyframeCount)
        self.frames : list[FrameInfo] = [None] * keyframeCount
        self.bone_index = 0
        
    def get_duration(self):
        return self.frames[-1].time

    def get_keyframe_count(self):
        return len(self.frames)

    def set_keyframe(self, keyframe_index, time, value):
        #keyframe_index *= self.FRAME_SPACING
        self.frames[keyframe_index] = FrameInfo(time = time, data = value)

    def apply(self, skeleton, time, alpha):
        if time < self.frames[0].time:
            return        

        bone = skeleton.bones[self.bone_index]

        if time >= self.frames[-1].time: # Time is after last frame
            amount = bone.data.rotation + self.frames[-1].data - bone.rotation
            amount = mod_m180_p180(amount)
            bone.rotation = bone.rotation + amount * alpha
            return

        # Interpolate between the last frame and the current frame
        frame_index = binary_search(self.frames, time)
        last_frame_value = self.frames[frame_index - 1].data
        frame_time = self.frames[frame_index].time
        percent = 1.0 - (time - frame_time) / (self.frames[frame_index - 1].time - frame_time)
        if percent < 0.0:
            percent = 0.0
        elif percent > 1.0:
            percent = 1.0
        percent = self.get_curve_percent(frame_index - 1, percent)

        amount = self.frames[frame_index].data - last_frame_value
        amount = mod_m180_p180(amount)
        amount = bone.data.rotation + (last_frame_value + amount * percent) - bone.rotation
        amount = mod_m180_p180(amount)
        bone.rotation = bone.rotation + amount * alpha

class TranslateTimeline(CurveTimeline):
    PositionFrame = namedtuple("PositionFrame", ["x", "y"])
    def __init__(self, keyframeCount):
        super().__init__(keyframeCount)
        self.frames = [None] * keyframeCount
        self.bone_index = 0
        
    def get_duration(self):
        return self.frames[-1].time

    def get_keyframe_count(self):
        return len(self.frames)

    def set_keyframe(self, keyframe_index, time, x, y):
        keyframe_index = keyframe_index
        self.frames[keyframe_index] = FrameInfo(
            time, 
            self.PositionFrame(x, y)
        )

    def apply(self, skeleton, time, alpha):
        if time < self.frames[0].time: # Time is before the first frame
            return 
        
        bone = skeleton.bones[self.bone_index]
        
        if time >= self.frames[-1].time: # Time is after the last frame.
            bone.x = bone.x + (bone.data.x + self.frames[-1].data.x - bone.x) * alpha
            bone.y = bone.y + (bone.data.y + self.frames[-1].data.y - bone.y) * alpha
            return 

        # Interpolate between the last frame and the current frame
        frame_index = binary_search(self.frames, time)
        last_frame_x = self.frames[frame_index - 1].data.x
        last_frame_y = self.frames[frame_index - 1].data.y
        frame_time = self.frames[frame_index].time
        percent = 1.0 - (time - frame_time) / (self.frames[frame_index - 1].time - frame_time)
        if percent < 0.0:
            percent = 0.0
        if percent > 1.0:
            percent = 1.0
        percent = self.get_curve_percent(frame_index - 1, percent)
        
        bone.x = bone.x + (bone.data.x + last_frame_x + (self.frames[frame_index].data.x - last_frame_x) * percent - bone.x) * alpha
        bone.y = bone.y + (bone.data.y + last_frame_y + (self.frames[frame_index].data.y - last_frame_y) * percent - bone.y) * alpha

class ScaleTimeline(TranslateTimeline):
    def __init__(self, keyframeCount):
        super().__init__(keyframeCount)

    def apply(self, skeleton, time, alpha):
        if time < self.frames[0].time:
            return 
        
        bone = skeleton.bones[self.bone_index]
        if time >= self.frames[-1].time: # Time is after last frame
            bone.scale_x += (bone.data.scale_x - 1 + self.frames[-1].data.x - bone.scale_x) * alpha
            bone.scale_y += (bone.data.scale_y - 1 + self.frames[-1].data.y - bone.scale_y) * alpha
            return
        
        # Interpolate between the last frame and the current frame
        frame_index = binary_search(self.frames, time)
        last_frame_x = self.frames[frame_index - 1].data.x
        last_frame_y = self.frames[frame_index - 1].data.y
        frame_time = self.frames[frame_index].time
        percent = 1.0 - (time - frame_time) / (self.frames[frame_index - 1].time - frame_time)
        if percent < 0.0:
            percent = 0.0
        elif percent > 1.0:
            percent = 1.0
        percent = self.get_curve_percent(frame_index - 1, percent)
        
        bone.scale_x += (
            bone.data.scale_x - 1 + last_frame_x + (self.frames[frame_index].data.x - last_frame_x) * percent - bone.scale_x
        ) * alpha
        bone.scale_y += (
            bone.data.scale_y - 1 + last_frame_y + (self.frames[frame_index].data.y - last_frame_y) * percent - bone.scale_y
        ) * alpha
        return 

class ColorTimeline(CurveTimeline):
    def __init__(self, keyframeCount):
        super().__init__(keyframeCount)
        self.LAST_FRAME_TIME = -5
        self.FRAME_SPACING = -self.LAST_FRAME_TIME
        self.FRAME_R = 1
        self.FRAME_G = 2
        self.FRAME_B = 3
        self.FRAME_A = 4
        self.frames = [0] * (keyframeCount * self.FRAME_SPACING)
        self.slot_index = 0

        
    def get_duration(self):
        return self.frames[self.LAST_FRAME_TIME]


    def get_keyframe_count(self):
        return len(self.frames) / self.FRAME_SPACING


    def set_keyframe(self, keyframe_index, time, r, g, b, a):
        keyframe_index *= self.FRAME_SPACING
        self.frames[keyframe_index] = time
        self.frames[keyframe_index + 1] = r
        self.frames[keyframe_index + 2] = g
        self.frames[keyframe_index + 3] = b
        self.frames[keyframe_index + 4] = a


    def apply(self, skeleton, time, alpha):
        if time < self.frames[0]: # Time is before first frame.
            return 
        
        slot = skeleton.slots[self.slot_index]
        
        if time >= self.frames[self.LAST_FRAME_TIME]:      # -5
            i = len(self.frames) - 1
            slot.r = self.frames[i - 3] # -4
            slot.g = self.frames[i - 2] # -3
            slot.b = self.frames[i - 1] # -2
            slot.a = self.frames[i] # -1
        
        # Interpolate between the last frame and the current frame.
        frame_index = binary_search(self.frames, time)
        lastFrameR = self.frames[frame_index - 4]
        lastFrameG = self.frames[frame_index - 3]
        lastFrameB = self.frames[frame_index - 2]
        lastFrameA = self.frames[frame_index - 1]
        frame_time = self.frames[frame_index]
        percent = 1 - (time - frame_time) / (self.frames[frame_index + self.LAST_FRAME_TIME] - frame_time)
        if percent < 0.0:
            percent = 0.0
        if percent > 255:
            percent = 255
        percent = self.get_curve_percent(frame_index / self.FRAME_SPACING - 1, percent)

        r = lastFrameR + (self.frames[frame_index + self.FRAME_R] - lastFrameR) * percent
        g = lastFrameG + (self.frames[frame_index + self.FRAME_G] - lastFrameG) * percent
        b = lastFrameB + (self.frames[frame_index + self.FRAME_B] - lastFrameB) * percent
        a = lastFrameA + (self.frames[frame_index + self.FRAME_A] - lastFrameA) * percent
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

class AttachmentTimeline:
    def __init__(self, keyframeCount):
        self.frames = [None] * keyframeCount
        self.slot_index = 0
    
    def get_duration(self):
        return self.frames[-1].time

    def get_keyframe_count(self):
        return len(self.frames)

    def set_keyframe(self, keyframe_index, time, attachmentName):
        self.frames[keyframe_index] = FrameInfo(time, attachmentName)

    def apply(self, skeleton, time, alpha):
        if time < self.frames[0].time: # Time is before first frame            
            return 

        frame_index = 0
        if time >= self.frames[-1].time: # Time is after last frame.
            frame_index = -1
        else:
            frame_index = binary_search(self.frames, time)
        attachmentName = self.frames[frame_index].data
        skeleton.slots[self.slot_index].set_attachment(skeleton.get_attachment_by_index(self.slot_index, attachmentName))        
        return 
