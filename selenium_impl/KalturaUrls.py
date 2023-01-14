


class KalturaUrls:
    _BASE_KALTURA_VIDEO_URL = "https://cdnapisec.kaltura.com/p/{PID}/sp/{PID}00/playManifest/entryId/{entryId}/format/download/protocol/https/flavorParamIds/0"

    @property
    def BASE_KALTURA_VIDEO_URL(self):
        return self._BASE_KALTURA_VIDEO_URL


    def get_kaltura_video(self, PID, entryId):
        return self.BASE_KALTURA_VIDEO_URL.format(PID=PID, entryId=entryId)


    # @property
    # def COURSE_OUTLINE_BASE_URL(self: Edx):
    #     return self.COURSE_OUTLINE_BASE_URL
