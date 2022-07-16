import math

class CurveTimeline:
    def __init__(self, keyframeCount):
        self.FRAME_SPACING = 6
        self.LINEAR = 0
        self.STEPPED = -1
        self.BEZIER_SEGMENTS = 10.0
        self.curves = [0] * ((keyframeCount - 1) * 6)


    def set_linear(self, keyframe_index):
        self.curves[keyframe_index * self.FRAME_SPACING] = self.LINEAR
        self.curves[keyframe_index * 6] = self.LINEAR


    def set_stepped(self, keyframe_index):
        self.curves[keyframe_index * self.FRAME_SPACING] = self.STEPPED
        self.curves[keyframe_index * 6] = self.STEPPED

    
    def set_curve(self, keyframe_index, cx1, cy1, cx2, cy2):
        subdiv_step = 1.0 / self.BEZIER_SEGMENTS
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
        i = keyframe_index * 6
        self.curves[i] = cx1 * pre1 + tmp1x * pre2 + tmp2x * subdiv_step3
        self.curves[i + 1] = cy1 * pre1 + tmp1y * pre2 + tmp2y * subdiv_step3
        self.curves[i + 2] = tmp1x * pre4 + tmp2x * pre5
        self.curves[i + 3] = tmp1y * pre4 + tmp2y * pre5
        self.curves[i + 4] = tmp2x * pre5
        self.curves[i + 5] = tmp2y * pre5


    def get_curve_percent(self, keyframe_index, percent):
        curveIndex = keyframe_index * self.FRAME_SPACING
        curveIndex = keyframe_index * 6
        curveIndex = int(curveIndex)
        dfx = self.curves[curveIndex]
        if dfx == self.LINEAR:
            return percent
        if dfx == self.STEPPED:
            return 0.0
        dfy = self.curves[curveIndex + 1]
        ddfx = self.curves[curveIndex + 2]
        ddfy = self.curves[curveIndex + 3]
        dddfx = self.curves[curveIndex + 4]
        dddfy = self.curves[curveIndex + 5]
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


def binary_search(values, target, step):
    low = 0
    high = int(len(values) / step - 2)
    if high == 0:
        return step
    current = int(high >> 1)
    while True:
        if values[(current + 1) * step] <= target:
            low = current + 1
        else:
            high = current
        if low == high:
            return (low + 1) * step
        current = int(math.floor((low + high) >> 1))
    return 0


class RotateTimeline(CurveTimeline):
    def __init__(self, keyframeCount):
        super().__init__(keyframeCount)
        self.LAST_FRAME_TIME = -2
        self.FRAME_SPACING = -self.LAST_FRAME_TIME
        self.FRAME_VALUE = 1
        self.frames = [0.0] * (keyframeCount * self.FRAME_SPACING)
        self.bone_index = 0
        
    
    def get_duration(self):
        return self.frames[self.LAST_FRAME_TIME]


    def get_keyframe_count(self):
        return len(self.frames) / self.FRAME_SPACING


    def set_keyframe(self, keyframe_index, time, value):
        keyframe_index *= self.FRAME_SPACING
        self.frames[keyframe_index] = time
        self.frames[keyframe_index + 1] = value


    def apply(self, skeleton, time, alpha):
        if time < self.frames[0]:
            return        

        bone = skeleton.bones[self.bone_index]

        if time >= self.frames[self.LAST_FRAME_TIME]: # Time is after last frame
            amount = bone.data.rotation + self.frames[-1] - bone.rotation
            while amount > 180:
                amount = amount - 360
            while amount < -180:
                amount = amount + 360
            bone.rotation = bone.rotation + amount * alpha
            return

        # Interpolate between the last frame and the current frame
        frame_index = binary_search(self.frames, time, self.FRAME_SPACING)
        last_frame_value = self.frames[frame_index - 1]
        frame_time = self.frames[frame_index]
        percent = 1.0 - (time - frame_time) / (self.frames[frame_index + self.LAST_FRAME_TIME] - frame_time)
        if percent < 0.0:
            percent = 0.0
        elif percent > 1.0:
            percent = 1.0
        percent = self.get_curve_percent(frame_index / self.FRAME_SPACING - 1, percent)

        amount = self.frames[frame_index + self.FRAME_VALUE] - last_frame_value
        while amount > 180:
            amount = amount - 360
        while amount < -180:
            amount = amount + 360
        amount = bone.data.rotation + (last_frame_value + amount * percent) - bone.rotation
        while amount > 180:
            amount = amount - 360
        while amount < -180:
            amount = amount + 360
        bone.rotation = bone.rotation + amount * alpha


class TranslateTimeline(CurveTimeline):
    def __init__(self, keyframeCount):
        super().__init__(keyframeCount)
        self.LAST_FRAME_TIME = -3
        self.FRAME_SPACING = -self.LAST_FRAME_TIME
        self.FRAME_X = 1
        self.FRAME_Y = 2
        self.frames = [0.0] * (keyframeCount * self.FRAME_SPACING)
        self.bone_index = 0
        
    def get_duration(self):
        return self.frames[self.LAST_FRAME_TIME]

    def get_keyframe_count(self):
        return len(self.frames) / self.FRAME_SPACING

    def set_keyframe(self, keyframe_index, time, x, y):
        keyframe_index = keyframe_index * self.FRAME_SPACING
        self.frames[keyframe_index] = time
        self.frames[keyframe_index + 1] = x
        self.frames[keyframe_index + 2] = y

    def apply(self, skeleton, time, alpha):
        if time < self.frames[0]: # Time is before the first frame
            return 
        
        bone = skeleton.bones[self.bone_index]
        
        if time >= self.frames[self.LAST_FRAME_TIME]: # Time is after the last frame.
            bone.x = bone.x + (bone.data.x + self.frames[self.LAST_FRAME_TIME + 1] - bone.x) * alpha
            bone.y = bone.y + (bone.data.y + self.frames[self.LAST_FRAME_TIME + 2] - bone.y) * alpha
            return 

        # Interpolate between the last frame and the current frame
        frame_index = binary_search(self.frames, time, self.FRAME_SPACING)
        last_frame_x = self.frames[frame_index - 2]
        last_frame_y = self.frames[frame_index - 1]
        frame_time = self.frames[frame_index]
        percent = 1.0 - (time - frame_time) / (self.frames[frame_index + self.LAST_FRAME_TIME] - frame_time)
        if percent < 0.0:
            percent = 0.0
        if percent > 1.0:
            percent = 1.0
        percent = self.get_curve_percent(frame_index / self.FRAME_SPACING - 1, percent)
        
        bone.x = bone.x + (bone.data.x + last_frame_x + (self.frames[frame_index + self.FRAME_X] - last_frame_x) * percent - bone.x) * alpha
        bone.y = bone.y + (bone.data.y + last_frame_y + (self.frames[frame_index + self.FRAME_Y] - last_frame_y) * percent - bone.y) * alpha

class ScaleTimeline(TranslateTimeline):
    def __init__(self, keyframeCount):
        super().__init__(keyframeCount)
        self.LAST_FRAME_TIME = -3
        self.FRAME_SPACING = -self.LAST_FRAME_TIME
        self.FRAME_X = 1
        self.FRAME_Y = 2

    def apply(self, skeleton, time, alpha):
        if time < self.frames[0]:
            return 
        
        bone = skeleton.bones[self.bone_index]
        if time >= self.frames[self.LAST_FRAME_TIME]: # Time is after last frame
            bone.scale_x += (bone.data.scale_x - 1 + self.frames[len(self.frames) - 2] - bone.scale_x) * alpha
            bone.scale_y += (bone.data.scale_y - 1 + self.frames[len(self.frames) - 1] - bone.scale_y) * alpha
            return
        
        # Interpolate between the last frame and the current frame
        frame_index = binary_search(self.frames, time, self.FRAME_SPACING)
        last_frame_x = self.frames[frame_index - 2]
        last_frame_y = self.frames[frame_index - 1]
        frame_time = self.frames[frame_index]
        percent = 1.0 - (time - frame_time) / (self.frames[frame_index + self.LAST_FRAME_TIME] - frame_time)
        if percent < 0.0:
            percent = 0.0
        elif percent > 1.0:
            percent = 1.0
        percent = self.get_curve_percent(frame_index / self.FRAME_SPACING - 1, percent)
        
        bone.scale_x += (bone.data.scale_x - 1 + last_frame_x + (self.frames[frame_index + self.FRAME_X] - last_frame_x) * percent - bone.scale_x) * alpha
        bone.scale_y += (bone.data.scale_y - 1 + last_frame_y + (self.frames[frame_index + self.FRAME_Y] - last_frame_y) * percent - bone.scale_y) * alpha
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
            return 
        
        # Interpolate between the last frame and the current frame.
        frame_index = binary_search(self.frames, time, self.FRAME_SPACING)
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
        self.LAST_FRAME_TIME = -1
        self.FRAME_SPACING = -self.LAST_FRAME_TIME
        self.frames = [0.0] * keyframeCount
        self.attachment_names = [None] * keyframeCount
        self.slot_index = 0
    
    def get_duration(self):
        return self.frames[self.LAST_FRAME_TIME]

    def get_keyframe_count(self):
        len(self.frames)

    def set_keyframe(self, keyframe_index, time, attachmentName):
        self.frames[keyframe_index] = time
        self.attachment_names[keyframe_index] = attachmentName

    def apply(self, skeleton, time, alpha):
        if time < self.frames[0]: # Time is before first frame            
            return 

        frame_index = 0
        if time >= self.frames[self.LAST_FRAME_TIME]: # Time is after last frame.
            frame_index = self.LAST_FRAME_TIME
        else:
            frame_index = binary_search(self.frames, time, self.FRAME_SPACING) - 1
        attachmentName = self.attachment_names[frame_index]
        skeleton.slots[self.slot_index].set_attachment(skeleton.get_attachment_by_index(self.slot_index, attachmentName))        
        return 



